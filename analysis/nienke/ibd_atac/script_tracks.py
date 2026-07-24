"""
Genomic track plot: chromatin accessibility at rs11867200 locus per cell type × disease
IBD ATAC — one plot per stimulation condition (RPMI baseline + LPS)
Outputs: images/fig3_genomic_tracks_RPMI.png, images/fig3_genomic_tracks_LPS.png
"""

import numpy as np
import pandas as pd
import anndata
import scipy.sparse as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FuncFormatter
import warnings
warnings.filterwarnings('ignore')

# ── Config ─────────────────────────────────────────────────────────────────
ATAC_PATH = '/home/jnourisa/agentic/datalake/omics/IBD/atac.h5ad'
OUT_DIR   = '/home/jnourisa/agentic/temp/nienke/ibd_atac'
IMG_DIR   = f'{OUT_DIR}/images'

SNP_CHR  = 'chr17'
SNP_POS  = 34_248_950
WINDOW   = 15_000

CCL2_START, CCL2_END = 34_255_274, 34_257_208   # GENCODE v45 GRCh38, + strand

CELLTYPES   = ['CD4 T cells', 'Monocytes', 'B cells', 'CD8 T cells', 'NK cells']
DISEASES    = ['CD', 'UC']
CONDITIONS  = ['RPMI', 'LPS']

CELLTYPE_COLORS = {
    'CD4 T cells': '#4878CF',
    'Monocytes':   '#D65F5F',
    'B cells':     '#6ACC65',
    'CD8 T cells': '#B47CC7',
    'NK cells':    '#C4AD66',
}
CELLTYPE_SHORT = {
    'CD4 T cells': 'CD4 T', 'Monocytes': 'Mono',
    'B cells': 'B', 'CD8 T cells': 'CD8 T', 'NK cells': 'NK',
}

def parse_peak(name):
    parts = name.replace(':', '-').split('-')
    return parts[0], int(parts[1]), int(parts[2])

# ── 1. Load ATAC ────────────────────────────────────────────────────────────
print("Loading ATAC h5ad ...")
adata = anndata.read_h5ad(ATAC_PATH)
print(f"  Shape: {adata.shape}")

# ── 2. Find peaks in region ─────────────────────────────────────────────────
region_start = SNP_POS - WINDOW
region_end   = SNP_POS + WINDOW

region_peaks = []
for pk in adata.var_names:
    chrom, start, end = parse_peak(pk)
    if chrom == SNP_CHR and start <= region_end and end >= region_start:
        region_peaks.append(pk)

print(f"\nPeaks in region: {len(region_peaks)}")
for pk in region_peaks:
    chrom, s, e = parse_peak(pk)
    direct = s <= SNP_POS <= e
    dist   = 0 if direct else max(SNP_POS - e, s - SNP_POS)
    print(f"  {pk}  ({'DIRECT OVERLAP' if direct else f'{dist} bp away'})")

if not region_peaks:
    raise RuntimeError("No peaks found in region.")

peak_starts = np.array([parse_peak(pk)[1] for pk in region_peaks])
peak_ends   = np.array([parse_peak(pk)[2] for pk in region_peaks])

# ── 3. Compute pseudobulk CPM for all conditions ────────────────────────────
mask_stim = adata.obs['stimulation'].isin(CONDITIONS)
sub       = adata[mask_stim].copy()
print(f"\nCells (LPS+RPMI): {sub.n_obs}")

X_region     = sub[:, region_peaks].X
if sp.issparse(X_region):
    X_region = X_region.toarray()
total_counts = np.asarray(sub.X.sum(axis=1)).flatten()

obs = sub.obs.copy()
obs['cell_idx'] = np.arange(len(obs))

print("\nComputing pseudobulk CPM ...")
cpm_dict = {}   # (condition, disease, celltype) → (n_peaks,)

for cond in CONDITIONS:
    for disease in DISEASES:
        for celltype in CELLTYPES:
            ct_cells = obs[
                (obs['stimulation'] == cond) &
                (obs['disease']     == disease) &
                (obs['celltype']    == celltype)
            ]
            donor_cpm_list = []
            for donor, grp in ct_cells.groupby('donorID'):
                idx      = grp['cell_idx'].values
                d_counts = X_region[idx, :].sum(axis=0)
                d_total  = total_counts[idx].sum()
                if d_total > 0:
                    donor_cpm_list.append(
                        np.asarray(d_counts).flatten() / d_total * 1e6
                    )
            mean_cpm = (
                np.mean(np.vstack(donor_cpm_list), axis=0)
                if donor_cpm_list else np.zeros(len(region_peaks))
            )
            cpm_dict[(cond, disease, celltype)] = mean_cpm

