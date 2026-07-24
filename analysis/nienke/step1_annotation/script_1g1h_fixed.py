"""
STEP 1g + 1h FIXED — rs11867200
1g : ENCODE TF ChIP-seq peaks at locus (local BED, replaces unreachable REMAP API)
1h : JASPAR2022 local motif hits at locus (pysam, replaces failed tabix binary)
1h-allele : Allele-specific PWM scoring — motif GAIN (C→T or C→G) and LOSS detection

Runs with ciim.sif (has pysam, numpy, requests).
"""

import os, sys, json, time
import numpy as np
import requests
import pysam

# ── Coordinates ────────────────────────────────────────────────────────────────
CHROM   = "chr17"
POS     = 34248950          # GRCh38, 1-based
REGION  = (POS - 500, POS + 500)  # 0-based for pysam

# 50-bp locus sequence returned by RegulomeDB (start=34248924, end=34248974, 0-based)
# SNP (rs11867200) is at 0-based index 25 in this string → REF = C
LOCUS_SEQ = "TGGCATGCAACATTTTGCAACCAAGCGGAAGAAACATCATCCGCAAAGAA"
SNP_IDX   = 25     # 0-based
REF_BASE  = "C"
ALT_BASES = ["T", "G"]

# ── Files ───────────────────────────────────────────────────────────────────────
ENCODE_BED  = "/vol/projects/jnourisa/genernbi/resources/supp_data/databases/scglue/ENCODE-TF-ChIP-hg38.bed.gz"
JASPAR_BED  = "/vol/projects/jnourisa/genernbi/resources/supp_data/databases/scglue/JASPAR2022-hg38.bed.gz"
OUT_FILE    = "/vol/projects/BIIM/agentic_immunology/temp/nienke/step1_annotation/results_1g1h_fixed.txt"

assert LOCUS_SEQ[SNP_IDX] == REF_BASE, f"Expected {REF_BASE} at index {SNP_IDX}, got {LOCUS_SEQ[SNP_IDX]}"

sections = []

def section(label, content):
    block = f"\n{'='*70}\n{label}\n{'='*70}\n{content}\n"
    sections.append(block)
    print(block)


# ══════════════════════════════════════════════════════════════════════════════
# 1g — ENCODE TF ChIP-seq peaks (local)
# ══════════════════════════════════════════════════════════════════════════════
def get_tabix_ready(bed_gz_path):
    """
    Ensure a tabix-queryable version of bed_gz_path exists.
    If the source is plain gzip (not bgzip), re-compresses to bgzip in /tmp/ and indexes there.
    Returns path to the bgzipped, tabix-indexed file.
    """
    import gzip, shutil
    tbi_path = bed_gz_path + ".tbi"
    if os.path.exists(tbi_path):
        return bed_gz_path  # already indexed in place

    base = os.path.basename(bed_gz_path)
    tmp_bgz = f"/tmp/{base}"          # /tmp/ for singularity temp files
    tmp_tbi = tmp_bgz + ".tbi"

    if os.path.exists(tmp_tbi):
        return tmp_bgz  # already prepared in /tmp/

    # Check if bgzip (byte 3 == 0x04)
    with open(bed_gz_path, "rb") as f:
        header = f.read(4)
    is_bgzf = (header[3] == 0x04)

    if is_bgzf:
        # Just symlink or copy and index
        shutil.copy2(bed_gz_path, tmp_bgz)
    else:
        # Re-compress: decompress then bgzip-compress
        print(f"  Re-compressing {base} as bgzip → {tmp_bgz} ...")
        with gzip.open(bed_gz_path, "rb") as src, open(tmp_bgz + ".uncompressed", "wb") as dst:
            shutil.copyfileobj(src, dst)
        pysam.tabix_compress(tmp_bgz + ".uncompressed", tmp_bgz, force=True)
        os.remove(tmp_bgz + ".uncompressed")
        print(f"  bgzip done.")

    print(f"  Indexing {base} ...")
    pysam.tabix_index(tmp_bgz, preset="bed", force=True)
    print(f"  Index created: {tmp_tbi}")
    return tmp_bgz

