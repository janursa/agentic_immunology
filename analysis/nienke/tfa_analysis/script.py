"""
TF Activity Analysis — rs11867200 / CCL2 locus (SI cohort)

Steps:
  1. Load dosage, covariates, CPM RNA-seq (LPS + NS 24h)
  2. Infer one GRN from REF-allele (dosage ≤ 0.5), age > 60, LPS + NS pooled
  3. Calculate per-sample TF activity (ULM via decoupler) for ALL samples
     (REF + Carrier, both conditions, all ages) using the GRN from step 2
  4. Visualize: heatmap (group means), boxplots for 16 candidate TFs, PCA
"""

import sys
import os
import numpy as np
import pandas as pd
import anndata as ad
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

# ── Paths ──────────────────────────────────────────────────────────────────────
AGENTIC = "/vol/projects/BIIM/agentic_immunology"
sys.path.insert(0, os.path.join(AGENTIC, "tools", "ciim", "code"))
from genomics import infer_grn_spearman, infer_tf_activity

BASE      = f"{AGENTIC}/temp/nienke/tfa_analysis"
DOSAGE    = "/vol/projects/CIIM/cohorts/SI/genotype_processed/dosage/chr17.txt"
COVARIATES= "/vol/projects/CIIM/meta_cQTL/data/SI/covariates.tsv"
RNA_NS    = "/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_ns_cpm.tsv"
RNA_LPS   = "/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_lps_cpm.tsv"
SNP_ID    = "chr17:34248950:C:T;rs11867200"

TFS_16 = ["CEBPB", "FOS", "FOSL2", "GATA2", "GATA3", "JUN", "JUND",
          "MAX", "MEF2A", "MYC", "NFIC", "PBX3", "TCF12",
          "SPI1", "SPIB", "ETV6"]

os.makedirs(f"{BASE}/results", exist_ok=True)
os.makedirs(f"{BASE}/images",  exist_ok=True)

# ── Plot style ─────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

PALETTE = {"REF_LPS": "#d62728", "REF_NS": "#ff9896",
           "Carrier_LPS": "#1f77b4", "Carrier_NS": "#aec7e8"}

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Load dosage, covariates, CPM
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== STEP 1: Load data ===")

dos = pd.read_csv(DOSAGE, sep="\t", index_col=0)
snp_row = dos.loc[SNP_ID]
dosage = snp_row.astype(float)
allele_group = dosage.apply(lambda x: "REF" if x <= 0.5 else "Carrier")
print(f"  Genotype samples:  {len(allele_group)}")
print(f"  REF (dosage ≤ 0.5): n={(allele_group == 'REF').sum()}")
print(f"  Carrier (> 0.5):    n={(allele_group == 'Carrier').sum()}")

cov = pd.read_csv(COVARIATES, sep="\t", index_col=0)
if "age" in cov.index:
    cov = cov.T
age_col = [c for c in cov.columns if "age" in c.lower()][0]
age = pd.to_numeric(cov[age_col], errors="coerce")
print(f"  Covariate samples: {len(age)}")

# CPM files: genes × samples — transpose to samples × genes
cpm_ns  = pd.read_csv(RNA_NS,  sep="\t", index_col=0).T   # samples × genes
cpm_lps = pd.read_csv(RNA_LPS, sep="\t", index_col=0).T
cpm_ns.index.name  = "sample_id"
cpm_lps.index.name = "sample_id"
print(f"  NS CPM shape (samples × genes):  {cpm_ns.shape}")
print(f"  LPS CPM shape (samples × genes): {cpm_lps.shape}")

