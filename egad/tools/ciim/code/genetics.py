"""genetics.py — GWAS and genetic variant analysis tools for immune research.

Main entry points
-----------------
phewas_opengwas(snps, pval=5e-8)
    Query OpenGWAS for all GWAS associations of a list of SNPs (PheWAS).

query_gwas_catalog(snps, ukb_only=False)
    Look up SNPs in the locally cached GWAS Catalog (622k entries, ~64k UKB).

query_opentarget_platform(query, variables, verbose)
    Direct GraphQL caller for the Open Targets Platform API (v4, post-July 2025).
    Replaces the deprecated query_opentarget from the biomni package.

get_disease_credible_sets(efo_id, page_size, max_pages, l2g_min_score)
    Retrieve all GWAS credible sets + L2G predictions for a disease from OT Platform.

run_coloc(gene, chr, pos, outdir, **kwargs)
    GWAS × eQTL colocalization for a single locus (coloc.abf + coloc.susie).
    Wraps tools/ciim/code/coloc.R via ${CIIM_SINGULARITY_DIR}/genotype.sif.

run_mr(gene, mode, outdir, **kwargs)
    Mendelian Randomization in two modes:
      mode='eqtl'     — DICE/generic eQTL instruments → local GWAS outcome.
                        Requires chr, pos (locus centre). All GWAS/eQTL kwargs
                        same as run_coloc. Additional: pval_iv, pval_iv_fb,
                        clump_r2, clump_kb.
      mode='opengwas' — 2-sample MR via OpenGWAS API. Python fetches top hits
                        for the exposure study and matches them in the outcome
                        study, then harmonises alleles before calling mr.R.
                        Requires exposure_id, outcome_id. Optional:
                        pval_iv, exposure_label, outcome_label.
    Wraps tools/ciim/code/mr.R via ${CIIM_SINGULARITY_DIR}/genotype.sif.
"""

import os
import subprocess
import time
import pickle
import tempfile

import pandas as pd
import requests

# ── paths ─────────────────────────────────────────────────────────────────────
_ROOT       = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
_ENV_FILE   = os.path.join(_ROOT, '.env')
_GWAS_PKL   = os.path.join(_ROOT, 'datalake', 'biomni', 'gwas_catalog.pkl')
_OPENGWAS_URL    = 'https://api.opengwas.io/api/phewas'
_OT_PLATFORM_URL = 'https://api.platform.opentargets.org/api/v4/graphql'

# ── Open Targets Platform — GraphQL query templates ───────────────────────────
# Note: Platform uses MONDO IDs (e.g. MONDO_0007915 for SLE). EFO IDs may work
# for disease() lookup but MONDO is canonical for studies(diseaseIds: ...).

_DISEASE_STUDIES_QUERY = """
query DiseaseStudies($diseaseId: String!, $pageIndex: Int!, $pageSize: Int!) {
  studies(
    diseaseIds: [$diseaseId]
    enableIndirect: true
    page: {index: $pageIndex, size: $pageSize}
  ) {
    count
    rows {
      id
      traitFromSource
      publicationFirstAuthor
      publicationDate
      nSamples
      studyType
    }
  }
}
"""

_CREDIBLE_SETS_QUERY = """
query CredibleSetsForStudies($studyIds: [String!]!, $pageIndex: Int!, $pageSize: Int!) {
  credibleSets(
    studyIds: $studyIds
    page: {index: $pageIndex, size: $pageSize}
  ) {
    count
    rows {
      studyLocusId
      studyId
      chromosome
      position
      pValueMantissa
      pValueExponent
      beta
      standardError
      finemappingMethod
      variant {
        id
        rsIds
        referenceAllele
        alternateAllele
      }
      study {
        traitFromSource
        publicationFirstAuthor
        publicationDate
        nSamples
      }
      l2GPredictions {
        count
        rows {
          score
          target {
            id
            approvedSymbol
          }
          features {
            name
            shapValue
            value
          }
        }
      }
    }
  }
}
"""

# ── auth ──────────────────────────────────────────────────────────────────────
def _load_token():
    """Read OPENGWAS_TOKEN from .env file."""
    if not os.path.exists(_ENV_FILE):
        raise FileNotFoundError(
            f".env not found at {_ENV_FILE}. "
            "Register at https://api.opengwas.io/ and store your token as "
            "OPENGWAS_TOKEN=<token> in that file."
        )
    for line in open(_ENV_FILE):
        line = line.strip()
        if line.startswith('OPENGWAS_TOKEN='):
            return line.split('=', 1)[1].strip()
    raise ValueError("OPENGWAS_TOKEN not found in .env file.")


