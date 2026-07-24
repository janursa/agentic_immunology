"""
Step 4 — SI cohort cQTL + eQTL characterisation of rs11867200 at CCL2 locus.

Outputs:
  temp/nienke/0_SI/results.txt      — formatted table of all QTL results
  temp/nienke/0_SI/images/mcp1_lps_boxplot.pdf  — genotype-stratified MCP-1 LPS 24h boxplot
"""

import os, gzip, glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUTDIR  = "/vol/projects/BIIM/agentic_immunology/temp/nienke/0_SI"
IMGDIR  = os.path.join(OUTDIR, "images")
os.makedirs(IMGDIR, exist_ok=True)

VARIANT       = "rs11867200"
VARIANT_CHR17 = "chr17:34248950:C:T;rs11867200"
CCL_GENES     = {"CCL2", "CCL7", "CCL8", "CCL11"}

CQTL_DIR  = "/vol/projects/CIIM/meta_cQTL/out/SI-senior/cytokines/mapping-chr/main/chr17"

# CCL-cluster cytokines in the SI panel: file-label → (gene_symbol, gene_name)
CCL_PROTEINS = {
    "mcp1":   ("CCL2",  "MCP-1/CCL2"),
    "mcp3":   ("CCL7",  "MCP-3/CCL7"),
    "eotaxin":("CCL11", "Eotaxin/CCL11"),
    "rantes": ("CCL5",  "RANTES/CCL5"),
    "mip1a":  ("CCL3",  "MIP-1α/CCL3"),
    "mip1b":  ("CCL4",  "MIP-1β/CCL4"),
    "ctack":  ("CCL27", "CTACK/CCL27"),
}
EXPR_LPS  = "/vol/projects/CIIM/meta_cQTL/out/SI-senior/expression_24h_lps/mapping/main/chr17"
EXPR_BASE = "/vol/projects/CIIM/meta_cQTL/out/SI-senior/expression/mapping/main/chr17"
EXPR_CPG  = "/vol/projects/CIIM/meta_cQTL/out/SI-senior/expression_24h_cpg/mapping/main/nominal"

TRAW_FILE = "/vol/projects/CIIM/meta_cQTL/out/SI-senior/genotype/traw/chr17.traw"
PHENO_FILE = "/vol/projects/CIIM/meta_cQTL/out/SI-senior/cytokines/phenotype/normalised.tsv"


# ── helpers ──────────────────────────────────────────────────────────────────

def grep_tsv(path, snp_id):
    """Return rows from uncompressed TSV matching snp_id."""
    hits = []
    with open(path) as fh:
        for line in fh:
            if snp_id in line:
                hits.append(line.rstrip("\n").split("\t"))
    return hits

def grep_gz(path, snp_id):
    """Return rows from gzipped TSV matching snp_id."""
    hits = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if snp_id in line:
                hits.append(line.rstrip("\n").split("\t"))
    return hits


# ── SECTION 1: cQTL — all CCL-cluster cytokines, all stimulations ─────────────

print("=== Section 1: cQTL (protein level — CCL cluster) ===")
cqtl_rows = []

for label, (gene_sym, gene_name) in CCL_PROTEINS.items():
    files = sorted(glob.glob(os.path.join(CQTL_DIR, f"pbmc_*_{label}_*.tsv")))
    for fp in files:
        stim_label = os.path.basename(fp).replace("pbmc_", "").replace(".tsv", "")
        rows = grep_tsv(fp, VARIANT)
        for r in rows:
            if len(r) >= 5:
                cqtl_rows.append({
                    "modality":  "cQTL",
                    "condition": stim_label,
                    "gene":      gene_name,
                    "beta":      r[2],
                    "t_stat":    r[3],
                    "p_value":   r[4],
                })

# ── SECTION 2: eQTL — 24h LPS expression ─────────────────────────────────────

