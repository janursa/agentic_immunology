"""
DisGeNET and OpenTargets heatmaps for CCL2 + CCL7.
Fig 1: DisGeNET — all disorders linked to both CCL2 AND CCL7, colored by disease category.
Fig 2: OpenTargets — diseases shared by CCL2 AND CCL7 (top 100 each), sorted by avg score.
"""

import sys, os, warnings
import ast
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches
from matplotlib.colors import ListedColormap, BoundaryNorm

warnings.filterwarnings('ignore')

sys.path.insert(0, '/vol/projects/BIIM/agentic_immunology/tools/ciim/code')

OUTDIR = '/vol/projects/BIIM/agentic_immunology/temp/nienke/ccl_disease'
IMGDIR = os.path.join(OUTDIR, 'images')
CCL_GENES = ['CCL2', 'CCL7']

plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 10,
    'axes.titlesize': 10,
    'axes.labelsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
})

def clean_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

CATEGORY_ORDER = ['IBD', 'Arthritis/SpA', 'SLE', 'CVD', 'Infection',
                  'Cancer', 'Metabolic', 'Neuro/MS', 'Allergy/Asthma',
                  'Renal', 'Pulmonary', 'Skin', 'Other']

# tab20 palette — designed for perceptual distinctness; Cancer is now brown (not gray)
CAT_COLORS = {
    'IBD':            '#d62728',  # red
    'SLE':            '#1f77b4',  # blue
    'Arthritis/SpA':  '#9467bd',  # purple
    'CVD':            '#ff7f0e',  # orange
    'Infection':      '#2ca02c',  # green
    'Cancer':         '#8c564b',  # brown  ← was gray, now clearly distinct from Other
    'Metabolic':      '#bcbd22',  # olive
    'Neuro/MS':       '#17becf',  # cyan
    'Allergy/Asthma': '#aec7e8',  # light blue
    'Renal':          '#98df8a',  # light green
    'Pulmonary':      '#ffbb78',  # light orange
    'Skin':           '#e377c2',  # pink
    'Other':          '#c7c7c7',  # light gray
}

def categorise(name):
    n = name.lower()
    if any(x in n for x in ['crohn','colitis','ibd','bowel','enteritis','proctitis']): return 'IBD'
    if any(x in n for x in ['lupus','sle']): return 'SLE'
    if any(x in n for x in ['arthritis','rheumatoid','psoriatic','ankylosing','spondyl']): return 'Arthritis/SpA'
    if any(x in n for x in ['atherosclerosis','coronary','myocardial','cardiac','cardiom','heart failure',
                              'cerebrovascular','infarction','middle cerebral','stroke','embol','thrombotic']): return 'CVD'
    if any(x in n for x in ['sepsis','infection','bacterial','viral','hiv','influenza','pneumonia','parvovir']): return 'Infection'
    if any(x in n for x in ['cancer','carcinoma','tumor','tumour','leukemia','lymphoma','melanoma','sarcoma',
                              'adenocarcinoma','glioma','myeloma','neoplasm','mesothelioma','neuroblastoma']): return 'Cancer'
    if any(x in n for x in ['diabetes','obesity','metabolic','insulin','sulfatase']): return 'Metabolic'
    if any(x in n for x in ['multiple sclerosis','alzheimer','parkinson','neurodegenerat','encephalitis','autism']): return 'Neuro/MS'
    if any(x in n for x in ['asthma','allerg','atopic','eosinophil','hypersensitiv']): return 'Allergy/Asthma'
    if any(x in n for x in ['nephritis','glomerulo','bright disease','renal failure','kidney']): return 'Renal'
    if any(x in n for x in ['pulmonary fibrosis','pneumonitis','bronchiolitis','silicosis','lung inflamm','hamman']): return 'Pulmonary'
    if any(x in n for x in ['psoriasis','scleroderma','eczema','ichthyosis','dermatitis','dermat']): return 'Skin'
    return 'Other'

# ─────────────────────────────────────────────────────────────────────────────
# DisGeNET — disorders with both CCL2 AND CCL7
# ─────────────────────────────────────────────────────────────────────────────
disgenet = pd.read_parquet('/vol/projects/BIIM/agentic_immunology/datalake/biomni/DisGeNET.parquet')
print(f"DisGeNET shape: {disgenet.shape}")

disgenet['ccl_genes_found'] = disgenet['Genes'].apply(
    lambda x: {g for g in CCL_GENES if g in str(x)}
)
disgenet['n_ccl_genes'] = disgenet['ccl_genes_found'].apply(len)
both = disgenet[disgenet['n_ccl_genes'] == 2].copy()
both['category'] = both['Disorder'].apply(categorise)

print(f"Disorders with both CCL2 AND CCL7: {len(both)}")
print(both.groupby('category').size().sort_values(ascending=False).to_string())

# Sort: by category order, then alphabetically within category
cat_to_idx = {c: i for i, c in enumerate(CATEGORY_ORDER)}
both['cat_idx'] = both['category'].map(cat_to_idx).fillna(len(CATEGORY_ORDER) - 1).astype(int)
both_sorted = both.sort_values(['cat_idx', 'Disorder']).reset_index(drop=True)

