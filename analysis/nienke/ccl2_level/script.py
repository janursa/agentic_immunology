"""
CCL2 expression (RNA) and protein (MCP-1) levels in the SI cohort.
Question: How does CCL2 change from young to old, and from baseline to perturbation (per age group)?
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

OUTDIR = Path('/vol/projects/BIIM/agentic_immunology/temp/nienke/ccl2_level')
IMGDIR = OUTDIR / 'images'
IMGDIR.mkdir(parents=True, exist_ok=True)

# ── paths ─────────────────────────────────────────────────────────────────────
COV_PATH    = '/vol/projects/CIIM/meta_cQTL/data/SI/covariates.tsv'
RNA_BASEDIR = '/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/'
CYT_PATH    = '/vol/projects/CIIM/cohorts/SI/cytokines_processed/cytokines_cleaned_log2.tsv'

# ── load covariates ────────────────────────────────────────────────────────────
cov = pd.read_csv(COV_PATH, sep='\t', index_col=0).T
cov.index.name = 'sample'
cov['age'] = pd.to_numeric(cov['age'])
cov['sex'] = pd.to_numeric(cov['sex'])

def age_group(age):
    if age <= 40:  return 'young'
    if age >= 60:  return 'old'
    return 'middle'

cov['age_group'] = cov['age'].apply(age_group)
n_young  = (cov['age_group'] == 'young').sum()
n_middle = (cov['age_group'] == 'middle').sum()
n_old    = (cov['age_group'] == 'old').sum()
print(f"Cohort: {len(cov)} samples | young (≤40): {n_young} | middle (41-59): {n_middle} | old (≥60): {n_old}")

# ── RNA ───────────────────────────────────────────────────────────────────────
RNA_CONDITIONS = {
    'baseline': 'baseline_cpm.tsv',
    '24h_LPS':  '24h_lps_cpm.tsv',
    '24h_polyIC': '24h_polyic_cpm.tsv',
    '24h_pam3cys': '24h_pam3cys_cpm.tsv',
    '24h_CPG':  '24h_cpg_cpm.tsv',
    '24h_influenza': '24h_influenza_cpm.tsv',
    '7d_influenza': '7d_influenza_cpm.tsv',
}

rna = {}
for label, fname in RNA_CONDITIONS.items():
    fpath = RNA_BASEDIR + fname
    df = pd.read_csv(fpath, sep='\t', index_col=0)
    if 'CCL2' in df.index:
        rna[label] = df.loc['CCL2']  # Series: index = Pr IDs
    else:
        print(f"WARNING: CCL2 not found in {fname}")

print(f"\nRNA conditions loaded: {list(rna.keys())}")
for k, v in rna.items():
    print(f"  {k}: {len(v)} samples")

# merge with covariates
def merge_rna_cov(rna_series):
    df = rna_series.rename('CCL2_RNA').to_frame()
    df.index.name = 'sample'
    return df.join(cov[['age','age_group']], how='inner')

rna_merged = {k: merge_rna_cov(v) for k, v in rna.items()}

# ── PROTEIN (MCP-1 = CCL2) ────────────────────────────────────────────────────
cyt = pd.read_csv(CYT_PATH, sep='\t', index_col=0)
cyt.index.name = 'sample'
mcp1_cols = [c for c in cyt.columns if 'mcp1' in c.lower()]
cyt_mcp1 = cyt[mcp1_cols].copy()
# convert to numeric
cyt_mcp1 = cyt_mcp1.apply(pd.to_numeric, errors='coerce')

# merge with covariates
cyt_full = cyt_mcp1.join(cov[['age','age_group']], how='inner')
print(f"\nCytokine data: {cyt_mcp1.shape[0]} samples; MCP1 columns: {len(mcp1_cols)}")
print("  Columns:", mcp1_cols)

# ── helper: Mann-Whitney U ────────────────────────────────────────────────────
def mannwhitney(a, b):
    a = a.dropna(); b = b.dropna()
    if len(a) < 3 or len(b) < 3:
        return np.nan, np.nan, len(a), len(b)
    stat, pval = stats.mannwhitneyu(a, b, alternative='two-sided')
    return stat, pval, len(a), len(b)

def spearman_age(series, ages):
    combined = pd.DataFrame({'val': series, 'age': ages}).dropna()
    if len(combined) < 5:
        return np.nan, np.nan, len(combined)
    r, p = stats.spearmanr(combined['age'], combined['val'])
    return r, p, len(combined)

# ── ANALYSIS 1: RNA — young vs old by condition ───────────────────────────────
print("\n" + "="*60)
print("RNA: CCL2 expression — young vs old per condition")
print("="*60)

rna_results = []
for cond, df in rna_merged.items():
    young = df[df['age_group']=='young']['CCL2_RNA']
    old   = df[df['age_group']=='old']['CCL2_RNA']
    stat, pval, ny, no = mannwhitney(young, old)
    fc = old.median() - young.median()  # log-space, so this is log2FC
    r, rp, rn = spearman_age(df['CCL2_RNA'], df['age'])
    rna_results.append({
        'condition': cond,
        'n_young': ny, 'median_young': young.median(),
        'n_old':   no, 'median_old':   old.median(),
        'delta_median': fc,
        'MWU_pval': pval,
        'spearman_r': r, 'spearman_p': rp, 'spearman_n': rn
    })
    print(f"  {cond}: young={young.median():.3f}(n={ny}), old={old.median():.3f}(n={no}), Δmedian={fc:+.3f}, p={pval:.3e} | ρ(age)={r:.3f}, p={rp:.3e}")

rna_res_df = pd.DataFrame(rna_results)
rna_res_df.to_csv(OUTDIR/'rna_young_vs_old.tsv', sep='\t', index=False)

# ── ANALYSIS 2: RNA — baseline vs stimulation per age group ──────────────────
print("\n" + "="*60)
print("RNA: CCL2 — baseline vs stimulation per age group")
print("="*60)

stim_rna_results = []
df_base = rna_merged['baseline']
for cond, df_stim in rna_merged.items():
    if cond == 'baseline':
        continue
    for grp in ['young','old']:
        base_vals = df_base[df_base['age_group']==grp]['CCL2_RNA']
        stim_vals = df_stim[df_stim['age_group']==grp]['CCL2_RNA']
        stat, pval, nb, ns = mannwhitney(base_vals, stim_vals)
        delta = stim_vals.median() - base_vals.median()
        stim_rna_results.append({
            'stimulation': cond, 'age_group': grp,
            'n_baseline': nb, 'median_baseline': base_vals.median(),
            'n_stim': ns, 'median_stim': stim_vals.median(),
            'delta_median': delta, 'MWU_pval': pval
        })
        print(f"  {grp} | {cond}: base={base_vals.median():.3f}(n={nb}), stim={stim_vals.median():.3f}(n={ns}), Δ={delta:+.3f}, p={pval:.3e}")

stim_rna_df = pd.DataFrame(stim_rna_results)
stim_rna_df.to_csv(OUTDIR/'rna_baseline_vs_stim.tsv', sep='\t', index=False)

# ── ANALYSIS 3: Protein — young vs old per stimulation ───────────────────────
print("\n" + "="*60)
print("Protein (MCP-1): young vs old per stimulation")
print("="*60)

prot_results = []
for col in mcp1_cols:
    young = cyt_full[cyt_full['age_group']=='young'][col]
    old   = cyt_full[cyt_full['age_group']=='old'][col]
    stat, pval, ny, no = mannwhitney(young, old)
    delta = old.median() - young.median()
    r, rp, rn = spearman_age(cyt_full[col], cyt_full['age'])
    prot_results.append({
        'stimulation': col,
        'n_young': ny, 'median_young': young.median(),
        'n_old':   no, 'median_old':   old.median(),
        'delta_median': delta, 'MWU_pval': pval,
        'spearman_r': r, 'spearman_p': rp, 'spearman_n': rn
    })
    print(f"  {col}: young={young.median():.3f}(n={ny}), old={old.median():.3f}(n={no}), Δ={delta:+.3f}, p={pval:.3e} | ρ={r:.3f}, p={rp:.3e}")

prot_res_df = pd.DataFrame(prot_results)
prot_res_df.to_csv(OUTDIR/'protein_young_vs_old.tsv', sep='\t', index=False)

# ── ANALYSIS 4: Protein — RPMI (baseline) vs each stimulation per age group ──
print("\n" + "="*60)
print("Protein: MCP-1 RPMI vs stimulation per age group (paired Wilcoxon)")
print("="*60)

# identify baseline columns
rpmi_24h = 'pbmc_24h_mcp1_rpmi'
rpmi_7d  = 'pbmc_7d_mcp1_rpmi'

stim_prot_results = []
for col in mcp1_cols:
    if 'rpmi' in col:
        continue
    # choose appropriate baseline
    baseline_col = rpmi_7d if col.startswith('pbmc_7d') else rpmi_24h
    for grp in ['young','old']:
        sub = cyt_full[cyt_full['age_group']==grp][[col, baseline_col]].dropna()
        if len(sub) < 5:
            continue
        # paired Wilcoxon
        stat, pval = stats.wilcoxon(sub[col], sub[baseline_col], alternative='two-sided')
        delta = (sub[col] - sub[baseline_col]).median()
        stim_prot_results.append({
            'stimulation': col, 'age_group': grp,
            'baseline': baseline_col, 'n': len(sub),
            'median_baseline': sub[baseline_col].median(),
            'median_stim': sub[col].median(),
            'delta_median': delta, 'Wilcoxon_pval': pval
        })
        print(f"  {grp} | {col}: base={sub[baseline_col].median():.3f}, stim={sub[col].median():.3f}, Δ={delta:+.3f}, p={pval:.3e} (n={len(sub)})")

stim_prot_df = pd.DataFrame(stim_prot_results)
stim_prot_df.to_csv(OUTDIR/'protein_baseline_vs_stim.tsv', sep='\t', index=False)


# ═══════════════════════════════════════════════════════════════════════════════
# PLOTS  (plotting-skill standards applied)
# ═══════════════════════════════════════════════════════════════════════════════

matplotlib.rcParams.update({'font.family': 'Arial', 'font.size': 10})
colors = {'young': '#4393c3', 'middle': '#92c5de', 'old': '#d6604d'}
groups = ['young', 'middle', 'old']

def add_stars(ax, x1, x2, y, pval):
    if pd.isna(pval):
        return
    if pval < 0.001:   sig = '***'
    elif pval < 0.01:  sig = '**'
    elif pval < 0.05:  sig = '*'
    else:              sig = 'ns'
    ax.plot([x1, x2], [y, y], color='black', lw=0.8)
    ax.text((x1+x2)/2, y, sig, ha='center', va='bottom', fontsize=9)

# ── Plot 1: RNA baseline — all 3 age groups boxplot ───────────────────────────
df_base = rna_merged['baseline'].copy()
vals = [df_base[df_base['age_group']==g]['CCL2_RNA'].dropna().values for g in groups]

# 3 groups → barplot spec → figsize=(3,3)
fig, ax = plt.subplots(figsize=(3, 3))
bp = ax.boxplot(vals, patch_artist=True, widths=0.5,
                medianprops=dict(color='black', lw=1.5),
                flierprops=dict(marker='o', markersize=3, alpha=0.5))
for patch, grp in zip(bp['boxes'], groups):
    patch.set_facecolor(colors[grp])
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['Young\n(≤40)', 'Middle\n(41-59)', 'Old\n(≥60)'], rotation=45, ha='right', fontsize=10)
ax.set_ylabel('CCL2 expression (log2 CPM)', fontsize=10)
ax.set_title('CCL2 RNA (baseline)', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(y=0.15)
row = rna_res_df[rna_res_df['condition'] == 'baseline'].iloc[0]
ymax = df_base['CCL2_RNA'].dropna().max() * 1.08
add_stars(ax, 1, 3, ymax, row['MWU_pval'])
plt.tight_layout()
fig.savefig(IMGDIR / 'rna_baseline_by_agegroup.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\nSaved: {IMGDIR / 'rna_baseline_by_agegroup.png'}")

# ── Plot 2: RNA — CCL2 vs age (scatter + regression) ─────────────────────────
# scatter → barplot-like spec; legend outside → +1.5 width → figsize=(4.5, 3)
fig, ax = plt.subplots(figsize=(4.5, 3))
x_all = df_base['age'].values
y_all = df_base['CCL2_RNA'].values
mask = ~(np.isnan(x_all) | np.isnan(y_all))
x_fit, y_fit = x_all[mask], y_all[mask]
gc = df_base['age_group'].values[mask]
ax.scatter(x_fit, y_fit, c=[colors[g] for g in gc], s=15, alpha=0.7, edgecolors='none')
m, b, r, p, _ = stats.linregress(x_fit, y_fit)
xl = np.linspace(x_fit.min(), x_fit.max(), 100)
ax.plot(xl, m * xl + b, color='black', lw=1.2)
ax.set_xlabel('Age (years)', fontsize=10)
ax.set_ylabel('CCL2 expression (log2 CPM)', fontsize=10)
ax.set_title(f'CCL2 RNA vs age (r={r:.2f}, p={p:.2e})', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(0.05)
legend_patches = [mpatches.Patch(color=colors[g], label=g) for g in groups]
ax.legend(handles=legend_patches, frameon=False, fontsize=9,
          loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()
fig.savefig(IMGDIR / 'rna_vs_age_scatter.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {IMGDIR / 'rna_vs_age_scatter.png'}")

# ── Plot 3: RNA — Δ (stim − baseline) per condition per age group ─────────────
# 6 conditions (≤10) → barplot spec → figsize=(3,3) + 1.5 legend = (4.5, 3)
stim_rna_plot = stim_rna_df.copy()
# keep timepoint prefix to avoid collision (e.g. 24h_influenza vs 7d_influenza)
stim_rna_plot['label'] = stim_rna_plot['stimulation']
stims_r = stim_rna_plot['label'].unique()
x = np.arange(len(stims_r))
w = 0.3

fig, ax = plt.subplots(figsize=(4.5, 3))
for i, grp in enumerate(['young', 'old']):
    sub = stim_rna_plot[stim_rna_plot['age_group'] == grp].set_index('label')
    deltas = [sub.loc[s, 'delta_median'] if s in sub.index else np.nan for s in stims_r]
    ax.bar(x + (i - 0.5) * w, deltas, width=w, color=colors[grp], label=grp, alpha=0.85)
ax.axhline(0, color='black', lw=0.8)
ax.set_xticks(x)
ax.set_xticklabels(stims_r, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Δ CCL2 RNA\n(stim − baseline, log2 CPM)', fontsize=10)
ax.set_title('CCL2 RNA: stimulation response per age group', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(x=0.05)
ax.legend(frameon=False, fontsize=9, loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()
fig.savefig(IMGDIR / 'rna_stim_response_by_agegroup.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {IMGDIR / 'rna_stim_response_by_agegroup.png'}")

# ── Plot 4: Protein — MCP1 RPMI (baseline) by age group ──────────────────────
# 3 groups → figsize=(3, 3)
fig, ax = plt.subplots(figsize=(3, 3))
rpmi_grp_vals = [cyt_full[cyt_full['age_group'] == g][rpmi_24h].dropna().values for g in groups]
bp = ax.boxplot(rpmi_grp_vals, patch_artist=True, widths=0.5,
                medianprops=dict(color='black', lw=1.5),
                flierprops=dict(marker='o', markersize=3, alpha=0.5))
for patch, grp in zip(bp['boxes'], groups):
    patch.set_facecolor(colors[grp])
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['Young\n(≤40)', 'Middle\n(41-59)', 'Old\n(≥60)'], rotation=45, ha='right', fontsize=10)
ax.set_ylabel('MCP-1 / CCL2 (log2, RPMI)', fontsize=10)
ax.set_title('CCL2 protein (RPMI, 24h)', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(y=0.15)
row_p = prot_res_df[prot_res_df['stimulation'] == rpmi_24h].iloc[0]
ymax = cyt_full[rpmi_24h].dropna().max() * 1.08
add_stars(ax, 1, 3, ymax, row_p['MWU_pval'])
plt.tight_layout()
fig.savefig(IMGDIR / 'protein_rpmi_by_agegroup.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {IMGDIR / 'protein_rpmi_by_agegroup.png'}")

# ── Plot 5: Protein — MCP1 vs age (RPMI, scatter) ────────────────────────────
# scatter + legend outside → figsize=(4.5, 3)
fig, ax = plt.subplots(figsize=(4.5, 3))
x_c = cyt_full['age'].values
y_c = cyt_full[rpmi_24h].values
mask_c = ~(np.isnan(x_c) | np.isnan(y_c))
x_cf, y_cf = x_c[mask_c], y_c[mask_c]
gc_c = cyt_full['age_group'].values[mask_c]
ax.scatter(x_cf, y_cf, c=[colors[g] for g in gc_c], s=10, alpha=0.6, edgecolors='none')
m, b, r, p, _ = stats.linregress(x_cf, y_cf)
xl = np.linspace(x_cf.min(), x_cf.max(), 100)
ax.plot(xl, m * xl + b, color='black', lw=1.2)
ax.set_xlabel('Age (years)', fontsize=10)
ax.set_ylabel('MCP-1 / CCL2 (log2, RPMI)', fontsize=10)
ax.set_title(f'CCL2 protein vs age (r={r:.2f}, p={p:.2e})', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(0.05)
legend_patches = [mpatches.Patch(color=colors[g], label=g) for g in groups]
ax.legend(handles=legend_patches, frameon=False, fontsize=9,
          loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()
fig.savefig(IMGDIR / 'protein_vs_age_scatter.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {IMGDIR / 'protein_vs_age_scatter.png'}")

# ── Plot 6: Protein — Δ (stim − RPMI) per stimulation per age group ──────────
# ~14 stims (>10) → +0.5 per 5 over 10 → 1 extra → width=3.5 + 1.5 legend = 5.0
stim_prot_plot = stim_prot_df.copy()
stim_prot_plot['label'] = (stim_prot_plot['stimulation']
                            .str.replace('pbmc_24h_mcp1_', '24h_')
                            .str.replace('pbmc_7d_mcp1_', '7d_'))
stims_p = stim_prot_plot['label'].unique()
n_stims_p = len(stims_p)
# figsize width: 3 + 0.5*max(0, ceil((n_stims_p-10)/5)) + 1.5 for legend
extra_w = 0.5 * max(0, int(np.ceil((n_stims_p - 10) / 5)))
fig_w = 3 + extra_w + 1.5
x = np.arange(n_stims_p)
w = 0.3

fig, ax = plt.subplots(figsize=(fig_w, 3))
for i, grp in enumerate(['young', 'old']):
    sub = stim_prot_plot[stim_prot_plot['age_group'] == grp].set_index('label')
    deltas  = [sub.loc[s, 'delta_median']    if s in sub.index else np.nan for s in stims_p]
    pv_list = [sub.loc[s, 'Wilcoxon_pval']   if s in sub.index else np.nan for s in stims_p]
    ax.bar(x + (i - 0.5) * w, deltas, width=w, color=colors[grp], label=grp, alpha=0.85)
    for xi, (delta, pv) in enumerate(zip(deltas, pv_list)):
        if not np.isnan(pv) and pv < 0.05 and not np.isnan(delta):
            ax.text(xi + (i - 0.5) * w, delta + (0.05 if delta >= 0 else -0.12),
                    '*', ha='center', va='bottom', fontsize=9, clip_on=False)
ax.axhline(0, color='black', lw=0.8)
ax.set_xticks(x)
ax.set_xticklabels(stims_p, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Δ CCL2 protein\n(stim − RPMI, log2)', fontsize=10)
ax.set_title('CCL2 protein: stimulation response per age group', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(x=0.03)
ax.legend(frameon=False, fontsize=9, loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()
fig.savefig(IMGDIR / 'protein_stim_response_by_agegroup.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {IMGDIR / 'protein_stim_response_by_agegroup.png'}")

# ── Plot 7: Protein — all stims, young vs old (horizontal dual-bar) ───────────
# Horizontal barplot with 16 items → height: 3 + 0.5*ceil((16-10)/5)=4
# 2-panel multi-panel: shared y-axis → y-labels on left panel only
# width: 3*2 panels - 1 (shared axis) = 5, no external legend → 5
prot_heatmap = prot_res_df.copy()
prot_heatmap['label'] = (prot_heatmap['stimulation']
                          .str.replace('pbmc_24h_mcp1_', '24h_')
                          .str.replace('pbmc_7d_mcp1_', '7d_'))
prot_heatmap = prot_heatmap.sort_values('delta_median')
n_prot = len(prot_heatmap)
fig_h = 3 + 0.5 * max(0, int(np.ceil((n_prot - 10) / 5)))
fig, axes = plt.subplots(1, 2, figsize=(5, fig_h))
ax_delta, ax_pval = axes

labels  = prot_heatmap['label'].tolist()
deltas  = prot_heatmap['delta_median'].tolist()
pvals   = prot_heatmap['MWU_pval'].tolist()
y_pos   = np.arange(n_prot)

# left panel: delta
bar_colors = ['#d6604d' if d > 0 else '#4393c3' for d in deltas]
ax_delta.barh(y_pos, deltas, color=bar_colors, alpha=0.85, height=0.7)
ax_delta.axvline(0, color='black', lw=0.8)
ax_delta.set_yticks(y_pos)
ax_delta.set_yticklabels(labels, fontsize=10)
ax_delta.set_xlabel('Δ median (old − young, log2)', fontsize=10)
ax_delta.set_title('Effect size', fontsize=10)
ax_delta.spines['top'].set_visible(False)
ax_delta.spines['right'].set_visible(False)
ax_delta.margins(y=0.03)

# right panel: −log10 p (shared y → no y-labels)
neg_log_p  = [-np.log10(p) if (not pd.isna(p) and p > 0) else 0 for p in pvals]
sig_thresh = -np.log10(0.05)
pbar_colors = ['#d6604d' if nlp >= sig_thresh else '#999999' for nlp in neg_log_p]
ax_pval.barh(y_pos, neg_log_p, color=pbar_colors, alpha=0.85, height=0.7)
ax_pval.axvline(sig_thresh, color='black', lw=0.8, linestyle='--')
ax_pval.set_yticks(y_pos)
ax_pval.set_yticklabels([])          # shared y-axis → labels on left only
ax_pval.set_xlabel('−log10(p), young vs old', fontsize=10)
ax_pval.set_title('Significance', fontsize=10)
ax_pval.spines['top'].set_visible(False)
ax_pval.spines['right'].set_visible(False)
ax_pval.margins(y=0.03)

plt.suptitle('CCL2 protein: young vs old per stimulation', fontsize=10)
plt.tight_layout()
fig.savefig(IMGDIR / 'protein_young_vs_old_allstim.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {IMGDIR / 'protein_young_vs_old_allstim.png'}")

# ── Write results.txt ─────────────────────────────────────────────────────────
lines = []
lines.append("# CCL2 / MCP-1 — SI cohort (young vs old; baseline vs perturbation)")
lines.append(f"# Age groups: young ≤40 (n={n_young}), middle 41-59 (n={n_middle}), old ≥60 (n={n_old})")
lines.append("")
lines.append("## RNA: CCL2 expression — young vs old per condition")
lines.append(f"{'Condition':<25} {'n_young':>7} {'median_young':>13} {'n_old':>6} {'median_old':>11} {'delta':>7} {'MWU_p':>12} {'spearman_r':>12} {'spearman_p':>12}")
for _, row in rna_res_df.iterrows():
    lines.append(f"{row['condition']:<25} {int(row['n_young']):>7} {row['median_young']:>13.3f} {int(row['n_old']):>6} {row['median_old']:>11.3f} {row['delta_median']:>+7.3f} {row['MWU_pval']:>12.3e} {row['spearman_r']:>12.3f} {row['spearman_p']:>12.3e}")

lines.append("")
lines.append("## RNA: CCL2 — baseline vs stimulation per age group")
lines.append(f"{'Stim':<25} {'group':<8} {'n_base':>7} {'med_base':>9} {'n_stim':>7} {'med_stim':>9} {'delta':>7} {'MWU_p':>12}")
for _, row in stim_rna_df.iterrows():
    lines.append(f"{row['stimulation']:<25} {row['age_group']:<8} {int(row['n_baseline']):>7} {row['median_baseline']:>9.3f} {int(row['n_stim']):>7} {row['median_stim']:>9.3f} {row['delta_median']:>+7.3f} {row['MWU_pval']:>12.3e}")

lines.append("")
lines.append("## Protein (MCP-1): young vs old per stimulation")
lines.append(f"{'Stimulation':<35} {'n_young':>7} {'med_young':>10} {'n_old':>6} {'med_old':>9} {'delta':>7} {'MWU_p':>12} {'spearman_r':>12} {'spearman_p':>12}")
for _, row in prot_res_df.iterrows():
    lines.append(f"{row['stimulation']:<35} {int(row['n_young']):>7} {row['median_young']:>10.3f} {int(row['n_old']):>6} {row['median_old']:>9.3f} {row['delta_median']:>+7.3f} {row['MWU_pval']:>12.3e} {row['spearman_r']:>12.3f} {row['spearman_p']:>12.3e}")

lines.append("")
lines.append("## Protein (MCP-1): RPMI vs stimulation per age group (paired Wilcoxon)")
lines.append(f"{'Stimulation':<35} {'group':<8} {'n':>5} {'med_base':>9} {'med_stim':>9} {'delta':>7} {'Wilcoxon_p':>12}")
for _, row in stim_prot_df.iterrows():
    lines.append(f"{row['stimulation']:<35} {row['age_group']:<8} {int(row['n']):>5} {row['median_baseline']:>9.3f} {row['median_stim']:>9.3f} {row['delta_median']:>+7.3f} {row['Wilcoxon_pval']:>12.3e}")

with open(OUTDIR/'results.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f"\nSaved: {OUTDIR/'results.txt'}")
print("\nDone.")
