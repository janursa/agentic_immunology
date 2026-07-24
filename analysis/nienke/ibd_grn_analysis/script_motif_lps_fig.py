"""
Step 2 extension — corrected figure:
  Panel A: Baseline→LPS Spearman ρ change per TF (general LPS effect)
  Panel B: REF allele binding strength at rs11867200 (pct of PWM max)
            → shows ONLY SPI1/SPIB/ETV6 bind at the SNP; ChIP TFs do not

Uses:
  - grn_spearman_results.tsv  (GRN correlations)
  - tf_motif_snp_scores.tsv   (new JASPAR scan output)
  - Step 1h hard-coded values for SPI1 and ETV6 (correct matrices)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUTDIR = "/vol/projects/BIIM/agentic_immunology/temp/nienke/step2_grn"
IMGDIR = os.path.join(OUTDIR, "images")
os.makedirs(IMGDIR, exist_ok=True)

# ── TF order ───────────────────────────────────────────────────────────────────
TFS_CHIP  = ['CEBPB','FOS','FOSL2','GATA2','GATA3','JUN','JUND','MAX',
             'MEF2A','MYC','NFIC','PBX3','TCF12']
TFS_MOTIF = ['SPI1','SPIB','ETV6']
ALL_TFS   = TFS_CHIP + TFS_MOTIF
MOTIF_LOSS = {'SPI1': 'T', 'SPIB': 'T', 'ETV6': 'T+G'}

# ── GRN data ───────────────────────────────────────────────────────────────────
df_grn = pd.read_csv(os.path.join(OUTDIR, "grn_spearman_results.tsv"), sep='\t')
rho_base = (df_grn[df_grn['condition'].isin(['CD_baseline','UC_baseline'])]
            .groupby('TF')['rho'].mean())
rho_lps  = (df_grn[df_grn['condition'].isin(['CD_LPS','UC_LPS'])]
            .groupby('TF')['rho'].mean())
delta_rho = (rho_lps - rho_base).reindex(ALL_TFS)

# ── JASPAR binding at rs11867200 ───────────────────────────────────────────────
# New JASPAR scoring (script_motif_lps.py) confirmed: all 13 ChIP TFs have
# pct_REF << 0 (negative; no binding at this locus).
# For SPI1 and ETV6, override with Step 1h correct matrices (MA0080.1, MA2296.1).
df_motif = pd.read_csv(os.path.join(OUTDIR, "tf_motif_snp_scores.tsv"), sep='\t')
df_motif = df_motif.set_index('TF')

# Step 1h correct values (these TFs actually bind at REF allele)
step1h_override = {
    'SPI1': {'pct_REF': 100.0, 'delta_T': -2.807, 'delta_G': -0.144, 'matrix': 'MA0080.1'},
    'ETV6': {'pct_REF':  81.8, 'delta_T': -4.982, 'delta_G': -4.683, 'matrix': 'MA2296.1 (aop)'},
    # SPIB MA0081.1 was correctly recovered by the new script
}
for tf, vals in step1h_override.items():
    for col, v in vals.items():
        if col in df_motif.columns:
            df_motif.at[tf, col] = v

pct_ref_all = []
delta_T_all = []
delta_G_all = []
for tf in ALL_TFS:
    pct   = df_motif.at[tf, 'pct_REF'] if tf in df_motif.index else np.nan
    dT    = df_motif.at[tf, 'delta_T'] if tf in df_motif.index else np.nan
    dG    = df_motif.at[tf, 'delta_G'] if tf in df_motif.index else np.nan
    pct_ref_all.append(pct)
    delta_T_all.append(dT)
    delta_G_all.append(dG)

# ── Print summary table ────────────────────────────────────────────────────────
print(f"{'TF':<8} {'source':<12} {'pct_REF':>8} {'delta_T':>8} {'delta_G':>8} "
      f"{'binds_REF':>10} {'delta_rho':>10}")
print("-" * 72)
for tf in ALL_TFS:
    src    = 'motif-LOSS' if tf in TFS_MOTIF else 'ChIP-seq'
    pct    = pct_ref_all[ALL_TFS.index(tf)]
    dT     = delta_T_all[ALL_TFS.index(tf)]
    dG     = delta_G_all[ALL_TFS.index(tf)]
    binds  = 'YES' if (not np.isnan(pct) and pct >= 80) else 'NO'
    drho   = delta_rho.get(tf, np.nan)
    print(f"{tf:<8} {src:<12} {pct:>8.1f} {dT:>8.3f} {dG:>8.3f} {binds:>10} {drho:>10.4f}")

# ── Figure: 2 panels ───────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'hspace': 0.60})
x          = np.arange(len(ALL_TFS))
chip_col   = '#4e8fd4'
motif_col  = '#8B0000'
xlabels    = [f'{tf}\n[{MOTIF_LOSS[tf]}]' if tf in MOTIF_LOSS else tf for tf in ALL_TFS]
shade_kw   = dict(color='#fee0d2', alpha=0.3, zorder=0)

# ── Panel A: Δρ (LPS − baseline) ──────────────────────────────────────────────
ax1 = axes[0]
bar_colors = [motif_col if tf in MOTIF_LOSS else chip_col for tf in ALL_TFS]
ax1.bar(x, delta_rho.values, color=bar_colors, alpha=0.85, edgecolor='white', linewidth=0.5)
ax1.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax1.set_xticks(x); ax1.set_xticklabels(xlabels, rotation=35, ha='right', fontsize=8.5)
ax1.set_ylabel('Δρ  (LPS − baseline)\n[mean CD + UC]', fontsize=10)
ax1.set_title(
    'A.  Change in TF–CCL2 Spearman ρ from baseline (RPMI) to LPS stimulation\n'
    '(general LPS-driven transcriptional reprogramming; not SNP-specific)',
    fontsize=10, fontweight='bold')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
for i, tf in enumerate(ALL_TFS):
    if tf in MOTIF_LOSS:
        ax1.axvspan(i - 0.45, i + 0.45, **shade_kw)
ax1.legend(handles=[
    mpatches.Patch(color=motif_col, label='motif-LOSS TF (Step 1h)'),
    mpatches.Patch(color=chip_col,  label='ChIP-seq TF (Step 1g)'),
], fontsize=9, loc='lower right', framealpha=0.9)

# ── Panel B: REF binding strength at rs11867200 ────────────────────────────────
ax2 = axes[1]

# cap display at 0 for negative pct_REF (negative = no binding)
pct_display = [max(0, p) if not np.isnan(p) else 0 for p in pct_ref_all]
b_colors = []
for tf, p in zip(ALL_TFS, pct_ref_all):
    if tf in MOTIF_LOSS:
        b_colors.append(motif_col if (not np.isnan(p) and p >= 80) else '#cc5555')
    else:
        b_colors.append('#bbbbbb')   # ChIP TFs: gray (no binding at locus)

bars = ax2.bar(x, pct_display, color=b_colors, alpha=0.88, edgecolor='white', linewidth=0.5)

# 80 % binding threshold
ax2.axhline(80, color='crimson', linewidth=1.3, linestyle=':', label='80% binding threshold (LOSS criterion)')

ax2.set_xticks(x); ax2.set_xticklabels(xlabels, rotation=35, ha='right', fontsize=8.5)
ax2.set_ylim(0, 115)
ax2.set_ylabel('REF-allele binding strength\n[% of PWM max score]', fontsize=10)
ax2.set_title(
    'B.  JASPAR motif binding at rs11867200 REF allele (C) for all 16 TFs\n'
    '(only TFs ≥ 80% can be "disrupted" by ALT alleles; ChIP TFs = 0 = no JASPAR motif at this SNP)',
    fontsize=10, fontweight='bold')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.legend(loc='upper right', fontsize=9, framealpha=0.9)

# Annotate binding TFs with delta_T
for i, (tf, p, dT, dG) in enumerate(zip(ALL_TFS, pct_ref_all, delta_T_all, delta_G_all)):
    if not np.isnan(p) and p >= 50:   # show annotation for any that partially bind
        ax2.text(i, p + 2, f'ΔT={dT:+.2f}', ha='center', va='bottom',
                 fontsize=8, color='black', fontweight='bold')

# "No binding" label for ChIP TF block
ax2.text(6, 4, '← ChIP-seq TFs: no JASPAR binding site at rs11867200 →',
         ha='center', va='bottom', fontsize=8.5, color='#555555',
         fontstyle='italic')

for i, tf in enumerate(ALL_TFS):
    if tf in MOTIF_LOSS:
        ax2.axvspan(i - 0.45, i + 0.45, **shade_kw)

plt.tight_layout()
out_path = os.path.join(IMGDIR, "grn_motif_lps_comparison.png")
fig.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\nFigure saved → {out_path}")
print("[DONE]")
