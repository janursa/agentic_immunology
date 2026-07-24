"""
Step 2 — CCL2 GRN via pairwise Spearman correlation (IBD dataset)

4 models: CD_RPMI, CD_LPS, UC_RPMI, UC_LPS
Regulators: 13 ENCODE ChIP-seq TFs (Step 1g) + 3 motif-disruption TFs (Step 1h): SPI1, SPIB, ETV6
Target: CCL2
Method: pairwise Spearman rho + p-value across cells (log-normalized expression)
"""

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
H5AD   = "/vol/projects/BIIM/agentic_immunology/datalake/omics/IBD/rna.h5ad"
OUTDIR = "/vol/projects/BIIM/agentic_immunology/temp/nienke/step2_grn"
IMGDIR = os.path.join(OUTDIR, "images")
os.makedirs(IMGDIR, exist_ok=True)

# ── TF sets ────────────────────────────────────────────────────────────────────
TFS_CHIP  = ['CEBPB','FOS','FOSL2','GATA2','GATA3','JUN','JUND','MAX',
             'MEF2A','MYC','NFIC','PBX3','TCF12']            # Step 1g ChIP-seq
TFS_MOTIF = ['SPI1','SPIB','ETV6']                           # Step 1h motif-LOSS TFs
ALL_TFS   = TFS_CHIP + TFS_MOTIF                             # 16 total
TARGET    = 'CCL2'

# ── Motif disruption annotations (for heatmap y-label decoration) ──────────────
MOTIF_LOSS = {'SPI1': 'T', 'SPIB': 'T', 'ETV6': 'T+G'}     # allele with LOSS

# ── Conditions ─────────────────────────────────────────────────────────────────
CONDITIONS = [
    ('CD',  'RPMI', 'CD_baseline'),
    ('CD',  'LPS',  'CD_LPS'),
    ('UC',  'RPMI', 'UC_baseline'),
    ('UC',  'LPS',  'UC_LPS'),
]

# ── Load + normalize ───────────────────────────────────────────────────────────
print("Loading IBD rna.h5ad ...")
adata = sc.read_h5ad(H5AD)
print(f"  Raw shape: {adata.shape}")

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
print("  Log-normalized (CPM + log1p)")

# ── Compute Spearman correlations ──────────────────────────────────────────────
# Bonferroni: 16 TFs × 4 conditions = 64 tests
N_TESTS  = len(ALL_TFS) * len(CONDITIONS)
BONF_THR = 0.05 / N_TESTS
print(f"\nBonferroni threshold: p < {BONF_THR:.2e}  ({N_TESTS} tests)")

results = {}   # {label: {tf: {r, p, n}}}

for disease, stim, label in CONDITIONS:
    mask = (adata.obs['disease'] == disease) & (adata.obs['stimulation'] == stim)
    sub  = adata[mask]
    n    = sub.n_obs
    print(f"\n{label}: {n} cells")

    expr = {}
    for g in ALL_TFS + [TARGET]:
        vec = sub[:, g].X
        if hasattr(vec, 'toarray'):
            vec = vec.toarray().flatten()
        expr[g] = vec.astype(float)

    ccl2 = expr[TARGET]
    results[label] = {}
    for tf in ALL_TFS:
        rho, p = spearmanr(expr[tf], ccl2)
        results[label][tf] = {'r': round(rho, 4), 'p': round(p, 6), 'n': n}
        sig = '*' if p < BONF_THR else ' '
        print(f"  {tf:<8} rho={rho:+.3f}  p={p:.2e} {sig}")

# ── Save results ───────────────────────────────────────────────────────────────
rows = []
for label, tf_dict in results.items():
    for tf, vals in tf_dict.items():
        rows.append({'condition': label, 'TF': tf,
                     'rho': vals['r'], 'p': vals['p'], 'n': vals['n'],
                     'sig_bonf': vals['p'] < BONF_THR,
                     'tf_source': 'ChIP-seq' if tf in TFS_CHIP else 'motif-LOSS'})
df_res = pd.DataFrame(rows)
tsv_out = os.path.join(OUTDIR, "grn_spearman_results.tsv")
df_res.to_csv(tsv_out, sep='\t', index=False)
print(f"\nResults saved → {tsv_out}")

# ── Heatmap with significance stars ───────────────────────────────────────────
labels = [c[2] for c in CONDITIONS]

rho_mat = pd.DataFrame({lbl: [results[lbl][tf]['r'] for tf in ALL_TFS]
                         for lbl in labels}, index=ALL_TFS)
