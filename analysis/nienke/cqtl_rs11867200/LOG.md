# Question
SI cohort cQTL results around rs11867200: show significant associations in the region
and identify which are specifically associated with CCL2.

---

## Step 1 — Locate the variant
- rs11867200 found at **chr17:34,248,950** (C>T) in the nominal cQTL file
  (`/vol/projects/CIIM/meta_cQTL/out/SI-senior/cytokines/mapping/main_nominal.tsv`)
- CCL2 maps to phenotype `pbmc_24h_mcp1_lps` (MCP-1 measured at 24h post-LPS stimulation)

## Step 2 — Define the window
- cQTL mapping was run with a ±1 Mb cis-window (standard)
- For display, used **±500 kb** around the lead variant: chr17:33,748,950–34,748,950
- This captures the full significant LD block plus flanking context

## Step 3 — Extract regional associations
- 2,525 unique variants × 286 cytokine phenotypes tested in the ±500 kb window
- 38,092 nominal association pairs total

## Step 4 — Genome-wide significant hits
- Significance threshold: p < 5×10⁻⁸
- **Only 1 cytokine has genome-wide sig associations in this window: CCL2 (pbmc_24h_mcp1_lps)**
- **27 genome-wide sig variants** spanning ~77 kb: chr17:34,190,728–34,267,238
- rs11867200 is the **lead variant** (strongest p = 4.43×10⁻⁹)

## Step 5 — All associations at rs11867200
Sorted by p-value:
| Cytokine | β | p-value | Notes |
|---|---|---|---|
| pbmc_24h_mcp1_lps | −0.354 | 4.43×10⁻⁹ | **Genome-wide sig** |
| pbmc_24h_mcp3_pam3cys | −0.309 | 2.99×10⁻⁶ | Nominal |
| pbmc_24h_mcp3_lps | −0.254 | 8.75×10⁻⁶ | Nominal |
| pbmc_24h_mcp1_pam3cys | −0.225 | 1.63×10⁻⁴ | Nominal |
| pbmc_24h_ifng_pam3cys | −0.130 | 1.93×10⁻³ | Nominal |
| … | … | … | p<0.05 only |

## Figures
All images in `temp/cqtl_rs11867200/images/`:
- `fig1_ccl2_regional_plot.png` — Regional association plot (CCL2 LPS 24h)
- `fig2_rs11867200_all_cytokines.png` — All cytokine associations at rs11867200
- `fig3_ccl2_stimulations.png` — CCL2/MCP-1 across all stimulation conditions
- `fig4_gw_sig_per_cytokine.png` — N genome-wide sig variants per cytokine in window

---

## Step 6 — Is rs11867200 truly the lead? GWAS LD analysis

**Follow-up question:** rs11867200 has no GWAS annotation in the Catalog. Nearby variants
(rs9889296 for IBD; rs3091315/16 for Crohn's/IBD; rs7218453 for monocyte %) DO have GWAS
associations. Are they in LD with rs11867200? Do they tag the same signal?

**Script:** `temp/cqtl_rs11867200/script_v2_gwas_ld.py`

**Data sources:**
- LD: 1000G EUR (GRCh37), plink bed/bim/fam, numpy bed-reader
- cQTL: `main_genomewide.tsv` + `regional_nominal.tsv` (CCL2 = pbmc_24h_mcp1_lps)
- GWAS: `temp/nienke/step4_phewas/gwascatalog_regional_all.csv`

### Key LD r² results (to rs11867200, 1000G EUR)

| Variant | dist (bp) | r² | GWAS trait | GWAS p | CCL2 cQTL p | cQTL status |
|---|---|---|---|---|---|---|
| rs9911144 | −56,111 | **0.832** | Monocyte count | 1×10⁻²⁴ | 1.60×10⁻⁸ | GW-sig |
| rs9891243 | −46,689 | **0.844** | Monocyte count | 3×10⁻¹⁴ | 9.57×10⁻⁹ | GW-sig |
| rs7218453 | −40,509 | **0.871** | Monocyte % | 3×10⁻²⁵ | 6.88×10⁻⁹ | GW-sig |
| rs9909465 | −34,625 | **0.871** | Monocyte count | 9×10⁻²⁴ | 6.90×10⁻⁹ | GW-sig |
| rs9906695 | −29,813 | **0.871** | Monocyte % | 3×10⁻¹¹ | 7.55×10⁻⁹ | GW-sig |
| rs9889296 | −5,422 | **0.086** | IBD/cross-inflam. | 5×10⁻²¹ | 8.60×10⁻⁷ | nominal |
| rs6505402 | −1,724 | 0.132 | pQTL CDSN | 1×10⁻⁵⁶ | 1.74×10⁻⁵ | nominal |
| rs4795893 | −1,521 | 0.132 | pQTL CDSN | 9×10⁻¹⁴ | 1.64×10⁻⁵ | nominal |
| rs2857656 | +6,038 | **0.084** | IBD/ALL pleiotropy | 2×10⁻⁹ | 3.44×10⁻⁶ | nominal |
| rs3091315 | +17,696 | **0.083** | Crohn's disease | 8×10⁻²⁵ | 3.58×10⁻⁶ | nominal |
| rs3091316 | +18,005 | **0.083** | IBD | 1×10⁻²⁶ | 3.58×10⁻⁶ | nominal |

### Interpretation

**Two independent signals at this locus — not one:**

1. **Signal A (rs11867200 haplotype, MAF=0.179)**
   - Strong CCL2 cQTL (p=4.43×10⁻⁹, the lead in SI cohort)
   - In moderate-high LD with monocyte count/% GWAS variants (r²=0.83–0.87)
   - Absent from IBD GWAS because it is a DIFFERENT haplotype from the IBD lead
   - rs11867200 itself not in GWAS Catalog likely because: (a) it falls just below the GWAS
     detection threshold across large cohorts given its low MAF, or (b) GWAS lead SNPs
     for this region (rs7218453, rs9909465) are chosen over rs11867200 due to higher MAF
     and marginal LD difference; both tag Signal A

2. **Signal B (rs3091315/rs3091316 haplotype, MAF≈0.317)**
   - Very strong IBD GWAS signal (p up to 1×10⁻²⁶)
   - In VERY LOW LD with rs11867200 (r²=0.083) — essentially independent
   - Only nominally associated with CCL2 in SI cohort (p~3.6×10⁻⁶) — this is likely a
     weaker or cell-type-specific CCL2 effect on a different haplotype, or confounded
     by LD with Signal A in the smaller SI cohort
   - This IBD signal is almost certainly driven by a different causal variant (~18 kb
     downstream of rs11867200), operating through a distinct mechanism

**rs11867200 IS a valid lead cQTL variant** — it tags Signal A (monocyte biology/CCL2 
production), not Signal B (IBD). The absence of GWAS annotation for rs11867200 reflects
that GWAS studies at this locus tag Signal A via nearby variants with higher MAF
(rs7218453, rs9909465, r²~0.87), not that rs11867200 is a false positive.

**The IBD GWAS signal (rs3091315/16) is a separate locus signal** operating on a distinct 
haplotype and likely affecting a different regulatory pathway in gut/immune cells.

### Output files
- `temp/cqtl_rs11867200/gwas_ld_cqtl_table.csv` — merged table (all variants)
- `temp/cqtl_rs11867200/images/fig5_locuszoom_ld_gwas.png` — LocusZoom + LD + GWAS labels
- `temp/cqtl_rs11867200/images/fig6_gwas_cqtl_comparison.png` — dual panel cQTL vs. GWAS
- `temp/cqtl_rs11867200/images/fig7_ld_r2_bar.png` — LD r² bar chart
