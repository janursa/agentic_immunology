# caQTL Data Lake

Chromatin-accessibility QTL summary statistics and derived outputs — TenK10K program (Xue, A. et al. 2025. *Genetic regulation of cell type–specific chromatin accessibility shapes immune function and disease risk*. medRxiv. doi:10.1101/2025.08.27.25334533. Preprint, CC-BY-4.0). 922 donors, 28 immune cell types, 3.47M PBMC nuclei, 440,996 consensus peaks, GRCh38.

**Physically stored at** `/vol/projects/CIIM/resources/TenK10K_multiome/` — this file is an index; data is not copied into `datalake/`.

---

## caQTL_common_TensorQTL/
*Common-variant (MAF≥1%) caQTL — TensorQTL, ±1Mb cis-window*

Per cell type (28) × per chromosome (22), three tiers:
- `TenK10K.cis_qtl_pairs.chr*.{csv,parquet}` — raw, all peak–variant pairs in window
- `TenK10K.sig_cis_qtl_pairs.chr*.csv` — permutation/FDR-significant pairs
- `TenK10K.independent_cis_qtl_pairs.chr*.csv` — conditionally independent lead pairs

**Raw schema:** `phenotype_id | variant_id | start_distance | af | ma_samples | ma_count | pval_nominal | slope | slope_se`
- `phenotype_id` — peak ID (chr:start-end); `variant_id` — chr:pos:ref:alt; `af` — alt allele freq; `slope`/`slope_se` — effect on accessibility

**Corrected schema adds:** `num_var | beta_shape1/2 | true_df | pval_true_df | pval_perm | pval_beta | qval | pval_nominal_threshold` (beta-approximated permutation FDR)

Size: ~1020 GB (28–64 GB/cell type; raw all-pairs dominates). `Replication/` subfolder (4.9 GB) = replication-cohort results.

## caQTL_rare_SAIGEQTL/
*Rare-variant (MAF<1%) gene-level caQTL — SAIGE-QTL*
Conditional + unconditional tests, gene-level aggregation: `RareSAIGEConditional.zip`, `RareSAIGEUnconditional.zip`, `Rare_SAIGE_Conditional_Gene_Level.zip`, `Rare_SAIGE_Unconditional_Gene_Level.zip`. Size: 61 GB.

## Cell_state_analysis/
*Cell-state-dependent (dynamic) caQTL*
- `Dynamic_SAIGEQTL/` — genotype × epigenetic-age interaction caQTL (`All_chr_raw.csv`, `All_chr_significant.csv`)
- `EpiAge/regression-results.zip` — epigenetic-age regression outputs
Size: 115 GB.

## ChromBPNet/
*Deep-learning variant-effect models*
Per cell type (28 dirs): trained ChromBPNet weights + base-resolution predicted variant-effect scores. Size: 14 GB.

## Fine_mapping/
*SuSiE / mvSuSiE fine-mapping*
`all_celltypes_caQTL_susie_annotated.zip` — 95% credible sets, all cell types, annotated. Size: 186 MB.

## colocalization/
*coloc (Bayesian colocalization)*
`coloc_results_caQTL2eQTL.zip`, `coloc_sig_H4_results_caQTL2eQTL.csv.zip` (PP.H4-significant subset), `coloc_results_caQTL2GWAS.zip`, `coloc_results_eQTL2GWAS.zip`, `coloc_results_MultiColoc.zip` (joint multi-trait). ⚠️ Updated 27-Jun-2026 — allele-flipping fix in caQTL↔eQTL coloc; re-download if fetched earlier. Size: 1.8 GB.

## SMR/
*Summary-based Mendelian Randomisation*
`SMR_results_caQTL2eQTL.zip`, `smr_sig_results_caQTL2eQTL.csv.zip`, `SMR_results_caQTL2GWAS.zip`, `SMR_results_eQTL2GWAS.zip`. Size: 1.7 GB.

## Gene_regulatory_network/
*GLUE peak–gene / TF–gene links*
`diff_TF_gene.csv`, `Peak_gene_links/{with_eQTL,without_eQTL}/`. Size: 99 MB.

## Miscellaneous/
`TenK10K_ATAC_MACS3_Combined_Peaks_Annotated.bed` — the 440,996-peak consensus set with functional annotations. Size: 19 MB.

---
Each subfolder has its own `README.md` at the physical location with full column-level detail beyond what's summarized here.
