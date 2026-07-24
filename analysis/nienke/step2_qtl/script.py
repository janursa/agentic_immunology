"""
QUESTION: rs11867200 associates with CCL2/MCP-1 production after 24h LPS stimulation in PBMCs,
but ONLY in old or disease individuals. What is the mechanism?

STEP 2: QTL sweep — mQTL, pQTL, sQTL, DICE eQTL, eQTLGen, OneK1K
Output: temp/nienke/step2_qtl/results.txt
"""

import sys, os, gzip, subprocess
import pysam

SNP = "rs11867200"
CHR = "17"
POS_38 = 34248950   # GRCh38 1-based
POS_37 = 32575969   # GRCh37 1-based

BASE = "/vol/projects/BIIM/agentic_immunology"
OUT  = f"{BASE}/temp/nienke/step2_qtl"
os.makedirs(OUT, exist_ok=True)

RESULT_FILE = f"{OUT}/results.txt"

# eQTL Catalogue shared column schema (pQTL + sQTL)
EQC_COLS = [
    'molecular_trait_id','chromosome','position','ref','alt','variant',
    'ma_samples','maf','pvalue','beta','se','type','ac','an','r2',
    'molecular_trait_object_id','gene_id','median_tpm','rsid'
]

# ── helpers ────────────────────────────────────────────────────────────

def log(msg):
    print(msg, flush=True)
    with open(RESULT_FILE, 'a') as f:
        f.write(msg + '\n')

def tabix_rsid(filepath, chrom, pos, rsid, window=200_000, col_schema=None):
    """Tabix query ±window around pos; return rows matching rsid."""
    hits = []
    try:
        tf   = pysam.TabixFile(filepath)
        s    = max(0, pos - window - 1)   # 0-based start
        e    = pos + window
        rows = []
        for c in [chrom, 'chr' + chrom]:
            try:
                rows = list(tf.fetch(c, s, e))
                if rows:
                    break
            except (ValueError, KeyError):
                pass
        for row in rows:
            if rsid not in row:
                continue
            fields = row.strip().split('\t')
            hits.append(dict(zip(col_schema, fields)) if col_schema else {'raw': row})
        tf.close()
    except Exception as ex:
        hits.append({'error': str(ex), 'file': os.path.basename(filepath)})
    return hits

def grep_gz(filepath, pattern, sep=None):
    """Stream-grep gzipped file; return matching rows as list-of-dicts.
    Header is always split by tab; data rows by sep or whitespace if mixed."""
    hits = []
    try:
        with gzip.open(filepath, 'rt', errors='replace') as f:
            raw_header = f.readline()
            header = raw_header.strip().split('\t')
            for line in f:
                if pattern in line:
                    # data rows may be space-sep even if header is tab-sep
                    fields = line.strip().split('\t') if '\t' in line else line.strip().split()
                    hits.append(dict(zip(header, fields)))
    except Exception as ex:
        hits.append({'error': str(ex)})
    return hits

