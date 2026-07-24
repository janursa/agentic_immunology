"""
Q: Does LPS perturbation change chromatin accessibility at rs11867200 (chr17:34,248,950 GRCh38)
   in IBD PBMCs, per disease (UC/CD) and major cell type?
"""

import numpy as np
import pandas as pd
import anndata
import statsmodels.api as sm
from statsmodels.genmod import families
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

# ── Config ───────────────────────────────────────────────────────────────────
ATAC_PATH   = '/home/jnourisa/agentic/datalake/omics/IBD/atac.h5ad'
OUT_DIR     = '/home/jnourisa/agentic/temp/nienke/ibd_atac'
IMG_DIR     = f'{OUT_DIR}/images'

SNP_CHR  = 'chr17'
SNP_POS  = 34_248_950       # GRCh38
WINDOW   = 500              # ±500 bp around SNP to look for peaks

MIN_DONORS = 5              # flag strata with fewer donors

DISEASES   = ['CD', 'UC']
CELLTYPES  = ['CD4 T cells', 'Monocytes', 'B cells', 'CD8 T cells', 'NK cells']
CONDITIONS = ['RPMI', 'LPS']

CELLTYPE_SHORT = {
    'CD4 T cells': 'CD4 T', 'Monocytes': 'Mono',
    'B cells': 'B', 'CD8 T cells': 'CD8 T', 'NK cells': 'NK'
}

# ── 1. Load ATAC ──────────────────────────────────────────────────────────────
print("Loading ATAC h5ad …")
adata = anndata.read_h5ad(ATAC_PATH)
print(f"  Shape: {adata.shape}")

# ── 2. Find target peak(s) ────────────────────────────────────────────────────
def parse_peak(name):
    parts = name.replace(':', '-').split('-')
    return parts[0], int(parts[1]), int(parts[2])

target_peaks = []
for pk in adata.var_names:
    chrom, start, end = parse_peak(pk)
    if chrom == SNP_CHR and start <= SNP_POS + WINDOW and end >= SNP_POS - WINDOW:
        target_peaks.append(pk)

print(f"\nPeaks overlapping {SNP_CHR}:{SNP_POS} ±{WINDOW} bp:")
for pk in target_peaks:
    chrom, s, e = parse_peak(pk)
    dist = max(0, max(SNP_POS - e, s - SNP_POS))
    overlap = "DIRECT OVERLAP" if s <= SNP_POS <= e else f"{dist} bp away"
    print(f"  {pk}  ({overlap})")

if not target_peaks:
    raise RuntimeError(f"No peak found within ±{WINDOW} bp of {SNP_CHR}:{SNP_POS}")

# Use the peak with direct overlap, or closest
direct = [pk for pk in target_peaks if parse_peak(pk)[1] <= SNP_POS <= parse_peak(pk)[2]]
focus_peak = direct[0] if direct else sorted(
    target_peaks, key=lambda pk: max(0, max(SNP_POS - parse_peak(pk)[2],
                                            parse_peak(pk)[1] - SNP_POS))
)[0]
print(f"\nFocus peak: {focus_peak}")

# ── 3. Subset to LPS + RPMI, extract peak counts ─────────────────────────────
mask = adata.obs['stimulation'].isin(CONDITIONS)
sub  = adata[mask].copy()
print(f"\nCells after filtering to LPS/RPMI: {sub.n_obs}")

# Extract raw counts for focus peak + total counts per cell (for offset)
peak_counts  = sub[:, focus_peak].X.toarray().flatten()
total_counts = np.asarray(sub.X.sum(axis=1)).flatten()

sub.obs['peak_raw']    = peak_counts
sub.obs['total_counts'] = total_counts

# ── 4. Pseudobulk aggregation ─────────────────────────────────────────────────
print("\nBuilding pseudobulk …")
pb_rows = []
for (disease, celltype, stimulation, donor), grp in sub.obs.groupby(
        ['disease', 'celltype', 'stimulation', 'donorID'], observed=True):
    if stimulation not in CONDITIONS:
        continue
    pb_rows.append({
        'disease':     disease,
        'celltype':    celltype,
        'stimulation': stimulation,
        'donorID':     donor,
        'peak_counts': int(grp['peak_raw'].sum()),
        'total_counts': int(grp['total_counts'].sum()),
        'n_cells':     len(grp),
    })

pb = pd.DataFrame(pb_rows)
pb['log_total'] = np.log(pb['total_counts'].clip(lower=1))
print(f"  Pseudobulk samples: {len(pb)}")
print(pb.groupby(['disease', 'celltype', 'stimulation'])['donorID'].count().to_string())

# ── 5. NB GLM per disease × cell type ────────────────────────────────────────
print("\nRunning NB GLM (LPS vs RPMI) …")
results = []
flags   = []