# Shared vmax across all conditions (enables direct comparison)
all_vals = np.concatenate([v for v in cpm_dict.values()])
nonzero  = all_vals[all_vals > 0]
vmax     = np.percentile(nonzero, 95) if len(nonzero) > 0 else 1.0
print(f"Shared vmax (95th pct, all conditions): {vmax:.2f}")

# ── 4. Plot — one figure per condition ─────────────────────────────────────
xlim   = (region_start, region_end)
n_ct   = len(CELLTYPES)
n_dis  = len(DISEASES)

def make_track_fig(condition):
    fig = plt.figure(figsize=(5, 3))
    gs  = GridSpec(
        n_ct + 1, n_dis,
        height_ratios=[1] * n_ct + [1.6],
        hspace=0.03, wspace=0.04,
        left=0.13, right=0.98, top=0.88, bottom=0.14,
        figure=fig,
    )
    ax_tracks = [[fig.add_subplot(gs[i, j]) for j in range(n_dis)] for i in range(n_ct)]
    ax_gene   = [fig.add_subplot(gs[-1, j])  for j in range(n_dis)]

    for col_i, disease in enumerate(DISEASES):
        for row_i, celltype in enumerate(CELLTYPES):
            ax    = ax_tracks[row_i][col_i]
            cpm   = cpm_dict[(condition, disease, celltype)]
            color = CELLTYPE_COLORS[celltype]

            for j in range(len(region_peaks)):
                height = min(1.0, max(0.0, cpm[j] / vmax)) if vmax > 0 else 0.0
                alpha  = max(0.12, height)
                ax.add_patch(mpatches.Rectangle(
                    (peak_starts[j], 0), peak_ends[j] - peak_starts[j], height,
                    facecolor=color, alpha=alpha, edgecolor='none', linewidth=0,
                ))

            ax.axvline(SNP_POS, color='#CC0000', lw=0.7, ls='--', alpha=0.75, zorder=5)
            ax.set_xlim(*xlim)
            ax.set_ylim(0, 1.05)
            ax.set_yticks([])
            ax.tick_params(bottom=False, labelbottom=False)
            ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)

            if col_i == 0:
                ax.set_ylabel(
                    CELLTYPE_SHORT[celltype], fontsize=6, rotation=0,
                    labelpad=22, va='center', ha='right',
                    color=color, fontweight='bold',
                )
            if row_i == 0:
                ax.set_title(disease, fontsize=7, fontweight='bold', pad=2)

    for col_i in range(n_dis):
        ax = ax_gene[col_i]
        ax.set_xlim(*xlim)
        ax.set_ylim(-0.4, 2.2)
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.yaxis.set_visible(False)

        ax.axvline(SNP_POS, color='#CC0000', lw=0.7, ls='--', alpha=0.75)
        ax.plot([CCL2_START, CCL2_END], [1.0, 1.0], color='#2b2b2b', lw=1.5)
        ax.annotate(
            '', xy=(CCL2_END + 200, 1.0), xytext=(CCL2_END, 1.0),
            arrowprops=dict(arrowstyle='->', color='#2b2b2b', lw=1.0),
        )
        ax.text(
            (CCL2_START + CCL2_END) / 2, 1.6, 'CCL2',
            ha='center', va='bottom', fontsize=6,
            fontstyle='italic', color='#2b2b2b',
        )
        ax.text(
            SNP_POS, -0.3, 'rs11867200',
            ha='center', va='top', fontsize=5, color='#CC0000', style='italic',
        )

        if col_i == 0:
            ax.set_ylabel(
                'Genes', fontsize=5.5, rotation=0,
                labelpad=22, va='center', ha='right',
            )

        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x / 1e6:.3f}'))
        plt.setp(ax.get_xticklabels(), fontsize=5, rotation=30, ha='right')
        ax.tick_params(axis='x', length=2, pad=1)

    fig.suptitle(
        f'Chromatin accessibility at rs11867200  |  IBD ATAC, {condition}',
        fontsize=7, fontweight='bold',
    )
    return fig

for cond in CONDITIONS:
    fig = make_track_fig(cond)
    out = f'{IMG_DIR}/fig3_genomic_tracks_{cond}.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved → {out}")

print("\nDone.")
