"""genetics.py — GWAS and genetic variant analysis tools for immune research.

Main entry points
-----------------
phewas_opengwas(snps, pval=5e-8)
    Query OpenGWAS for all GWAS associations of a list of SNPs (PheWAS).

query_gwas_catalog(snps, ukb_only=False)
    Look up SNPs in the locally cached GWAS Catalog (622k entries, ~64k UKB).
"""

import os
import time
import pickle

import pandas as pd
import requests

# ── paths ─────────────────────────────────────────────────────────────────────
_ROOT       = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
_ENV_FILE   = os.path.join(_ROOT, '.env')
_GWAS_PKL   = os.path.join(_ROOT, 'datalake', 'biomni', 'gwas_catalog.pkl')
_OPENGWAS_URL = 'https://api.opengwas.io/api/phewas'

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