# ── public API ────────────────────────────────────────────────────────────────
def phewas_opengwas(
    snps,
    pval=5e-8,
    batch_size=30,
    sleep=1.0,
    drop_expression=True,
):
    """Query OpenGWAS PheWAS for a list of SNPs across all indexed GWAS studies.

    Covers Neale Lab UKB (~4,000 phenotypes), Pan-UKBB, IEU curated studies, and
    >10,000 other published GWAS. Requires a JWT token in .env (free registration
    at https://api.opengwas.io/).

    Parameters
    ----------
    snps : list[str]
        rsID strings, e.g. ['rs10944479', 'rs1004870'].
    pval : float, optional
        P-value threshold for returned associations (default 5e-8).
    batch_size : int, optional
        Number of SNPs per API request (default 30, max ~50 before timeouts).
    sleep : float, optional
        Seconds to wait between batches to avoid rate limits (default 1.0).
    drop_expression : bool, optional
        If True (default), drop eQTL / expression studies (traits that are
        ENSG IDs or study IDs starting with 'eqtl-', 'met-', 'prot-').

    Returns
    -------
    pd.DataFrame
        Columns: rsid, id (study), trait, chr, position, ea, nea, eaf,
                 beta, se, p, n, is_ukb.
        One row per SNP × study association.

    Examples
    --------
    >>> from genetics import phewas_opengwas
    >>> hits = phewas_opengwas(['rs10944479', 'rs1004870'], pval=1e-5)
    >>> hits[hits['is_ukb']].sort_values('p').head(10)
    """
    token = _load_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    snps = list(snps)
    all_hits = []

    for i in range(0, len(snps), batch_size):
        batch = snps[i:i + batch_size]
        try:
            r = requests.post(
                _OPENGWAS_URL,
                headers=headers,
                json={'variant': batch, 'pval': pval},
                timeout=90,
            )
            data = r.json()
            if isinstance(data, list):
                all_hits.extend(data)
            else:
                msg = data.get('message', str(data))
                print(f"[phewas_opengwas] batch {i//batch_size+1} warning: {msg}")
        except Exception as exc:
            print(f"[phewas_opengwas] batch {i//batch_size+1} error: {exc}")
        if i + batch_size < len(snps):
            time.sleep(sleep)

    if not all_hits:
        return pd.DataFrame()

    df = pd.DataFrame(all_hits)

    # Flag UKB studies
    df['is_ukb'] = df['id'].str.startswith(('ukb-', 'ieu-b-'), na=False)

    if drop_expression:
        expr_mask = (
            df['trait'].str.startswith('ENSG', na=False) |
            df['id'].str.startswith(('eqtl-', 'met-', 'prot-'), na=False)
        )
        df = df[~expr_mask].reset_index(drop=True)

    return df


def query_gwas_catalog(snps, ukb_only=False):
    """Look up SNPs in the locally cached GWAS Catalog (622k entries).

    The catalog covers genome-wide significant (p<5e-8) associations from
    published papers. UKB-tagged entries (~64k) can be selected with
    ``ukb_only=True``. For broader UKB coverage use ``phewas_opengwas`` instead.

    Parameters
    ----------
    snps : list[str]
        rsID strings.
    ukb_only : bool, optional
        If True, restrict to entries mentioning 'UK Biobank' or 'British' in
        the sample description (default False).

    Returns
    -------
    pd.DataFrame
        Subset of GWAS Catalog rows matching the requested SNPs, sorted by
        descending -log10(p).

    Examples
    --------
    >>> from genetics import query_gwas_catalog
    >>> hits = query_gwas_catalog(['rs10944479', 'rs1004870'])
    >>> hits[['SNPS', 'DISEASE/TRAIT', 'PVALUE_MLOG']].head()
    """
    if not os.path.exists(_GWAS_PKL):
        raise FileNotFoundError(f"GWAS Catalog pickle not found at {_GWAS_PKL}")

    gwas = pickle.load(open(_GWAS_PKL, 'rb'))
    hits = gwas[gwas['SNPS'].isin(snps)].copy()

    if ukb_only:
        ukb_mask = (
            hits['INITIAL SAMPLE SIZE'].str.contains('UK Biobank|UKB|British', na=False, case=False) |
            hits['STUDY'].str.contains('UK Biobank|UKB', na=False, case=False)
        )
        hits = hits[ukb_mask]

    return hits.sort_values('PVALUE_MLOG', ascending=False).reset_index(drop=True)


# ── Open Targets Platform (post-July 2025) ────────────────────────────────────

