"""
QUESTION: rs11867200 associates with CCL2/MCP-1 production after 24h LPS stimulation in PBMCs,
but ONLY in old or disease individuals. What is the mechanism, and what does this tell us about
the variant's biology?

STEP 1 — Variant annotation: characterise rs11867200 at the DNA/regulatory level.
Uses direct REST APIs (no LLM layer needed).
"""

import sys
import os
import json
import re
import time
import requests

sys.path.insert(0, '/vol/projects/BIIM/agentic_immunology/external/biomni')
from biomni.tool.database import region_to_ccre_screen  # direct API, works without LLM

SNP = "rs11867200"
RS_NUM = "11867200"   # numeric part
OUTPUT_DIR = "/vol/projects/BIIM/agentic_immunology/temp/nienke/step1_annotation"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUTPUT_DIR, "results.txt")

sections = []

def section(label, content):
    block = f"\n{'='*70}\n{label}\n{'='*70}\n{content}\n"
    sections.append(block)
    print(block)

def safe_get(url, params=None, headers=None, timeout=30, label=""):
    """GET with error handling."""
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f"  [WARN] {label} failed: {e}")
        return None

def safe_post(url, json_data=None, headers=None, timeout=30, label=""):
    try:
        resp = requests.post(url, json=json_data, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f"  [WARN] {label} failed: {e}")
        return None


# ==========================================================================
# 1a. dbSNP — position (GRCh38), alleles, MAF
# ==========================================================================
print("[1a] Querying NCBI Variation API (dbSNP)...")
url_dbsnp = f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{RS_NUM}"
resp = safe_get(url_dbsnp, label="dbSNP")
if resp:
    data = resp.json()
    # Extract key fields
    out = {"raw": data}
    # Primary snapshot
    snap = data.get("primary_snapshot_data", {})
    # Alleles
    alleles = snap.get("alleles", [])
    # Placements (GRCh38)
    placements = snap.get("placements_with_allele", [])
    grch38 = [p for p in placements if "GRCh38" in str(p.get("placement_annot", {}).get("seq_id_traits_by_assembly", [{}]))]

    summary = {
        "variant_id": data.get("refsnp_id"),
        "alleles_raw": [a.get("allele", {}).get("spdi", {}) for a in alleles[:6]],
        "placements_count": len(placements),
        "grch38_placements": grch38[:2] if grch38 else placements[:2],
    }
    # Try to get simple position from placements
    for p in placements[:5]:
        annot = p.get("placement_annot", {})
        traits = annot.get("seq_id_traits_by_assembly", [])
        for t in traits:
            if "GRCh38" in str(t):
                summary["assembly"] = t.get("assembly_name", "")
                summary["chromosome"] = t.get("chromosome", "")
        allele_ann = p.get("alleles", [])
        for aa in allele_ann:
            spdi = aa.get("allele", {}).get("spdi", {})
            if spdi and p.get("is_ptlp"):
                summary["position_grch38"] = spdi

    section("1a. dbSNP — position / alleles / MAF",
            json.dumps(summary, indent=2, default=str))

    # Save GRCh38 coordinates — ONLY update pos_screen when placement is confirmed GRCh38
    chrom_screen = "chr17"
    pos_screen = 34248950  # confirmed GRCh38 fallback for rs11867200
    for p in placements[:10]:
        annot = p.get("placement_annot", {})
        traits = annot.get("seq_id_traits_by_assembly", [])
        is_grch38 = any("GRCh38" in str(t) for t in traits)
        if not is_grch38:
            continue  # skip GRCh37 and other assemblies
        for t in traits:
            if "GRCh38" in str(t):
                chrom_screen = "chr" + str(t.get("chromosome", "17"))
        for aa in p.get("alleles", []):
            spdi = aa.get("allele", {}).get("spdi", {})
            if spdi and "position" in spdi:
                pos_screen = int(spdi["position"])
                break  # take first allele position from this GRCh38 placement
        break  # stop after first GRCh38 placement
    print(f"  Coordinates for SCREEN (GRCh38): {chrom_screen}:{pos_screen}")