p_mat   = pd.DataFrame({lbl: [results[lbl][tf]['p'] for tf in ALL_TFS]
                         for lbl in labels}, index=ALL_TFS)

vmax = max(abs(rho_mat.values.min()), abs(rho_mat.values.max()))

fig, ax = plt.subplots(figsize=(6, 7.5))
im = ax.imshow(rho_mat.values, aspect='auto', cmap='RdBu_r',
               vmin=-vmax, vmax=vmax)
plt.colorbar(im, ax=ax, label='Spearman ρ (TF vs CCL2)', fraction=0.046, pad=0.04)

ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=10)
ax.set_yticks(range(len(ALL_TFS)))

# Y-axis labels: motif-LOSS TFs get allele annotation
ylabels = []
for tf in ALL_TFS:
    if tf in MOTIF_LOSS:
        ylabels.append(f'{tf}  [motif-LOSS {MOTIF_LOSS[tf]}]')
    else:
        ylabels.append(tf)
ax.set_yticklabels(ylabels, fontsize=9)

# Color motif-LOSS row labels red
for tick, tf in zip(ax.get_yticklabels(), ALL_TFS):
    if tf in MOTIF_LOSS:
        tick.set_color('#8B0000')

ax.set_title('Spearman ρ — TF vs CCL2 (IBD)\n'
             '* = Bonferroni p < 0.05/64 | red = motif-LOSS TFs (Step 1h)', fontsize=10)

# Cell annotations: rho value + * if significant
for i, tf in enumerate(ALL_TFS):
    for j, lbl in enumerate(labels):
        val  = rho_mat.values[i, j]
        pval = p_mat.values[i, j]
        star = '*' if pval < BONF_THR else ''
        txt  = f'{val:.2f}{star}'
        tc   = 'white' if abs(val) > vmax * 0.5 else 'black'
        ax.text(j, i, txt, ha='center', va='center', fontsize=8,
                color=tc, fontweight='bold' if star else 'normal')

# Horizontal separator between ChIP-seq and motif-LOSS blocks
ax.axhline(len(TFS_CHIP) - 0.5, color='white', linewidth=2, linestyle='--')

plt.tight_layout()
hm_out = os.path.join(IMGDIR, "grn_spearman_heatmap.png")
fig.savefig(hm_out, dpi=150, bbox_inches='tight')
print(f"Heatmap saved → {hm_out}")

# ── Barplot ────────────────────────────────────────────────────────────────────
colors  = ['#4e8fd4', '#d45c4e', '#6abf69', '#c97bb2']
x       = np.arange(len(ALL_TFS))
width   = 0.18
offsets = np.linspace(-(len(labels)-1)/2 * width, (len(labels)-1)/2 * width, len(labels))

fig2, ax2 = plt.subplots(figsize=(16, 5.5))

for gi, (label, col) in enumerate(zip(labels, colors)):
    rs = [results[label][tf]['r'] for tf in ALL_TFS]
    ps = [results[label][tf]['p'] for tf in ALL_TFS]
    ax2.bar(x + offsets[gi], rs, width, label=label, color=col, alpha=0.85,
            edgecolor='white', linewidth=0.5)
    for bi, (r_val, p_val) in enumerate(zip(rs, ps)):
        if p_val < BONF_THR:
            ax2.text(x[bi] + offsets[gi], r_val + (0.003 if r_val >= 0 else -0.01),
                     '*', ha='center', va='bottom', fontsize=9, color='black', fontweight='bold')

# Shade motif-LOSS TF region
for i, tf in enumerate(ALL_TFS):
    if tf in MOTIF_LOSS:
        ax2.axvspan(i - 0.4, i + 0.4, color='#fee0d2', alpha=0.4, zorder=0)

ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax2.set_xticks(x)
xlabels = [f'{tf}\n[{MOTIF_LOSS[tf]}]' if tf in MOTIF_LOSS else tf for tf in ALL_TFS]
ax2.set_xticklabels(xlabels, rotation=35, ha='right', fontsize=9)
ax2.set_ylabel('Spearman ρ  (TF vs CCL2)', fontsize=11)
ax2.set_title('CCL2 GRN — Pairwise Spearman correlation (IBD dataset)\n'
              '* = Bonferroni p < 0.05/64 | shaded = motif-LOSS TFs (Step 1h)', fontsize=11)
ax2.legend(loc='upper right', fontsize=9, framealpha=0.9)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout()
bp_out = os.path.join(IMGDIR, "grn_spearman_barplot.png")
fig2.savefig(bp_out, dpi=150, bbox_inches='tight')
print(f"Barplot saved → {bp_out}")

print("\n[DONE]")