def query_opentarget_platform(query, variables=None, verbose=False):
    """Direct GraphQL caller for the Open Targets Platform API (v4).

    Replaces the deprecated query_opentarget from tools/biomni/database_biomni.py.
    The Genetics Portal (genetics.opentargets.org) was shut down on 9 July 2025;
    all GWAS, credible-set, and L2G data now lives in the unified Platform API.

    Parameters
    ----------
    query : str
        GraphQL query string.
    variables : dict, optional
        Variable bindings for the query.
    verbose : bool, optional
        Print request URL and response status.

    Returns
    -------
    dict
        Parsed JSON response. Raises ValueError if the response contains
        GraphQL errors.

    Examples
    --------
    >>> from genetics import query_opentarget_platform
    >>> q = 'query { disease(efoId: "EFO_0002690") { name } }'
    >>> result = query_opentarget_platform(q)
    >>> result['data']['disease']['name']
    'systemic lupus erythematosus'
    """
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    if verbose:
        print(f"[OT Platform] POST {_OT_PLATFORM_URL}")
        print(f"[OT Platform] variables: {variables}")

    r = requests.post(
        _OT_PLATFORM_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    r.raise_for_status()
    result = r.json()

    if verbose:
        print(f"[OT Platform] HTTP {r.status_code}")

    if "errors" in result:
        raise ValueError(f"GraphQL errors: {result['errors']}")

    return result


def get_disease_credible_sets(disease_id, page_size=50, max_cs_pages=20, l2g_min_score=0.0,
                               study_batch_size=20):
    """Retrieve GWAS credible sets and L2G predictions for a disease.

    Two-step workflow against the Open Targets Platform (v25+):
      1. Fetch all GWAS study IDs for the disease via studies(diseaseIds=...).
      2. Fetch credible sets for those studies in batches via credibleSets(studyIds=...),
         with L2G predictions (target, score, SHAP features) per locus.

    Parameters
    ----------
    disease_id : str
        MONDO or EFO disease ID. Use MONDO IDs for best coverage
        (e.g. 'MONDO_0007915' for SLE, 'MONDO_0008383' for RA).
        Search IDs at: platform.opentargets.org or via the search query below.
    page_size : int, optional
        Credible sets per API page (default 50).
    max_cs_pages : int, optional
        Maximum credible set pages per study batch (default 20 = up to 1000 per batch).
    l2g_min_score : float, optional
        Minimum L2G score to include (default 0.0 = all predictions).
    study_batch_size : int, optional
        How many study IDs to send per credibleSets request (default 20).

    Returns
    -------
    pd.DataFrame
        One row per (credible_set × gene) pair. Columns:
        study_locus_id, study_id, trait, author, pub_date, n_samples,
        variant_id, rsids, chromosome, position, ref, alt,
        pval_mantissa, pval_exponent, beta, se, finemapping_method,
        l2g_n_genes, gene_id, gene_symbol, l2g_score,
        shap_features (list of {name, shapValue, value}).

    Examples
    --------
    >>> from genetics import get_disease_credible_sets
    >>> df = get_disease_credible_sets('MONDO_0007915', l2g_min_score=0.5)
    >>> df.sort_values('l2g_score', ascending=False).head(10)
    """
    # ── Step 1: collect all GWAS study IDs for the disease ───────────────────
    study_ids = []
    study_meta = {}
    page_idx = 0
    while True:
        result = query_opentarget_platform(
            _DISEASE_STUDIES_QUERY,
            variables={"diseaseId": disease_id, "pageIndex": page_idx, "pageSize": 100},
        )
        studies_block = (result.get("data") or {}).get("studies") or {}
        total_studies = studies_block.get("count", 0)
        study_rows = studies_block.get("rows") or []
        if not study_rows:
            break
        for s in study_rows:
            if s.get("studyType") == "gwas":
                sid = s["id"]
                study_ids.append(sid)
                study_meta[sid] = {
                    "trait":    s.get("traitFromSource"),
                    "author":   s.get("publicationFirstAuthor"),
                    "pub_date": s.get("publicationDate"),
                    "n_samples": s.get("nSamples"),
                }
        fetched = page_idx * 100 + len(study_rows)
        if fetched >= total_studies:
            break
        page_idx += 1

    print(f"[OT Platform] {disease_id}: {len(study_ids)} GWAS studies found")

    # ── Step 2: fetch credible sets in study batches ──────────────────────────
    rows = []
    for batch_start in range(0, len(study_ids), study_batch_size):
        batch_ids = study_ids[batch_start:batch_start + study_batch_size]
        cs_page = 0
        cs_total = None

        while cs_page < max_cs_pages:
            result = query_opentarget_platform(
                _CREDIBLE_SETS_QUERY,
                variables={"studyIds": batch_ids, "pageIndex": cs_page, "pageSize": page_size},
            )
            cs_block = (result.get("data") or {}).get("credibleSets") or {}
            if cs_total is None:
                cs_total = cs_block.get("count", 0)
            cs_rows = cs_block.get("rows") or []
            if not cs_rows:
                break

            for cs in cs_rows:
                variant = cs.get("variant") or {}
                study   = cs.get("study") or {}
                sid     = cs.get("studyId", "")
                meta    = study_meta.get(sid, {})
                base = {
                    "study_locus_id":     cs.get("studyLocusId"),
                    "study_id":           sid,
                    "trait":              study.get("traitFromSource") or meta.get("trait"),
                    "author":             study.get("publicationFirstAuthor") or meta.get("author"),
                    "pub_date":           study.get("publicationDate") or meta.get("pub_date"),
                    "n_samples":          study.get("nSamples") or meta.get("n_samples"),
                    "variant_id":         variant.get("id"),
                    "rsids":              variant.get("rsIds"),
                    "chromosome":         cs.get("chromosome"),
                    "position":           cs.get("position"),
                    "ref":                variant.get("referenceAllele"),
                    "alt":                variant.get("alternateAllele"),
                    "pval_mantissa":      cs.get("pValueMantissa"),
                    "pval_exponent":      cs.get("pValueExponent"),
                    "beta":               cs.get("beta"),
                    "se":                 cs.get("standardError"),
                    "finemapping_method": cs.get("finemappingMethod"),
                }

                l2g_block = cs.get("l2GPredictions") or {}
                base["l2g_n_genes"] = l2g_block.get("count", 0)
                l2g_preds = l2g_block.get("rows") or []

                if not l2g_preds:
                    rows.append({**base, "gene_id": None, "gene_symbol": None,
                                 "l2g_score": None, "shap_features": None})
                else:
                    for pred in l2g_preds:
                        score = pred.get("score") or 0.0
                        if score >= l2g_min_score:
                            tgt = pred.get("target") or {}
                            rows.append({
                                **base,
                                "gene_id":      tgt.get("id"),
                                "gene_symbol":  tgt.get("approvedSymbol"),
                                "l2g_score":    score,
                                "shap_features": pred.get("features"),
                            })

            fetched = cs_page * page_size + len(cs_rows)
            if fetched >= (cs_total or 0):
                break
            cs_page += 1

        print(f"[OT Platform]   studies {batch_start+1}–{batch_start+len(batch_ids)}: "
              f"{cs_total} credible sets")

    return pd.DataFrame(rows)


# ── Colocalization ─────────────────────────────────────────────────────────────

def run_coloc(gene, chr, pos, outdir, **kwargs):
    """Run GWAS × eQTL colocalization for a single locus (coloc.abf + coloc.susie).

    Wraps ${CIIM_TEMP_DIR}/coloc/coloc.R executed inside ${CIIM_SINGULARITY_DIR}/genotype.sif (R 4.5,
    coloc, susieR, data.table, ggplot2, plink). Defaults target the SLE Bentham
    2015 GWAS against the DICE immune-cell eQTL atlas (15 cell types).

    Parameters
    ----------
    gene : str
        Gene symbol, e.g. 'IRF5'.
    chr : int
        Chromosome number.
    pos : int
        Lead-SNP position in bp (locus centre).
    outdir : str
        Output directory (created if absent).
    **kwargs
        Any coloc.R flag without the leading '--'. Key options:

        GWAS
          gwas_file  : path to harmonised GWAS .tsv.gz
                       (cols: hm_chrom, hm_pos, hm_rsid, hm_beta,
                              standard_error, p_value, hm_code)
          gwas_n     : total sample size            (default 14267)
          gwas_s     : proportion cases, cc only    (default 0.3645)
          gwas_type  : 'cc' or 'quant'             (default 'cc')

        eQTL
          eqtl_dir    : directory of per-cell-type eQTL files
          eqtl_n      : eQTL sample size            (default 91)
          eqtl_sdy    : expression SD               (default 1)
          eqtl_format : 'dice_vcf' or 'generic_tsv' (default 'dice_vcf')

        generic_tsv column names (only when eqtl_format='generic_tsv')
          col_gene, col_rsid, col_beta, col_se, col_pval

        LD reference
          kg_bfile : plink bfile prefix  (default bundled 1KG EUR)
          plink    : plink binary path   (default 'plink')

        Locus
          lead_rsid : rsID for regional plots only
          window    : half-width in bp  (default 1e6)
          susie_n   : top N cell types for coloc.susie (default 5)

    Returns
    -------
    str
        Path to outdir. Key output files:
        - coloc_abf_{gene}_results.csv       PP.H0–H4 per cell type
        - coloc_susie_{gene}_results.csv     SuSiE signals (when present)
        - coloc_abf_{gene}_PP.H4_barplot.png
        - coloc_abf_{gene}_posteriors_stacked.png
        - regional_gwas_{gene}.png
        - regional_eqtl_{top_cell_type}_{gene}.png

    Examples
    --------
    >>> from genetics import run_coloc
    >>> run_coloc('IRF5', chr=7, pos=128954129, outdir='/tmp/coloc_irf5',
    ...           lead_rsid='rs10488631')
    '/tmp/coloc_irf5'

    >>> # Different GWAS + GTEx-style TSV eQTL
    >>> run_coloc('PTPN22', chr=1, pos=114377568, outdir='/tmp/coloc_ptpn22',
    ...           gwas_file='/path/to/ra_gwas.tsv.gz', gwas_n=58284,
    ...           gwas_s=0.25, eqtl_dir='/path/to/gtex_whole_blood',
    ...           eqtl_format='generic_tsv', eqtl_n=670,
    ...           col_gene='gene_name', col_rsid='variant_id',
    ...           col_beta='slope', col_se='slope_se', col_pval='pval_nominal')
    '/tmp/coloc_ptpn22'
    """
    coloc_r = os.path.join(_ROOT, 'tools', 'ciim', 'code', 'coloc.R')
    sif     = os.path.join(_ROOT, 'singularity', 'genotype.sif')

    cmd = [
        'singularity', 'exec',
        '--bind', '/vol/projects:/vol/projects',
        sif,
        'Rscript', coloc_r,
        '--gene',   str(gene),
        '--chr',    str(chr),
        '--pos',    str(pos),
        '--outdir', str(outdir),
    ]

    _flag_map = {
        'lead_rsid':   '--lead_rsid',
        'window':      '--window',
        'susie_n':     '--susie_n',
        'gwas_file':   '--gwas_file',
        'gwas_n':      '--gwas_n',
        'gwas_s':      '--gwas_s',
        'gwas_type':   '--gwas_type',
        'eqtl_dir':    '--eqtl_dir',
        'eqtl_n':      '--eqtl_n',
        'eqtl_sdy':    '--eqtl_sdy',
        'eqtl_format': '--eqtl_format',
        'col_gene':    '--col_gene',
        'col_rsid':    '--col_rsid',
        'col_beta':    '--col_beta',
        'col_se':      '--col_se',
        'col_pval':    '--col_pval',
        'kg_bfile':    '--kg_bfile',
        'plink':       '--plink',
    }
    for key, flag in _flag_map.items():
        if key in kwargs and kwargs[key] is not None:
            cmd += [flag, str(kwargs[key])]

    subprocess.run(cmd, check=True)
    return str(outdir)


# ── Mendelian Randomization ───────────────────────────────────────────────────

_OPENGWAS_TOPHITS_URL = 'https://api.opengwas.io/api/tophits/{study_id}'
_OPENGWAS_ASSOC_URL   = 'https://api.opengwas.io/api/associations'

_COMPLEMENTS = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}