for disease in DISEASES:
    for celltype in CELLTYPES:
        sub_pb = pb[(pb['disease'] == disease) & (pb['celltype'] == celltype)].copy()
        n_lps  = sub_pb[sub_pb['stimulation'] == 'LPS']['donorID'].nunique()
        n_rpmi = sub_pb[sub_pb['stimulation'] == 'RPMI']['donorID'].nunique()

        flag = None
        if min(n_lps, n_rpmi) < MIN_DONORS:
            flag = f"⚠ only {min(n_lps, n_rpmi)} donors in smaller group"
            flags.append(f"{disease} {celltype}: {flag}")

        sub_pb['is_lps'] = (sub_pb['stimulation'] == 'LPS').astype(int)
        X      = sm.add_constant(sub_pb[['is_lps']])
        offset = sub_pb['log_total'].values

        try:
            model  = sm.GLM(sub_pb['peak_counts'], X,
                            family=families.NegativeBinomial(),
                            offset=offset)
            res    = model.fit(disp=False)
            coef   = res.params['is_lps']
            se     = res.bse['is_lps']
            pval   = res.pvalues['is_lps']
            log2fc = coef / np.log(2)   # NB log link → convert to log2
            converged = res.converged
        except Exception as e:
            coef = se = pval = log2fc = np.nan
            converged = False
            flag = (flag or '') + f' GLM error: {e}'

        results.append({
            'disease':    disease,
            'celltype':   celltype,
            'n_lps':      n_lps,
            'n_rpmi':     n_rpmi,
            'log2FC':     log2fc,
            'coef':       coef,
            'SE':         se,
            'pval':       pval,
            'converged':  converged,
            'flag':       flag or '',
        })
        sig = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else 'ns'
        print(f"  {disease:3s} | {celltype:<15s} | log2FC={log2fc:+.2f}  p={pval:.3g}  {sig}"
              + (f"  [{flag}]" if flag else ''))

results_df = pd.DataFrame(results)
results_df.to_csv(f'{OUT_DIR}/da_results.tsv', sep='\t', index=False)
print(f"\nResults saved → {OUT_DIR}/da_results.tsv")

if flags:
    print("\nFLAGS:")
    for f in flags:
        print(f"  {f}")

# ── 6. Visualization ───────────────────────────────────────────────────────────

# Log1p-normalize per cell for visualization (not used in GLM)
sub.obs['log1p_cpm'] = np.log1p(
    sub.obs['peak_raw'] / sub.obs['total_counts'].clip(lower=1) * 1e4
)

# ── Fig 1: Violin plots per disease × cell type ───────────────────────────────
fig, axes = plt.subplots(2, 5, figsize=(20, 8), sharey=False)
fig.suptitle(f'Chromatin accessibility at rs11867200 locus\n{focus_peak}',
             fontsize=13, fontweight='bold')

cond_colors = {'RPMI': '#4878CF', 'LPS': '#D65F5F'}

for row_i, disease in enumerate(DISEASES):
    for col_i, celltype in enumerate(CELLTYPES):
        ax = axes[row_i][col_i]
        data_plot = sub.obs[
            (sub.obs['disease'] == disease) & (sub.obs['celltype'] == celltype)
        ]
        positions = []
        for ci, cond in enumerate(CONDITIONS):
            vals = data_plot[data_plot['stimulation'] == cond]['log1p_cpm'].values
            vp = ax.violinplot([vals], positions=[ci], widths=0.6,
                               showmedians=True, showextrema=False)
            for pc in vp['bodies']:
                pc.set_facecolor(cond_colors[cond])
                pc.set_alpha(0.7)
            vp['cmedians'].set_color('black')
            vp['cmedians'].set_linewidth(2)

        # Significance annotation
        row = results_df[(results_df['disease'] == disease) &
                         (results_df['celltype'] == celltype)].iloc[0]
        pval = row['pval']
        sig  = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else 'ns'
        lfc  = row['log2FC']
        ax.set_title(f"{CELLTYPE_SHORT[celltype]}\nlog2FC={lfc:+.2f} {sig}", fontsize=9)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(CONDITIONS, fontsize=8)
        if col_i == 0:
            ax.set_ylabel(f'{disease}\nlog1p(CPM×10⁴)', fontsize=9)
        else:
            ax.set_ylabel('')

legend_patches = [mpatches.Patch(color=c, label=l) for l, c in cond_colors.items()]
fig.legend(handles=legend_patches, loc='lower right', fontsize=9)
plt.tight_layout()
fig.savefig(f'{IMG_DIR}/fig1_violins.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Fig1 saved → {IMG_DIR}/fig1_violins.png")

# ── Fig 2: log2FC heatmap ─────────────────────────────────────────────────────
lfc_mat  = results_df.pivot(index='disease',  columns='celltype', values='log2FC')[CELLTYPES]
pval_mat = results_df.pivot(index='disease', columns='celltype', values='pval')[CELLTYPES]

fig, ax = plt.subplots(figsize=(10, 3))
vmax = np.nanmax(np.abs(lfc_mat.values))
vmax = max(vmax, 0.5)
im = ax.imshow(lfc_mat.values, cmap='RdBu_r', vmin=-vmax, vmax=vmax, aspect='auto')
plt.colorbar(im, ax=ax, label='log2FC (LPS / RPMI)')

ax.set_xticks(range(len(CELLTYPES)))
ax.set_xticklabels([CELLTYPE_SHORT[c] for c in CELLTYPES], fontsize=10)
ax.set_yticks(range(len(DISEASES)))
ax.set_yticklabels(DISEASES, fontsize=10)
ax.set_title(f'Differential accessibility LPS vs RPMI — {focus_peak}\nrs11867200 locus', fontsize=11)

for row_i, disease in enumerate(DISEASES):
    for col_i, celltype in enumerate(CELLTYPES):
        pval = pval_mat.loc[disease, celltype]
        sig  = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
        lfc  = lfc_mat.loc[disease, celltype]
        ax.text(col_i, row_i, f'{lfc:+.2f}\n{sig}', ha='center', va='center',
                fontsize=9, color='white' if abs(lfc) > vmax * 0.6 else 'black')

plt.tight_layout()
fig.savefig(f'{IMG_DIR}/fig2_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Fig2 saved → {IMG_DIR}/fig2_heatmap.png")

print("\nDone.")