else:
    section("1a. dbSNP — ERROR", "Could not reach NCBI Variation API")
    chrom_screen = "chr17"
    pos_screen = 34248950  # confirmed GRCh38 for rs11867200


# ==========================================================================
# 1b. Ensembl — variant consequence, overlapping genes
# ==========================================================================
print("[1b] Querying Ensembl VEP + variation endpoint...")
headers_ensembl = {"Content-Type": "application/json"}

# 1b-i: Variation endpoint (position, alleles, existing_variation)
url_var = f"https://rest.ensembl.org/variation/human/{SNP}"
resp_var = safe_get(url_var, params={"content-type": "application/json"}, label="Ensembl variation")
if resp_var:
    section("1b-i. Ensembl variation — position/alleles", json.dumps(resp_var.json(), indent=2, default=str))

# 1b-ii: VEP endpoint — transcript consequences
url_vep = f"https://rest.ensembl.org/vep/human/id/{SNP}"
resp_vep = safe_get(url_vep, params={"content-type": "application/json", "canonical": 1,
                                      "regulatory": 1, "protein": 1},
                    label="Ensembl VEP")
if resp_vep:
    section("1b-ii. Ensembl VEP — transcript + regulatory consequences",
            json.dumps(resp_vep.json(), indent=2, default=str))
    # Confirm GRCh38 coordinates from VEP (always GRCh38) — overrides dbSNP extraction
    vep_data = resp_vep.json()
    if isinstance(vep_data, list) and len(vep_data) > 0:
        v = vep_data[0]
        vep_pos = v.get("start")
        vep_chrom = v.get("seq_region_name", "")
        if vep_pos and vep_chrom:
            pos_screen = int(vep_pos)
            chrom_screen = "chr" + str(vep_chrom)
            print(f"  GRCh38 coordinates confirmed from VEP: {chrom_screen}:{pos_screen}")

# 1b-iii: Regulatory features overlapping the locus (±5 kb)
if pos_screen:
    url_reg = (f"https://rest.ensembl.org/overlap/region/human/"
               f"{chrom_screen.replace('chr','')}:{max(1,pos_screen-5000)}-{pos_screen+5000}"
               f"?feature=regulatory;content-type=application/json")
    resp_reg = safe_get(url_reg, label="Ensembl regulatory")
    if resp_reg:
        section("1b-iii. Ensembl regulatory features (±5 kb)", json.dumps(resp_reg.json(), indent=2, default=str))

    # Genes within 100 kb
    url_genes = (f"https://rest.ensembl.org/overlap/region/human/"
                 f"{chrom_screen.replace('chr','')}:{max(1,pos_screen-100000)}-{pos_screen+100000}"
                 f"?feature=gene;content-type=application/json")
    resp_genes = safe_get(url_genes, label="Ensembl genes")
    if resp_genes:
        genes = resp_genes.json()
        # Summarise: just gene names, biotypes, distances
        gene_summary = [
            {
                "name": g.get("external_name", g.get("gene_id", "?")),
                "biotype": g.get("biotype"),
                "start": g.get("start"),
                "end": g.get("end"),
                "strand": g.get("strand"),
                "distance_to_snp": abs(g.get("start", pos_screen) - pos_screen),
            }
            for g in genes
        ]
        gene_summary.sort(key=lambda x: x["distance_to_snp"])
        section("1b-iv. Ensembl genes within 100 kb (sorted by distance)", json.dumps(gene_summary, indent=2))


# ==========================================================================
# 1c. RegulomeDB — regulatory score
# ==========================================================================
print("[1c] Querying RegulomeDB...")
url_rdb = "https://regulomedb.org/regulome-search/"
resp_rdb = safe_get(url_rdb, params={"regions": SNP, "genome": "GRCh38", "format": "json"},
                    timeout=60, label="RegulomeDB")