def _complement(allele):
    return _COMPLEMENTS.get(allele.upper(), allele)


def _harmonize_alleles(exp_df, out_df):
    """Merge exposure + outcome by SNP and harmonise effect-allele direction.

    Parameters
    ----------
    exp_df : pd.DataFrame  — snp, beta_exp, se_exp, ea_exp, nea_exp, eaf_exp
    out_df : pd.DataFrame  — snp, beta_out, se_out, ea_out, nea_out, eaf_out

    Returns
    -------
    pd.DataFrame with columns: snp, beta_exp, se_exp, ea_exp, nea_exp,
                                beta_out, se_out, ea_out, nea_out, eaf_exp, eaf_out
    """
    df = pd.merge(exp_df, out_df, on='snp', how='inner')
    if df.empty:
        return df

    keep = []
    for _, row in df.iterrows():
        ea_e = str(row['ea_exp']).upper()
        nea_e = str(row['nea_exp']).upper()
        ea_o = str(row['ea_out']).upper()
        nea_o = str(row['nea_out']).upper()

        palindromic = (ea_e == _complement(nea_e))

        if palindromic:
            eaf_e = row.get('eaf_exp', float('nan'))
            eaf_o = row.get('eaf_out', float('nan'))
            try:
                eaf_e, eaf_o = float(eaf_e), float(eaf_o)
                if abs(eaf_e - 0.5) < 0.1:
                    continue  # ambiguous
                # flip if EAFs are discordant
                if abs((1 - eaf_e) - eaf_o) < abs(eaf_e - eaf_o):
                    df.at[_, 'beta_exp'] = -row['beta_exp']
                # else: same direction
                keep.append(_)
            except (ValueError, TypeError):
                continue  # can't resolve palindromic without EAF
        else:
            ea_e_c = _complement(ea_e)
            if ea_e == ea_o or ea_e_c == ea_o:
                keep.append(_)
            elif ea_e == nea_o or ea_e_c == nea_o:
                df.at[_, 'beta_exp'] = -row['beta_exp']
                keep.append(_)
            # else: incompatible alleles — drop

    return df.loc[keep].reset_index(drop=True)