print("=== Section 2: eQTL 24h LPS (mRNA) ===")
expr_lps_rows = []
for fp in sorted(glob.glob(os.path.join(EXPR_LPS, "part_*.tsv"))):
    rows = grep_tsv(fp, VARIANT)
    for r in rows:
        if len(r) >= 5 and r[1] in CCL_GENES:
            expr_lps_rows.append({
                "modality":  "eQTL_24h_LPS",
                "condition": "24h_lps_expression",
                "gene":      r[1],
                "beta":      r[2],
                "t_stat":    r[3],
                "p_value":   r[4],
            })

# ── SECTION 3: eQTL — baseline expression ────────────────────────────────────

print("=== Section 3: eQTL baseline (mRNA) ===")
expr_base_rows = []
for fp in sorted(glob.glob(os.path.join(EXPR_BASE, "part_*.tsv"))):
    rows = grep_tsv(fp, VARIANT)
    for r in rows:
        if len(r) >= 5 and r[1] in CCL_GENES:
            expr_base_rows.append({
                "modality":  "eQTL_baseline",
                "condition": "baseline_expression",
                "gene":      r[1],
                "beta":      r[2],
                "t_stat":    r[3],
                "p_value":   r[4],
            })

# ── SECTION 4: eQTL — 24h CPG expression ─────────────────────────────────────

print("=== Section 4: eQTL 24h CPG (mRNA) ===")
expr_cpg_rows = []
cpg_file = os.path.join(EXPR_CPG, "chr17.tsv.gz")
if os.path.exists(cpg_file):
    rows = grep_gz(cpg_file, VARIANT)
    for r in rows:
        if len(r) >= 5 and r[1] in CCL_GENES:
            expr_cpg_rows.append({
                "modality":  "eQTL_24h_CPG",
                "condition": "24h_cpg_expression",
                "gene":      r[1],
                "beta":      r[2],
                "t_stat":    r[3],
                "p_value":   r[4],
            })

# ── SECTION 5: eQTL — 24h CPG expression (gz with .tsv extension fallback) ───

if not expr_cpg_rows:
    cpg_file2 = os.path.join(EXPR_CPG, "chr17.tsv")
    if os.path.exists(cpg_file2):
        rows = grep_tsv(cpg_file2, VARIANT)
        for r in rows:
            if len(r) >= 5 and r[1] in CCL_GENES:
                expr_cpg_rows.append({
                    "modality":  "eQTL_24h_CPG",
                    "condition": "24h_cpg_expression",
                    "gene":      r[1],
                    "beta":      r[2],
                    "t_stat":    r[3],
                    "p_value":   r[4],
                })

# ── Compile and write results table ──────────────────────────────────────────

all_rows = cqtl_rows + expr_lps_rows + expr_base_rows + expr_cpg_rows
df = pd.DataFrame(all_rows, columns=["modality", "condition", "gene", "beta", "t_stat", "p_value"])

results_path = os.path.join(OUTDIR, "results.txt")
with open(results_path, "w") as fh:
    fh.write(f"# rs11867200 — SI cohort cQTL + eQTL results\n")
    fh.write(f"# Columns: modality | condition | gene | beta | t_stat | p_value\n\n")

    fh.write("## cQTL (protein level — CCL cluster)\n")
    for _, row in df[df.modality == "cQTL"].iterrows():
        fh.write(f"{row.modality}\t{row.condition}\t{row.gene}\t{row.beta}\t{row.t_stat}\t{row.p_value}\n")

    fh.write("\n## eQTL 24h LPS (mRNA)\n")
    for _, row in df[df.modality == "eQTL_24h_LPS"].iterrows():
        fh.write(f"{row.modality}\t{row.condition}\t{row.gene}\t{row.beta}\t{row.t_stat}\t{row.p_value}\n")

    fh.write("\n## eQTL 24h CPG (mRNA)\n")
    for _, row in df[df.modality == "eQTL_24h_CPG"].iterrows():
        fh.write(f"{row.modality}\t{row.condition}\t{row.gene}\t{row.beta}\t{row.t_stat}\t{row.p_value}\n")

    fh.write("\n## eQTL baseline (mRNA)\n")
    for _, row in df[df.modality == "eQTL_baseline"].iterrows():
        fh.write(f"{row.modality}\t{row.condition}\t{row.gene}\t{row.beta}\t{row.t_stat}\t{row.p_value}\n")

