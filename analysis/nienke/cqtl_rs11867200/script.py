"""
Question: SI cohort cQTL results around rs11867200. Show variants in the window
with significant associations, specifically associated with CCL2.

rs11867200 = chr17:34,248,950 (C>T)
CCL2 = MCP-1 = pbmc_24h_mcp1_lps
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
TEMP  = Path("/vol/projects/BIIM/agentic_immunology/temp/cqtl_rs11867200")
IMGS  = TEMP / "images"
IMGS.mkdir(exist_ok=True)

NOMINAL_ALL  = Path("/vol/projects/CIIM/meta_cQTL/out/SI-senior/cytokines/mapping/main_nominal.tsv")
GW_SIG       = Path("/vol/projects/CIIM/meta_cQTL/out/SI-senior/cytokines/mapping/main_genomewide.tsv")

LEAD_SNP = "rs11867200"
CHR      = "chr17"
POS_LEAD = 34_248_950
WIN      = 500_000          # ±500 kb display window
POS_LO   = POS_LEAD - WIN
POS_HI   = POS_LEAD + WIN
GW_TRESH = 5e-8

FONT = {"fontname": "Arial", "fontsize": 10}
FONT_SMALL = {"fontname": "Arial", "fontsize": 9}

# ── Helper ─────────────────────────────────────────────────────────────────────
def parse_pos(snp):
    """chr17:34248950:C:T;rs11867200 → 34248950"""
    return int(snp.split(":")[1])

def parse_rsid(snp):
    parts = snp.split(";")
    return parts[1] if len(parts) > 1 else snp

# ── Load nominal (chr17 window only) ──────────────────────────────────────────
print("Loading nominal associations …")
chunks = []
for chunk in pd.read_csv(NOMINAL_ALL, sep="\t", chunksize=500_000):
    c = chunk[chunk["SNP"].str.startswith(f"{CHR}:")].copy()
    c["pos"] = c["SNP"].apply(parse_pos)
    c = c[(c["pos"] >= POS_LO) & (c["pos"] <= POS_HI)]
    if len(c):
        chunks.append(c)
df_nom = pd.concat(chunks, ignore_index=True)
df_nom["rsid"] = df_nom["SNP"].apply(parse_rsid)
df_nom["neglog10p"] = -np.log10(df_nom["p-value"])
print(f"  {len(df_nom):,} associations, {df_nom['SNP'].nunique():,} variants, "
      f"{df_nom['gene'].nunique()} cytokines")

# ── Load genome-wide sig (chr17 window) ───────────────────────────────────────
df_gw = pd.read_csv(GW_SIG, sep="\t")
df_gw["pos"] = df_gw["SNP"].apply(parse_pos)
df_gw["rsid"] = df_gw["SNP"].apply(parse_rsid)
df_gw = df_gw[
    df_gw["SNP"].str.startswith(f"{CHR}:") &
    (df_gw["pos"] >= POS_LO) &
    (df_gw["pos"] <= POS_HI)
].copy()
df_gw["neglog10p"] = -np.log10(df_gw["p-value"])
print(f"  {len(df_gw)} genome-wide sig hits in window")
print(df_gw[["rsid","gene","p-value","pos"]].to_string(index=False))

# ── Subset: CCL2 (mcp1_lps) associations ─────────────────────────────────────
df_ccl2 = df_nom[df_nom["gene"] == "pbmc_24h_mcp1_lps"].copy()
df_ccl2_gw = df_gw[df_gw["gene"] == "pbmc_24h_mcp1_lps"].copy()
print(f"\nCCL2 (mcp1_lps): {len(df_ccl2):,} variants in window, "
      f"{len(df_ccl2_gw)} genome-wide sig")

# ── rs11867200 rows ───────────────────────────────────────────────────────────
df_lead_all = df_nom[df_nom["rsid"] == LEAD_SNP].sort_values("p-value")
print(f"\nAll associations for {LEAD_SNP}:")
print(df_lead_all[["gene","beta","p-value"]].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Regional association plot: CCL2 (MCP-1 LPS 24h)
# Shows all variants in ±500kb window, colour-codes genome-wide sig
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(5.5, 3.5))

# All variants: grey background
ax.scatter(
    df_ccl2["pos"] / 1e6,
    df_ccl2["neglog10p"],
    color="#BDBDBD", s=18, alpha=0.7, linewidths=0, zorder=2, label="All variants"
)

# Genome-wide sig (not lead): teal
gw_not_lead = df_ccl2_gw[df_ccl2_gw["rsid"] != LEAD_SNP]
if len(gw_not_lead):
    ax.scatter(
        gw_not_lead["pos"] / 1e6,
        gw_not_lead["neglog10p"],
        color="#1B7837", s=35, alpha=0.9, linewidths=0, zorder=3,
        label=f"Genome-wide sig (p<5×10⁻⁸)"
    )

# Lead SNP: red star
lead_row = df_ccl2[df_ccl2["rsid"] == LEAD_SNP]
if len(lead_row):
    ax.scatter(
        lead_row["pos"] / 1e6,
        lead_row["neglog10p"],
        color="#D62728", s=100, marker="*", zorder=5, label=LEAD_SNP
    )
    ax.annotate(
        LEAD_SNP,
        xy=(lead_row["pos"].values[0] / 1e6, lead_row["neglog10p"].values[0]),
        xytext=(8, 4), textcoords="offset points",
        fontsize=9, fontname="Arial", color="#D62728",
        arrowprops=dict(arrowstyle="->", color="#D62728", lw=0.8),
        clip_on=False
    )

# Genome-wide significance line
gw_line = -np.log10(GW_TRESH)
ax.axhline(gw_line, color="#666666", lw=0.9, ls="--", zorder=1)
ax.text(
    POS_LO / 1e6 + 0.01, gw_line + 0.15,
    "p = 5×10⁻⁸", **FONT_SMALL, color="#666666"
)

# Styling
ax.set_xlabel("Chromosome 17 position (Mb)", **FONT)
ax.set_ylabel("–log₁₀(p)", **FONT)
ax.set_title("CCL2 (MCP-1 LPS 24 h) cQTL — SI cohort", **FONT)
ax.tick_params(labelsize=10)
for t in ax.get_xticklabels():
    t.set_fontname("Arial")
for t in ax.get_yticklabels():
    t.set_fontname("Arial")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.margins(x=0.03)

leg = ax.legend(
    frameon=False, fontsize=9,
    loc="upper left", bbox_to_anchor=(1, 1),
    prop={"family": "Arial", "size": 9}
)

plt.tight_layout()
out1 = IMGS / "fig1_ccl2_regional_plot.png"
fig.savefig(out1, dpi=200, bbox_inches="tight")
plt.close()
print(f"\nSaved: {out1}")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — All cytokine associations for rs11867200 (sorted by -log10p)
#   dot plot: y = cytokine, x = -log10(p), coloured by direction (beta sign)
# ══════════════════════════════════════════════════════════════════════════════
df_lead_all = df_lead_all.copy()
df_lead_all["neglog10p"] = -np.log10(df_lead_all["p-value"])

# Annotate significance tier
def sig_tier(p):
    if p < GW_TRESH:
        return "Genome-wide (p<5×10⁻⁸)"
    elif p < 1e-4:
        return "Nominal (p<10⁻⁴)"
    elif p < 0.01:
        return "Nominal (p<0.01)"
    else:
        return "Nominal (p<0.05)"

df_lead_all["tier"] = df_lead_all["p-value"].apply(sig_tier)

tier_colors = {
    "Genome-wide (p<5×10⁻⁸)": "#D62728",
    "Nominal (p<10⁻⁴)":        "#FF7F0E",
    "Nominal (p<0.01)":        "#1F77B4",
    "Nominal (p<0.05)":        "#BDBDBD",
}

# Clean cytokine labels
def fmt_gene(g):
    return g.replace("pbmc_24h_", "").replace("pbmc_7d_", "7d_").replace("_", " ")

df_lead_all["label"] = df_lead_all["gene"].apply(fmt_gene)
df_lead_all = df_lead_all.sort_values("neglog10p", ascending=True)

n = len(df_lead_all)
# figsize: base 3x3, add 0.5 per 2 extra items beyond 5
h = 3 + max(0, (n - 5) / 2 * 0.5)

fig2, ax2 = plt.subplots(figsize=(5.5, h))

for _, row in df_lead_all.iterrows():
    color = tier_colors[row["tier"]]
    marker = "^" if row["beta"] > 0 else "v"
    ax2.scatter(row["neglog10p"], row["label"], color=color,
                s=55, marker=marker, zorder=3)

# significance lines
ax2.axvline(-np.log10(GW_TRESH), color="#D62728", lw=0.9, ls="--", alpha=0.8)
ax2.axvline(-np.log10(1e-4),     color="#FF7F0E", lw=0.9, ls=":",  alpha=0.8)
ax2.axvline(-np.log10(0.05),     color="#BDBDBD", lw=0.9, ls=":",  alpha=0.6)

ax2.set_xlabel("–log₁₀(p)", **FONT)
ax2.set_ylabel("Cytokine phenotype", **FONT)
ax2.set_title(f"All associations for {LEAD_SNP}", **FONT)
ax2.tick_params(labelsize=10)
for t in ax2.get_xticklabels():
    t.set_fontname("Arial")
for t in ax2.get_yticklabels():
    t.set_fontname("Arial")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.margins(y=0.05)

# Legend: tiers + direction
tier_handles = [
    mpatches.Patch(color=c, label=t)
    for t, c in tier_colors.items()
    if t in df_lead_all["tier"].values
]
dir_handles = [
    plt.Line2D([0], [0], marker="^", color="gray", ls="none",
               markersize=7, label="Positive β"),
    plt.Line2D([0], [0], marker="v", color="gray", ls="none",
               markersize=7, label="Negative β"),
]
ax2.legend(
    handles=tier_handles + dir_handles,
    frameon=False, fontsize=9,
    loc="upper left", bbox_to_anchor=(1, 1),
    prop={"family": "Arial", "size": 9}
)

plt.tight_layout()
out2 = IMGS / "fig2_rs11867200_all_cytokines.png"
fig2.savefig(out2, dpi=200, bbox_inches="tight")
plt.close()
print(f"Saved: {out2}")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — CCL2 across all MCP-1 stimulation conditions at rs11867200
# ══════════════════════════════════════════════════════════════════════════════
df_mcp1_lead = df_lead_all[df_lead_all["gene"].str.contains("mcp1")].copy()
df_mcp1_lead["label"] = df_mcp1_lead["gene"].apply(fmt_gene)
df_mcp1_lead = df_mcp1_lead.sort_values("neglog10p", ascending=False)

fig3, ax3 = plt.subplots(figsize=(3.5, 3))
colors_stim = ["#D62728" if p < GW_TRESH else "#1F77B4" for p in df_mcp1_lead["p-value"]]
bars = ax3.barh(df_mcp1_lead["label"], df_mcp1_lead["neglog10p"],
                color=colors_stim, alpha=0.85)
ax3.axvline(-np.log10(GW_TRESH), color="#666666", lw=0.9, ls="--")
ax3.set_xlabel("–log₁₀(p)", **FONT)
ax3.set_title(f"MCP-1 (CCL2) stimulations\n{LEAD_SNP}", **FONT)
ax3.tick_params(labelsize=10)
for t in ax3.get_xticklabels():
    t.set_fontname("Arial")
for t in ax3.get_yticklabels():
    t.set_fontname("Arial")
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.margins(y=0.1)
ax3.text(
    -np.log10(GW_TRESH) + 0.05, ax3.get_ylim()[0] + 0.1,
    "GW sig", fontsize=9, fontname="Arial", color="#666666", va="bottom"
)

plt.tight_layout()
out3 = IMGS / "fig3_ccl2_stimulations.png"
fig3.savefig(out3, dpi=200, bbox_inches="tight")
plt.close()
print(f"Saved: {out3}")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Locus overview: genome-wide sig variants, all cytokines in window
#   Show how many gw-sig associations each cytokine has in the window
# ══════════════════════════════════════════════════════════════════════════════
df_gw_all_window = df_nom[df_nom["p-value"] < GW_TRESH].copy()
gw_counts = (
    df_gw_all_window.groupby("gene")["SNP"]
    .nunique()
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={"SNP": "n_gw_variants"})
)
gw_counts["label"] = gw_counts["gene"].apply(fmt_gene)
print(f"\nCytokines with genome-wide sig hits in window:\n{gw_counts.to_string(index=False)}")

if len(gw_counts) > 0:
    n_gw = len(gw_counts)
    h4 = 3 + max(0, (n_gw - 5) / 2 * 0.5)
    fig4, ax4 = plt.subplots(figsize=(3.5, max(3, h4)))
    ax4.barh(gw_counts["label"], gw_counts["n_gw_variants"], color="#1B7837", alpha=0.85)
    ax4.set_xlabel("N genome-wide sig variants", **FONT)
    ax4.set_title("GW-sig variants in ±500 kb\naround rs11867200", **FONT)
    ax4.tick_params(labelsize=10)
    for t in ax4.get_xticklabels():
        t.set_fontname("Arial")
    for t in ax4.get_yticklabels():
        t.set_fontname("Arial")
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)
    ax4.margins(y=0.1)
    plt.tight_layout()
    out4 = IMGS / "fig4_gw_sig_per_cytokine.png"
    fig4.savefig(out4, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out4}")

print("\nDone.")