def _fetch_tophits(study_id, token, pval=5e-8):
    """Fetch LD-clumped top hits for an OpenGWAS study.

    Returns
    -------
    pd.DataFrame — snp, beta, se, ea, nea, eaf, p, n, study_id
    """
    url = _OPENGWAS_TOPHITS_URL.format(study_id=study_id)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    r = requests.get(url, headers=headers, params={'pval': pval}, timeout=120)
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # Normalise column names from OpenGWAS response
    rename = {'rsid': 'snp', 'effect_allele': 'ea', 'other_allele': 'nea',
              'effect_allele_frequency': 'eaf', 'beta': 'beta', 'se': 'se', 'p': 'p'}
    df = df.rename(columns=rename)
    # Ensure required columns exist
    for col in ('snp', 'beta', 'se', 'ea', 'nea'):
        if col not in df.columns:
            raise ValueError(f"OpenGWAS tophits for {study_id} missing column '{col}'")
    if 'eaf' not in df.columns:
        df['eaf'] = float('nan')
    df['study_id'] = study_id
    return df[['snp', 'beta', 'se', 'ea', 'nea', 'eaf', 'p', 'study_id']].dropna(subset=['snp'])


def _fetch_associations(study_id, snps, token, batch_size=100, sleep=1.0):
    """Fetch SNP–study associations from OpenGWAS for a list of rsIDs.

    Returns
    -------
    pd.DataFrame — snp, beta, se, ea, nea, eaf, p, study_id
    """
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    all_rows = []
    for i in range(0, len(snps), batch_size):
        batch = snps[i:i + batch_size]
        try:
            r = requests.post(
                _OPENGWAS_ASSOC_URL,
                headers=headers,
                json={'id': [study_id], 'variant': batch},
                timeout=120,
            )
            data = r.json()
            if isinstance(data, list):
                all_rows.extend(data)
        except Exception as exc:
            print(f'[run_mr] associations batch {i // batch_size + 1} error: {exc}')
        if i + batch_size < len(snps):
            time.sleep(sleep)

    if not all_rows:
        return pd.DataFrame()
    df = pd.DataFrame(all_rows)
    rename = {'rsid': 'snp', 'effect_allele': 'ea', 'other_allele': 'nea',
              'effect_allele_frequency': 'eaf'}
    df = df.rename(columns=rename)
    for col in ('snp', 'beta', 'se', 'ea', 'nea'):
        if col not in df.columns:
            df[col] = float('nan') if col not in ('snp', 'ea', 'nea') else ''
    if 'eaf' not in df.columns:
        df['eaf'] = float('nan')
    df['study_id'] = study_id
    return df[['snp', 'beta', 'se', 'ea', 'nea', 'eaf', 'study_id']].dropna(subset=['snp'])