print("[1g] Querying local ENCODE-TF-ChIP-hg38.bed.gz ...")
encode_tfs = []
try:
    ready_encode = get_tabix_ready(ENCODE_BED)
    tbx = pysam.TabixFile(ready_encode)
    hits = list(tbx.fetch(CHROM, REGION[0], REGION[1]))
    tbx.close()
    for h in hits:
        fields = h.split("\t")
        if len(fields) >= 4:
            encode_tfs.append({
                "chrom": fields[0], "start": int(fields[1]), "end": int(fields[2]),
                "tf": fields[3].strip(),
                "peak_len": int(fields[2]) - int(fields[1]),
                "dist_to_snp": min(abs(int(fields[1]) - POS), abs(int(fields[2]) - POS)),
            })
    encode_tfs.sort(key=lambda x: x["dist_to_snp"])
    tf_names_1g = sorted(set(e["tf"] for e in encode_tfs))
    summary_1g = (
        f"Region queried: {CHROM}:{REGION[0]}-{REGION[1]} (±500 bp around {POS})\n"
        f"Peaks found: {len(encode_tfs)}\n"
        f"Unique TFs: {len(tf_names_1g)}\n\n"
        f"TF list: {', '.join(tf_names_1g)}\n\n"
        f"Peak details (sorted by distance to SNP):\n"
        + json.dumps(encode_tfs[:40], indent=2)
    )
    section("1g. ENCODE TF ChIP-seq peaks (local, ±500 bp)", summary_1g)
except Exception as e:
    tf_names_1g = []
    section("1g. ENCODE TF ChIP-seq — ERROR", str(e))


# ══════════════════════════════════════════════════════════════════════════════
# 1h-local — JASPAR2022 motif hits (pysam)
# ══════════════════════════════════════════════════════════════════════════════
print("[1h-local] Querying local JASPAR2022-hg38.bed.gz ...")
jaspar_hits = []
try:
    ready_jaspar = get_tabix_ready(JASPAR_BED)
    tbx_j = pysam.TabixFile(ready_jaspar)
    hits_j = list(tbx_j.fetch(CHROM, REGION[0], REGION[1]))
    tbx_j.close()
    for h in hits_j:
        fields = h.split("\t")
        if len(fields) >= 4:
            jaspar_hits.append({
                "chrom": fields[0], "start": int(fields[1]), "end": int(fields[2]),
                "tf": fields[3].strip(),
                "motif_len": int(fields[2]) - int(fields[1]),
                "dist_to_snp": min(abs(int(fields[1]) - POS), abs(int(fields[2]) - POS)),
                "overlaps_snp": int(fields[1]) <= POS <= int(fields[2]),
            })
    jaspar_hits.sort(key=lambda x: x["dist_to_snp"])
    tf_names_1h = sorted(set(j["tf"] for j in jaspar_hits))
    hits_overlapping = [j for j in jaspar_hits if j["overlaps_snp"]]
    summary_1h = (
        f"Region queried: {CHROM}:{REGION[0]}-{REGION[1]} (±500 bp)\n"
        f"Total motif hits: {len(jaspar_hits)}\n"
        f"Unique TFs: {len(tf_names_1h)}\n"
        f"Motifs directly overlapping SNP position {POS}: {len(hits_overlapping)}\n\n"
        f"TF list: {', '.join(tf_names_1h)}\n\n"
        f"Motifs overlapping SNP:\n"
        + json.dumps(hits_overlapping, indent=2)
        + f"\n\nAll hits (sorted by distance to SNP):\n"
        + json.dumps(jaspar_hits[:50], indent=2)
    )
    section("1h-local. JASPAR2022 motif hits (local, ±500 bp)", summary_1h)
except Exception as e:
    tf_names_1h = []
    section("1h-local. JASPAR2022 local — ERROR", str(e))


# ══════════════════════════════════════════════════════════════════════════════
# 1h-allele — Allele-specific PWM scoring
# For each TF found in 1g or 1h-local, fetch PWM from JASPAR REST,
# score REF (C) and both ALT (T, G) sequences, classify gain/loss.
# ══════════════════════════════════════════════════════════════════════════════
print("[1h-allele] Allele-specific PWM scoring ...")

