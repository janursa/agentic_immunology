# LOG — rs11867200 / IBD ATAC differential accessibility

**Question:** Does LPS perturbation change chromatin accessibility at rs11867200 (chr17:34,248,950 GRCh38) in IBD PBMCs, per disease (UC/CD) and major cell type?

---

## Context

From step1 annotation: rs11867200 sits in a high-density enhancer cluster (7 dELS within ±2 kb), 6.3 kb upstream of CCL2. The C→T SNP disrupts a perfect PU.1/SPI1 ETS binding site (100% → 70% motif score). Hypothesis: LPS should increase accessibility at this locus, and this effect may differ between CD and UC, and across cell types.

## Data

- **ATAC**: `/home/jnourisa/agentic/datalake/omics/IBD/atac.h5ad` — 120,361 cells × 182,416 peaks
- **Stimulations**: LPS (52,619 cells), RPMI (49,613 cells) — used here; S. salmonella excluded
- **Diseases**: CD (62,385 cells), UC (57,976 cells)
- **Cell types** (major): CD4 T cells, Monocytes, B cells, CD8 T cells, NK cells
- **Donors per group**: CD: 17 (LPS), 17 (RPMI); UC: 19 (LPS), 16 (RPMI) — well-powered for NB GLM

## Method

1. **Peak lookup**: parse peak names (chr-start-end format), find peaks overlapping chr17:34,248,950 ±500 bp
2. **Pseudobulk**: sum raw counts per donorID × disease × celltype × stimulation (avoids pseudoreplication)
3. **Negative Binomial GLM** (statsmodels): `counts ~ is_LPS + offset(log(total_counts))` per disease × cell type stratum
   - Same statistical model as DESeq2 (NB with log link, library-size offset)
   - Dispersion shrinkage not applied (DESeq2 advantage for genome-wide; not needed for single peak)
   - log2FC = NB coefficient / log(2)
4. **Visualization**: violin plots per stratum (cell-level log1p CPM) + log2FC heatmap with significance

## Singularity

`ciim.sif` with `--bind /vol/projects:/vol/projects --bind /home/jnourisa:/home/jnourisa`

## Script

`temp/nienke/ibd_atac/script.py`

---

## Step 1 — Execution (2026-05-23)

**Target peak found:** `chr17-34248263-34249207` (944 bp peak, directly overlaps SNP position chr17:34,248,950)
A second peak `chr17-34249247-34250190` is 297 bp away but not used (focus peak is the direct overlap).

**Donor counts per stratum:** CD 17/17 (LPS/RPMI); UC 19/16 — sufficient for NB GLM.

### Results

| Disease | Cell type   | log2FC  | p-value | Sig |
|---------|-------------|---------|---------|-----|
| CD      | CD4 T cells | −0.84   | 0.378   | ns  |
| CD      | Monocytes   | +0.47   | 0.377   | ns  |
| CD      | B cells     | −1.67   | 0.379   | ns  |
| CD      | CD8 T cells | −1.60   | 0.378   | ns  |
| CD      | NK cells    | −1.14   | 0.435   | ns  |
| UC      | CD4 T cells | −1.56   | 0.131   | ns  |
| UC      | Monocytes   | +0.65   | 0.216   | ns  |
| UC      | B cells     | −0.16   | 0.916   | ns  |
| UC      | CD8 T cells | −1.29   | 0.479   | ns  |
| UC      | NK cells    | −1.24   | 0.496   | ns  |

### Interpretation

No significant LPS-induced changes at the rs11867200 locus in any disease × cell type combination.

**Consistent directional signal in Monocytes:** +0.47 (CD) and +0.65 (UC) — both positive, suggesting a trend toward increased accessibility with LPS in the most CCL2-relevant cell type. Not statistically significant likely due to high variance across donors.

**Critical limitation:** The IBD dataset has no genotype information. The mechanistic model predicts the effect is **genotype × context-dependent**: the T allele shows more accessibility specifically because it alters PU.1/CEBPB occupancy. Without stratifying by rs11867200 allele, any allele-specific chromatin effect is diluted across carriers and non-carriers (minor allele T freq ~20–30%).

**Why IBD context matters but may not recapitulate the aging effect:** The rs11867200 stimQTL was discovered in aged/SLE individuals where CEBPB/RELA activity is elevated (inflammaging). IBD is a different inflammatory context — while CEBPB may be elevated, the chromatin priming landscape differs from aging. Additionally, the IBD cohort has no healthy controls, so we cannot compare to a baseline.

### Output files
- `da_results.tsv` — full NB GLM results
- `images/fig1_violins.png` — violin plots per disease × cell type
- `images/fig2_heatmap.png` — log2FC heatmap with significance

---

## Step 2 — Genomic track visualization (2026-05-23)

**Script:** `script_tracks.py`

**Question:** Which cell types show chromatin accessibility across the rs11867200 locus (±15 kb), visualized as genome-browser-style tracks?

**Region:** chr17:34,233,950–34,263,950 (±15 kb around SNP) — 9 peaks found.

### Data-derived cell-type accessibility (RPMI baseline, mean pseudobulk CPM)

| Cell type  | Max CPM (CD) | Max CPM (UC) |
|------------|-------------|-------------|
| Monocytes  | 28.1        | 29.4        |
| B cells    | 7.9         | 5.5         |
| CD8 T      | 2.3         | 3.4         |
| NK         | 1.9         | 1.4         |
| CD4 T      | 1.1         | 1.4         |

**Key finding:** The locus is **predominantly accessible in Monocytes** (max CPM 28–29), with ~4× higher signal than B cells and ~15–27× higher than T/NK cells. This is now **data-derived** from IBD ATAC pseudobulk CPM, not a biological inference. The pattern is consistent between CD and UC, confirming it is a cell-type-intrinsic chromatin state (likely driven by PU.1/SPI1 occupancy, which is a monocyte-lineage TF).

The direct-overlap peak (`chr17-34248263-34249207`, SNP position) shows the highest accessibility in Monocytes in both diseases.

### Output files
- `images/fig3_genomic_tracks.png` — genome-browser-style tracks, CD vs UC, RPMI baseline
