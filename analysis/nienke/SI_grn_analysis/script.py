"""
SI GRN Analysis v4 — one GRN per allele group, then compare
- GRN_REF:     REF allele (dosage ≤ 0.5), age > 60, LPS + RPMI pooled
- GRN_Carrier: Carrier (dosage > 0.5),   age > 60, LPS + RPMI pooled
- Compare TF-CCL2 edges globally and for the 16 candidate TFs
- Fisher Z-test: REF GRN ρ vs Carrier GRN ρ per TF, BH FDR correction
"""

import sys
import os
import numpy as np
import pandas as pd
import anndata as ad
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy import stats

AGENTIC = "/vol/projects/BIIM/agentic_immunology"
sys.path.insert(0, os.path.join(AGENTIC, "tools", "ciim", "code"))
from genomics import infer_grn_spearman

BASE       = f"{AGENTIC}/temp/nienke/SI_grn_analysis"
DOSAGE     = "/vol/projects/CIIM/cohorts/SI/genotype_processed/dosage/chr17.txt"
COVARIATES = "/vol/projects/CIIM/meta_cQTL/data/SI/covariates.tsv"
RNA_NS     = "/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_ns_cpm.tsv"
RNA_LPS    = "/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_lps_cpm.tsv"

SNP_ID         = "chr17:34248950:C:T;rs11867200"
TFS_16         = ["CEBPB", "FOS", "FOSL2", "GATA2", "GATA3", "JUN", "JUND",
                  "MAX", "MEF2A", "MYC", "NFIC", "PBX3", "TCF12",
                  "SPI1", "SPIB", "ETV6"]
MOTIF_LOSS_TFS = ["SPI1", "SPIB", "ETV6"]
TARGET         = "CCL2"

os.makedirs(f"{BASE}/results", exist_ok=True)
os.makedirs(f"{BASE}/images",  exist_ok=True)

# ── Plot style (Arial 10 throughout; 9 for legend/annotations) ───────────────
plt.rcParams.update({
    "font.family": "Arial", "font.size": 10,
    "axes.titlesize": 10, "axes.labelsize": 10,
    "xtick.labelsize": 10, "ytick.labelsize": 10,
})
COL_REF = "#2166ac"
COL_CAR = "#d6604d"

# ── 1. Load dosage ────────────────────────────────────────────────────────────
print("=== STEP 1: Loading dosage ===")
dos = pd.read_csv(DOSAGE, sep="\t", index_col=0)
dosage = dos.loc[SNP_ID].astype(float)
allele_group = dosage.apply(lambda x: "REF" if x <= 0.5 else "Carrier")
print(f"  REF (dosage ≤ 0.5): n={(allele_group == 'REF').sum()}")
print(f"  Carrier (> 0.5):    n={(allele_group == 'Carrier').sum()}")

# ── 2. Age filter (> 60) ─────────────────────────────────────────────────────
print("\n=== STEP 2: Age filter ===")
cov = pd.read_csv(COVARIATES, sep="\t", index_col=0)
if "age" in cov.index:
    cov = cov.T
age_col = [c for c in cov.columns if "age" in c.lower()][0]
age = pd.to_numeric(cov[age_col], errors="coerce")
old_samples = set(age[age > 60].index)
allele_old = allele_group[allele_group.index.isin(old_samples)]
print(f"  Samples age > 60: {len(old_samples)}")
print(f"  REF age > 60:     n={(allele_old == 'REF').sum()}")
print(f"  Carrier age > 60: n={(allele_old == 'Carrier').sum()}")

# ── 3. Load RNA-seq (genes × samples → transpose to samples × genes) ─────────
print("\n=== STEP 3: Loading RNA-seq ===")
cpm_ns  = pd.read_csv(RNA_NS,  sep="\t", index_col=0).T
cpm_lps = pd.read_csv(RNA_LPS, sep="\t", index_col=0).T
shared_genes = cpm_ns.columns.intersection(cpm_lps.columns)
cpm_ns  = cpm_ns[shared_genes]
cpm_lps = cpm_lps[shared_genes]
print(f"  NS shape:  {cpm_ns.shape}  |  LPS shape: {cpm_lps.shape}")
print(f"  Shared genes: {len(shared_genes)}")

# ── 4. Build AnnData per allele (pool LPS + RPMI, age > 60) ──────────────────
print("\n=== STEP 4: Build per-allele AnnData (LPS + RPMI pooled) ===")