if resp_rdb:
    section("1c. RegulomeDB — regulatory score", json.dumps(resp_rdb.json(), indent=2, default=str))
else:
    # Try alternate endpoint
    url_rdb2 = f"https://regulomedb.org/regulome-search/?regions={SNP}&genome=GRCh38&format=json"
    resp_rdb2 = safe_get(url_rdb2, timeout=60, label="RegulomeDB alt")
    if resp_rdb2:
        section("1c. RegulomeDB — regulatory score (alt endpoint)", resp_rdb2.text[:5000])
    else:
        section("1c. RegulomeDB — ERROR", "Could not reach RegulomeDB API")


# ==========================================================================
# 1d. SCREEN (ENCODE cCRE) — overlapping regulatory elements
# ==========================================================================
print("[1d] Querying ENCODE SCREEN cCRE...")
try:
    r1d = region_to_ccre_screen(
        coord_chrom=chrom_screen,
        coord_start=max(1, pos_screen - 2000),
        coord_end=pos_screen + 2000,
        assembly="GRCh38",
    )
    section(f"1d. SCREEN cCRE — {chrom_screen}:{pos_screen-2000}-{pos_screen+2000} (±2 kb)",
            str(r1d))
except Exception as e:
    section("1d. SCREEN cCRE — ERROR", str(e))


# ==========================================================================
# 1e. GWAS Catalog — disease/trait associations
# ==========================================================================
print("[1e] Querying GWAS Catalog...")
url_gwas = f"https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/{SNP}"
resp_gwas = safe_get(url_gwas, headers={"Accept": "application/json"}, label="GWAS Catalog SNP")
if resp_gwas:
    section("1e-i. GWAS Catalog — SNP summary", json.dumps(resp_gwas.json(), indent=2, default=str)[:8000])

# Associations for this SNP
url_gwas_assoc = f"https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/{SNP}/associations"
resp_assoc = safe_get(url_gwas_assoc, params={"size": 50},
                      headers={"Accept": "application/json"}, label="GWAS Catalog assoc")
if resp_assoc:
    data_assoc = resp_assoc.json()
    # Extract key fields from associations
    embedded = data_assoc.get("_embedded", {})
    associations = embedded.get("associations", [])
    assoc_summary = []
    for a in associations:
        loci = a.get("loci", [])
        snp_ids = []
        for l in loci:
            for s in l.get("strongestRiskAlleles", []):
                snp_ids.append(s.get("riskAlleleName", ""))
        assoc_summary.append({
            "trait": a.get("efoTraits", [{}])[0].get("trait", "?") if a.get("efoTraits") else "?",
            "p_value": a.get("pvalue"),
            "p_value_mlog": a.get("pvalueMlog"),
            "risk_allele": snp_ids,
            "or_beta": a.get("orPerCopyNum"),
            "study": a.get("study", {}).get("accessionId", "?") if isinstance(a.get("study"), dict) else "?",
        })
    section("1e-ii. GWAS Catalog — associations", json.dumps(assoc_summary, indent=2, default=str))


# ==========================================================================
# 1f. gnomAD — population allele frequencies
# ==========================================================================
print("[1f] Querying gnomAD GraphQL...")
gnomad_query = """
query Variant($variantId: String!) {
  variant(variantId: $variantId, dataset: gnomad_r4) {
    variantId
    chrom
    pos
    ref
    alt
    genome {
      af
      ac
      an
      populations {
        id
        af
        ac
        an
      }
    }
    rsids
    colocatedVariants
  }
}
"""
# gnomAD needs the variant in format: chr-pos-ref-alt
# First need position from dbSNP result; fallback to known position
# rs11867200 is on chr17 near CCL2; actual position will be refined
# Use Ensembl to get alleles
gnomad_variant_id = None
if resp_vep:
    vep_data = resp_vep.json()
    if isinstance(vep_data, list) and len(vep_data) > 0:
        v = vep_data[0]
        chrom_g = v.get("seq_region_name", "17")
        start_g = v.get("start", pos_screen)
        allele_str = v.get("allele_string", "")
        if "/" in allele_str:
            ref_g, alt_g = allele_str.split("/", 1)
            gnomad_variant_id = f"{chrom_g}-{start_g}-{ref_g}-{alt_g}"
            print(f"  gnomAD variant ID from VEP: {gnomad_variant_id}")

