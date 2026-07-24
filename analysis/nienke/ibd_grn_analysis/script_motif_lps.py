"""
Step 2 extension — JASPAR sub-threshold motif scores at rs11867200 for all 16 TFs
+ Baseline→LPS Spearman ρ change

Goal: check whether the 13 ChIP-seq TFs also have motif disruption at rs11867200
below the Step 1h significance threshold, and visualise the LPS ρ reduction pattern.
"""

import os, time
import numpy as np
import pandas as pd
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── SNP locus ──────────────────────────────────────────────────────────────────
LOCUS_SEQ = "TGGCATGCAACATTTTGCAACCAAGCGGAAGAAACATCATCCGCAAAGAA"
SNP_IDX   = 25   # 0-based; REF = C
assert LOCUS_SEQ[SNP_IDX] == "C"

SEQ = {
    "REF_C": LOCUS_SEQ,
    "ALT_T": LOCUS_SEQ[:SNP_IDX] + "T" + LOCUS_SEQ[SNP_IDX+1:],
    "ALT_G": LOCUS_SEQ[:SNP_IDX] + "G" + LOCUS_SEQ[SNP_IDX+1:],
}

# ── TF sets ────────────────────────────────────────────────────────────────────
TFS_CHIP  = ['CEBPB','FOS','FOSL2','GATA2','GATA3','JUN','JUND','MAX',
             'MEF2A','MYC','NFIC','PBX3','TCF12']
TFS_MOTIF = ['SPI1','SPIB','ETV6']
ALL_TFS   = TFS_CHIP + TFS_MOTIF

MOTIF_LOSS = {'SPI1': 'T', 'SPIB': 'T', 'ETV6': 'T+G'}
LOSS_DELTA_THRESH = -2.0   # log2 bits
SCORE_FRAC        = 0.80   # binding threshold (%max)

# ETV6 → use aop matrix (MA2296.1) which was the match in Step 1h
ETV6_FALLBACK_MATRIX = "MA2296.1"

OUTDIR = "/vol/projects/BIIM/agentic_immunology/temp/nienke/step2_grn"
IMGDIR = os.path.join(OUTDIR, "images")
os.makedirs(IMGDIR, exist_ok=True)

# ── Load existing Spearman results ─────────────────────────────────────────────
df_grn = pd.read_csv(os.path.join(OUTDIR, "grn_spearman_results.tsv"), sep='\t')

# ── JASPAR scoring utilities ───────────────────────────────────────────────────
BASE_IDX    = {"A": 0, "C": 1, "G": 2, "T": 3}
PSEUDOCOUNT = 0.001
BG          = 0.25

def normalize_pfm(pfm_dict):
    L = len(pfm_dict["A"])
    mat = np.zeros((L, 4))
    for col, k in enumerate(["A", "C", "G", "T"]):
        mat[:, col] = np.array(pfm_dict[k], dtype=float)
    mat += PSEUDOCOUNT
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
    L_seq, L_mot = len(seq), pwm_freq.shape[0]
    best = -1e9
    for start in range(max(0, SNP_IDX - L_mot + 1),
                       min(L_seq - L_mot + 1, SNP_IDX + 1)):
        s = score_window(seq[start:start + L_mot], pwm_freq)
        if s > best:
            best = s
    return best

def fetch_matrices_by_name(tf_name, tax_id=9606, retries=3):
    url = "https://jaspar.genereg.net/api/v1/matrix/"
    params = {"name": tf_name, "species": tax_id, "format": "json", "page_size": 50}
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, timeout=20)
            r.raise_for_status()
            return r.json().get("results", [])
        except Exception:
            if attempt < retries:
                time.sleep(0.5)
    return []

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