def build_adata(allele_val):
    ids     = allele_old[allele_old == allele_val].index
    ns_ids  = sorted(set(ids) & set(cpm_ns.index))
    lps_ids = sorted(set(ids) & set(cpm_lps.index))
    ns_df   = cpm_ns.loc[ns_ids].copy()
    lps_df  = cpm_lps.loc[lps_ids].copy()
    ns_df.index  = [s + "_NS"  for s in ns_df.index]
    lps_df.index = [s + "_LPS" for s in lps_df.index]
    combined = pd.concat([ns_df, lps_df])
    expr_log = np.log1p(np.clip(combined.values.astype(np.float32), 0, None))
    obs_df   = pd.DataFrame({
        "condition": ["NS"] * len(ns_ids) + ["LPS"] * len(lps_ids),
        "allele": allele_val,
    }, index=combined.index)
    adata = ad.AnnData(X=expr_log, obs=obs_df,
                       var=pd.DataFrame(index=shared_genes))
    return adata, len(ns_ids), len(lps_ids)

adata_ref, n_ref_ns, n_ref_lps = build_adata("REF")
adata_car, n_car_ns, n_car_lps = build_adata("Carrier")
print(f"  GRN_REF:     {adata_ref.n_obs} obs ({n_ref_ns} NS + {n_ref_lps} LPS)")
print(f"  GRN_Carrier: {adata_car.n_obs} obs ({n_car_ns} NS + {n_car_lps} LPS)")

h5ad_ref = f"{BASE}/results/adata_ref.h5ad"
h5ad_car = f"{BASE}/results/adata_carrier.h5ad"
adata_ref.write_h5ad(h5ad_ref)
adata_car.write_h5ad(h5ad_car)
print(f"  Saved: {h5ad_ref}")
print(f"  Saved: {h5ad_car}")

# ── 5. Infer GRN per allele group ─────────────────────────────────────────────
print("\n=== STEP 5: Infer GRNs via infer_grn_spearman ===")
grn_ref_csv = f"{BASE}/results/grn_ref.csv"
grn_car_csv = f"{BASE}/results/grn_carrier.csv"

print("  Inferring GRN_REF …")
print(infer_grn_spearman(
    adata_path=h5ad_ref, output_file=grn_ref_csv,
    data_type="bulk", p_value_filter=True, top_n_edges=100_000,
))

print("  Inferring GRN_Carrier …")
print(infer_grn_spearman(
    adata_path=h5ad_car, output_file=grn_car_csv,
    data_type="bulk", p_value_filter=True, top_n_edges=100_000,
))

grn_ref = pd.read_csv(grn_ref_csv)
grn_car = pd.read_csv(grn_car_csv)
print(f"  GRN_REF:     {len(grn_ref):,} edges | {grn_ref['source'].nunique()} TFs | {grn_ref['target'].nunique()} targets")
print(f"  GRN_Carrier: {len(grn_car):,} edges | {grn_car['source'].nunique()} TFs | {grn_car['target'].nunique()} targets")

# ── 6. Global GRN overlap stats ───────────────────────────────────────────────
print("\n=== STEP 6: Global GRN overlap ===")
ref_set  = set(zip(grn_ref["source"], grn_ref["target"]))
car_set  = set(zip(grn_car["source"], grn_car["target"]))
shared   = ref_set & car_set
ref_only = ref_set - car_set
car_only = car_set - ref_set
union    = ref_set | car_set
jaccard  = len(shared) / len(union) if union else 0.0
print(f"  REF only: {len(ref_only):,}  |  Carrier only: {len(car_only):,}  |  Shared: {len(shared):,}  |  Jaccard: {jaccard:.4f}")

pd.DataFrame({
    "metric": ["n_edges_REF", "n_edges_Carrier", "n_shared", "n_REF_only", "n_Carrier_only", "jaccard"],
    "value":  [len(grn_ref), len(grn_car), len(shared), len(ref_only), len(car_only), jaccard],
}).to_csv(f"{BASE}/results/grn_global_comparison.csv", index=False)