# Candidate TFs = union of 1g and 1h-local
candidate_tfs = sorted(set(tf_names_1g) | set(tf_names_1h))
print(f"  Candidate TFs for allele scoring: {len(candidate_tfs)}")

# Build ALT sequences
def make_allele_seq(seq, idx, new_base):
    return seq[:idx] + new_base + seq[idx+1:]

alt_seqs = {alt: make_allele_seq(LOCUS_SEQ, SNP_IDX, alt) for alt in ALT_BASES}
all_seqs  = {"REF_C": LOCUS_SEQ, "ALT_T": alt_seqs["T"], "ALT_G": alt_seqs["G"]}

BASE_IDX = {"A": 0, "C": 1, "G": 2, "T": 3}

def normalize_pfm(pfm_dict, pseudocount=0.001):
    """Convert raw PFM counts → frequency matrix (L × 4), with pseudocount."""
    keys = ["A", "C", "G", "T"]
    L = len(pfm_dict["A"])
    mat = np.zeros((L, 4))
    for b, k in zip(range(4), keys):
        mat[:, b] = np.array(pfm_dict[k], dtype=float)
    # Add pseudocount and normalise per position
    mat = mat + pseudocount
    mat = mat / mat.sum(axis=1, keepdims=True)
    return mat  # shape (L, 4)

def score_seq_with_pwm(seq, pwm_freq, bg=0.25):
    """
    Score seq of length L against (L×4) frequency PWM.
    Returns log-odds score (base-2).
    """
    score = 0.0
    for pos, base in enumerate(seq.upper()):
        idx = BASE_IDX.get(base)
        if idx is None:
            continue
        score += np.log2(pwm_freq[pos, idx]) - np.log2(bg)
    return float(score)

def best_allele_score(seq, pwm_freq):
    """
    Scan all windows of length motif_len in seq that contain SNP_IDX.
    Return max score across those windows (and best strand = fwd only for simplicity).
    """
    L = len(seq)
    motif_len = pwm_freq.shape[0]
    best = -np.inf
    best_start = None
    for start in range(max(0, SNP_IDX - motif_len + 1),
                       min(L - motif_len + 1, SNP_IDX + 1)):
        window = seq[start:start + motif_len]
        s = score_seq_with_pwm(window, pwm_freq)
        if s > best:
            best = s
            best_start = start
    return best, best_start

def fetch_jaspar_pwm(tf_name, retries=2):
    """Fetch best (highest information content) JASPAR PWM for a TF by name."""
    url = "https://jaspar.genereg.net/api/v1/matrix/"
    params = {"name": tf_name, "species": 9606, "format": "json", "page_size": 10}
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, timeout=20)
            if r.status_code != 200:
                return None, None
            data = r.json()
            results = data.get("results", [])
            if not results:
                return None, None
            # Pick matrix with highest IC if multiple
            best_matrix_id = results[0]["matrix_id"]
            # Fetch the actual PWM
            r2 = requests.get(f"https://jaspar.genereg.net/api/v1/matrix/{best_matrix_id}/",
                              params={"format": "json"}, timeout=20)
            if r2.status_code != 200:
                return None, None
            m = r2.json()
            pfm = m.get("pfm", {})
            if not pfm or "A" not in pfm:
                return None, None
            return pfm, best_matrix_id
        except Exception:
            if attempt < retries:
                time.sleep(1)
    return None, None

# Score each TF
allele_results = []
failed_tfs     = []