print(f"Results written: {results_path}")
print(df.to_string(index=False))


# ── SECTION 6: genotype-stratified MCP-1 LPS boxplot ─────────────────────────

print("\n=== Section 6: MCP-1 LPS boxplot ===")

# Load traw — strip "0_0_" prefix from sample IDs
traw = pd.read_csv(TRAW_FILE, sep="\t")
snp_row = traw[traw["SNP"].str.contains(VARIANT, na=False)]
if snp_row.empty:
    print("WARNING: variant not found in traw — skipping boxplot")
else:
    snp_row = snp_row.iloc[0]
    # Sample columns start after column index 5 (CHR, SNP, (C)M, POS, COUNTED, ALT)
    sample_cols = traw.columns[6:]
    dosage = snp_row[sample_cols].astype(float)
    # Strip "0_0_" prefix
    sample_ids = [c.replace("0_0_", "") for c in sample_cols]
    dosage.index = sample_ids

    # COUNTED allele in traw = T (alt), so dosage = number of T alleles
    counted = snp_row["COUNTED"]   # T
    alt     = snp_row["ALT"]       # C
    print(f"  COUNTED (effect) allele: {counted}  |  ALT: {alt}")

    # Map dosage → genotype label: 0=CC, 1=CT, 2=TT
    def dos_to_gt(d):
        d_round = round(d)
        if d_round == 0:
            return f"{alt}{alt}"
        elif d_round == 1:
            return f"{alt}{counted}"
        else:
            return f"{counted}{counted}"

    gt_series = dosage.map(dos_to_gt)

    # Load normalised phenotype
    pheno = pd.read_csv(PHENO_FILE, sep="\t", index_col=0)
    if "pbmc_24h_mcp1_lps" not in pheno.index:
        print("WARNING: pbmc_24h_mcp1_lps not in phenotype — skipping boxplot")
    else:
        mcp1_lps = pheno.loc["pbmc_24h_mcp1_lps"]
        mcp1_lps.index = [str(i) for i in mcp1_lps.index]

        # Align samples
        common = list(set(sample_ids) & set(mcp1_lps.index))
        print(f"  Common samples: {len(common)}")
        gt_aligned = gt_series[common]
        ph_aligned = mcp1_lps[common].astype(float)

        plot_df = pd.DataFrame({"genotype": gt_aligned, "mcp1_lps": ph_aligned})
        gt_order = ["CC", "CT", "TT"]
        gt_present = [g for g in gt_order if g in plot_df.genotype.values]
        groups = [plot_df.loc[plot_df.genotype == g, "mcp1_lps"].dropna().values for g in gt_present]
        counts = [len(g) for g in groups]

        # colours: light→dark blue for 0,1,2 T copies
        colours = ["#9ecae1", "#3182bd", "#08306b"][:len(gt_present)]

        fig, ax = plt.subplots(figsize=(4.5, 5))
        bp = ax.boxplot(groups, patch_artist=True, widths=0.5,
                        medianprops=dict(color="white", linewidth=2),
                        whiskerprops=dict(color="#444"),
                        capprops=dict(color="#444"),
                        flierprops=dict(marker="o", markersize=3, alpha=0.5, markerfacecolor="#999"))

        for patch, col in zip(bp["boxes"], colours):
            patch.set_facecolor(col)

        ax.set_xticks(range(1, len(gt_present)+1))
        ax.set_xticklabels([f"{g}\n(n={n})" for g, n in zip(gt_present, counts)], fontsize=10)
        ax.set_ylabel("Normalised MCP-1 level\n(24h LPS)", fontsize=11)
        ax.set_title(f"rs11867200 genotype vs MCP-1 (LPS 24h)\nSI cohort — β=−0.354, p=4.4×10⁻⁹", fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plot_path = os.path.join(IMGDIR, "mcp1_lps_boxplot.pdf")
        fig.tight_layout()
        fig.savefig(plot_path, bbox_inches="tight")
        plt.close()
        print(f"Boxplot saved: {plot_path}")

print("\nDone.")