# ── Helper functions ──────────────────────────────────────────────────────────
def fisher_z_test(rho1, n1, rho2, n2):
    if np.isnan(rho1) or np.isnan(rho2):
        return np.nan, np.nan
    z1 = np.arctanh(np.clip(rho1, -0.9999, 0.9999))
    z2 = np.arctanh(np.clip(rho2, -0.9999, 0.9999))
    se = np.sqrt(1.0 / (n1 - 3) + 1.0 / (n2 - 3))
    zs = (z1 - z2) / se
    return zs, 2.0 * (1.0 - stats.norm.cdf(abs(zs)))

def bh_correction(pvals):
    pv = np.array(pvals, dtype=float)
    n  = len(pv)
    si = np.argsort(pv)
    sp = pv[si]
    adj = np.minimum(1.0, sp * n / np.arange(1, n + 1))
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty(n)
    out[si] = adj
    return out

# ── 7. CCL2-specific TF edges ─────────────────────────────────────────────────
# top_n_edges=100k is too strict for CCL2 edges — directly compute Spearman
# ρ(TF, CCL2) from each allele's AnnData; BH FDR within each GRN.
print("\n=== STEP 7: CCL2 edge comparison (16 candidate TFs, direct Spearman) ===")
from scipy.stats import spearmanr

def compute_ccl2_edges(adata, label):
    """Spearman ρ(TF, CCL2) with BH FDR for all 16 TFs from AnnData."""
    gene_names = list(adata.var_names)
    if TARGET not in gene_names:
        raise ValueError(f"{TARGET} not found in AnnData genes")
    ccl2_idx  = gene_names.index(TARGET)
    ccl2_expr = adata.X[:, ccl2_idx].flatten()

    rhos, pvals = [], []
    for tf in TFS_16:
        if tf in gene_names:
            tf_idx  = gene_names.index(tf)
            tf_expr = adata.X[:, tf_idx].flatten()
            rho, pval = spearmanr(tf_expr, ccl2_expr)
        else:
            rho, pval = np.nan, np.nan
        rhos.append(rho)
        pvals.append(pval)

    # BH FDR over 16 tests within this GRN
    valid_mask = ~np.isnan(pvals)
    fdrs = np.full(len(TFS_16), np.nan)
    if valid_mask.sum() > 0:
        fdrs[valid_mask] = bh_correction(np.array(pvals)[valid_mask])

    df = pd.DataFrame({
        "TF": TFS_16,
        f"rho_{label}":     rhos,
        f"pval_{label}":    pvals,
        f"fdr_{label}":     fdrs,
        f"sig_{label}":     fdrs < 0.05,
    })
    print(f"  [{label}] FDR<0.05 TF–CCL2 edges:")
    for _, r in df[df[f"sig_{label}"]].iterrows():
        print(f"    {r['TF']}: rho={r[f'rho_{label}']:+.3f}  FDR={r[f'fdr_{label}']:.3f}")
    return df

df_ref_ccl2 = compute_ccl2_edges(adata_ref, "REF")
df_car_ccl2 = compute_ccl2_edges(adata_car, "Carrier")

df_comp = (df_ref_ccl2
           .merge(df_car_ccl2, on="TF")
           .assign(motif_loss_tf=lambda d: d["TF"].isin(MOTIF_LOSS_TFS)))
df_comp["delta_rho"] = df_comp["rho_Carrier"] - df_comp["rho_REF"]

# "in GRN" flag = FDR-significant within that GRN
df_comp["in_REF_GRN"]     = df_comp["sig_REF"]
df_comp["in_Carrier_GRN"] = df_comp["sig_Carrier"]

print(f"\n  CCL2 FDR-sig TFs in GRN_REF:     {df_comp['in_REF_GRN'].sum()}")
print(f"  CCL2 FDR-sig TFs in GRN_Carrier: {df_comp['in_Carrier_GRN'].sum()}")

# ── 8. Fisher Z-test ──────────────────────────────────────────────────────────
print("\n=== STEP 8: Fisher Z-test (REF GRN ρ vs Carrier GRN ρ) ===")
n_ref = adata_ref.n_obs
n_car = adata_car.n_obs

zs, ps = zip(*[fisher_z_test(r.rho_REF, n_ref, r.rho_Carrier, n_car)
               for _, r in df_comp.iterrows()])
df_comp["z_stat"]      = zs
df_comp["pval_fisher"] = ps

valid = df_comp["pval_fisher"].notna()
df_comp.loc[valid, "pval_fdr"] = bh_correction(df_comp.loc[valid, "pval_fisher"].values)
df_comp["pval_fdr"] = df_comp["pval_fdr"].where(valid, np.nan)
df_comp["sig_fdr05"] = df_comp["pval_fdr"] < 0.05
df_comp["sig_fdr10"] = df_comp["pval_fdr"] < 0.10

