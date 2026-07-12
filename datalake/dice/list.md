# DICE -- File List

All files located in `datalake/dice/`. Downloaded from the DICE (Database of Immune Cell Expression, eQTLs, and Epigenomics) database at https://dice-database.org.

**Reference**: Schmiedel et al. 2018, *Cell* (doi:10.1016/j.cell.2018.10.022)  
**Genome build**: GRCh37.p19 | **DICE Build ID**: DICE-DB 1 | **Donors**: 91 healthy individuals

Two subdirectories: `expression/` (gene expression TPM per cell type) and `eqtls/` (cis-eQTLs per cell type in VCF format).

---

## expression/
**Expression**

Gene expression data in TPM (transcripts per million) for each immune cell subtype. Each file has one row per gene. Columns: `Feature_name` (Ensembl gene ID + version), `Transcript_Length(bp)`, `Additional_annotations` (gene symbol + biotype), followed by 88 columns of donor TPM values (numbered 0–87).

### CD4_NAIVE_TPM.csv
**CD4 T cell, naive (resting)**  
Unstimulated naive CD4+ T cells. Baseline state for naive CD4 T cell gene expression.

### CD4_STIM_TPM.csv
**CD4 T cell, naive (TCR-activated)**  
Naive CD4+ T cells stimulated via TCR + CD28. Built-in perturbation comparison against CD4_NAIVE for identifying the TCR activation gene program.

### TH1_TPM.csv
**CD4 T cell, Th1**  
In vitro differentiated Th1 effector cells (IFN-γ producing). Use to characterize the Th1 effector gene program.

### TH2_TPM.csv
**CD4 T cell, Th2**  
In vitro differentiated Th2 effector cells (IL-4/IL-13 producing).

### TH17_TPM.csv
**CD4 T cell, Th17**  
In vitro differentiated Th17 effector cells (IL-17 producing).

### THSTAR_TPM.csv
**CD4 T cell, Th1/17 (Th1*)**  
Intermediate Th1/Th17 cells co-producing IFN-γ and IL-17.

### TFH_TPM.csv
**CD4 T cell, T follicular helper (Tfh)**  
Tfh cells that support B cell responses in germinal centers.

### TREG_NAIVE_TPM.csv
**CD4 T cell, naive Treg**  
Naive (thymic) regulatory T cells. FOXP3+ suppressor lineage.

### TREG_MEM_TPM.csv
**CD4 T cell, memory Treg**  
Memory regulatory T cells. Antigen-experienced FOXP3+ suppressor lineage.

### CD8_NAIVE_TPM.csv
**CD8 T cell, naive (resting)**  
Unstimulated naive CD8+ T cells. Baseline for cytotoxic lineage.

### CD8_STIM_TPM.csv
**CD8 T cell, naive (TCR-activated)**  
Naive CD8+ T cells stimulated via TCR + CD28. Built-in perturbation comparison for the CD8 activation program.

### B_CELL_NAIVE_TPM.csv
**B cell, naive**  
Naive B cells. Baseline B cell gene expression.

### NK_TPM.csv
**NK cell, CD56dim CD16+**  
Mature cytotoxic NK cells (CD56dim CD16-bright). The dominant NK subset in peripheral blood.

### MONOCYTES_TPM.csv
**Monocyte, classical (CD14++)**  
Classical inflammatory monocytes.

### M2_TPM.csv
**Monocyte, non-classical (CD16+)**  
Non-classical patrolling monocytes.

---

## eqtls/
**eQTL**

Two subdirectories with different filtering levels:

### eqtls/ (filtered, significant only)
Cis-eQTL data in VCF format. Only significant associations. Filters applied: adjusted p-value < 0.05, raw p-value < 0.0001, TPM > 1.0.  
VCF INFO fields: `Gene` (Ensembl ID), `GeneSymbol`, `Pvalue`, `Beta`, `ANOVA`, `FDR`.  
~347K SNP-gene pairs per cell type (example: CD4_NAIVE).

### eqtls/full_summary_stats/ (unfiltered, all tested pairs)
Full cis-eQTL summary statistics with no p-value or TPM filter. Use for colocalization (coloc/SuSiE) or fine-mapping.  
VCF INFO fields: `Gene` (Ensembl ID), `GeneSymbol`, `Pvalue`, `Beta`, `Statistic` (t-statistic), `FDR`.  
~220M SNP-gene pairs per cell type (example: CD4_NAIVE).

Position-sorted, bgzip-compressed, tabix-indexed (`.vcf.bgz` + `.vcf.bgz.tbi`) — drop-in compatible with `run_coloc`'s `dice_vcf` format, which does a regional `tabix` lookup on the cis-window instead of scanning the file. As distributed by DICE, these files shipped gzip-compressed and sorted by ascending p-value (not position), so they weren't tabix-indexable; re-sorted and reindexed via `analysis/dice_reindex/reindex_dice.sh` (~2.1 GB per file, 31 GB total). The original `.vcf.gz` files were deleted after validating line counts matched exactly.

One file per cell type (same naming, `.vcf` for filtered, `.vcf.gz` for full):

| File | Cell type |
|---|---|
| `CD4_NAIVE` | CD4 T cell, naive |
| `CD4_STIM` | CD4 T cell, naive activated |
| `TH1` | Th1 |
| `TH2` | Th2 |
| `TH17` | Th17 |
| `THSTAR` | Th1/17 |
| `TFH` | T follicular helper |
| `TREG_NAIVE` | Naive Treg |
| `TREG_MEM` | Memory Treg |
| `CD8_NAIVE` | CD8 T cell, naive |
| `CD8_STIM` | CD8 T cell, naive activated |
| `B_CELL_NAIVE` | Naive B cell |
| `NK` | NK cell |
| `MONOCYTES` | Classical monocyte |
| `M2` | Non-classical monocyte |