# ── Figure 1: DisGeNET categorical heatmap ────────────────────────────────────
n_dis = len(both_sorted)
# Both columns carry same category index (CCL2 and CCL7 both always present)
data_arr = np.column_stack([both_sorted['cat_idx'].values, both_sorted['cat_idx'].values])

colors_list = [CAT_COLORS[c] for c in CATEGORY_ORDER]
cmap_cat = ListedColormap(colors_list)
norm_cat = BoundaryNorm(list(range(len(CATEGORY_ORDER) + 1)), cmap_cat.N)

# height: 3 + 0.3 per 2 items above 5 (shorter); width 7 (wider + legend room)
fig_h1 = 3 + max(0, 0.2 * ((n_dis - 5) // 2))
fig, ax = plt.subplots(figsize=(6, fig_h1))

ax.imshow(data_arr, aspect='auto', cmap=cmap_cat, norm=norm_cat, interpolation='nearest')

ax.set_xticks([0, 1])
ax.set_xticklabels(['CCL2', 'CCL7'], fontsize=10, rotation=45, ha='right')
ax.set_yticks(range(n_dis))
ax.set_yticklabels(both_sorted['Disorder'], fontsize=9)
ax.set_title('DisGeNET: disorders linked to both CCL2 and CCL7\n(sorted by disease category)',
             fontsize=10, fontweight='bold')

present_cats = both_sorted['category'].unique()
legend_handles = [
    matplotlib.patches.Patch(facecolor=CAT_COLORS[c], edgecolor='black', linewidth=0.5, label=c)
    for c in CATEGORY_ORDER if c in present_cats
]
ax.legend(handles=legend_handles, frameon=False, fontsize=9,
          loc='upper left', bbox_to_anchor=(1, 1))

ax.margins(y=0.02)
clean_ax(ax)
plt.tight_layout()

out1 = os.path.join(IMGDIR, 'fig1_disgenet_heatmap.png')
plt.savefig(out1, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nFigure saved: {out1}")

# ─────────────────────────────────────────────────────────────────────────────
# Figure 2: OpenTargets heatmap — diseases shared by CCL2 AND CCL7 (top 100)
# ─────────────────────────────────────────────────────────────────────────────
from genetics import query_opentarget_platform

CCL_IDS = {
    'CCL2': 'ENSG00000108691',
    'CCL7': 'ENSG00000108688',
}

q_large = """
query targetDiseases($ensId: String!) {
  target(ensemblId: $ensId) {
    associatedDiseases(page: {index: 0, size: 100}) {
      rows {
        disease { id name }
        score
      }
    }
  }
}
"""

ot_large = {}
for gene, ensid in CCL_IDS.items():
    rows = []
    try:
        res = query_opentarget_platform(q_large, variables={'ensId': ensid})
        for r in res['data']['target']['associatedDiseases']['rows']:
            rows.append({'disease': r['disease']['name'], 'score': r['score']})
        print(f"{gene}: {len(rows)} diseases retrieved")
    except Exception as e:
        print(f"ERROR {gene}: {e}")
    ot_large[gene] = (pd.DataFrame(rows).set_index('disease')['score']
                      if rows else pd.Series(dtype=float))

shared = set(ot_large['CCL2'].index) & set(ot_large['CCL7'].index)
print(f"\nShared diseases (CCL2 ∩ CCL7) in OT top-100: {len(shared)}")

if shared:
    df_shared = pd.DataFrame({
        'CCL2': ot_large['CCL2'].reindex(list(shared)),
        'CCL7': ot_large['CCL7'].reindex(list(shared)),
    }).dropna()
    df_shared['_avg'] = df_shared.mean(axis=1)
    df_shared = df_shared.sort_values('_avg', ascending=True).drop(columns='_avg')

    n_ot = len(df_shared)
    fig_h2 = 3 + max(0, 0.2 * ((n_ot - 5) // 2))
    fig, ax = plt.subplots(figsize=(4, fig_h2))

    im = ax.imshow(df_shared.values, aspect='auto', cmap='YlOrRd', vmin=0, vmax=0.5)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(['CCL2', 'CCL7'], fontsize=10, rotation=45, ha='right')
    ax.set_yticks(range(n_ot))
    ax.set_yticklabels(df_shared.index, fontsize=9)
    ax.set_title('OpenTargets: diseases associated with both CCL2 and CCL7\n(sorted by average score)',
                 fontsize=10, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax, shrink=0.5, pad=0.02)
    cbar.set_label('OT association score', fontsize=10)
    cbar.ax.tick_params(labelsize=10)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.margins(y=0.02)

    plt.tight_layout()
    out2 = os.path.join(IMGDIR, 'fig2_ot_shared_heatmap.png')
    plt.savefig(out2, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nFigure saved: {out2}")
else:
    print("No shared diseases found — Fig 2 skipped.")

# Remove old plot files no longer generated
for old in ['fig1_disgenet_ccl2_ccl7.png', 'fig2_opentargets_ccl2_ccl7.png', 'fig3_ot_shared_heatmap.png']:
    p = os.path.join(IMGDIR, old)
    if os.path.exists(p):
        os.remove(p)
        print(f"Removed: {p}")

print("DONE.")
