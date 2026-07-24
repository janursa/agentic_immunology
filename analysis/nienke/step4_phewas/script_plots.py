"""
GWAS Catalog regional plots — consistent plotting standards applied.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 10

OUTDIR = '/vol/projects/BIIM/agentic_immunology/temp/nienke/step4_phewas'
IMGDIR = os.path.join(OUTDIR, 'images')
os.makedirs(IMGDIR, exist_ok=True)

SNP_POS = 34_248_950
SNP_ID  = 'rs11867200'

region = pd.read_csv(os.path.join(OUTDIR, 'gwascatalog_regional_all.csv'))
region['CHR_POS']     = pd.to_numeric(region['CHR_POS'], errors='coerce')
region['PVALUE_MLOG'] = pd.to_numeric(region['PVALUE_MLOG'], errors='coerce')
region['P-VALUE']     = pd.to_numeric(region['P-VALUE'], errors='coerce')
region['abs_dist']    = (region['CHR_POS'] - SNP_POS).abs()

cat_palette = {
    "IBD / Crohn's disease":      '#d62728',
    'Autoimmune / inflammatory':  '#ff7f0e',
    'Cancer':                     '#9467bd',
    'Blood cell traits':          '#1f77b4',
    'Protein/biomarker QTL':      '#2ca02c',
    'Microbiome':                 '#8c564b',
    'Cardiovascular':             '#e377c2',
    'Metabolic':                  '#bcbd22',
    'Anthropometric / ratio':     '#17becf',
    'Neurological / psychiatric': '#aec7e8',
    'GxE interaction':            '#ffbb78',
    'Other':                      '#c7c7c7',
}

disease_cats = [
    "IBD / Crohn's disease", 'Autoimmune / inflammatory', 'Cancer',
    'Cardiovascular', 'Neurological / psychiatric', 'Metabolic', 'GxE interaction',
]

# ── Plot 1 — Regional locus overview ────────────────────────────────────────
# 138 dots across a wide genomic range — HIGH density.
# Annotation strategy: ≤5 top disease hits only, with arrows offset upward
# away from the dense lower region.
fig, ax = plt.subplots(figsize=(9, 4))

for cat, grp in region.groupby('category'):
    color = cat_palette.get(cat, '#888888')
    ax.scatter(grp['CHR_POS'] / 1e6, grp['PVALUE_MLOG'],
               color=color, s=40, alpha=0.85, label=cat, zorder=3, edgecolors='none')

ax.axvline(SNP_POS / 1e6, color='black', linestyle='--', lw=1.5, zorder=5)
ax.axhline(7.3, color='red', linestyle=':', lw=1.0, alpha=0.7)

# Annotate top 5 disease hits only — arrows offset upward to avoid overlap
top5 = (region[region['category'].isin(disease_cats)]
        .drop_duplicates(subset='SNPS')
        .nlargest(5, 'PVALUE_MLOG'))

y_max = region['PVALUE_MLOG'].max()
offsets = [(0, 18), (0, 28), (0, 38), (0, 48), (0, 58)]  # stagger vertically
for i, (_, row) in enumerate(top5.iterrows()):
    label = str(row['DISEASE/TRAIT'])[:30]
    ox, oy = offsets[i % len(offsets)]
    ax.annotate(
        label,
        xy=(row['CHR_POS'] / 1e6, row['PVALUE_MLOG']),
        xytext=(ox, oy), textcoords='offset points',
        fontsize=9, color='black', ha='center',
        arrowprops=dict(arrowstyle='->', color='gray', lw=0.8),
        clip_on=False,
    )

ax.set_xlabel('chr17 position (Mb)', fontsize=10)
ax.set_ylabel('-log10(p)', fontsize=10)
ax.set_title(f'Regional GWAS Catalog — chr17 CCL2 locus (±500 kb of {SNP_ID})', fontsize=10)
ax.tick_params(axis='both', labelsize=10)
ax.tick_params(axis='x', rotation=45)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(x=0.02, y=0.15)

categories_present = sorted(region['category'].unique())
legend_patches = [mpatches.Patch(color=cat_palette.get(c, '#888'), label=c)
                  for c in categories_present]
legend_patches.append(plt.Line2D([0], [0], color='black', linestyle='--', label=SNP_ID))
ax.legend(handles=legend_patches, fontsize=9, frameon=False,
          loc='upper left', bbox_to_anchor=(1, 1))

fig.set_size_inches(9 + 1.5, 4)
plt.tight_layout()
p1 = os.path.join(IMGDIR, 'gwascatalog_regional_locus.png')
plt.savefig(p1, dpi=150, bbox_inches='tight')
plt.close()
print(f'Plot 1: {p1}')

# ── Plot 2 — Disease category bar chart ─────────────────────────────────────
# Bar chart — no dot annotations. p-values labelled inline on bars.
disease_only = region[region['category'].isin(disease_cats + ['Blood cell traits', 'Microbiome'])]
cat_summary = (
    disease_only.groupby('category')
    .agg(n_hits=('SNPS', 'count'), min_p=('P-VALUE', 'min'))
    .sort_values('n_hits', ascending=True)
    .reset_index()
)

n_cats = len(cat_summary)
fig_h = 3 + max(0, (n_cats - 10)) / 5 * 0.5
fig, ax = plt.subplots(figsize=(3 + 1.5, fig_h))

colors = [cat_palette.get(c, '#888') for c in cat_summary['category']]
bars = ax.barh(cat_summary['category'], cat_summary['n_hits'],
               color=colors, edgecolor='white', height=0.6)
for bar, row in zip(bars, cat_summary.itertuples()):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
            f'p={row.min_p:.0e}', va='center', fontsize=9)

ax.set_xlabel('Number of GWAS Catalog associations', fontsize=10)
ax.set_title(f'Disease associations\n±500 kb of {SNP_ID}', fontsize=10)
ax.tick_params(axis='both', labelsize=10)
ax.tick_params(axis='x', rotation=45)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(x=0.2, y=0.05)

plt.tight_layout()
p2 = os.path.join(IMGDIR, 'gwascatalog_disease_categories.png')
plt.savefig(p2, dpi=150, bbox_inches='tight')
plt.close()
print(f'Plot 2: {p2}')

# ── Plot 3 — Distance vs significance ────────────────────────────────────────
# Moderate density near x=0. Annotate ≤5 closest high-significance disease
# hits with arrows, labels offset to upper-right to avoid the dense zone.
fig, ax = plt.subplots(figsize=(6 + 1.5, 4))

for cat in disease_cats + ['Blood cell traits']:
    grp = region[region['category'] == cat]
    if len(grp) == 0:
        continue
    color = cat_palette.get(cat, '#888')
    ax.scatter(grp['abs_dist'] / 1e3, grp['PVALUE_MLOG'],
               color=color, s=50, alpha=0.85, label=cat, edgecolors='none', zorder=3)

# Top 5 closest significant disease hits — offset labels upper-right
top_close = (
    region[region['category'].isin(disease_cats)]
    .drop_duplicates(subset='SNPS')
    .sort_values(['abs_dist', 'P-VALUE'])
    .head(5)
)
x_offsets = [40, 60, 80, 60, 40]
y_offsets = [20, 30, 20, 40, 50]
for i, (_, row) in enumerate(top_close.iterrows()):
    label = f"{row['SNPS']}\n{str(row['DISEASE/TRAIT'])[:22]}"
    ax.annotate(
        label,
        xy=(row['abs_dist'] / 1e3, row['PVALUE_MLOG']),
        xytext=(x_offsets[i], y_offsets[i]), textcoords='offset points',
        fontsize=9, ha='left',
        arrowprops=dict(arrowstyle='->', color='gray', lw=0.8),
        clip_on=False,
    )

ax.axvline(50, color='gray', linestyle='--', lw=1, alpha=0.6)
ax.axhline(7.3, color='red', linestyle=':', lw=1.0, alpha=0.7)

ax.set_xlabel(f'Distance from {SNP_ID} (kb)', fontsize=10)
ax.set_ylabel('-log10(p)', fontsize=10)
ax.set_title(f'Proximity of disease GWAS hits to {SNP_ID}', fontsize=10)
ax.tick_params(axis='both', labelsize=10)
ax.tick_params(axis='x', rotation=45)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.margins(x=0.05, y=0.15)
ax.legend(fontsize=9, frameon=False, loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
p3 = os.path.join(IMGDIR, 'gwascatalog_distance_vs_significance.png')
plt.savefig(p3, dpi=150, bbox_inches='tight')
plt.close()
print(f'Plot 3: {p3}')