def score_single_matrix(matrix_id):
    pfm = fetch_pfm(matrix_id)
    if pfm is None or "A" not in pfm:
        return None
    pwm_freq  = normalize_pfm(pfm)
    max_score = pwm_max_score(pwm_freq)
    if max_score <= 0:
        return None
    threshold = SCORE_FRAC * max_score
    s_ref = best_score_over_snp(SEQ["REF_C"], pwm_freq)
    s_T   = best_score_over_snp(SEQ["ALT_T"], pwm_freq)
    s_G   = best_score_over_snp(SEQ["ALT_G"], pwm_freq)
    return dict(
        matrix_id   = matrix_id,
        max_score   = round(max_score, 3),
        threshold80 = round(threshold, 3),
        score_REF   = round(s_ref, 3),
        score_T     = round(s_T, 3),
        score_G     = round(s_G, 3),
        delta_T     = round(s_T - s_ref, 3),
        delta_G     = round(s_G - s_ref, 3),
        pct_REF     = round(s_ref / max_score * 100, 1),
        pct_T       = round(s_T   / max_score * 100, 1),
        pct_G       = round(s_G   / max_score * 100, 1),
    )

def score_tf(tf_name):
    """Score a TF: try all JASPAR human matrices; pick the one with largest |delta|."""
    matrices = fetch_matrices_by_name(tf_name)
    # ETV6 fallback: if no human matrix found, use aop (MA2296.1)
    if not matrices and tf_name == "ETV6":
        print(f"    ETV6 not found by name → using aop fallback {ETV6_FALLBACK_MATRIX}")
        res = score_single_matrix(ETV6_FALLBACK_MATRIX)
        if res:
            res['tf'] = tf_name
        return res

    best, best_abs = None, 0
    for mat in matrices:
        res = score_single_matrix(mat["matrix_id"])
        if res is None:
            continue
        abs_delta = max(abs(res['delta_T']), abs(res['delta_G']))
        if abs_delta > best_abs:
            best_abs = abs_delta
            best = res
            best['tf'] = tf_name
        time.sleep(0.05)
    return best

# ── Score all 16 TFs ───────────────────────────────────────────────────────────
print("Querying JASPAR and scoring at rs11867200 locus ...")
motif_data = {}
for tf in ALL_TFS:
    print(f"  {tf:<8}", end=" ", flush=True)
    res = score_tf(tf)
    if res:
        motif_data[tf] = res
        print(f"REF={res['score_REF']:.2f} ({res['pct_REF']:.0f}%)  "
              f"delta_T={res['delta_T']:+.3f}  delta_G={res['delta_G']:+.3f}  "
              f"[matrix {res['matrix_id']}]")
    else:
        print("NOT FOUND")

# ── Compute baseline→LPS ρ change per TF (mean over CD + UC) ──────────────────
rho_base = (df_grn[df_grn['condition'].isin(['CD_baseline','UC_baseline'])]
            .groupby('TF')['rho'].mean())
rho_lps  = (df_grn[df_grn['condition'].isin(['CD_LPS','UC_LPS'])]
            .groupby('TF')['rho'].mean())
delta_rho = (rho_lps - rho_base).reindex(ALL_TFS)

# ── Save motif scores table ────────────────────────────────────────────────────
rows = []
for tf in ALL_TFS:
    m = motif_data.get(tf, {})
    rows.append({
        'TF':         tf,
        'tf_source':  'motif-LOSS' if tf in TFS_MOTIF else 'ChIP-seq',
        'matrix_id':  m.get('matrix_id', 'N/A'),
        'pct_REF':    m.get('pct_REF', np.nan),
        'score_REF':  m.get('score_REF', np.nan),
        'delta_T':    m.get('delta_T', np.nan),
        'delta_G':    m.get('delta_G', np.nan),
        'effect_T':   ('LOSS' if m.get('pct_REF', 0) >= 80 and m.get('delta_T', 0) <= LOSS_DELTA_THRESH
                       else 'GAIN' if m.get('delta_T', 0) >= 2.0 else 'sub-threshold'),
        'rho_baseline': rho_base.get(tf, np.nan),
        'rho_lps':      rho_lps.get(tf, np.nan),
        'delta_rho':    delta_rho.get(tf, np.nan),
    })
df_out = pd.DataFrame(rows)
tsv_path = os.path.join(OUTDIR, "tf_motif_snp_scores.tsv")
df_out.to_csv(tsv_path, sep='\t', index=False)
print(f"\nMotif scores table → {tsv_path}")
print(df_out[['TF','pct_REF','delta_T','delta_G','effect_T','rho_baseline','rho_lps','delta_rho']].to_string(index=False))

