# eQTL Data Lake

Cis-eQTL summary statistics across multiple studies and tissues/cell types.

---

## eqtlgen/
*eQTLGen consortium — Võsa et al. 2021, Nature Genetics*

Whole-blood cis-eQTL meta-analysis across 37 cohorts, **n=31,684** individuals. 16,987 genes tested. GRCh37.

**Column schema** (both files):
`Pvalue | SNP | SNPChr | SNPPos | AssessedAllele | OtherAllele | Zscore | Gene | GeneSymbol | GeneChr | GenePos | NrCohorts | NrSamples | FDR | BonferroniP`

- `SNP` — variant rsID
- `Gene` — Ensembl gene ID
- `Zscore` — effect direction and magnitude
- `NrSamples` — per-variant sample size (varies across cohorts)

| File | Content | Size |
|------|---------|------|
| `sig/eQTLGen_cis_sig_FDR05.txt.gz` | Significant cis-eQTLs (FDR < 0.05) | 308 MB |
| `allpairs/eQTLGen_cis_allpairs.txt.gz` | All tested cis SNP–gene pairs | 3.7 GB |

---

## gtex_v10/sig/
*GTEx v10 — GTEx Consortium; GTEx Portal*

Cis-eQTL significant results across **50 tissues**. GRCh38 (b38). Per tissue: one eGenes file (best variant per gene, with permutation p-values) and one signif_pairs parquet (all significant cis-pairs).

**eGenes file schema** (`*.v10.eGenes.txt.gz`):
`gene_id | gene_name | biotype | gene_chr | gene_start | gene_end | strand | num_var | variant_id | tss_distance | chr | variant_pos | ref | alt | rs_id_dbSNP155_GRCh38p13 | ma_samples | ma_count | af | pval_nominal | slope | slope_se | pval_perm | pval_beta | qval | pval_nominal_threshold | afc | afc_se`

**signif_pairs file schema** (`*.v10.eQTLs.signif_pairs.parquet`):
`gene_id | variant_id | tss_distance | af | ma_samples | ma_count | pval_nominal | slope | slope_se | pval_nominal_threshold | min_pval_nominal | pval_beta`

- `variant_id` — `chr:pos:ref:alt:b38` format
- `slope` / `slope_se` — effect size in normalised expression units
- `pval_beta` — beta-approximation permutation p-value per gene
- `rs_id_dbSNP155_GRCh38p13` — rsID field (in eGenes file only)

Total: ~3.0 GB across 50 tissues. Tissues include all major GTEx tissue types (adipose, brain regions, heart, liver, lung, muscle, skin, spleen, whole blood, and more).

---

## gtex_v8_eqtl_catalogue/allpairs/
*GTEx v8 — GTEx Consortium; eQTL Catalogue r7, tabix-indexed*

All cis-eQTL pairs for **spleen** and **whole blood** from GTEx v8. Standard eQTL Catalogue format — drop-in compatible with `run_coloc` (`generic_tsv` format).

**Column schema**:
`molecular_trait_id | chromosome | position | ref | alt | variant | ma_samples | maf | pvalue | beta | se | type | ac | an | r2 | molecular_trait_object_id | gene_id | median_tpm | rsid`

- `molecular_trait_id` — Ensembl gene ID
- `gene_id` — Ensembl gene ID
- `rsid` — variant rsID (use for coloc rsID-matching)
- `beta`, `se`, `pvalue` — effect size and standard error (normalised expression)

For **coloc** (`generic_tsv` format): `col_gene=gene_id`, `col_rsid=rsid`, `col_beta=beta`, `col_se=se`, `col_pval=pvalue`

| File | Tissue | N | Size |
|------|--------|---|------|
| `GTEx_v8_spleen_allpairs.tsv.gz` | Spleen | ~670 | 3.3 GB |
| `GTEx_v8_whole_blood_allpairs.tsv.gz` | Whole blood | 670 | 2.7 GB |

---

## onek1k/sig/
*OneK1K — Yazar et al. 2022, Science; direct download*

Cis-eQTL results for **14 primary human immune cell types** from **982 donors** (PBMCs). GRCh37. Two files per cell type: `*_eqtl_table.tsv.gz` (all tested pairs) and `*_esnp_table.tsv.gz` (significant eSNPs only, FDR < 0.05).

**Column schema**:
`CELL_ID | CELL_TYPE | RSID | SNPID | GENE | GENE_ID | CHR | POS | A1 | A2 | A2_FREQ_ONEK1K | A2_FREQ_HRC | SPEARMANS_RHO | S_STATISTICS | P_VALUE | Q_VALUE | FDR | RSQUARE | GENOTYPED | ROUND`

- `GENE_ID` — Ensembl gene ID
- `RSID` — variant rsID
- `SPEARMANS_RHO` — effect size (Spearman rank correlation)
- `FDR` — within-cell-type Benjamini-Hochberg FDR