if gnomad_variant_id:
    payload = {"query": gnomad_query, "variables": {"variantId": gnomad_variant_id}}
    resp_gnomad = safe_post("https://gnomad.broadinstitute.org/api",
                             json_data=payload,
                             headers={"Content-Type": "application/json"},
                             timeout=60, label="gnomAD")
    if resp_gnomad:
        gnomad_data = resp_gnomad.json()
        section("1f. gnomAD — population allele frequencies", json.dumps(gnomad_data, indent=2, default=str))
    else:
        section("1f. gnomAD — ERROR", f"Could not query gnomAD for variant {gnomad_variant_id}")
else:
    section("1f. gnomAD — SKIP", "Could not determine variant ID from VEP; skipping gnomAD query")


# ==========================================================================
# 1g. REMAP — TF ChIP-seq peaks at the locus
# ==========================================================================
print("[1g] Querying REMAP...")
# REMAP2022 API: peaks overlapping a genomic region
# Endpoint: https://remap2022.univ-amu.fr/api/v1/peaks/byRegion
chrom_remap = chrom_screen.replace("chr", "")
remap_region = f"chr{chrom_remap}:{max(1,pos_screen-500)}-{pos_screen+500}"
url_remap = "https://remap2022.univ-amu.fr/api/v1/peaks/byRegion"
resp_remap = safe_get(url_remap,
                       params={"region": remap_region, "assembly": "hg38", "format": "json"},
                       timeout=60, label="REMAP")
if resp_remap and resp_remap.status_code == 200:
    section("1g. REMAP — TF ChIP-seq peaks (±500 bp)", json.dumps(resp_remap.json(), indent=2, default=str)[:10000])
else:
    # Try alternate REMAP endpoint
    url_remap2 = "https://remap2022.univ-amu.fr/api/v1/peaks/findByRegion"
    resp_remap2 = safe_get(url_remap2,
                            params={"chr": f"chr{chrom_remap}", "start": pos_screen-500,
                                    "end": pos_screen+500, "assembly": "hg38"},
                            timeout=60, label="REMAP alt")
    if resp_remap2:
        section("1g. REMAP — TF ChIP-seq peaks (alt endpoint)", str(resp_remap2.text)[:10000])
    else:
        # Use ENCODE ChIP-seq data as fallback
        section("1g. REMAP — NOTE",
                f"REMAP API not reachable. Region queried: {remap_region}. "
                "Will use ENCODE ChIP-seq data or motif_databases/ENCODE-TF-ChIP-hg38.bed.gz as alternative.")


# ==========================================================================
# 1h. JASPAR — TF binding profiles in this region
# ==========================================================================
print("[1h] Querying JASPAR REST API...")
# JASPAR TFBS predictions for genomic region
# Use the JASPAR v2 API: /api/v1/binding_sites/?genome=hg38&chr=...
url_jaspar_bs = "https://jaspar.genereg.net/api/v1/binding_sites/"
resp_jaspar = safe_get(url_jaspar_bs,
                        params={"genome": "hg38",
                                "chr": chrom_screen,
                                "start": max(1, pos_screen - 100),
                                "end": pos_screen + 100,
                                "score": 0.85,
                                "tax_id": 9606,
                                "format": "json"},
                        timeout=60, label="JASPAR binding sites")