df_comp.to_csv(f"{BASE}/results/grn_ccl2_comparison.csv", index=False)
print(f"  n_REF={n_ref}  n_Carrier={n_car}")
print(f"  Saved: {BASE}/results/grn_ccl2_comparison.csv")
print(f"\n  {'TF':<10}  {'ρ_REF':>7}  {'ρ_Car':>7}  {'Δρ':>7}  {'p(Fisher)':>11}  {'FDR':>6}")
for _, row in df_comp.sort_values("pval_fisher").iterrows():
    flag = " **" if row["sig_fdr05"] else (" *" if row["sig_fdr10"] else "  ")
    ml   = "[ML]" if row["motif_loss_tf"] else "    "
    rr   = f"{row['rho_REF']:+.3f}"      if not np.isnan(row["rho_REF"])      else "  NaN"
    rc   = f"{row['rho_Carrier']:+.3f}"  if not np.isnan(row["rho_Carrier"])  else "  NaN"
    dr   = f"{row['delta_rho']:+.3f}"    if not np.isnan(row["delta_rho"])    else "  NaN"
    pf   = f"{row['pval_fisher']:.3e}"   if not np.isnan(row["pval_fisher"])  else "     NA"
    fd   = f"{row['pval_fdr']:.3f}"      if not np.isnan(row.get("pval_fdr", np.nan)) else "  NA"
    ins  = f"R={'Y' if row['in_REF_GRN'] else 'N'} C={'Y' if row['in_Carrier_GRN'] else 'N'}"
    print(f"  {row['TF']:<10} {rr:>7} {rc:>7} {dr:>7}  {pf:>11}  {fd:>6}{flag} {ml} {ins}")

# ── 9. Barplot: REF vs Carrier GRN TF–CCL2 weights ───────────────────────────
# 16 TFs on x → figsize width: 3 + (16-10)/5*0.5 = 3.5; +1.5 for outside legend → 5
print("\n=== STEP 9: Barplot ===")
tf_order = [t for t in TFS_16 if t not in MOTIF_LOSS_TFS] + MOTIF_LOSS_TFS

def get_val(col, tf):
    v = df_comp.loc[df_comp["TF"] == tf, col].values[0]
    return float(v) if not (isinstance(v, float) and np.isnan(v)) else np.nan

rho_r_vals = [get_val("rho_REF", t)     for t in tf_order]
rho_c_vals = [get_val("rho_Carrier", t) for t in tf_order]
in_r       = [bool(df_comp.loc[df_comp["TF"] == t, "in_REF_GRN"].values[0])     for t in tf_order]
in_c       = [bool(df_comp.loc[df_comp["TF"] == t, "in_Carrier_GRN"].values[0]) for t in tf_order]

fig, ax = plt.subplots(figsize=(5.0, 3.0))
x = np.arange(len(tf_order))
w = 0.38

bars1 = ax.bar(x - w / 2, [v if not np.isnan(v) else 0 for v in rho_r_vals], w,
               label=f"GRN_REF (n={n_ref})", color=COL_REF, alpha=0.85)
bars2 = ax.bar(x + w / 2, [v if not np.isnan(v) else 0 for v in rho_c_vals], w,
               label=f"GRN_Carrier (n={n_car})", color=COL_CAR, alpha=0.85)

for bar, present in zip(bars1, in_r):
    if not present:
        bar.set_hatch("///")
        bar.set_alpha(0.35)
for bar, present in zip(bars2, in_c):
    if not present:
        bar.set_hatch("///")
        bar.set_alpha(0.35)

for i, tf in enumerate(tf_order):
    row = df_comp[df_comp["TF"] == tf].iloc[0]
    if row["sig_fdr05"] or row["sig_fdr10"]:
        rr_ = row["rho_REF"]     if not np.isnan(row["rho_REF"])     else 0.0
        rc_ = row["rho_Carrier"] if not np.isnan(row["rho_Carrier"]) else 0.0
        ymax = max(abs(rr_), abs(rc_)) + 0.12
        sign = "**" if row["sig_fdr05"] else "*"
        ax.text(x[i], ymax, sign, ha="center", va="bottom", fontsize=9,
                color="black", clip_on=False)