def grep_vcfgz_stream(filepath, rsid):
    """Stream zcat of a VCF.gz, return rows matching rsid (column 3 = ID)."""
    hits = []
    try:
        proc = subprocess.Popen(
            ['zcat', filepath],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        for line in proc.stdout:
            if line.startswith('#'):
                continue
            if rsid in line:
                hits.append(_parse_dice_vcf(line))
        proc.stdout.close()
        proc.wait()
    except Exception as ex:
        hits.append({'error': str(ex)})
    return hits

def _parse_dice_vcf(line):
    """Parse one DICE VCF data line into a dict."""
    parts = line.strip().split('\t')
    if len(parts) < 8:
        return {'raw': line}
    chrom, pos, vid, ref, alt, _, _, info_str = parts[:8]
    info = {}
    for item in info_str.split(';'):
        if '=' in item:
            k, v = item.split('=', 1)
            info[k] = v
    return {'CHROM': chrom, 'POS': pos, 'ID': vid,
            'REF': ref, 'ALT': alt, **info}

# ── initialise output ─────────────────────────────────────────────────

with open(RESULT_FILE, 'w') as f:
    f.write("STEP 2 — QTL sweep for rs11867200\n")
    f.write(f"GRCh38: chr{CHR}:{POS_38}  |  GRCh37: chr{CHR}:{POS_37}\n")
    f.write("=" * 70 + "\n\n")

# ══════════════════════════════════════════════════════════════════════
# 2a.  mQTL — BLUEPRINT (Chen et al. 2016, Cell)  [GRCh37, rsid lookup]
# ══════════════════════════════════════════════════════════════════════
log("=" * 70)
log("2a. mQTL — BLUEPRINT monocyte / neutrophil / T cell (FDR < 0.05)")
log("=" * 70)

mqtl_files = {
    'monocyte':   f"{BASE}/datalake/mQTL/blueprint/mono_meth_fdr05.tsv.gz",
    'neutrophil': f"{BASE}/datalake/mQTL/blueprint/neut_meth_fdr05.tsv.gz",
    'T_cell':     f"{BASE}/datalake/mQTL/blueprint/tcel_meth_fdr05.tsv.gz",
}
any_mqtl = False
for ct, path in mqtl_files.items():
    hits = grep_gz(path, SNP)
    if hits and 'error' in hits[0]:
        log(f"  [{ct}] ERROR: {hits[0]['error']}")
    elif hits:
        any_mqtl = True
        log(f"\n  [{ct}] {len(hits)} mQTL hit(s):")
        for h in hits:
            log(f"    CpG={h.get('phenotypeID','?')}  beta={h.get('beta','?')}  "
                f"p={h.get('p.value','?')}  FDR={h.get('FDR','?')}  "
                f"variant={h.get('chr_pos_ref_alt','?')}")
    else:
        log(f"  [{ct}] No significant mQTL hits")
if not any_mqtl:
    log("\n  SUMMARY: rs11867200 is NOT a significant mQTL in any BLUEPRINT cell type.")

# ══════════════════════════════════════════════════════════════════════
# 2b.  pQTL — Sun et al. 2018 plasma proteins  [GRCh37, tabix]
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("2b. pQTL — Sun et al. 2018, Nature (~2,994 plasma proteins, n=3,301)")
log("=" * 70)

PQTL = f"{BASE}/datalake/pQTL/sun_2018/plasma.cc.tsv.gz"
hits = tabix_rsid(PQTL, CHR, POS_37, SNP, window=200_000, col_schema=EQC_COLS)
if hits and 'error' in hits[0]:
    log(f"  ERROR: {hits[0]}")
elif hits:
    log(f"\n  {len(hits)} pQTL hit(s) for {SNP}:")
    for h in hits:
        log(f"    aptamer={h.get('molecular_trait_id','?')}  gene={h.get('gene_id','?')}  "
            f"beta={h.get('beta','?')}  p={h.get('pvalue','?')}  maf={h.get('maf','?')}")
else:
    log(f"  No pQTL hits for {SNP} in ±200 kb (GRCh37 chr{CHR}:{POS_37})")

# ══════════════════════════════════════════════════════════════════════
# 2c.  sQTL — BLUEPRINT, DICE, GTEx whole blood  [GRCh38, tabix]
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("2c. sQTL — leafcutter intron excision (GRCh38, ±200 kb)")
log("=" * 70)

sqtl_files = {
    'BLUEPRINT_monocyte':   f"{BASE}/datalake/sQTL/blueprint/monocyte.cc.tsv.gz",
    'BLUEPRINT_neutrophil': f"{BASE}/datalake/sQTL/blueprint/neutrophil.cc.tsv.gz",
    'BLUEPRINT_CD4T':       f"{BASE}/datalake/sQTL/blueprint/cd4_t_cell.cc.tsv.gz",
    'DICE_monocyte':        f"{BASE}/datalake/sQTL/schmiedel_2018/monocyte.cc.tsv.gz",
    'DICE_CD16mono':        f"{BASE}/datalake/sQTL/schmiedel_2018/cd16_monocyte.cc.tsv.gz",
    'GTEx_whole_blood':     f"{BASE}/datalake/sQTL/gtex_v8/whole_blood.cc.tsv.gz",
}
any_sqtl = False
for label, path in sqtl_files.items():
    hits = tabix_rsid(path, CHR, POS_38, SNP, window=200_000, col_schema=EQC_COLS)
    if hits and 'error' in hits[0]:
        log(f"\n  [{label}] ERROR: {hits[0]['error']}")
    elif hits:
        any_sqtl = True
        log(f"\n  [{label}] {len(hits)} sQTL hit(s):")
        for h in hits:
            log(f"    cluster={h.get('molecular_trait_id','?')}  "
                f"gene={h.get('gene_id','?')}  "
                f"beta={h.get('beta','?')}  p={h.get('pvalue','?')}  "
                f"maf={h.get('maf','?')}")
    else:
        log(f"\n  [{label}] No sQTL hits")
if not any_sqtl:
    log("\n  SUMMARY: rs11867200 is not a significant sQTL in any tested cell type.")

# ══════════════════════════════════════════════════════════════════════
# 2d.  DICE eQTL — monocytes (filtered + full summary stats)
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("2d. DICE eQTL — MONOCYTES and M2 (Schmiedel et al. 2018, n=91)")
log("=" * 70)

# Filtered significant VCFs (p < 0.0001, TPM > 1)
log("\n  [Filtered significant hits — p<0.0001 & TPM>1]")
for ct in ['MONOCYTES', 'M2']:
    path = f"{BASE}/datalake/dice/eqtls/{ct}.vcf"
    hits = []
    try:
        with open(path) as f:
            for line in f:
                if SNP in line and not line.startswith('#'):
                    hits.append(_parse_dice_vcf(line))
    except Exception as ex:
        hits = [{'error': str(ex)}]
    if hits and 'error' in hits[0]:
        log(f"    [{ct}] ERROR: {hits[0]['error']}")
    elif hits:
        log(f"    [{ct}] {len(hits)} hit(s):")
        for h in hits:
            log(f"      Gene={h.get('GeneSymbol','?')}  beta={h.get('Beta','?')}  "
                f"p={h.get('Pvalue','?')}  FDR={h.get('FDR','?')}")
    else:
        log(f"    [{ct}] No significant eQTL hits for {SNP}")

# Full summary stats (all tested pairs — relaxed threshold)
log(f"\n  [Full summary stats — all p-values (streaming zcat)]")
for ct in ['MONOCYTES', 'M2']:
    path = f"{BASE}/datalake/dice/eqtls/full_summary_stats/{ct}.vcf.gz"
    log(f"    [{ct}] Scanning {os.path.basename(path)} ...")
    hits = grep_vcfgz_stream(path, SNP)
    if hits and 'error' in hits[0]:
        log(f"    [{ct}] ERROR: {hits[0]['error']}")
    elif hits:
        log(f"    [{ct}] {len(hits)} hit(s) (no p-value filter):")
        for h in hits:
            log(f"      Gene={h.get('GeneSymbol','?')}  beta={h.get('Beta','?')}  "
                f"p={h.get('Pvalue','?')}  Stat={h.get('Statistic','?')}")
    else:
        log(f"    [{ct}] {SNP} not found in full summary stats (not tested or outside window)")

# ══════════════════════════════════════════════════════════════════════
# 2e.  eQTLGen — whole blood meta-analysis  (n=31,684, GRCh37)
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("2e. eQTLGen — whole blood (Võsa et al. 2021, n=31,684, FDR<0.05)")
log("=" * 70)

EQTLGEN = f"{BASE}/datalake/eQTL/eqtlgen/sig/eQTLGen_cis_sig_FDR05.txt.gz"
hits = grep_gz(EQTLGEN, SNP)
if hits and 'error' in hits[0]:
    log(f"  ERROR: {hits[0]}")
elif hits:
    log(f"\n  {len(hits)} eQTLGen hit(s):")
    for h in hits:
        log(f"    Gene={h.get('GeneSymbol','?')} ({h.get('Gene','?')})  "
            f"Z={h.get('Zscore','?')}  p={h.get('Pvalue','?')}  "
            f"FDR={h.get('FDR','?')}  N={h.get('NrSamples','?')}")
else:
    log(f"  No eQTLGen hits for {SNP} (FDR < 0.05)")

# ══════════════════════════════════════════════════════════════════════
# 2f.  OneK1K — 14 immune PBMC cell types  (n=982, GRCh37)
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("2f. OneK1K — PBMC immune cell types (Yazar et al. 2022, n=982, FDR<0.05)")
log("=" * 70)

ONEK1K = f"{BASE}/datalake/eQTL/onek1k/sig"
ct_codes = ['monoc','mononc','dc','nk','nkr','cd4nc','cd4et','cd4sox4',
            'cd8nc','cd8et','cd8s100b','bin','bmem','plasma']
any_onek = False
for ct in ct_codes:
    path = f"{ONEK1K}/{ct}_esnp_table.tsv.gz"
    if not os.path.exists(path):
        continue
    hits = grep_gz(path, SNP)
    if hits and 'error' in hits[0]:
        log(f"  [{ct}] ERROR: {hits[0]['error']}")
    elif hits:
        any_onek = True
        log(f"\n  [{ct}] {len(hits)} eSNP hit(s):")
        for h in hits:
            log(f"    GENE={h.get('GENE','?')} ({h.get('GENE_ID','?')})  "
                f"rho={h.get('SPEARMANS_RHO','?')}  p={h.get('P_VALUE','?')}  "
                f"FDR={h.get('FDR','?')}")
if not any_onek:
    log(f"  No OneK1K significant eSNP hits for {SNP} in any cell type")

# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("STEP 2 COMPLETE")
log(f"Output: {RESULT_FILE}")
log("=" * 70)