if resp_jaspar:
    data_j = resp_jaspar.json()
    section("1h. JASPAR — TF binding sites at locus (±100 bp, score≥0.85)",
            json.dumps(data_j, indent=2, default=str)[:10000])
else:
    # Fallback: query JASPAR profiles for immune TFs and report which have NF-kB/AP-1 motifs
    url_jaspar_matrix = "https://jaspar.genereg.net/api/v1/matrix/"
    resp_j2 = safe_get(url_jaspar_matrix,
                        params={"tax_id": 9606, "name": "RELA", "format": "json"},
                        timeout=30, label="JASPAR RELA")
    if resp_j2:
        section("1h. JASPAR — RELA (NF-kB) profile", json.dumps(resp_j2.json(), indent=2, default=str)[:3000])
    else:
        section("1h. JASPAR — NOTE",
                "JASPAR binding site API not reachable. "
                "Available locally: motif_databases/scglue/JASPAR2022-hg38.bed.gz — "
                "can be used to query TF motif hits at this locus.")

# ==========================================================================
# 1h-local: JASPAR2022 local bed.gz — grep for locus
# ==========================================================================
print("[1h-local] Checking JASPAR2022 local bed.gz...")
import subprocess
jaspar_bed = "/vol/projects/jnourisa/genernbi/resources/supp_data/databases/scglue/JASPAR2022-hg38.bed.gz"
if os.path.exists(jaspar_bed):
    chrom_str = chrom_screen  # e.g. chr17
    start_str = str(max(1, pos_screen - 500))
    end_str = str(pos_screen + 500)
    cmd = f"tabix {jaspar_bed} {chrom_str}:{start_str}-{end_str}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            section("1h-local. JASPAR2022 local — TF motif hits at locus (±500 bp)",
                    result.stdout[:8000])
        else:
            section("1h-local. JASPAR2022 local — No hits or error",
                    result.stderr[:500] or "No hits found in this region")
    except Exception as e:
        section("1h-local. JASPAR2022 local — ERROR", str(e))
else:
    section("1h-local. JASPAR2022", f"File not found: {jaspar_bed}")


# ==========================================================================
# 1i. CpG probe positions — cg07431106 and cg12698626 (Illumina 450k)
# Genomic coordinates from UCSC genome browser annotation track
# ==========================================================================
print("[1i] Looking up CpG probe positions (Illumina 450k)...")
CpG_PROBES = ["cg07431106", "cg12698626"]
cpg_results = []
for probe in CpG_PROBES:
    # UCSC genome browser search API
    url_ucsc = f"https://api.genome.ucsc.edu/search?search={probe}&genome=hg38"
    resp_ucsc = safe_get(url_ucsc, timeout=30, label=f"UCSC {probe}")
    if resp_ucsc:
        data_ucsc = resp_ucsc.json()
        cpg_results.append({
            "probe": probe,
            "ucsc_response": data_ucsc
        })
    else:
        # Fallback: myvariant.info
        url_mv = f"https://myvariant.info/v1/query"
        resp_mv = safe_get(url_mv,
                           params={"q": probe, "species": "human", "fields": "all"},
                           timeout=30, label=f"myvariant {probe}")
        if resp_mv:
            cpg_results.append({"probe": probe, "myvariant_response": resp_mv.json()})
        else:
            cpg_results.append({"probe": probe, "error": "Could not retrieve position"})

section("1i. CpG probe positions (Illumina 450k, GRCh38)", json.dumps(cpg_results, indent=2, default=str))

