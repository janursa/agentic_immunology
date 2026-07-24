"""
STEP 1h-allele FULL — rs11867200 allele-specific motif scan (all JASPAR human TFs)

Significance criteria (principled, from motif literature):
  GAIN: ALT score  > 0.80 * PWM_max_score  AND  delta > 2.0 log2
  LOSS: REF score  > 0.80 * PWM_max_score  AND  delta < -2.0 log2

This catches true gain-of-function sites (ALT actually matches the motif) and
avoids the "less bad" false positives where both alleles score poorly.

Runs with ciim.sif.
"""

import os, sys, json, time
import numpy as np
import requests

# ── Locus ──────────────────────────────────────────────────────────────────────
LOCUS_SEQ = "TGGCATGCAACATTTTGCAACCAAGCGGAAGAAACATCATCCGCAAAGAA"
SNP_IDX   = 25       # 0-based; REF = C
REF_BASE  = "C"
ALT_BASES = ["T", "G"]
assert LOCUS_SEQ[SNP_IDX] == REF_BASE

# ALT sequences
def make_alt(seq, idx, base):
    return seq[:idx] + base + seq[idx+1:]

SEQ = {
    "REF_C": LOCUS_SEQ,
    "ALT_T": make_alt(LOCUS_SEQ, SNP_IDX, "T"),
    "ALT_G": make_alt(LOCUS_SEQ, SNP_IDX, "G"),
}

OUT_FILE = "/vol/projects/BIIM/agentic_immunology/temp/nienke/step1_annotation/results_1h_allele_full.txt"

# ── Scoring ───────────────────────────────────────────────────────────────────
BASE_IDX  = {"A": 0, "C": 1, "G": 2, "T": 3}
PSEUDOCOUNT = 0.001
BG = 0.25

def normalize_pfm(pfm_dict):
    keys = ["A", "C", "G", "T"]
    L = len(pfm_dict["A"])
    mat = np.zeros((L, 4))
    for col, k in enumerate(keys):
        mat[:, col] = np.array(pfm_dict[k], dtype=float)
    mat += PSEUDOCOUNT
    mat /= mat.sum(axis=1, keepdims=True)
    return mat  # (L, 4)

def pwm_max_score(pwm_freq):
    """Theoretical maximum score: sum of best log-odds at each position."""
    return float(np.sum(np.max(np.log2(pwm_freq) - np.log2(BG), axis=1)))

def score_window(seq_window, pwm_freq):
    s = 0.0
    for pos, base in enumerate(seq_window.upper()):
        idx = BASE_IDX.get(base)
        if idx is not None:
            s += np.log2(pwm_freq[pos, idx]) - np.log2(BG)
    return float(s)

def best_score_over_snp(seq, pwm_freq):
    """Max log-odds score across all windows of length motif_len that contain SNP_IDX."""
    L_seq = len(seq)
    L_mot = pwm_freq.shape[0]
    best, best_start = -1e9, None
    for start in range(max(0, SNP_IDX - L_mot + 1),
                       min(L_seq - L_mot + 1, SNP_IDX + 1)):
        s = score_window(seq[start:start + L_mot], pwm_freq)
        if s > best:
            best, best_start = s, start
    return best, best_start

# ── Fetch all JASPAR human matrices (paginated) ───────────────────────────────
def fetch_all_jaspar_human(tax_id=9606, page_size=100, retries=3):
    matrices = []
    url = "https://jaspar.genereg.net/api/v1/matrix/"
    params = {"species": tax_id, "format": "json", "page_size": page_size}
    page = 1
    while True:
        params["page"] = page
        for attempt in range(retries + 1):
            try:
                r = requests.get(url, params=params, timeout=30)
                r.raise_for_status()
                data = r.json()
                break
            except Exception as e:
                if attempt == retries:
                    print(f"  [WARN] page {page} failed after {retries} retries: {e}")
                    data = None
                time.sleep(1)
        if data is None:
            break
        results = data.get("results", [])
        matrices.extend(results)
        print(f"  Page {page}: {len(results)} matrices (total so far: {len(matrices)})")
        if not data.get("next"):
            break
        page += 1
        time.sleep(0.05)
    return matrices

def fetch_pfm(matrix_id, retries=3):
    url = f"https://jaspar.genereg.net/api/v1/matrix/{matrix_id}/"
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params={"format": "json"}, timeout=20)
            r.raise_for_status()
            return r.json().get("pfm", None)
        except Exception:
            if attempt < retries:
                time.sleep(0.5)
    return None

# ── Main scan ─────────────────────────────────────────────────────────────────
print("Fetching all JASPAR human matrices ...")
all_matrices = fetch_all_jaspar_human()
print(f"Total matrices: {len(all_matrices)}")

# Significance thresholds
SCORE_FRAC   = 0.80   # ALT/REF score must be >= 80% of max PWM score to count as "binding"
DELTA_THRESH = 2.0    # |delta| >= 2.0 log2 bits

results = []
failed  = []