# ── Shared genes between conditions ───────────────────────────────────────────
shared_genes = cpm_ns.columns.intersection(cpm_lps.columns)
cpm_ns  = cpm_ns[shared_genes]
cpm_lps = cpm_lps[shared_genes]
print(f"  Shared genes: {len(shared_genes)}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Define sample groups
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== STEP 2: Define groups ===")

def intersect_samples(cpm_df, allele_ser, age_ser=None, min_age=None, allele_val=None):
    ids = allele_ser.index
    if allele_val is not None:
        ids = allele_ser[allele_ser == allele_val].index
    if age_ser is not None and min_age is not None:
        ids = ids.intersection(age_ser[age_ser > min_age].index)
    return cpm_df.index.intersection(ids)

# GRN cohort: REF allele + age > 60, both conditions
grn_ns_ids  = intersect_samples(cpm_ns,  allele_group, age, min_age=60, allele_val="REF")
grn_lps_ids = intersect_samples(cpm_lps, allele_group, age, min_age=60, allele_val="REF")
print(f"  GRN — REF >60yo NS:  n={len(grn_ns_ids)}")
print(f"  GRN — REF >60yo LPS: n={len(grn_lps_ids)}")

# TFA cohort: all genotyped samples, both conditions
tfa_ns_ids  = cpm_ns.index.intersection(allele_group.index)
tfa_lps_ids = cpm_lps.index.intersection(allele_group.index)
print(f"  TFA — all NS:  n={len(tfa_ns_ids)}")
print(f"  TFA — all LPS: n={len(tfa_lps_ids)}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Build GRN AnnData and infer GRN
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== STEP 3: Build GRN AnnData ===")

# Pool REF + >60yo NS and LPS samples
grn_ns_df  = cpm_ns.loc[grn_ns_ids].copy()
grn_lps_df = cpm_lps.loc[grn_lps_ids].copy()

# Add condition suffix to avoid duplicate index collisions
grn_ns_df.index  = grn_ns_df.index  + "_NS"
grn_lps_df.index = grn_lps_df.index + "_LPS"

grn_expr = pd.concat([grn_ns_df, grn_lps_df], axis=0)
print(f"  Combined GRN matrix: {grn_expr.shape} (samples × genes)")

# log1p transform CPM
grn_expr_log = np.log1p(np.clip(grn_expr.values.astype(np.float32), 0, None))

adata_grn = ad.AnnData(
    X=grn_expr_log,
    obs=pd.DataFrame({
        "condition": (["NS"] * len(grn_ns_ids)) + (["LPS"] * len(grn_lps_ids)),
    }, index=grn_expr.index),
    var=pd.DataFrame(index=shared_genes),
)
print(f"  GRN AnnData: {adata_grn.n_obs} obs × {adata_grn.n_vars} vars")

grn_h5ad = f"{BASE}/results/grn_adata.h5ad"
adata_grn.write_h5ad(grn_h5ad)
print(f"  Saved: {grn_h5ad}")

print("\n=== STEP 3b: Infer GRN (Spearman, bulk, BH FDR < 0.05) ===")
grn_csv = f"{BASE}/results/grn.csv"
log_msg = infer_grn_spearman(
    adata_path=grn_h5ad,
    output_file=grn_csv,
    data_type="bulk",
    p_value_filter=True,
    top_n_edges=100_000,
)
print(log_msg)

grn = pd.read_csv(grn_csv)
print(f"  GRN edges loaded: {len(grn)}")
print(f"  Unique TFs (sources): {grn['source'].nunique()}")
print(f"  Genes covered: {grn['target'].nunique()}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Build TFA AnnData (all genotyped samples, both conditions)
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== STEP 4: Build TFA AnnData (all samples) ===")

tfa_ns_df  = cpm_ns.loc[tfa_ns_ids].copy()
tfa_lps_df = cpm_lps.loc[tfa_lps_ids].copy()

# Unique indices: append condition suffix
tfa_ns_df.index  = tfa_ns_df.index  + "_NS"
tfa_lps_df.index = tfa_lps_df.index + "_LPS"

tfa_expr = pd.concat([tfa_ns_df, tfa_lps_df], axis=0)
tfa_expr_log = np.log1p(np.clip(tfa_expr.values.astype(np.float32), 0, None))

# Build obs metadata
def make_obs(ids_ns, ids_lps, allele_ser, age_ser):
    obs_rows = []
    for sid in list(ids_ns) + list(ids_lps):
        raw_id = sid.replace("_NS", "").replace("_LPS", "")
        cond   = "LPS" if sid.endswith("_LPS") else "NS"
        allele = allele_ser.get(raw_id, "unknown")
        ag     = age_ser.get(raw_id, np.nan) if hasattr(age_ser, "get") else age_ser.get(raw_id, np.nan)
        grp    = f"{allele}_{cond}"
        obs_rows.append({"condition": cond, "allele": allele, "age": ag, "group": grp})
    return pd.DataFrame(obs_rows, index=list(ids_ns) + list(ids_lps))

obs_meta = make_obs(
    tfa_ns_df.index, tfa_lps_df.index,
    allele_group.to_dict(), age.to_dict()
)

adata_tfa = ad.AnnData(
    X=tfa_expr_log,
    obs=obs_meta,
    var=pd.DataFrame(index=shared_genes),
)
print(f"  TFA AnnData: {adata_tfa.n_obs} obs × {adata_tfa.n_vars} vars")
print(adata_tfa.obs["group"].value_counts().to_string())

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Infer TF activity (ULM)
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== STEP 5: Infer TF activity (ULM) ===")

tf_scores = infer_tf_activity(adata_tfa, net=grn, method="ulm", verbose=True)
print(f"  TF activity matrix: {tf_scores.shape} (samples × TFs)")
print(f"  TFs scored: {tf_scores.shape[1]}")

# Save
tf_scores_out = f"{BASE}/results/tf_activity.tsv"
tf_scores.to_csv(tf_scores_out, sep="\t")
print(f"  Saved: {tf_scores_out}")

# Save metadata alongside
obs_out = f"{BASE}/results/sample_metadata.tsv"
adata_tfa.obs.to_csv(obs_out, sep="\t")
print(f"  Saved: {obs_out}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Visualizations
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== STEP 6: Visualizations ===")

meta = adata_tfa.obs.copy()
meta.index = tf_scores.index
groups = ["REF_NS", "REF_LPS", "Carrier_NS", "Carrier_LPS"]

# ── Fig 1: Heatmap — group-mean TF activity (candidate 16 TFs) ────────────────
print("  Fig 1: Heatmap group-mean TF activity")

avail_16 = [tf for tf in TFS_16 if tf in tf_scores.columns]
print(f"  Candidate TFs in GRN: {len(avail_16)}/{len(TFS_16)}: {avail_16}")

if avail_16:
    group_means = {}
    for g in groups:
        mask = meta["group"] == g
        if mask.sum() > 0:
            group_means[g] = tf_scores.loc[mask, avail_16].mean()
    hm_df = pd.DataFrame(group_means).T   # groups × TFs
    hm_df = hm_df.reindex(columns=avail_16)

    n_tfs = len(avail_16)
    n_grp = len(hm_df)
    fw = 3 + max(0, (n_tfs - 5) / 2) * 0.5
    fh = 3 + max(0, (n_grp - 5) / 2) * 0.5

    fig, ax = plt.subplots(figsize=(fw, fh))
    im = ax.imshow(hm_df.values, aspect="auto", cmap="RdBu_r")
    ax.set_xticks(range(n_tfs))
    ax.set_xticklabels(avail_16, rotation=45, ha="right", fontsize=10)
    ax.set_yticks(range(n_grp))
    ax.set_yticklabels(hm_df.index, fontsize=10)
    ax.set_title("Mean TF activity (ULM) — candidate TFs", fontsize=10)
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("ULM score", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{BASE}/images/fig1_heatmap_candidate_tfs.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {BASE}/images/fig1_heatmap_candidate_tfs.png")

# ── Fig 2: Heatmap — group-mean TF activity (all scored TFs) ─────────────────
print("  Fig 2: Heatmap — all scored TFs")

group_means_all = {}
for g in groups:
    mask = meta["group"] == g
    if mask.sum() > 0:
        group_means_all[g] = tf_scores.loc[mask].mean()
hm_all = pd.DataFrame(group_means_all).T   # groups × TFs

# Sort TFs by variance across groups
tf_var = hm_all.var(axis=0)
top50 = tf_var.nlargest(50).index
hm_top50 = hm_all[top50]

n_tfs = len(top50)
fw = 3 + max(0, (n_tfs - 5) / 2) * 0.5
fh = 3 + max(0, (n_grp - 5) / 2) * 0.5

fig, ax = plt.subplots(figsize=(fw, fh))
im = ax.imshow(hm_top50.values, aspect="auto", cmap="RdBu_r")
ax.set_xticks(range(n_tfs))
ax.set_xticklabels(top50, rotation=45, ha="right", fontsize=9)
ax.set_yticks(range(n_grp))
ax.set_yticklabels(hm_top50.index, fontsize=10)
ax.set_title("Mean TF activity (ULM) — top 50 by variance", fontsize=10)
cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label("ULM score", fontsize=10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(f"{BASE}/images/fig2_heatmap_top50.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {BASE}/images/fig2_heatmap_top50.png")

# ── Fig 3: Boxplots — candidate TFs by group ──────────────────────────────────
print("  Fig 3: Boxplots — candidate TFs")

if avail_16:
    n_tfs = len(avail_16)
    ncols = 4
    nrows = int(np.ceil(n_tfs / ncols))
    # multi-panel: 3×3 per panel, reduce assembled size by 1 on each axis
    fw = ncols * 3 - 1
    fh = nrows * 3 - 1

    fig, axes = plt.subplots(nrows, ncols, figsize=(fw, fh))
    axes = axes.flatten()

    for i, tf in enumerate(avail_16):
        ax = axes[i]
        plot_data = []
        for g in groups:
            mask = meta["group"] == g
            vals = tf_scores.loc[mask, tf].dropna()
            plot_data.append(vals)

        bp = ax.boxplot(plot_data, patch_artist=True, widths=0.5,
                        medianprops=dict(color="black", linewidth=1.5),
                        flierprops=dict(marker="o", markersize=2, alpha=0.5))
        for patch, g in zip(bp["boxes"], groups):
            patch.set_facecolor(PALETTE[g])
            patch.set_alpha(0.8)

        ax.set_xticks(range(1, len(groups) + 1))
        ax.set_xticklabels(groups, rotation=45, ha="right", fontsize=9)
        ax.set_title(tf, fontsize=10, fontweight="bold")
        if i % ncols == 0:
            ax.set_ylabel("ULM score", fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Remove empty panels
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{BASE}/images/fig3_boxplots_candidate_tfs.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {BASE}/images/fig3_boxplots_candidate_tfs.png")

# ── Fig 4: PCA of TF activity space ───────────────────────────────────────────
print("  Fig 4: PCA of TF activity space")

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

scores_mat = tf_scores.dropna(axis=1)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(scores_mat.values)
pca = PCA(n_components=2, random_state=42)
pcs = pca.fit_transform(X_scaled)
pc_df = pd.DataFrame(pcs, columns=["PC1", "PC2"], index=tf_scores.index)
pc_df = pc_df.join(meta[["group", "condition", "allele"]])

fig, ax = plt.subplots(figsize=(4.5, 3))
for g in groups:
    mask = pc_df["group"] == g
    ax.scatter(pc_df.loc[mask, "PC1"], pc_df.loc[mask, "PC2"],
               color=PALETTE[g], s=12, alpha=0.6, label=g, linewidths=0)
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=10)
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=10)
ax.set_title("PCA — TF activity space", fontsize=10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.savefig(f"{BASE}/images/fig4_pca_tf_activity.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {BASE}/images/fig4_pca_tf_activity.png")

# ── Fig 5: Allele effect per candidate TF (LPS condition) ─────────────────────
print("  Fig 5: Allele × LPS — median TF activity (candidate TFs)")

if avail_16:
    ref_lps   = tf_scores.loc[meta["group"] == "REF_LPS",     avail_16].median()
    carr_lps  = tf_scores.loc[meta["group"] == "Carrier_LPS", avail_16].median()
    delta = carr_lps - ref_lps  # positive = Carrier > REF

    delta_sorted = delta.sort_values()
    n_items = len(delta_sorted)
    # horizontal barplot: categorical axis is y — scale height
    fh = 3 + max(0, (n_items - 10) / 5) * 0.5
    fig, ax = plt.subplots(figsize=(3, fh))
    colors = ["#1f77b4" if v >= 0 else "#d62728" for v in delta_sorted.values]
    ax.barh(range(n_items), delta_sorted.values, color=colors, alpha=0.85)
    ax.set_yticks(range(n_items))
    ax.set_yticklabels(delta_sorted.index, fontsize=9)
    ax.set_xlabel("Δ median ULM (Carrier − REF), LPS", fontsize=10)
    ax.set_title("Allele effect on TF activity (LPS)", fontsize=10)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(y=0.02)
    plt.tight_layout()
    plt.savefig(f"{BASE}/images/fig5_allele_delta_lps.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {BASE}/images/fig5_allele_delta_lps.png")

print("\n=== DONE ===")
print(f"  GRN:            {grn_csv}")
print(f"  TF activity:    {tf_scores_out}")
print(f"  Sample metadata:{obs_out}")
print(f"  Images folder:  {BASE}/images/")