# Also compute distances if we got coordinates
cpg_dist_notes = []
for entry in cpg_results:
    probe = entry["probe"]
    # Try to extract position from UCSC response
    ucsc = entry.get("ucsc_response", {})
    tracks = ucsc.get("results", [])
    for t in tracks:
        for item in t.get("items", []):
            chrom_p = item.get("chrom", "")
            start_p = item.get("chromStart", item.get("start", None))
            if start_p and "17" in str(chrom_p):
                dist = abs(int(start_p) - pos_screen)
                cpg_dist_notes.append(
                    f"  {probe}: {chrom_p}:{start_p} → {dist:,} bp from variant ({chrom_screen}:{pos_screen})"
                )
                break

if cpg_dist_notes:
    section("1i-summary. CpG probe distances to rs11867200", "\n".join(cpg_dist_notes))


# ==========================================================================
# 1j. lncRNA identity — what is ENSG00000301139?
# ==========================================================================
print("[1j] Looking up lncRNA ENSG00000301139 identity...")
url_gene = "https://rest.ensembl.org/lookup/id/ENSG00000301139"
resp_gene = safe_get(url_gene, params={"content-type": "application/json",
                                        "expand": 1, "xrefs": 1},
                     timeout=30, label="Ensembl gene lookup")
if resp_gene:
    gene_data = resp_gene.json()
    gene_summary = {
        "id": gene_data.get("id"),
        "display_name": gene_data.get("display_name"),
        "description": gene_data.get("description"),
        "biotype": gene_data.get("biotype"),
        "chromosome": gene_data.get("seq_region_name"),
        "start": gene_data.get("start"),
        "end": gene_data.get("end"),
        "strand": gene_data.get("strand"),
    }
    # Also get xrefs for HGNC name
    url_xref = "https://rest.ensembl.org/xrefs/id/ENSG00000301139"
    resp_xref = safe_get(url_xref, params={"content-type": "application/json"},
                         timeout=30, label="Ensembl xrefs")
    if resp_xref:
        xrefs = [x for x in resp_xref.json()
                 if x.get("dbname") in ("HGNC", "WikiGene", "EntrezGene", "Uniprot_gn", "Clone_based_ensembl_gene")]
        gene_summary["xrefs"] = xrefs
    # Distance to CCL2 (ENSG00000108691)
    url_ccl2 = "https://rest.ensembl.org/lookup/id/ENSG00000108691"
    resp_ccl2 = safe_get(url_ccl2, params={"content-type": "application/json"},
                         timeout=30, label="CCL2 lookup")
    if resp_ccl2:
        ccl2 = resp_ccl2.json()
        ccl2_start = ccl2.get("start")
        ccl2_end = ccl2.get("end")
        variant_dist_to_ccl2 = min(abs(pos_screen - ccl2_start), abs(pos_screen - ccl2_end))
        gene_summary["CCL2_GRCh38_coords"] = f"{ccl2.get('seq_region_name')}:{ccl2_start}-{ccl2_end} (strand {ccl2.get('strand')})"
        gene_summary["variant_distance_to_CCL2_bp"] = variant_dist_to_ccl2
    section("1j. lncRNA ENSG00000301139 — identity and CCL2 relationship",
            json.dumps(gene_summary, indent=2, default=str))
else:
    section("1j. lncRNA ENSG00000301139 — ERROR", "Could not query Ensembl gene lookup")


# ==========================================================================
# Write combined results
# ==========================================================================
header = f"""STEP 1 — Variant annotation for {SNP} (FIXED: GRCh38 coordinates throughout)
Generated: 2026-05-21
Question: rs11867200 associates with CCL2/MCP-1 production after 24h LPS stimulation in PBMCs,
          but ONLY in old or disease individuals. Mechanism?

Substeps: 1a dbSNP | 1b Ensembl VEP | 1c RegulomeDB | 1d SCREEN |
          1e GWAS Catalog | 1f gnomAD | 1g REMAP | 1h JASPAR | 1i CpG probes | 1j lncRNA identity
==========================================================================
"""

with open(OUT_FILE, "w") as fh:
    fh.write(header)
    fh.write("".join(sections))

print(f"\n[DONE] Results written to: {OUT_FILE}")