for i, mat in enumerate(all_matrices):
    matrix_id = mat["matrix_id"]
    tf_name   = mat.get("name", matrix_id)

    pfm = fetch_pfm(matrix_id)
    if pfm is None or "A" not in pfm:
        failed.append(matrix_id)
        continue

    try:
        pwm_freq = normalize_pfm(pfm)
        motif_len = pwm_freq.shape[0]
        max_score = pwm_max_score(pwm_freq)

        if max_score <= 0:
            continue  # degenerate motif

        threshold = SCORE_FRAC * max_score

        scores = {}
        for allele, seq in SEQ.items():
            s, w = best_score_over_snp(seq, pwm_freq)
            scores[allele] = (s, w)

        s_ref = scores["REF_C"][0]
        s_T   = scores["ALT_T"][0]
        s_G   = scores["ALT_G"][0]
        dT    = s_T - s_ref
        dG    = s_G - s_ref

        # Classify
        def classify(s_alt, s_ref, delta):
            if s_alt >= threshold and delta >= DELTA_THRESH:
                return "GAIN"
            if s_ref >= threshold and delta <= -DELTA_THRESH:
                return "LOSS"
            return "neutral"

        eff_T = classify(s_T, s_ref, dT)
        eff_G = classify(s_G, s_ref, dG)

        if eff_T != "neutral" or eff_G != "neutral":
            results.append({
                "tf":           tf_name,
                "matrix_id":    matrix_id,
                "motif_len":    int(motif_len),
                "max_score":    round(max_score, 3),
                "threshold_80": round(threshold, 3),
                "score_REF_C":  round(s_ref, 3),
                "score_ALT_T":  round(s_T, 3),
                "score_ALT_G":  round(s_G, 3),
                "delta_T":      round(dT, 3),
                "delta_G":      round(dG, 3),
                "pct_max_REF":  round(s_ref / max_score * 100, 1),
                "pct_max_T":    round(s_T   / max_score * 100, 1),
                "pct_max_G":    round(s_G   / max_score * 100, 1),
                "effect_T":     eff_T,
                "effect_G":     eff_G,
            })
    except Exception as e:
        failed.append(f"{matrix_id}({e})")

    if (i + 1) % 50 == 0:
        print(f"  Scored {i+1}/{len(all_matrices)} matrices, {len(results)} significant so far")
    time.sleep(0.03)

print(f"\nDone. Significant: {len(results)} | Failed: {len(failed)}")

# ── Sort and report ───────────────────────────────────────────────────────────
gains_T = sorted([r for r in results if r["effect_T"] == "GAIN"],
                 key=lambda x: -x["delta_T"])
gains_G = sorted([r for r in results if r["effect_G"] == "GAIN"],
                 key=lambda x: -x["delta_G"])
losses_T = sorted([r for r in results if r["effect_T"] == "LOSS"],
                  key=lambda x: x["delta_T"])
losses_G = sorted([r for r in results if r["effect_G"] == "LOSS"],
                  key=lambda x: x["delta_G"])

def fmt_table(rows, delta_key):
    if not rows:
        return "  (none)\n"
    hdr = (f"  {'TF':<14} {'matrix':<12} {'motif_len':>10} {'score_REF':>10} "
           f"{'score_ALT':>10} {'delta':>7} {'%max_REF':>9} {'%max_ALT':>9}\n")
    sep = "  " + "-"*85 + "\n"
    body = ""
    alt_key = "score_ALT_T" if "T" in delta_key else "score_ALT_G"
    pct_key = "pct_max_T" if "T" in delta_key else "pct_max_G"
    for r in rows:
        body += (f"  {r['tf']:<14} {r['matrix_id']:<12} {r['motif_len']:>10} "
                 f"{r['score_REF_C']:>10.3f} {r[alt_key]:>10.3f} {r[delta_key]:>7.3f} "
                 f"{r['pct_max_REF']:>9.1f} {r[pct_key]:>9.1f}\n")
    return hdr + sep + body

summary = f"""
Locus: chr17:34,248,950 (GRCh38) | rs11867200
Sequence (50 bp, RegulomeDB):
  {LOCUS_SEQ}
  {'':>25}^ SNP (index {SNP_IDX}): REF=C | ALT-T | ALT-G

Significance criteria:
  GAIN: ALT score >= {SCORE_FRAC*100:.0f}% of PWM max score  AND  delta >= +{DELTA_THRESH:.1f} log2 bits
  LOSS: REF score >= {SCORE_FRAC*100:.0f}% of PWM max score  AND  delta <= -{DELTA_THRESH:.1f} log2 bits

Total JASPAR human matrices scored: {len(all_matrices)}
Significant results: {len(results)} | Failed to retrieve: {len(failed)}

━━━ GAIN: C→T creates new TF binding site ━━━  (n={len(gains_T)})
{fmt_table(gains_T, 'delta_T')}
━━━ GAIN: C→G creates new TF binding site ━━━  (n={len(gains_G)})
{fmt_table(gains_G, 'delta_G')}
━━━ LOSS: C→T disrupts existing binding ━━━  (n={len(losses_T)})
{fmt_table(losses_T, 'delta_T')}
━━━ LOSS: C→G disrupts existing binding ━━━  (n={len(losses_G)})
{fmt_table(losses_G, 'delta_G')}

━━━ ALL SIGNIFICANT RESULTS (JSON) ━━━
{json.dumps(results, indent=2)}
"""

with open(OUT_FILE, "w") as fh:
    fh.write(f"STEP 1h-allele FULL — rs11867200 allele-specific motif scan (all JASPAR human TFs)\n")
    fh.write(f"Generated: 2026-05-23\n{'='*70}\n")
    fh.write(summary)

print(f"\n[DONE] Results written to: {OUT_FILE}")