def _load_dice_vcf_locus(gene, vcf_path, chr, pos, window=1_000_000):
    """Load a DICE eQTL VCF for one gene/locus → standardised DataFrame.

    Returns columns: snp, beta_exp, se_exp, ea_exp, nea_exp, pval_exp
    (ea_exp = ALT allele in DICE convention = effect allele)
    """
    import io
    win_start = int(pos - window)
    win_end   = int(pos + window)
    awk = (
        f"awk 'NR==1 || "
        f"(/GeneSymbol={gene};/ && "
        f"($1==\"chr{chr}\" || $1==\"{chr}\") && "
        f"$2>={win_start} && $2<={win_end})'"
    )
    cmd = f"zcat {vcf_path} | grep -v '^##' | {awk}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        return None
    df = pd.read_csv(io.StringIO(result.stdout), sep='\t')
    if '#CHROM' in df.columns:
        df.rename(columns={'#CHROM': 'CHROM'}, inplace=True)
    info = df['INFO']
    df['beta_exp'] = info.str.extract(r'Beta=([^;]+)', expand=False).astype(float)
    df['stat']     = info.str.extract(r'Statistic=([^;]+)', expand=False).astype(float)
    df['pval_exp'] = info.str.extract(r'Pvalue=([^;]+)', expand=False).astype(float)
    df['se_exp']   = (df['beta_exp'] / df['stat']).abs()
    df = df.rename(columns={'ID': 'snp', 'REF': 'nea_exp', 'ALT': 'ea_exp'})
    df = df[['snp', 'beta_exp', 'se_exp', 'ea_exp', 'nea_exp', 'pval_exp']]
    df = df[df['snp'].notna() & (df['snp'] != '.') & (df['snp'] != '')]
    df = df[df['se_exp'] > 0].drop_duplicates('snp')
    return df


