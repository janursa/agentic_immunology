"""
Extension of cqtl_rs11867200 analysis.

Question: rs11867200 has no GWAS annotation despite being the lead CCL2 cQTL.
Are nearby GWAS-annotated variants in LD with rs11867200?
Do they also show CCL2 cQTL signal? Is rs11867200 truly the lead, or a proxy?

Approach:
  - CCL2 cQTL p-values for all variants (GW-sig + GWAS-nearby) from SI cohort
  - LD r2 computed from 1000G EUR (GRCh37)
  - GWAS annotations from regional GWAS Catalog query
  - LocusZoom-style plot with LD colour-coding + GWAS labels
  - LD r2 bar chart + dual-signal comparison panel
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Global plot style ──────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":   "Arial",
    "font.size":     10,
    "axes.labelsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.titlesize": 10,
})

# ── Paths ──────────────────────────────────────────────────────────────────────
WORK  = Path("/vol/projects/BIIM/agentic_immunology/temp/cqtl_rs11867200")
IMGS  = WORK / "images"
IMGS.mkdir(exist_ok=True)

BIM = Path("/vol/projects/BIIM/agentic_immunology/datalake/gwas/1kg/EUR.bim")
BED = Path("/vol/projects/BIIM/agentic_immunology/datalake/gwas/1kg/EUR.bed")
FAM = Path("/vol/projects/BIIM/agentic_immunology/datalake/gwas/1kg/EUR.fam")

NOMINAL  = WORK / "regional_nominal.tsv"
GW_SIG   = Path("/vol/projects/CIIM/meta_cQTL/out/SI-senior/cytokines/mapping/main_genomewide.tsv")
GWAS_CSV = Path("/vol/projects/BIIM/agentic_immunology/temp/nienke/step4_phewas/gwascatalog_regional_all.csv")

LEAD_SNP  = "rs11867200"
GW_THRESH = 5e-8

# ── 1. Target variants ────────────────────────────────────────────────────────
GW_SIG_RSIDS = [
    "rs9916162", "rs9903934", "rs9911144", "rs1024613", "rs7215001",
    "rs9891243", "rs7218453", "rs7216532", "rs35006836", "rs9915488",
    "rs9909465", "rs143613963", "rs12946932", "rs9906695", "rs11655679",
    "rs17652000", "rs67586205", "rs17652139", "rs11868941", "rs35062913",
    "rs113274498", "rs17652343", "rs56389898", "rs11867200",
    "rs3760396", "rs4795889", "rs3091317",
]
GWAS_RSIDS = [
    "rs9889296",   # IBD p=5e-21, 5.4 kb upstream
    "rs6505402",   # protein QTL, 1.7 kb upstream
    "rs4795893",   # protein QTL, 1.5 kb upstream
    "rs2857656",   # IBD/Crohn's, 6 kb downstream
    "rs3091315",   # IBD p=8e-25, 17.7 kb downstream
    "rs3091316",   # IBD p=1e-26, 18 kb downstream
    "rs7218453",   # monocyte % p=3e-25, also GW-sig cQTL
    "rs9909465",   # monocyte count p=9e-24, also GW-sig cQTL
    "rs9906695",   # monocyte % p=3e-11, also GW-sig cQTL
    "rs9891243",   # monocyte count p=3e-14, also GW-sig cQTL
    "rs9911144",   # monocyte count p=1e-24, also GW-sig cQTL
    "rs12601658",  # CCL2/CCL7/CCL8 protein QTL, 42.5 kb upstream
]
ALL_RSIDS = list(dict.fromkeys(GW_SIG_RSIDS + GWAS_RSIDS))

print(f"Target variants: {len(ALL_RSIDS)} total")

# ── 2. Load CCL2 cQTL data ───────────────────────────────────────────────────
print("\n[1] Loading CCL2 cQTL data...")

def extract_rsid(snp_str):
    parts = str(snp_str).split(";")
    return parts[1] if len(parts) > 1 else None

def extract_pos38(snp_str):
    return int(str(snp_str).split(":")[1])

df_gw = pd.read_csv(GW_SIG, sep="\t")
df_gw["rsid"]  = df_gw["SNP"].apply(extract_rsid)
df_gw_ccl2     = df_gw[df_gw["gene"] == "pbmc_24h_mcp1_lps"].copy()
df_gw_ccl2["pos38"] = df_gw_ccl2["SNP"].apply(extract_pos38)

df_nom = pd.read_csv(NOMINAL, sep="\t")
df_nom["rsid"]  = df_nom["SNP"].apply(extract_rsid)
df_nom_ccl2     = df_nom[df_nom["gene"] == "pbmc_24h_mcp1_lps"].copy()
df_nom_ccl2["pos38"] = df_nom_ccl2["SNP"].apply(extract_pos38)

cqtl = {}
for rsid in ALL_RSIDS:
    gw_rows  = df_gw_ccl2[df_gw_ccl2["rsid"] == rsid]
    nom_rows = df_nom_ccl2[df_nom_ccl2["rsid"] == rsid]
    if len(gw_rows):
        r = gw_rows.iloc[0]
        cqtl[rsid] = {"beta": r["beta"], "pval": r["p-value"],
                      "pos38": r["pos38"], "source": "gw_sig"}
    elif len(nom_rows):
        r = nom_rows.iloc[0]
        cqtl[rsid] = {"beta": r["beta"], "pval": r["p-value"],
                      "pos38": r["pos38"], "source": "nominal"}
    else:
        cqtl[rsid] = {"beta": np.nan, "pval": np.nan,
                      "pos38": np.nan, "source": "not_found"}

found = sum(1 for v in cqtl.values() if not np.isnan(v["pval"]))
print(f"  cQTL data found for {found}/{len(ALL_RSIDS)} variants")

# ── 3. LD computation from 1000G EUR (GRCh37) ────────────────────────────────
print("\n[2] Computing LD from 1000G EUR...")

bim = pd.read_csv(BIM, sep="\t", header=None,
                  names=["chrom", "snp", "cm", "pos37", "a1", "a2"])
n_samples     = sum(1 for _ in open(FAM))
n_bytes_per_snp = (n_samples + 3) // 4
print(f"  {n_samples} EUR samples, {n_bytes_per_snp} bytes/SNP")

def read_bed_snp(snp_global_idx):
    """Minor allele dosage (0/1/2, NaN=missing) for one SNP from bed file."""
    with open(BED, "rb") as f:
        magic = f.read(3)
        assert magic == b"\x6c\x1b\x01", "Invalid plink bed magic"
        f.seek(3 + snp_global_idx * n_bytes_per_snp)
        raw = np.frombuffer(f.read(n_bytes_per_snp), dtype=np.uint8)
    bits = np.unpackbits(raw, bitorder="little")
    bit0 = bits[0::2][:n_samples]
    bit1 = bits[1::2][:n_samples]
    # plink: 00=hom_a1(minor), 01=missing, 10=het, 11=hom_a2(major)
    g = np.full(n_samples, np.nan)
    g[(bit0 == 0) & (bit1 == 0)] = 2
    g[(bit0 == 0) & (bit1 == 1)] = 1
    g[(bit0 == 1) & (bit1 == 1)] = 0
    return g

bim_lookup = bim[bim["snp"].isin(ALL_RSIDS)].copy()
print(f"  Found {len(bim_lookup)} target variants in EUR.bim")

geno = {}
for _, row in bim_lookup.iterrows():
    rsid       = row["snp"]
    global_idx = bim.index.get_loc(bim.index[bim["snp"] == rsid][0])
    g          = read_bed_snp(global_idx)
    maf        = min(np.nanmean(g) / 2, 1 - np.nanmean(g) / 2)
    geno[rsid] = g
    print(f"    {rsid}: pos37={row['pos37']}, a1={row['a1']}, a2={row['a2']}, "
          f"MAF={maf:.3f}, n_missing={np.isnan(g).sum()}")

lead_g = geno.get(LEAD_SNP)
ld_r2, ld_r = {}, {}
if lead_g is not None:
    lead_valid = ~np.isnan(lead_g)
    for rsid, g in geno.items():
        valid = lead_valid & ~np.isnan(g)
        if valid.sum() < 50:
            ld_r2[rsid] = np.nan; ld_r[rsid] = np.nan
            continue
        r = np.corrcoef(lead_g[valid], g[valid])[0, 1]
        ld_r2[rsid] = r ** 2
        ld_r[rsid]  = r

print(f"\n  LD r2 to {LEAD_SNP}:")
for rsid in sorted(ld_r2, key=lambda x: -(ld_r2[x] or 0)):
    print(f"    {rsid}: r2={ld_r2[rsid]:.3f}  r={ld_r.get(rsid, np.nan):.3f}")

# ── 4. Load GWAS Catalog annotations ─────────────────────────────────────────
print("\n[3] Loading GWAS Catalog annotations...")
df_gwas = pd.read_csv(GWAS_CSV)
gwas_best = (
    df_gwas.sort_values("P-VALUE")
    .drop_duplicates("SNPS")
    .set_index("SNPS")[["DISEASE/TRAIT", "P-VALUE", "FIRST AUTHOR", "category"]]
)

# ── 5. Build merged summary table ────────────────────────────────────────────
print("\n[4] Building merged table...")
rows = []
for rsid in ALL_RSIDS:
    c   = cqtl[rsid]
    row = {
        "rsid":        rsid,
        "pos38":       c["pos38"],
        "cqtl_beta":   c["beta"],
        "cqtl_pval":   c["pval"],
        "cqtl_nlp":    -np.log10(c["pval"]) if not np.isnan(c["pval"]) else np.nan,
        "cqtl_source": c["source"],
        "in_gw_sig":   c["source"] == "gw_sig",
        "ld_r2":       ld_r2.get(rsid, np.nan),
        "ld_r":        ld_r.get(rsid, np.nan),
        "in_gwas":     rsid in GWAS_RSIDS,
    }
    if rsid in gwas_best.index:
        g = gwas_best.loc[rsid]
        row["gwas_trait"]    = g["DISEASE/TRAIT"]
        row["gwas_pval"]     = g["P-VALUE"]
        row["gwas_category"] = g["category"]
    else:
        row["gwas_trait"]    = None
        row["gwas_pval"]     = np.nan
        row["gwas_category"] = None
    rows.append(row)

df_tab = pd.DataFrame(rows).sort_values("pos38")
df_tab.to_csv(WORK / "gwas_ld_cqtl_table.csv", index=False)

key = df_tab[df_tab["rsid"].isin(GWAS_RSIDS + [LEAD_SNP])].copy()
print("\nKey variants — CCL2 cQTL + LD + GWAS:")
print(key[["rsid","pos38","cqtl_beta","cqtl_pval","ld_r2",
           "gwas_trait","gwas_pval"]].to_string(index=False))

# ── LD colour helper ──────────────────────────────────────────────────────────
def ld_color(r2):
    if np.isnan(r2): return "#BDBDBD"
    if r2 >= 0.8:    return "#D62728"
    if r2 >= 0.6:    return "#FF7F0E"
    if r2 >= 0.4:    return "#1F77B4"
    if r2 >= 0.2:    return "#AEC7E8"
    return "#BDBDBD"

# ── 6. FIGURE 5 — LocusZoom-style: CCL2 cQTL + LD + GWAS annotation ─────────
# figsize: scatter (like barplot geometry): base (3,3), +1.5 for external legend
# x-span ~170 kb → wider; use (5+1.5, 3.5) = (6.5, 3.5)
print("\n[5] Plotting Fig 5 – LocusZoom...")

bg_mask = (df_nom_ccl2["pos38"] >= 34_140_000) & (df_nom_ccl2["pos38"] <= 34_320_000)
df_bg   = df_nom_ccl2[bg_mask].copy()
df_bg["nlp"] = -np.log10(df_bg["p-value"])

fig, ax = plt.subplots(figsize=(6.5, 3.5))

# Grey background: all nominal CCL2 variants
ax.scatter(df_bg["pos38"] / 1e6, df_bg["nlp"],
           color="#E0E0E0", s=12, alpha=0.6, linewidths=0, zorder=1)

# Foreground: variants with known LD
df_fg = df_tab.dropna(subset=["pos38", "cqtl_nlp"]).copy()
for _, row in df_fg.iterrows():
    rsid = row["rsid"]
    col  = ld_color(row["ld_r2"])
    mk   = "*" if rsid == LEAD_SNP else ("D" if row["in_gwas"] and not row["in_gw_sig"] else "o")
    sz   = 80 if rsid == LEAD_SNP else (40 if mk == "D" else 28)
    ax.scatter(row["pos38"] / 1e6, row["cqtl_nlp"],
               color=col, s=sz, marker=mk, zorder=4,
               edgecolors="k" if mk in ("*", "D") else "none",
               linewidths=0.5)

# Annotate only the 5 most biologically important variants (sparse regions)
# Lead cQTL + top IBD variants; use arrows and offsets to avoid overlap
# Dots are moderately dense in the 34.19-34.27 Mb cluster; annotate outside cluster
annotate = {
    LEAD_SNP:   {"xytext": (0,  10), "ha": "center"},
    "rs9889296":{"xytext": (-25, 8), "ha": "right"},
    "rs3091315":{"xytext": (10,  8), "ha": "left"},
    "rs2857656":{"xytext": (18, -12),"ha": "left"},
    "rs7218453":{"xytext": (-25,-10),"ha": "right"},
}
for rsid, opts in annotate.items():
    row = df_tab[df_tab["rsid"] == rsid]
    if len(row) == 0 or np.isnan(row.iloc[0]["cqtl_nlp"]): continue
    r = row.iloc[0]
    ax.annotate(
        rsid,
        xy=(r["pos38"] / 1e6, r["cqtl_nlp"]),
        xytext=opts["xytext"], textcoords="offset points",
        fontsize=9, ha=opts["ha"],
        arrowprops=dict(arrowstyle="->", color="gray", lw=0.8),
        clip_on=False,
    )

# GW significance line
gw_y = -np.log10(GW_THRESH)
ax.axhline(gw_y, color="#555555", lw=0.8, ls="--", zorder=2)
ax.text(34.145, gw_y + 0.2, "p=5×10⁻⁸",
        fontsize=9, color="#555555")

ax.set_xlabel("Chromosome 17 position (Mb)")
ax.set_ylabel("-log₁₀(p) CCL2 cQTL")
ax.set_title("CCL2 (MCP-1 LPS 24h) cQTL locus — colour = LD r² to rs11867200 (1000G EUR)")
ax.set_xlim(34.14, 34.31)
ax.margins(y=0.08)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ld_handles = [
    mpatches.Patch(color="#D62728", label="r² ≥ 0.8"),
    mpatches.Patch(color="#FF7F0E", label="0.6 – 0.8"),
    mpatches.Patch(color="#1F77B4", label="0.4 – 0.6"),
    mpatches.Patch(color="#AEC7E8", label="0.2 – 0.4"),
    mpatches.Patch(color="#BDBDBD", label="< 0.2 / NA"),
]
mk_handles = [
    plt.Line2D([0],[0], marker="*", color="#444", ls="none", markersize=9,
               label="Lead cQTL"),
    plt.Line2D([0],[0], marker="D", color="#444", ls="none", markersize=6,
               label="GWAS-annotated (nominal cQTL)"),
    plt.Line2D([0],[0], marker="o", color="#444", ls="none", markersize=6,
               label="GW-sig cQTL"),
]
ax.legend(handles=ld_handles + mk_handles, frameon=False, fontsize=9,
          loc="upper left", bbox_to_anchor=(1, 1))

plt.tight_layout()
out5 = IMGS / "fig5_locuszoom_ld_gwas.png"
fig.savefig(out5, dpi=200, bbox_inches="tight")
plt.close()
print(f"Saved: {out5}")

# ── 7. FIGURE 6 — Dual-panel: CCL2 cQTL signal vs. GWAS signal per variant ──
# 2 horizontal panels sharing the y (variant) axis
# ~12 GWAS variants → barplot height: base 3 + (12-10)/5*0.5 = 3.2
# Width: 2 panels × 3 − 1 (shared axis reduction) + 1.5 (external legend) = 6.5
print("\n[6] Plotting Fig 6 – dual cQTL/GWAS panel...")

gwas_cqtl = df_tab[df_tab["in_gwas"] & ~df_tab["cqtl_pval"].isna()].copy()
gwas_cqtl = gwas_cqtl.sort_values("pos38").reset_index(drop=True)
n = len(gwas_cqtl)
h = 3 + max(0, (n - 10) / 5 * 0.5)

def short_trait(t):
    if pd.isna(t): return "no GWAS"
    mapping = {
        "inflammatory bowel disease":                                "IBD",
        "crohn's disease":                                           "Crohn's",
        "monocyte count":                                            "Mono count",
        "monocyte percentage of white cells":                        "Mono %",
        "serum levels of protein ccl8":                              "pQTL CCL8",
        "c-c motif chemokine 7 levels":                              "pQTL CCL7",
        "monocyte chemoattractant protein-1 levels":                 "pQTL CCL2",
        "corneodesmosin levels":                                     "pQTL CDSN",
        "granulocyte percentage of myeloid white cells":             "Gran %",
        "b-cell lymphoblastic leukemia or crohn's disease (pleiotropy)": "ALL/Crohn's",
        "chronic inflammatory diseases (ankylosing spondylitis, crohn's disease, psoriasis, primary sclerosing cholangitis, ulcerative colitis) (pleiotropy)": "Cross-inflam.",
    }
    return mapping.get(str(t).lower(), str(t)[:20])

gwas_cqtl["trait_label"] = gwas_cqtl["gwas_trait"].apply(short_trait)
gwas_cqtl["y_label"]     = gwas_cqtl.apply(
    lambda r: f"{r['rsid']}  ({r['trait_label']})", axis=1)
gwas_cqtl["gwas_nlp"]    = -np.log10(gwas_cqtl["gwas_pval"].clip(lower=1e-310))

cat_colors = {
    "IBD / Crohn's disease":   "#D62728",
    "Blood cell traits":       "#1F77B4",
    "Protein/biomarker QTL":   "#FF7F0E",
    "Other":                   "#7F7F7F",
}

fig2, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(6.5, h), sharey=True)

# Panel A — CCL2 cQTL -log10(p)
for yi, row in gwas_cqtl.iterrows():
    col = ld_color(row["ld_r2"])
    sz  = max(20, row["ld_r2"] * 120 + 15) if not np.isnan(row["ld_r2"]) else 20
    ax_l.scatter(row["cqtl_nlp"], yi, color=col, s=sz, zorder=3,
                 edgecolors="k" if row["in_gw_sig"] else "none", linewidths=0.5)

ax_l.axvline(-np.log10(GW_THRESH), color="#555555", lw=0.8, ls="--", alpha=0.8)
ax_l.set_yticks(range(n))
ax_l.set_yticklabels(gwas_cqtl["y_label"].tolist(), fontsize=9)
ax_l.set_xlabel("-log₁₀(p) CCL2 cQTL")
ax_l.set_ylabel("Variant (GWAS trait)")
ax_l.set_title("CCL2 cQTL signal")
ax_l.margins(x=0.15, y=0.06)
ax_l.spines["top"].set_visible(False)
ax_l.spines["right"].set_visible(False)

# Panel B — GWAS -log10(p); y-axis shared (sharey=True), labels suppressed
for yi, row in gwas_cqtl.iterrows():
    col = cat_colors.get(row.get("gwas_category", "Other"), "#7F7F7F")
    gp  = row["gwas_nlp"] if not np.isnan(row["gwas_nlp"]) else 0
    ax_r.scatter(gp, yi, color=col, s=45, zorder=3)

ax_r.set_xlabel("-log₁₀(p) GWAS")
ax_r.set_title("GWAS signal")
ax_r.margins(x=0.15, y=0.06)
ax_r.spines["top"].set_visible(False)
ax_r.spines["right"].set_visible(False)

# Shared legend on last panel (upper left outside)
cat_handles = [mpatches.Patch(color=c, label=t) for t, c in cat_colors.items()]
ld_leg = [
    mpatches.Patch(color="#D62728", label="LD r² ≥ 0.8"),
    mpatches.Patch(color="#FF7F0E", label="0.6 – 0.8"),
    mpatches.Patch(color="#1F77B4", label="0.4 – 0.6"),
    mpatches.Patch(color="#AEC7E8", label="0.2 – 0.4"),
    mpatches.Patch(color="#BDBDBD", label="< 0.2 / NA"),
    mpatches.Patch(color="none", label=""),
    mpatches.Patch(color="none",
                   label="Dot size ∝ LD r²\n(left panel only)"),
]
ax_r.legend(handles=cat_handles + ld_leg, frameon=False, fontsize=9,
            loc="upper left", bbox_to_anchor=(1, 1))

fig2.suptitle("GWAS-annotated variants near rs11867200:\n"
              "CCL2 cQTL vs. GWAS signal", fontsize=10, y=1.01)
plt.tight_layout()
out6 = IMGS / "fig6_gwas_cqtl_comparison.png"
fig2.savefig(out6, dpi=200, bbox_inches="tight")
plt.close()
print(f"Saved: {out6}")

# ── 8. FIGURE 7 — LD r2 bar chart (GWAS variants vs. rs11867200) ─────────────
# Horizontal barplot; n ~12 items → height = 3 + (12-10)/5*0.5 = 3.2
# Width: 3 + 1.5 (external legend) = 4.5
print("\n[7] Plotting Fig 7 – LD r2 bar chart...")

gwas_ld = df_tab[df_tab["in_gwas"] & ~df_tab["ld_r2"].isna()].sort_values("ld_r2")
n_bar   = len(gwas_ld)
h_bar   = 3 + max(0, (n_bar - 10) / 5 * 0.5)

fig3, ax3 = plt.subplots(figsize=(4.5, h_bar))
colors_bar = [ld_color(r) for r in gwas_ld["ld_r2"]]
ax3.barh(gwas_ld["rsid"], gwas_ld["ld_r2"], color=colors_bar, alpha=0.9)

for thresh, lbl in [(0.8, "0.8"), (0.6, "0.6"), (0.4, "0.4")]:
    ax3.axvline(thresh, color="#777777", lw=0.7, ls="--", alpha=0.7)

ax3.set_xlabel("LD r² to rs11867200 (1000G EUR)")
ax3.set_ylabel("Variant")
ax3.set_title("LD of GWAS-nearby variants\nto lead CCL2 cQTL (rs11867200)")
ax3.set_xlim(0, 1.1)
ax3.margins(y=0.05)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)

ld_leg3 = [
    mpatches.Patch(color="#D62728", label="r² ≥ 0.8"),
    mpatches.Patch(color="#FF7F0E", label="0.6 – 0.8"),
    mpatches.Patch(color="#1F77B4", label="0.4 – 0.6"),
    mpatches.Patch(color="#AEC7E8", label="0.2 – 0.4"),
    mpatches.Patch(color="#BDBDBD", label="< 0.2 / NA"),
]
ax3.legend(handles=ld_leg3, frameon=False, fontsize=9,
           loc="upper left", bbox_to_anchor=(1, 1))

plt.tight_layout()
out7 = IMGS / "fig7_ld_r2_bar.png"
fig3.savefig(out7, dpi=200, bbox_inches="tight")
plt.close()
print(f"Saved: {out7}")

# ── 9. Final summary to stdout ────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY — GWAS variants + CCL2 cQTL + LD to rs11867200 (EUR)")
print("="*70)
for _, row in df_tab[df_tab["in_gwas"]].sort_values("pos38").iterrows():
    dist     = f"{int(row['pos38'] - 34_248_950):+d}" if not np.isnan(row["pos38"]) else "?"
    gwas_str = (f"{str(row['gwas_trait'])[:35]:<35} p={row['gwas_pval']:.1e}"
                if row["gwas_trait"] else "no GWAS annotation")
    cqtl_str = (f"beta={row['cqtl_beta']:+.3f} p={row['cqtl_pval']:.2e}"
                if not np.isnan(row["cqtl_pval"]) else "not found")
    ld_str   = f"r2={row['ld_r2']:.3f}" if not np.isnan(row["ld_r2"]) else "r2=NA"
    gw_tag   = "[GW-SIG]" if row["in_gw_sig"] else "[nominal]"
    print(f"\n{row['rsid']} (dist={dist} bp):")
    print(f"  GWAS: {gwas_str}")
    print(f"  cQTL: {cqtl_str} {gw_tag}")
    print(f"  LD:   {ld_str}")

print(f"\nLead cQTL ({LEAD_SNP}): beta=-0.354 p=4.43e-09 [GW-SIG] | no GWAS annotation")
print("\nDone.")
