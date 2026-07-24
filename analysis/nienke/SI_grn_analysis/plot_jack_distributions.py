"""
Plot jackknife rho distributions: REF vs Carrier, per TF, per stimulation.
4x4 grid of KDE plots per stimulation condition (RPMI and LPS).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

BASE     = "/vol/projects/BIIM/agentic_immunology/temp/nienke/SI_grn_analysis"
JACK_RAW = f"{BASE}/results/grn_jackknife_raw.tsv"
OBS      = f"{BASE}/results/grn_results.tsv"
IMG_DIR  = f"{BASE}/images"

TFS_16 = ["CEBPB", "FOS", "FOSL2", "GATA2", "GATA3", "JUN", "JUND",
          "MAX", "MEF2A", "MYC", "NFIC", "PBX3", "TCF12",
          "SPI1", "SPIB", "ETV6"]
MOTIF_LOSS = {"SPI1", "SPIB", "ETV6"}

COL_REF = "#2166ac"
COL_CAR = "#d6604d"

plt.rcParams.update({
    "font.family": "Arial", "font.size": 10,
    "axes.titlesize": 10, "axes.labelsize": 10,
    "xtick.labelsize": 10, "ytick.labelsize": 10,
})

jack = pd.read_csv(JACK_RAW, sep="\t")
obs  = pd.read_csv(OBS, sep="\t",
                   names=["group","TF","rho","pval","n","sig_bonf","motif_loss","alpha"])

# figsize: 4x4 grid → base 3 per panel × 4 = 12 each direction,
# reduce by 1 for multi-panel assembly → (11, 11),
# add 1.5 for legend outside last panel → (12.5, 11)
NROWS, NCOLS = 4, 4
FIG_W, FIG_H = 12.5, 11

for stim, ref_grp, car_grp in [("RPMI", "REF_RPMI", "Carrier_RPMI"),
                                 ("LPS",  "REF_LPS",  "Carrier_LPS")]:

    fig, axes = plt.subplots(NROWS, NCOLS, figsize=(FIG_W, FIG_H))
    axes_flat = axes.flatten()

    for ax_i, tf in enumerate(TFS_16):
        ax = axes_flat[ax_i]
        row, col = divmod(ax_i, NCOLS)

        ref_vals = jack[(jack["group"] == ref_grp) & (jack["TF"] == tf)]["rho"].values
        car_vals = jack[(jack["group"] == car_grp) & (jack["TF"] == tf)]["rho"].values
        obs_ref  = obs[(obs["group"] == ref_grp) & (obs["TF"] == tf)]["rho"].values
        obs_car  = obs[(obs["group"] == car_grp) & (obs["TF"] == tf)]["rho"].values

        all_vals = np.concatenate([ref_vals, car_vals])
        x_min = all_vals.min() - 0.05
        x_max = all_vals.max() + 0.05
        x_grid = np.linspace(x_min, x_max, 300)

        for vals, color in [(ref_vals, COL_REF), (car_vals, COL_CAR)]:
            if vals.std() > 1e-10:
                kde = gaussian_kde(vals, bw_method='scott')
                density = kde(x_grid)
                ax.plot(x_grid, density, color=color, lw=1.5)
                ax.fill_between(x_grid, density, alpha=0.25, color=color)

        if len(obs_ref) > 0:
            ax.axvline(obs_ref[0], color=COL_REF, lw=1.2, linestyle="--", alpha=0.9)
        if len(obs_car) > 0:
            ax.axvline(obs_car[0], color=COL_CAR, lw=1.2, linestyle="--", alpha=0.9)
        ax.axvline(0, color="black", lw=0.7, linestyle=":")

        # title: orange for motif-LOSS TFs
        title_color = "darkorange" if tf in MOTIF_LOSS else "black"
        ax.set_title(tf, fontsize=10, color=title_color, pad=3)

        # x-axis label only on bottom row
        if row == NROWS - 1:
            ax.set_xlabel("Spearman ρ", fontsize=10)
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.set_xlabel("")
            ax.tick_params(axis='x', labelbottom=False)

        # y-axis label only on leftmost column
        if col == 0:
            ax.set_ylabel("Density", fontsize=10)
        else:
            ax.set_ylabel("")

        ax.set_yticks([])
        ax.margins(x=0.05)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

    # legend on last panel only
    legend_handles = [
        Patch(facecolor=COL_REF, alpha=0.6, label="REF/REF"),
        Patch(facecolor=COL_CAR, alpha=0.6, label="Carrier HET+ALT"),
        Line2D([0],[0], color="gray", lw=1.2, linestyle="--", label="full-sample ρ"),
        Line2D([0],[0], color="black", lw=0.7, linestyle=":", label="ρ = 0"),
    ]
    axes_flat[-1].legend(handles=legend_handles, fontsize=9, frameon=False,
                         loc="upper left", bbox_to_anchor=(1.05, 1))

    fig.suptitle(
        f"{stim}: jackknife ρ distribution per TF  |  REF vs Carrier  |  age>60\n"
        f"orange titles = motif-LOSS TFs   dashed line = full-sample ρ",
        fontsize=10
    )
    plt.tight_layout()
    out = f"{IMG_DIR}/jack_distributions_{stim}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")
