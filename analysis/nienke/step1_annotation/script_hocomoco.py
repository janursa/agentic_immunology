"""
HOCOMOCO H12INVIVO bed overlap + GIMME vertebrate v5.0 allele-specific motif scoring
for rs11867200 (chr17:34,248,950 GRCh38, REF=C)

Step 1 — HOCOMOCO H12INVIVO bed overlap:
  Check whether any of the 1,442 H12INVIVO TFBS bed files have a pre-mapped motif
  overlapping the SNP position in the reference genome (hg38).

Step 2 — GIMME vertebrate v5.0 allele-specific scoring:
  Score all 1,796 GIMME motifs (vertebrate TFs from JASPAR/HOCOMOCO/CIS-BP/ENCODE)
  for allele-specific effects using the same log-odds PWM approach as the original
  JASPAR scan (80% threshold, Δ≥2.0 log2).

Output: temp/nienke/step1_annotation/results_hocomoco.txt
"""

import os, glob, gzip, json, re
import numpy as np

# ── Locus ──────────────────────────────────────────────────────────────────────
LOCUS_SEQ = "TGGCATGCAACATTTTGCAACCAAGCGGAAGAAACATCATCCGCAAAGAA"
SNP_IDX   = 25         # 0-based; REF = C
REF_BASE  = "C"
SNP_CHROM = "chr17"
SNP_POS_0 = 34248949   # 0-based (BED half-open)
assert LOCUS_SEQ[SNP_IDX] == REF_BASE

def make_alt(seq, idx, base):
    return seq[:idx] + base + seq[idx+1:]

SEQ = {
    "REF_C": LOCUS_SEQ,
    "ALT_T": make_alt(LOCUS_SEQ, SNP_IDX, "T"),
    "ALT_G": make_alt(LOCUS_SEQ, SNP_IDX, "G"),
}

# ── Paths ──────────────────────────────────────────────────────────────────────
HOCOMOCO_DIR = "/vol/projects/jnourisa/genernbi/resources/supp_data/databases/granie/H12INVIVO/"
GIMME_PFM    = "/vol/projects/jnourisa/genernbi/resources/supp_data/databases/celloracle/gimme.vertebrate.v5.0.pfm"
OUT_FILE     = "/vol/projects/BIIM/agentic_immunology/temp/nienke/step1_annotation/results_hocomoco.txt"

# ── Scoring constants (same as original JASPAR scan) ──────────────────────────
BASE_IDX     = {"A": 0, "C": 1, "G": 2, "T": 3}
PSEUDOCOUNT  = 0.001
BG           = 0.25
SCORE_FRAC   = 0.80
DELTA_THRESH = 2.0

# ── PWM scoring utilities ──────────────────────────────────────────────────────
def normalize_pfm(mat):
    mat = mat + PSEUDOCOUNT
    mat /= mat.sum(axis=1, keepdims=True)
    return mat

def pwm_max_score(pwm_freq):
    return float(np.sum(np.max(np.log2(pwm_freq) - np.log2(BG), axis=1)))

def score_window(seq_window, pwm_freq):
    s = 0.0
    for pos, base in enumerate(seq_window.upper()):
        idx = BASE_IDX.get(base)
        if idx is not None:
            s += np.log2(pwm_freq[pos, idx]) - np.log2(BG)
    return float(s)

def best_score_over_snp(seq, pwm_freq):
    L_seq = len(seq)
    L_mot = pwm_freq.shape[0]
    best = -1e9
    for start in range(max(0, SNP_IDX - L_mot + 1), min(L_seq - L_mot + 1, SNP_IDX + 1)):
        s = score_window(seq[start:start + L_mot], pwm_freq)
        if s > best:
            best = s
    return best

def classify(s_alt, s_ref, delta, threshold):
    if s_alt >= threshold and delta >= DELTA_THRESH:
        return "GAIN"
    if s_ref >= threshold and delta <= -DELTA_THRESH:
        return "LOSS"
    return "neutral"

# ── Step 1: HOCOMOCO H12INVIVO bed overlap ─────────────────────────────────────
print("=" * 70)
print("STEP 1 — HOCOMOCO H12INVIVO bed overlap")
print(f"SNP: {SNP_CHROM}:{SNP_POS_0 + 1} (1-based GRCh38)")
print("=" * 70)

bed_files = sorted(glob.glob(os.path.join(HOCOMOCO_DIR, "*.bed.gz")))
print(f"Scanning {len(bed_files)} HOCOMOCO H12INVIVO bed files ...")