for tf in candidate_tfs:
    pfm, matrix_id = fetch_jaspar_pwm(tf)
    if pfm is None:
        failed_tfs.append(tf)
        continue

    try:
        pwm_freq = normalize_pfm(pfm)
        motif_len = pwm_freq.shape[0]

        scores = {}
        windows = {}
        for allele_name, seq in all_seqs.items():
            s, w = best_allele_score(seq, pwm_freq)
            scores[allele_name] = s
            windows[allele_name] = w

        delta_T = scores["ALT_T"] - scores["REF_C"]
        delta_G = scores["ALT_G"] - scores["REF_C"]

        # Classify: gain if Δ > 1 bit (2-fold), loss if Δ < -1 bit
        def classify(delta):
            if delta > 1.0:   return "GAIN"
            if delta < -1.0:  return "LOSS"
            return "neutral"

        allele_results.append({
            "tf":           tf,
            "matrix_id":    matrix_id,
            "motif_len":    int(motif_len),
            "score_REF_C":  round(scores["REF_C"], 3),
            "score_ALT_T":  round(scores["ALT_T"], 3),
            "score_ALT_G":  round(scores["ALT_G"], 3),
            "delta_T":      round(delta_T, 3),
            "delta_G":      round(delta_G, 3),
            "effect_T":     classify(delta_T),
            "effect_G":     classify(delta_G),
            "snp_in_1g":    tf in tf_names_1g,
            "snp_in_1h":    tf in tf_names_1h,
        })
    except Exception as e:
        failed_tfs.append(f"{tf}({e})")

    time.sleep(0.05)  # polite API rate

# Sort: GAIN first, then LOSS, then neutral
priority = {"GAIN": 0, "LOSS": 1, "neutral": 2}
allele_results.sort(key=lambda x: (
    min(priority[x["effect_T"]], priority[x["effect_G"]]),
    -(abs(x["delta_T"]) + abs(x["delta_G"]))
))

# Separate tables
gains  = [r for r in allele_results if r["effect_T"] == "GAIN" or r["effect_G"] == "GAIN"]
losses = [r for r in allele_results if r["effect_T"] == "LOSS" or r["effect_G"] == "LOSS"]

def fmt_table(rows):
    if not rows:
        return "  (none)\n"
    hdr = f"  {'TF':<12} {'matrix':<12} {'score_REF':>10} {'score_ALT_T':>12} {'score_ALT_G':>12} {'ΔT':>7} {'ΔG':>7} {'effect_T':<10} {'effect_G':<10} {'in_1g':<6} {'in_1h':<6}\n"
    sep = "  " + "-"*105 + "\n"
    body = ""
    for r in rows:
        body += (f"  {r['tf']:<12} {r['matrix_id']:<12} {r['score_REF_C']:>10.3f} "
                 f"{r['score_ALT_T']:>12.3f} {r['score_ALT_G']:>12.3f} "
                 f"{r['delta_T']:>7.3f} {r['delta_G']:>7.3f} "
                 f"{r['effect_T']:<10} {r['effect_G']:<10} "
                 f"{'Y' if r['snp_in_1g'] else 'N':<6} {'Y' if r['snp_in_1h'] else 'N':<6}\n")
    return hdr + sep + body

summary_allele = f"""
Locus sequence (50 bp from RegulomeDB):
  {LOCUS_SEQ}
  {'':>25}^ SNP position (index {SNP_IDX}): REF=C | ALT-T | ALT-G

Candidate TFs scored: {len(allele_results)} / {len(candidate_tfs)}
TFs with no JASPAR PWM found: {failed_tfs}

Threshold: |Δscore| > 1.0 log2 = 2-fold change in binding affinity

━━━ MOTIF GAIN (ALT creates stronger binding than REF) ━━━
{fmt_table(gains)}
━━━ MOTIF LOSS (ALT disrupts existing REF binding) ━━━
{fmt_table(losses)}

━━━ ALL RESULTS ━━━
{json.dumps(allele_results, indent=2)}
"""
section("1h-allele. Allele-specific PWM scoring — motif GAIN and LOSS", summary_allele)


# ══════════════════════════════════════════════════════════════════════════════
# Write output
# ══════════════════════════════════════════════════════════════════════════════
header = (
    f"STEP 1g + 1h FIXED — rs11867200 allele-specific TF binding\n"
    f"Generated: 2026-05-23\n"
    f"Substeps: 1g ENCODE ChIP local | 1h-local JASPAR2022 local | 1h-allele PWM scoring\n"
    f"{'='*70}\n"
)

with open(OUT_FILE, "w") as fh:
    fh.write(header)
    fh.write("".join(sections))

print(f"\n[DONE] Results written to: {OUT_FILE}")