# ── Figure: 2-panel ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'hspace': 0.55})
x = np.arange(len(ALL_TFS))
chip_col   = '#4e8fd4'
motif_col  = '#8B0000'
xlabels    = [f'{tf}\n[{MOTIF_LOSS[tf]}]' if tf in MOTIF_LOSS else tf for tf in ALL_TFS]
shade_kw   = dict(color='#fee0d2', alpha=0.3, zorder=0)

# --- Panel A: GRN ρ change (baseline → LPS) ---
ax1 = axes[0]
bar_colors = [motif_col if tf in MOTIF_LOSS else chip_col for tf in ALL_TFS]
ax1.bar(x, delta_rho.values, color=bar_colors, alpha=0.85, edgecolor='white', linewidth=0.5)
ax1.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax1.set_xticks(x); ax1.set_xticklabels(xlabels, rotation=35, ha='right', fontsize=8.5)
ax1.set_ylabel('Δρ  (LPS − baseline)\n[mean CD + UC]', fontsize=10)
ax1.set_title('A. Change in TF–CCL2 Spearman ρ from baseline (RPMI) to LPS stimulation',
              fontsize=10, fontweight='bold')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
for i, tf in enumerate(ALL_TFS):
    if tf in MOTIF_LOSS:
        ax1.axvspan(i - 0.45, i + 0.45, **shade_kw)
# legend
ax1.legend(handles=[
    mpatches.Patch(color=motif_col, label='motif-LOSS TF (Step 1h)'),
    mpatches.Patch(color=chip_col, label='ChIP-seq TF (Step 1g)'),
], fontsize=9, loc='lower right', framealpha=0.9)

# --- Panel B: JASPAR motif delta at rs11867200 ---
ax2 = axes[1]
dT  = [motif_data.get(tf, {}).get('delta_T', np.nan) for tf in ALL_TFS]
dG  = [motif_data.get(tf, {}).get('delta_G', np.nan) for tf in ALL_TFS]
pct = [motif_data.get(tf, {}).get('pct_REF', np.nan) for tf in ALL_TFS]

w = 0.35
ax2.bar(x - w/2, dT, w, label='C→T allele', color='#e76f51', alpha=0.85, edgecolor='white', linewidth=0.5)
ax2.bar(x + w/2, dG, w, label='C→G allele', color='#457b9d', alpha=0.85, edgecolor='white', linewidth=0.5)
ax2.axhline(LOSS_DELTA_THRESH, color='crimson', linewidth=1.3, linestyle=':', label=f'LOSS threshold ({LOSS_DELTA_THRESH} bits)')
ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax2.set_xticks(x); ax2.set_xticklabels(xlabels, rotation=35, ha='right', fontsize=8.5)
ax2.set_ylabel('ΔPWM score (ALT − REF)\n[log2 bits]', fontsize=10)
ax2.set_title(
    'B. JASPAR motif score change at rs11867200 for all 16 TFs\n'
    '(dotted = LOSS threshold; % annotation = REF binding strength ≥ 80% of PWM max)',
    fontsize=10, fontweight='bold')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.legend(loc='lower right', fontsize=9, framealpha=0.9)

# Annotate REF binding % for TFs that actually bind (>=80%)
for i, (tf, p, dt, dg) in enumerate(zip(ALL_TFS, pct, dT, dG)):
    if not np.isnan(p) and p >= 80:
        top = max(dt if not np.isnan(dt) else 0,
                  dg if not np.isnan(dg) else 0)
        ax2.text(i, top + 0.15, f'{p:.0f}%', ha='center', va='bottom',
                 fontsize=7, color='#333333', fontweight='bold')

for i, tf in enumerate(ALL_TFS):
    if tf in MOTIF_LOSS:
        ax2.axvspan(i - 0.45, i + 0.45, **shade_kw)

plt.tight_layout()
out_path = os.path.join(IMGDIR, "grn_motif_lps_comparison.png")
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\nFigure saved → {out_path}")
print("[DONE]")