bed_hits = []
for i, fpath in enumerate(bed_files):
    fname = os.path.basename(fpath)
    tf_hoco_id = fname.replace("_TFBS.bed.gz", "")
    tf_symbol  = tf_hoco_id.split(".")[0]
    try:
        with gzip.open(fpath, "rt") as fh:
            on_chr17 = False
            for line in fh:
                parts = line.split("\t", 6)
                if parts[0] != SNP_CHROM:
                    if on_chr17:
                        break  # left chr17, done
                    continue
                on_chr17 = True
                start, end = int(parts[1]), int(parts[2])
                if start > SNP_POS_0:
                    break  # sorted; won't find it further
                if end > SNP_POS_0:  # start <= SNP_POS_0 < end
                    bed_hits.append({
                        "tf_symbol":  tf_symbol,
                        "hoco_id":    tf_hoco_id,
                        "start":      start,
                        "end":        end,
                        "motif_seq":  parts[3].strip() if len(parts) > 3 else "N/A",
                        "score":      parts[4].strip() if len(parts) > 4 else "N/A",
                        "strand":     parts[5].strip() if len(parts) > 5 else "N/A",
                    })
                    break
    except Exception as e:
        print(f"  [WARN] {fname}: {e}")

    if (i + 1) % 200 == 0:
        print(f"  Scanned {i+1}/{len(bed_files)}, hits so far: {len(bed_hits)}")

print(f"\nHOCOMOCO H12INVIVO direct hits at {SNP_CHROM}:{SNP_POS_0 + 1}: {len(bed_hits)}")
for h in bed_hits:
    print(f"  {h['tf_symbol']:12s}  {h['hoco_id']:40s}  "
          f"pos {h['start']}-{h['end']}  strand {h['strand']}  "
          f"score {h['score']}  seq {h['motif_seq']}")

# ── Step 2: GIMME vertebrate v5.0 allele-specific scoring ─────────────────────
print("\n" + "=" * 70)
print("STEP 2 — GIMME vertebrate v5.0 allele-specific motif scoring")
print("=" * 70)

def parse_gimme_pfm(pfm_file):
    """Parse GIMME .pfm: #ID desc, >ID, then A C G T probability rows."""
    motifs = []
    current_id, current_desc, current_rows = None, "", []
    with open(pfm_file) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#"):
                if current_id and current_rows:
                    motifs.append((current_id, current_desc,
                                   np.array(current_rows, dtype=float)))
                    current_rows = []
                parts = line[1:].split("\t", 1)
                current_id   = parts[0].strip()
                current_desc = parts[1].strip() if len(parts) > 1 else ""
            elif line.startswith(">"):
                pass  # ID confirmation, skip
            elif line.strip():
                vals = [float(x) for x in line.split()]
                if len(vals) == 4:
                    current_rows.append(vals)
    if current_id and current_rows:
        motifs.append((current_id, current_desc,
                       np.array(current_rows, dtype=float)))
    return motifs

def extract_human_tfs(desc):
    """Return recognisable human TF symbols from a GIMME description string."""
    # HOCOMOCO human: GENE_HUMAN.H...
    hocomoco = re.findall(r'([A-Z][A-Z0-9]+)_HUMAN\.H', desc)
    # JASPAR: MA\d+\.\d+_GENE
    jaspar   = re.findall(r'MA\d+\.\d+_([A-Z][A-Z0-9]+)', desc)
    # Standalone uppercase gene names (word boundary, ≥2 chars, not all-digit)
    standalone = re.findall(r'\b([A-Z][A-Z0-9]{1,8})\b', desc)
    # Deduplicate, prefer HOCOMOCO > JASPAR > standalone; cap at 5
    seen = set()
    result = []
    for t in hocomoco + jaspar + standalone:
        if t not in seen and not t.isdigit():
            seen.add(t)
            result.append(t)
        if len(result) >= 6:
            break
    return result

print(f"Parsing GIMME PFM: {GIMME_PFM}")
motifs = parse_gimme_pfm(GIMME_PFM)
print(f"Total GIMME motifs: {len(motifs)}")

results = []
for motif_id, desc, pfm_raw in motifs:
    if pfm_raw.shape[1] != 4:
        continue

    pwm_freq  = normalize_pfm(pfm_raw.copy())
    max_score = pwm_max_score(pwm_freq)
    if max_score <= 0:
        continue

    threshold = SCORE_FRAC * max_score

    s_ref = best_score_over_snp(SEQ["REF_C"], pwm_freq)
    s_T   = best_score_over_snp(SEQ["ALT_T"], pwm_freq)
    s_G   = best_score_over_snp(SEQ["ALT_G"], pwm_freq)
    dT    = s_T - s_ref
    dG    = s_G - s_ref

    eff_T = classify(s_T, s_ref, dT, threshold)
    eff_G = classify(s_G, s_ref, dG, threshold)

    if eff_T != "neutral" or eff_G != "neutral":
        human_tfs = extract_human_tfs(desc)
        results.append({
            "motif_id":    motif_id,
            "human_tfs":   human_tfs,
            "description": desc,
            "motif_len":   int(pfm_raw.shape[0]),
            "max_score":   round(max_score, 3),
            "threshold_80": round(threshold, 3),
            "score_REF_C": round(s_ref, 3),
            "score_ALT_T": round(s_T, 3),
            "score_ALT_G": round(s_G, 3),
            "delta_T":     round(dT, 3),
            "delta_G":     round(dG, 3),
            "pct_max_REF": round(s_ref / max_score * 100, 1),
            "pct_max_T":   round(s_T   / max_score * 100, 1),
            "pct_max_G":   round(s_G   / max_score * 100, 1),
            "effect_T":    eff_T,
            "effect_G":    eff_G,
        })