| Cell type code | Cell type | eQTL table size | eSNP table size |
|---------------|-----------|-----------------|-----------------|
| `all` | All cell types combined | 20 GB | 2.1 MB |
| `bin` | B intermediate | 1.6 GB | 146 KB |
| `bmem` | B memory | 1.5 GB | 113 KB |
| `cd4et` | CD4+ effector/transitional | 1.6 GB | 133 KB |
| `cd4nc` | CD4+ naive/central memory | 2.2 GB | 518 KB |
| `cd4sox4` | CD4+ SOX4+ | 748 MB | 31 KB |
| `cd8et` | CD8+ effector/transitional | 1.9 GB | 285 KB |
| `cd8nc` | CD8+ naive/central memory | 1.8 GB | 224 KB |
| `cd8s100b` | CD8+ S100B+ | 1.4 GB | 87 KB |
| `dc` | Dendritic cells | 1.2 GB | 44 KB |
| `monoc` | Classical monocyte | 1.5 GB | 92 KB |
| `mononc` | Non-classical monocyte | 1.3 GB | 82 KB |
| `nk` | NK cells | 1.8 GB | 294 KB |
| `nkr` | NK receptor+ | 1.1 GB | 43 KB |
| `plasma` | Plasma cells | 859 MB | 31 KB |

---

## onek1k_eqtl_catalogue/allpairs/
*OneK1K — Yazar et al. 2022, Science; eQTL Catalogue r7, tabix-indexed*

All cis-eQTL pairs for **10 immune cell types** from the OneK1K study, reprocessed through the eQTL Catalogue pipeline. Same standard column schema as `gtex_v8_eqtl_catalogue/` — drop-in compatible with `run_coloc`.

For **coloc** (`generic_tsv` format): `col_gene=gene_id`, `col_rsid=rsid`, `col_beta=beta`, `col_se=se`, `col_pval=pvalue`

| File | Cell type | Size |
|------|-----------|------|
| `OneK1K_B_intermediate_allpairs.tsv.gz` | B intermediate | 1.4 GB |
| `OneK1K_B_naive_allpairs.tsv.gz` | B naive | 1.8 GB |
| `OneK1K_CD16_Mono_allpairs.tsv.gz` | CD16+ monocyte | 1.2 GB |
| `OneK1K_MAIT_allpairs.tsv.gz` | MAIT cells | 606 MB |
| `OneK1K_NK_allpairs.tsv.gz` | NK cells | 2.4 GB |
| `OneK1K_NK_Proliferating_allpairs.tsv.gz` | NK proliferating | 441 MB |
| `OneK1K_Treg_allpairs.tsv.gz` | Treg | 1.3 GB |
| `OneK1K_cDC2_allpairs.tsv.gz` | cDC2 | 932 MB |
| `OneK1K_dnT_allpairs.tsv.gz` | DN T cells | 301 MB |
| `OneK1K_gdT_allpairs.tsv.gz` | γδ T cells | 1.1 GB |

---

## tenk10k/
*TenK10K Phase 1 — Cuomo, A.S.E. et al. 2025. medRxiv 2025.03.20.25324352 (preprint); data: Zenodo doi:10.5281/zenodo.17474113*

Single-cell cis-eQTL summary statistics, 1,925 donors, 5.4M cells, 28 immune cell types, GRCh38. Companion resource to the `caQTL` TenK10K multiome release — same program, gene-expression side.

⚠️ **No significant/gene-level/fine-mapped subset exists.** The Zenodo record's `common_variant_gene_level_results_with_annotated_fails.zip`, `rare_variant_gene_level_results*.zip`, `susie_summary.zip`, and `results_iscovariateoffset_true.zip` are empty placeholders (verified: unzip to a single empty directory entry, 0 bytes of content) despite being described in the record text. Only full nominal-pairs files were actually deposited.

**Physically stored at** `/vol/projects/CIIM/resources/TenK10K_eQTL/` (170 GB — not mirrored into `${CIIM_DATALAKE_DIR}/eQTL/`).

| File | Content | Size |
|------|---------|------|
| `common_all_cis_pvalues_100kb.zip` | common-variant (MAF≥1%) full nominal cis pairs, ±100kb, per cell type | 16.6 GB |
| `part1-7_common_all_cis_pvalues_1Mb.zip` (×7) | common-variant full nominal cis pairs, ±1Mb, per cell type (7-way split for size) | 129.7 GB |
| `rare_all_cis_pvalues_100kb_single_variant_test.zip` | rare-variant (MAF<1%) single-variant test, ±100kb, per cell type | 23.5 GB |
| `coloc_100kb.zip` | coloc colocalization based on 100kb common-variant results; organized by trait/cell type/chromosome | 0.63 GB |

Column schemas to be confirmed against actual unzipped content once download completes (not yet inspected).
