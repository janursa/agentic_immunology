"""
TF activity distribution: REF vs Carrier allele for 13 candidate TFs.
Mann-Whitney U + BH FDR correction (26 tests: 13 TFs × 2 conditions).
"""
import sys, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Patch
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

# ── Paths ──────────────────────────────────────────────────────────────────
BASE     = '/vol/projects/BIIM/agentic_immunology/temp/nienke/tfa_analysis'
TFA_PATH = os.path.join(BASE, 'results', 'tf_activity.tsv')
META_PATH= os.path.join(BASE, 'results', 'sample_metadata.tsv')
OUT_IMG  = os.path.join(BASE, 'images', 'fig6_allele_dist_candidate_tfs.png')
OUT_CSV  = os.path.join(BASE, 'results', 'allele_tfa_stats.csv')

# ── Font ───────────────────────────────────────────────────────────────────
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

# ── Data ───────────────────────────────────────────────────────────────────
tfa  = pd.read_csv(TFA_PATH,  sep='\t', index_col=0)
meta = pd.read_csv(META_PATH, sep='\t', index_col=0)

TFS_13 = ["CEBPB","FOS","FOSL2","GATA2","GATA3","JUND",
          "MAX","MEF2A","NFIC","PBX3","SPI1","SPIB","ETV6"]
TFS_13 = [t for t in TFS_13 if t in tfa.columns]
print(f"TFs available: {TFS_13} ({len(TFS_13)}/13)")

# align index
shared = tfa.index.intersection(meta.index)
tfa  = tfa.loc[shared, TFS_13]
meta = meta.loc[shared]

# ── Statistics ─────────────────────────────────────────────────────────────
records = []
for tf in TFS_13:
    for cond in ['LPS', 'NS']:
        ref_idx     = meta[(meta['condition']==cond) & (meta['allele']=='REF')].index
        carrier_idx = meta[(meta['condition']==cond) & (meta['allele']=='Carrier')].index
        ref_vals     = tfa.loc[ref_idx, tf].dropna().values
        carrier_vals = tfa.loc[carrier_idx, tf].dropna().values
        stat, pval   = mannwhitneyu(ref_vals, carrier_vals, alternative='two-sided')
        records.append({
            'TF': tf, 'condition': cond,
            'U': stat, 'p': pval,
            'n_REF': len(ref_vals), 'n_Carrier': len(carrier_vals),
            'median_REF': np.median(ref_vals), 'median_Carrier': np.median(carrier_vals),
        })

stats_df = pd.DataFrame(records)
_, fdr, _, _ = multipletests(stats_df['p'], method='fdr_bh')
stats_df['FDR'] = fdr
stats_df['sig']  = stats_df['FDR'].apply(
    lambda q: '***' if q < 0.001 else ('**' if q < 0.01 else ('*' if q < 0.05 else 'ns')))
stats_df.to_csv(OUT_CSV, index=False)
print("\nStatistics:")
print(stats_df[['TF','condition','n_REF','n_Carrier','p','FDR','sig']].to_string(index=False))

# ── Figure ─────────────────────────────────────────────────────────────────
GROUPS = ['REF_NS', 'Carrier_NS', 'REF_LPS', 'Carrier_LPS']
COLORS = {
    'REF_NS':      '#A8C8E8',
    'Carrier_NS':  '#2171B5',
    'REF_LPS':     '#FDAE61',
    'Carrier_LPS': '#D7191C',
}
X_POS  = [0, 1, 2.6, 3.6]          # gap between NS and LPS groups

ncols, nrows = 7, 2
fw = ncols * 3 - 1 + 1.5            # 1.5 for legend outside last panel
fh = nrows * 3 - 1
fig, axes = plt.subplots(nrows, ncols, figsize=(fw, fh))
axes_flat = axes.flatten()

rng = np.random.default_rng(42)

def draw_bracket(ax, x1, x2, y_base, label, h_frac):
    h = h_frac
    ax.plot([x1, x1, x2, x2], [y_base, y_base+h, y_base+h, y_base], lw=0.8, color='k')
    ax.text((x1+x2)/2, y_base+h*1.05, label,
            ha='center', va='bottom', fontsize=9, clip_on=False)

for i, tf in enumerate(TFS_13):
    ax = axes_flat[i]

    # collect data per group
    grp_data = {}
    for g in GROUPS:
        parts = g.split('_')
        allele_label = parts[0]
        cond_label   = parts[1]
        idx = meta[(meta['condition']==cond_label) & (meta['allele']==allele_label)].index
        grp_data[g] = tfa.loc[idx, tf].dropna().values

    # violin + strip
    for xi, g in zip(X_POS, GROUPS):
        d = grp_data[g]
        if len(d) < 3:
            continue
        vp = ax.violinplot(d, positions=[xi], widths=0.65,
                           showmedians=True, showextrema=False)
        for pc in vp['bodies']:
            pc.set_facecolor(COLORS[g])
            pc.set_alpha(0.65)
            pc.set_edgecolor('none')
        vp['cmedians'].set_color('black')
        vp['cmedians'].set_linewidth(1.5)
        jitter = rng.uniform(-0.14, 0.14, len(d))
        ax.scatter(xi + jitter, d, s=3, alpha=0.35,
                   color=COLORS[g], linewidths=0)

    # y range for brackets
    all_vals = np.concatenate(list(grp_data.values()))
    ymin_data = np.nanpercentile(all_vals, 1)
    ymax_data = np.nanpercentile(all_vals, 99)
    span = ymax_data - ymin_data
    h = span * 0.08

    # NS bracket (x=0 vs x=1)
    row_ns = stats_df[(stats_df['TF']==tf) & (stats_df['condition']=='NS')]
    if len(row_ns):
        draw_bracket(ax, X_POS[0], X_POS[1], ymax_data + span*0.03,
                     row_ns.iloc[0]['sig'], h)

    # LPS bracket (x=2.6 vs x=3.6)
    row_lps = stats_df[(stats_df['TF']==tf) & (stats_df['condition']=='LPS')]
    if len(row_lps):
        draw_bracket(ax, X_POS[2], X_POS[3], ymax_data + span*0.03,
                     row_lps.iloc[0]['sig'], h)

    # visual separator between NS and LPS
    ax.axvline(x=1.8, color='#CCCCCC', linestyle='--', linewidth=0.7, alpha=0.8)

    ax.set_title(tf, fontsize=10)
    ax.set_xticks(X_POS)
    ax.set_xticklabels(GROUPS, rotation=45, ha='right', fontsize=9)
    ax.set_xlim(-0.6, 4.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if i % ncols == 0:
        ax.set_ylabel('ULM activity score', fontsize=10)
    else:
        ax.set_ylabel('')

# hide unused panels
for j in range(len(TFS_13), len(axes_flat)):
    axes_flat[j].set_visible(False)

# shared legend on last visible panel
legend_handles = [Patch(facecolor=COLORS[g], label=g, alpha=0.75) for g in GROUPS]
axes_flat[len(TFS_13)-1].legend(
    handles=legend_handles, frameon=False, fontsize=9,
    loc='upper left', bbox_to_anchor=(1.05, 1))

plt.tight_layout()
plt.savefig(OUT_IMG, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nSaved figure: {OUT_IMG}")
print(f"Saved stats:  {OUT_CSV}")