print(f"Significant GIMME results: {len(results)}")

losses_T = sorted([r for r in results if r["effect_T"] == "LOSS"], key=lambda x: x["delta_T"])
losses_G = sorted([r for r in results if r["effect_G"] == "LOSS"], key=lambda x: x["delta_G"])
gains_T  = sorted([r for r in results if r["effect_T"] == "GAIN"], key=lambda x: -x["delta_T"])
gains_G  = sorted([r for r in results if r["effect_G"] == "GAIN"], key=lambda x: -x["delta_G"])

# ── Formatting ─────────────────────────────────────────────────────────────────
def fmt_table(rows, delta_key):
    if not rows:
        return "  (none)\n"
    alt_k = "score_ALT_T" if "T" in delta_key else "score_ALT_G"
    pct_k = "pct_max_T"   if "T" in delta_key else "pct_max_G"
    hdr = (f"  {'MotifID':<28} {'Human TFs':<28} {'len':>4} "
           f"{'REF':>8} {'ALT':>8} {'Δ':>7} {'%REF':>6} {'%ALT':>6}\n"
           f"  {'-'*103}\n")
    body = ""
    for r in rows:
        tf_str = " | ".join(r["human_tfs"][:3]) if r["human_tfs"] else "?"
        body += (f"  {r['motif_id']:<28} {tf_str:<28} {r['motif_len']:>4} "
                 f"{r['score_REF_C']:>8.3f} {r[alt_k]:>8.3f} {r[delta_key]:>7.3f} "
                 f"{r['pct_max_REF']:>6.1f} {r[pct_k]:>6.1f}\n")
    return hdr + body

# ── Write output ───────────────────────────────────────────────────────────────
lines = []
lines.append("HOCOMOCO H12INVIVO bed overlap + GIMME vertebrate v5.0 allele scoring")
lines.append(f"Locus: chr17:34,248,950 (GRCh38) | rs11867200  REF=C | ALT-T | ALT-G")
lines.append(f"Sequence (50 bp): {LOCUS_SEQ}")
lines.append(f"{'':>25}^ SNP index {SNP_IDX}")
lines.append("=" * 70)

lines.append(f"\n── STEP 1: HOCOMOCO H12INVIVO bed overlap  (n={len(bed_hits)}) ──")
if bed_hits:
    lines.append(f"  {'TF':12s}  {'HOCOMOCO ID':40s}  {'pos':20s}  strand  score  seq")
    lines.append("  " + "-" * 100)
    for h in bed_hits:
        lines.append(f"  {h['tf_symbol']:12s}  {h['hoco_id']:40s}  "
                     f"{h['start']}-{h['end']:20}  {h['strand']}  {h['score']}  {h['motif_seq']}")
else:
    lines.append("  No direct HOCOMOCO H12INVIVO motif hit at this exact position.")
    lines.append("  (Absence indicates ChIP-seq evidence was not available at this locus,")
    lines.append("   not that TF binding is absent — allele scoring below is more sensitive.)")

lines.append(f"\n── STEP 2: GIMME vertebrate v5.0 allele scoring  ──")
lines.append(f"   Total motifs scored: {len(motifs)}")
lines.append(f"   Significant hits:    {len(results)}")
lines.append(f"   Criteria: GAIN: ALT ≥80% max AND Δ≥+{DELTA_THRESH}  |  "
             f"LOSS: REF ≥80% max AND Δ≤-{DELTA_THRESH}")

lines.append(f"\n  LOSS: C→T disrupts binding  (n={len(losses_T)})")
lines.append(fmt_table(losses_T, "delta_T"))

lines.append(f"  GAIN: C→T creates binding   (n={len(gains_T)})")
lines.append(fmt_table(gains_T, "delta_T"))

lines.append(f"  LOSS: C→G disrupts binding  (n={len(losses_G)})")
lines.append(fmt_table(losses_G, "delta_G"))

lines.append(f"  GAIN: C→G creates binding   (n={len(gains_G)})")
lines.append(fmt_table(gains_G, "delta_G"))

lines.append("\n── ALL SIGNIFICANT RESULTS (JSON) ──")
lines.append(json.dumps(results, indent=2))

output = "\n".join(lines)

with open(OUT_FILE, "w") as fh:
    fh.write(output)

print(f"\n[DONE] Written to: {OUT_FILE}")
# Also print summary to stdout
for l in lines[:-1]:  # skip the json block in stdout
    if "JSON" in l:
        break
    print(l)