def _load_gwas_locus(gwas_file, chr, pos, window=1_000_000):
    """Load a harmonised GWAS TSV for one locus → standardised DataFrame.

    Expects NHGRI-EBI harmonised format (hm_rsid, hm_beta, standard_error, …).
    Returns columns: snp, beta_out, se_out, ea_out, nea_out, eaf_out
    """
    import io
    win_start = int(pos - window)
    win_end   = int(pos + window)
    cmd = (
        f"zcat {gwas_file} | "
        f"awk 'NR==1 || ($3=={chr} && $4>={win_start} && $4<={win_end})'"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        return None
    df = pd.read_csv(io.StringIO(result.stdout), sep='\t')
    df = df[df['hm_code'].isin([10, 11])]
    df = df[df['hm_rsid'].notna() & (df['hm_rsid'] != '') & (df['hm_rsid'] != 'NA')]
    df = df.drop_duplicates('hm_rsid')
    return df.rename(columns={
        'hm_rsid':                    'snp',
        'hm_beta':                    'beta_out',
        'standard_error':             'se_out',
        'hm_effect_allele':           'ea_out',
        'hm_other_allele':            'nea_out',
        'hm_effect_allele_frequency': 'eaf_out',
    })[['snp', 'beta_out', 'se_out', 'ea_out', 'nea_out', 'eaf_out']]


def _call_mr_r(gene, outdir, exposure_file, outcome_file, **kwargs):
    """Call mr.R with pre-formatted exposure/outcome CSVs."""
    mr_r = os.path.join(_ROOT, 'tools', 'ciim', 'code', 'mr.R')
    sif  = os.path.join(_ROOT, 'singularity', 'genotype.sif')

    cmd = [
        'singularity', 'exec',
        '--bind', '/vol/projects:/vol/projects',
        sif, 'Rscript', mr_r,
        '--gene',          str(gene),
        '--outdir',        str(outdir),
        '--exposure_file', str(exposure_file),
        '--outcome_file',  str(outcome_file),
    ]
    _flag_map = {
        'exposure_label': '--exposure_label',
        'outcome_label':  '--outcome_label',
        'pval_iv':        '--pval_iv',
        'pval_iv_fb':     '--pval_iv_fb',
        'clump_r2':       '--clump_r2',
        'clump_kb':       '--clump_kb',
        'kg_bfile':       '--kg_bfile',
        'plink':          '--plink',
    }
    for key, flag in _flag_map.items():
        if key in kwargs and kwargs[key] is not None:
            cmd += [flag, str(kwargs[key])]
    subprocess.run(cmd, check=True)


def run_mr(gene, outdir, eqtl_file=None, gwas_file=None, chr=None, pos=None,
           window=1_000_000, exposure_file=None, outcome_file=None, **kwargs):
    """Run Mendelian Randomization.

    If exposure_file + outcome_file are provided, calls mr.R directly with
    those pre-formatted CSVs (columns: snp, beta_exp/out, se_exp/out,
    ea_exp/out, nea_exp/out, [eaf_exp/out], pval_exp).

    Otherwise loads from eqtl_file (DICE VCF) + gwas_file (harmonised TSV)
    using chr/pos/window to subset the locus, writes standardised CSVs to
    outdir, then calls mr.R.

    kwargs passed to mr.R: exposure_label, outcome_label, pval_iv, pval_iv_fb,
    clump_r2, clump_kb, kg_bfile, plink.
    """
    os.makedirs(outdir, exist_ok=True)

    if exposure_file is None:
        if not all([eqtl_file, gwas_file, chr is not None, pos is not None]):
            raise ValueError(
                'run_mr requires either (exposure_file + outcome_file) '
                'or (eqtl_file + gwas_file + chr + pos)')

        exp_df = _load_dice_vcf_locus(gene, eqtl_file, chr, pos, window)
        out_df = _load_gwas_locus(gwas_file, chr, pos, window)

        if exp_df is None or exp_df.empty:
            raise RuntimeError(f'No eQTL variants found for {gene} at chr{chr}:{pos}±{window}')
        if out_df is None or out_df.empty:
            raise RuntimeError(f'No GWAS variants found at chr{chr}:{pos}±{window}')

        print(f'[run_mr] eQTL variants: {len(exp_df)}, GWAS variants: {len(out_df)}')

        exposure_file = os.path.join(outdir, f'exposure_{gene}.csv')
        outcome_file  = os.path.join(outdir, f'outcome_{gene}.csv')
        exp_df.to_csv(exposure_file, index=False)
        out_df.to_csv(outcome_file,  index=False)

    _call_mr_r(gene, outdir, exposure_file, outcome_file, **kwargs)
    return str(outdir)


def _run_mr_opengwas(gene, outdir, **kwargs):
    """Fetch OpenGWAS data in Python, harmonise, then call mr.R in opengwas mode."""
    exposure_id    = kwargs.get('exposure_id')
    outcome_id     = kwargs.get('outcome_id')
    pval_iv        = kwargs.get('pval_iv', 5e-8)
    exposure_label = kwargs.get('exposure_label', exposure_id)
    outcome_label  = kwargs.get('outcome_label', outcome_id)

    # ── Short-circuit: caller provides pre-formatted CSV files ────────────────
    exp_file_direct = kwargs.get('exposure_file')
    out_file_direct = kwargs.get('outcome_file')

    if exp_file_direct and out_file_direct:
        print('[run_mr] Using caller-provided exposure/outcome files (no API call)')
        _call_mr_r(gene, outdir, exp_file_direct, out_file_direct,
                   exposure_label=exposure_label, outcome_label=outcome_label,
                   **{k: v for k, v in kwargs.items()
                      if k in ('pval_iv','pval_iv_fb','clump_r2','clump_kb','kg_bfile','plink')})
        return

    if not exposure_id or not outcome_id:
        raise ValueError("run_mr(mode='opengwas') requires exposure_id and outcome_id "
                         "(or exposure_file + outcome_file for pre-fetched data)")

    token = _load_token()

    # ── 1. Fetch top hits for exposure ────────────────────────────────────────
    print(f'[run_mr] Fetching top hits for exposure: {exposure_id} (p<{pval_iv})')
    exp_df = _fetch_tophits(exposure_id, token, pval=pval_iv)
    if exp_df.empty:
        raise RuntimeError(f'No hits returned for exposure study {exposure_id}')
    print(f'[run_mr] {len(exp_df)} exposure instruments')

    # ── 2. Fetch outcome associations for the same SNPs ───────────────────────
    snps = exp_df['snp'].dropna().tolist()
    print(f'[run_mr] Fetching outcome associations: {outcome_id} for {len(snps)} SNPs')
    out_df = _fetch_associations(outcome_id, snps, token)
    if out_df.empty:
        raise RuntimeError(f'No outcome associations returned from {outcome_id}')
    print(f'[run_mr] {len(out_df)} outcome associations returned')

    # ── 3. Rename for harmonisation ───────────────────────────────────────────
    exp_h = exp_df.rename(columns={'beta': 'beta_exp', 'se': 'se_exp',
                                    'ea': 'ea_exp', 'nea': 'nea_exp', 'eaf': 'eaf_exp'})
    out_h = out_df.rename(columns={'beta': 'beta_out', 'se': 'se_out',
                                    'ea': 'ea_out', 'nea': 'nea_out', 'eaf': 'eaf_out'})

    # ── 4. Harmonise ──────────────────────────────────────────────────────────
    harm = _harmonize_alleles(exp_h[['snp','beta_exp','se_exp','ea_exp','nea_exp','eaf_exp']],
                               out_h[['snp','beta_out','se_out','ea_out','nea_out','eaf_out']])
    print(f'[run_mr] {len(harm)} SNPs after harmonisation')
    if harm.empty:
        raise RuntimeError('No SNPs remain after harmonisation')

    # ── 5. Write harmonised CSVs for mr.R ────────────────────────────────────
    exp_file = os.path.join(outdir, f'mr_{gene}_opengwas_exposure.csv')
    out_file = os.path.join(outdir, f'mr_{gene}_opengwas_outcome.csv')

    harm[['snp', 'beta_exp', 'se_exp', 'ea_exp', 'nea_exp', 'eaf_exp']].to_csv(exp_file, index=False)
    harm[['snp', 'beta_out', 'se_out', 'ea_out', 'nea_out', 'eaf_out']].to_csv(out_file, index=False)

    # ── 6. Call mr.R ──────────────────────────────────────────────────────────
    _call_mr_r(gene, outdir, exp_file, out_file,
               exposure_label=exposure_label, outcome_label=outcome_label,
               **{k: v for k, v in kwargs.items()
                  if k in ('pval_iv','pval_iv_fb','clump_r2','clump_kb','kg_bfile','plink')})