for idx in [i for i, t in enumerate(tf_order) if t in MOTIF_LOSS_TFS]:
    ax.axvspan(idx - 0.5, idx + 0.5, alpha=0.10, color="orange", zorder=0)
if any(t in MOTIF_LOSS_TFS for t in tf_order):
    ml_start = next(i for i, t in enumerate(tf_order) if t in MOTIF_LOSS_TFS)
    ax.text(ml_start - 0.4, 1.18, "motif-LOSS →", fontsize=9,
            color="darkorange", clip_on=False)

ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(tf_order, rotation=45, ha="right", fontsize=10)
ax.set_ylabel("Spearman ρ  (TF → CCL2)", fontsize=10)
ax.set_title(
    "GRN_REF vs GRN_Carrier — TF–CCL2 edge weight\n"
    "age>60, LPS+RPMI pooled  |  hatched = absent  |  * FDR<0.10  ** FDR<0.05",
    fontsize=10)
ax.set_ylim(-1.1, 1.35)
ax.margins(x=0.03)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(handles=[
    Patch(facecolor=COL_REF, alpha=0.85, label=f"GRN_REF (n={n_ref})"),
    Patch(facecolor=COL_CAR, alpha=0.85, label=f"GRN_Carrier (n={n_car})"),
    Patch(facecolor="gray",  hatch="///", alpha=0.35, label="Edge absent"),
    Patch(facecolor="orange", alpha=0.25, label="Motif-LOSS TFs"),
], fontsize=9, frameon=False, loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
out_bar = f"{BASE}/images/grn_ccl2_comparison.png"
plt.savefig(out_bar, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {out_bar}")

# ── 10. Scatter: REF ρ vs Carrier ρ — moderate-density: annotate candidates only
# figsize: (3,3) + 1.5 for outside legend → (4.5, 3)
print("\n=== STEP 10: Scatter plot ===")

all_ccl2_tfs = sorted(set(ccl2_ref_df.index) | set(ccl2_car_df.index))
srows = []
for tf in all_ccl2_tfs:
    rr = float(ccl2_ref_df.loc[tf, "rho_REF"])     if tf in ccl2_ref_df.index else np.nan
    rc = float(ccl2_car_df.loc[tf, "rho_Carrier"]) if tf in ccl2_car_df.index else np.nan
    srows.append({"TF": tf, "rho_REF": rr, "rho_Carrier": rc,
                  "is_candidate": tf in TFS_16, "motif_loss": tf in MOTIF_LOSS_TFS})
sdf = pd.DataFrame(srows).dropna()

fig, ax = plt.subplots(figsize=(4.5, 3.0))
bg = sdf[~sdf["is_candidate"]]
ax.scatter(bg["rho_REF"], bg["rho_Carrier"], s=8, alpha=0.3, color="gray",
           linewidths=0, label=f"Other TFs (n={len(bg)})")
cand = sdf[sdf["is_candidate"] & ~sdf["motif_loss"]]
ax.scatter(cand["rho_REF"], cand["rho_Carrier"], s=40, alpha=0.85, color=COL_REF,
           linewidths=0, label="Candidate TFs (13)")
ml_pts = sdf[sdf["motif_loss"]]
ax.scatter(ml_pts["rho_REF"], ml_pts["rho_Carrier"], s=55, alpha=0.9,
           color="darkorange", marker="^", linewidths=0, label="Motif-LOSS TFs (3)")

# Moderate density: annotate candidate + motif-loss TFs only, offset away from origin
for _, row in pd.concat([cand, ml_pts]).iterrows():
    ax.annotate(row["TF"], (row["rho_REF"], row["rho_Carrier"]),
                fontsize=9, xytext=(5, 3), textcoords="offset points",
                clip_on=False)

vmin = min(sdf["rho_REF"].min(), sdf["rho_Carrier"].min()) - 0.05
vmax = max(sdf["rho_REF"].max(), sdf["rho_Carrier"].max()) + 0.05
ax.plot([vmin, vmax], [vmin, vmax], color="black", lw=0.8, ls="--", alpha=0.5)
ax.axhline(0, color="gray", lw=0.5, ls=":")
ax.axvline(0, color="gray", lw=0.5, ls=":")
ax.set_xlabel("Spearman ρ (TF→CCL2)  GRN_REF",    fontsize=10)
ax.set_ylabel("Spearman ρ (TF→CCL2)  GRN_Carrier", fontsize=10)
ax.set_title("TF–CCL2 edge weights: REF vs Carrier GRN\n(FDR-sig. edges only)", fontsize=10)
ax.margins(0.05)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
out_sct = f"{BASE}/images/grn_ccl2_scatter.png"
plt.savefig(out_sct, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {out_sct}")

# ── 11. Δρ horizontal barplot (Carrier − REF) ────────────────────────────────
# ~13–16 items on y-axis: figsize (3, 3.5); no outside legend → no width addition
print("\n=== STEP 11: Δρ barplot ===")

df_delta = df_comp.dropna(subset=["delta_rho"]).copy().sort_values("delta_rho")
n_items  = len(df_delta)
fh       = 3.0 + max(0, (n_items - 10) / 5) * 0.5

fig, ax = plt.subplots(figsize=(3.0, fh))
colors = [COL_CAR if v > 0 else COL_REF for v in df_delta["delta_rho"]]
ax.barh(range(n_items), df_delta["delta_rho"].values, color=colors, alpha=0.8)

for i, (_, row) in enumerate(df_delta.iterrows()):
    if row["sig_fdr05"] or row["sig_fdr10"]:
        sign = "**" if row["sig_fdr05"] else "*"
        xpos = row["delta_rho"] + (0.01 if row["delta_rho"] >= 0 else -0.01)
        ha   = "left" if row["delta_rho"] >= 0 else "right"
        ax.text(xpos, i, sign, ha=ha, va="center", fontsize=9,
                color="black", clip_on=False)

ytlabels = [row["TF"] + (" ◆" if row["motif_loss_tf"] else "")
            for _, row in df_delta.iterrows()]
ax.set_yticks(range(n_items))
ax.set_yticklabels(ytlabels, fontsize=10)
for tick, (_, row) in zip(ax.get_yticklabels(), df_delta.iterrows()):
    if row["motif_loss_tf"]:
        tick.set_color("darkorange")

ax.axvline(0, color="black", lw=0.8, ls="--")
ax.set_xlabel("Δρ  (Carrier − REF)  TF→CCL2", fontsize=10)
ax.set_title("Allele effect on TF–CCL2 edge weight\nage>60, LPS+RPMI  |  ◆ motif-LOSS", fontsize=10)
ax.margins(y=0.03)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
out_dr = f"{BASE}/images/grn_delta_rho.png"
plt.savefig(out_dr, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {out_dr}")

# ── 12. Summary ───────────────────────────────────────────────────────────────
print("\n=== SUMMARY ===")
print(f"  GRN_REF:     {len(grn_ref):,} edges  (n={n_ref}: {n_ref_ns} NS + {n_ref_lps} LPS)")
print(f"  GRN_Carrier: {len(grn_car):,} edges  (n={n_car}: {n_car_ns} NS + {n_car_lps} LPS)")
print(f"  Shared edges: {len(shared):,}  |  Jaccard: {jaccard:.4f}")
print(f"  TF–CCL2 edges: REF={len(ccl2_ref_df)}  Carrier={len(ccl2_car_df)}")

sig5  = df_comp[df_comp["sig_fdr05"]]
sig10 = df_comp[df_comp["sig_fdr10"] & ~df_comp["sig_fdr05"]]
if len(sig5):
    print(f"\n  FDR<0.05 TFs:")
    for _, r in sig5.iterrows():
        print(f"    {r['TF']}: Δρ={r['delta_rho']:+.3f}  FDR={r['pval_fdr']:.3f}")
elif len(sig10):
    print(f"\n  FDR<0.10 TFs:")
    for _, r in sig10.iterrows():
        print(f"    {r['TF']}: Δρ={r['delta_rho']:+.3f}  FDR={r['pval_fdr']:.3f}")
else:
    print("  No TF reaches FDR<0.10 in Fisher Z-test")

print("\n=== OUTPUT FILES ===")
print(f"  GRN_REF:           {grn_ref_csv}")
print(f"  GRN_Carrier:       {grn_car_csv}")
print(f"  Global comparison: {BASE}/results/grn_global_comparison.csv")
print(f"  CCL2 comparison:   {BASE}/results/grn_ccl2_comparison.csv")
print(f"  Barplot:           {out_bar}")
print(f"  Scatter:           {out_sct}")
print(f"  Delta-rho:         {out_dr}")
print("\n=== DONE ===")
