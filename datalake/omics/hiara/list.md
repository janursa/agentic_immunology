# Omics Data Lake -- File List

All files are .h5ad (AnnData) located in datalake/omics/.
Suffix convention: _sc = single-cell, _bulk = pseudobulked by major cell type.
(A `_bulk_minor` = pseudobulked-by-Sub_CT variant also exists on disk for most cohorts but is
out of scope here and not documented — analyses use Major_CT resolution.)

---

Files: `/vol/projects/jnourisa/hiara/datasets/{sc,bulk}/aida.h5ad`

## sc/aida.h5ad
**AIDA Single-Cell**
Single-cell RNA-seq. Multi-ethnic Asian healthy PBMC cohort (625 donors, ages 19-77, 350 F / 275 M).
Cells: 1,265,245 | Genes: 13,772
obs columns: donor_id, age, sex, race, batch_info, dataset, donor_age, bulk_group, Major_CT, Sub_CT, ct_major_published, n_genes_by_counts, total_counts, total_counts_mt, pct_counts_mt, n_genes, orig.ident

## bulk/aida.h5ad
**AIDA Bulk**
Pseudobulked from aida_sc by donor_id x Major_CT.
Samples: 3,963 | Genes: 13,772
obs columns: donor_id, age, sex, race, batch_info, dataset, donor_age, bulk_group, Major_CT, cell_count, sum_by, orig.ident
Major_CT: B, CD4T, CD8T, DC, MONO, Megakaryocyte, NK, Others

---

Files: `/vol/projects/jnourisa/hiara/datasets/{sc,bulk}/abf300.h5ad`

## sc/abf300.h5ad
**ABF300 Single-Cell**
Single-cell RNA-seq. Healthy PBMC cohort (166 donors, ages 25-81, 36 F / 130 M).
Cells: 1,916,367 | Genes: 15,437
obs columns: donor_id, age, sex, batch_info, ct_major_published, dataset, donor_age, bulk_group, Major_CT, Sub_CT, n_genes_by_counts, total_counts, total_counts_mt, pct_counts_mt, n_genes, orig.ident

## bulk/abf300.h5ad
**ABF300 Bulk**
Pseudobulked from abf300_sc by donor_id x Major_CT.
Samples: 1,915 | Genes: 15,437
obs columns: donor_id, age, sex, dataset, bulk_group, Major_CT, donor_age, cell_count, sum_by, orig.ident
Major_CT: B, CD4T, CD8T, DC, HSC, MONO, NK

---

Files: `/vol/projects/jnourisa/hiara/datasets/{sc,bulk}/onek1k.h5ad`

## sc/onek1k.h5ad
**OneK1K Single-Cell**
Single-cell RNA-seq. Australian European healthy PBMC cohort (981 donors, ages 19-97, 565 F / 416 M).
Cells: 1,248,940 | Genes: 9,894
obs columns: donor_id, age, sex, batch_info, ct_major_published, dataset, donor_age, bulk_group, Major_CT, Sub_CT, nCount_RNA, nFeature_RNA, n_genes_by_counts, total_counts, total_counts_mt, pct_counts_mt, n_genes, orig.ident

## bulk/onek1k.h5ad
**OneK1K Bulk**
Pseudobulked from onek1k_sc by donor_id x Major_CT.
Samples: 4,961 | Genes: 9,894
obs columns: donor_id, age, sex, batch_info, dataset, bulk_group, Major_CT, donor_age, total_counts_mt, pct_counts_mt, cell_count, sum_by, orig.ident
Major_CT: B, CD4T, CD8T, DC, MONO, Megakaryocyte, NK

---

Files: `/vol/projects/jnourisa/hiara/datasets/{sc,bulk}/perez_sle.h5ad`

## sc/perez_sle.h5ad
**Perez SLE Single-Cell**
Single-cell RNA-seq. SLE patients and healthy controls (261 donors, ages 20-83, 244 F / 17 M; European, Asian, African American, Hispanic). Use condition column to split cases (systemic lupus erythematosus) vs controls (normal).
Cells: 1,263,676 | Genes: 11,918
obs columns: donor_id, age, sex, race, condition, disease_state, batch_info, ct_major_published, dataset, donor_age, bulk_group, Major_CT, Sub_CT, n_genes_by_counts, total_counts, total_counts_mt, pct_counts_mt, n_genes, orig.ident

## bulk/perez_sle.h5ad
**Perez SLE Bulk**
Pseudobulked from perez_sle_sc by donor_id x Major_CT x condition.
Samples: 1,708 | Genes: 11,918
obs columns: donor_id, age, sex, race, condition, dataset, bulk_group, Major_CT, donor_age, cell_count, sum_by, orig.ident
Major_CT: B, CD4T, CD8T, DC, HSC, MONO, NK, Others

---

Files: `/vol/projects/jnourisa/hiara/datasets/{sc,bulk}/zhang.h5ad`

## sc/zhang.h5ad
**Zhang Single-Cell**
Single-cell RNA-seq. Broad age-range healthy PBMC cohort (61 donors, ages 0-90, 32 M / 29 F; pediatric to elderly).
Cells: 538,266 | Genes: 14,468
obs columns: donor_id, age, sex, batch_info, ct_major_published, dataset, donor_age, bulk_group, Major_CT, Sub_CT, nCount_RNA, nFeature_RNA, n_genes_by_counts, total_counts, total_counts_mt, pct_counts_mt, n_genes, orig.ident

## bulk/zhang.h5ad
**Zhang Bulk**
Pseudobulked from zhang_sc by donor_id x Major_CT.
Samples: 404 | Genes: 14,468
obs columns: donor_id, age, sex, batch_info, dataset, bulk_group, Major_CT, donor_age, cell_count, sum_by, orig.ident
Major_CT: B, CD4T, CD8T, DC, MONO, Megakaryocyte, NK, Others

---

Files: `/vol/projects/jnourisa/hiara/datasets/{sc,bulk}/CXCL9.h5ad`

## sc/CXCL9.h5ad
**CXCL9 Single-Cell**
Single-cell RNA-seq. Ex-vivo cytokine/drug stimulation cohort (7 donors, ages 25-31, 4 F / 3 M). Conditions: rhCXCL9, rhIFN-gamma, LPS, metformin, ruxolitinib, and combinations (24h timepoint).
Cells: 253,390 | Genes: 17,011
obs columns: donor_id, age, sex, condition, treatment_id, batch_info, pool_id, donor_letter, dataset, donor_age, bulk_group, Major_CT, Sub_CT, n_genes_by_counts, total_counts, total_counts_mt, pct_counts_mt, n_genes, orig.ident

## bulk/CXCL9.h5ad
**CXCL9 Bulk**
Pseudobulked from CXCL9_sc by donor_id x Major_CT x condition.
Samples: 597 | Genes: 17,011
obs columns: donor_id, age, sex, condition, treatment_id, batch_info, pool_id, donor_letter, dataset, bulk_group, Major_CT, cell_count, sum_by, orig.ident
Major_CT: B, CD4T, CD8T, DC, Erythroid, MONO, Megakaryocyte, NK, Others

---

Files: `/vol/projects/jnourisa/hiara/datasets/sc/op.h5ad`

## sc/op.h5ad
**OP Drug Perturbation — Single-Cell**
Single-cell RNA-seq. Ex-vivo drug perturbation cohort (3 donors, ages 45-52, 2 M / 1 F). ~150 drugs at 24h timepoint. No pseudobulk available. Use condition and is_control columns to define comparisons.
Cells: 299,045 | Genes: 11,606
obs columns: donor_id, age, sex, condition, is_control, is_positive_control, dose_uM, timepoint_hr, cell_type, plate_name, well, row, col, container_format, hashtag_id, raw_cell_id, cell_id, split, dataset, donor_age, bulk_group, Major_CT, Sub_CT, n_genes_by_counts, total_counts, total_counts_mt, pct_counts_mt, n_genes
uns: log1p, neighbors, over_clustering
No drug_moa/drug_target/drug_confidence fields on file (verified via h5py, 2026-07-07) despite earlier docs claiming otherwise — MOA/target must be cross-referenced externally by drug name in `condition`.

---

Files: `/vol/projects/jnourisa/hiara/datasets/{sc,bulk}/parsebioscience.h5ad`

## sc/parsebioscience.h5ad
**ParseBioscience Cytokine Perturbation — Single-Cell**
Single-cell RNA-seq. Ex-vivo cytokine stimulation on PBMCs from 12 healthy donors (ages 34–75). 90 cytokines + PBS control at 24h. No sex metadata available.
Cells: 9,514,301 | Genes: 13,364
obs columns: cell_type, condition, donor_id, is_control, well, cell_type_original, perturbation_type, age, dataset, donor_age, bulk_group, n_genes_by_counts, total_counts, total_counts_mt, pct_counts_mt, n_genes, Major_CT_original, Sub_CT_original, Major_CT, Sub_CT
Major_CT: B, CD4T, CD8T, DC, MONO, NK, Others
Sub_CT: Tcm_Naive_CD4, Tem_Trm_CD8, Tem_Temra_CD8, Naive_B, Memory_B, Plasma_B, Classic_MONO, NonClassic_MONO, Int_Macrophage, Treg, MAIT, Others
Conditions (90 cytokines + PBS control): IFN-alpha1/beta/gamma/epsilon/omega/lambda1-3, IL-1α/β through IL-36/IL-36Ra, TNF-alpha, TGF-beta1, GM-CSF, M-CSF, G-CSF, and many more. Control: PBS (is_control = True).

## bulk/parsebioscience.h5ad
**ParseBioscience Cytokine Perturbation Bulk**
Pseudobulk RNA-seq from a Parse Biosciences ex-vivo cytokine stimulation experiment (12 healthy donors, ages 34–75). 90 cytokines + PBS control stimulated on PBMCs. Pseudobulked by donor_id × Major_CT × condition. 
Samples: 5,760 | Genes: 20,968
obs columns: sum_by, Major_CT_original, Major_CT, well, donor_id, dataset, perturbation_type, condition, cell_type, is_control, age, donor_age, bulk_group, cell_count
Cell types: B, CD4T, CD8T, MONO, NK
Conditions (90 cytokines + PBS control): IFN-alpha1/beta/gamma/epsilon/omega/lambda1-3, IL-1α/β through IL-36/IL-36Ra, TNF-alpha, TGF-beta1, GM-CSF, M-CSF, G-CSF, and many more. Control: PBS (is_control = True).

---

Files: `/vol/projects/jnourisa/hiara/datasets/{sc,bulk}/soundlife.h5ad`

## sc/soundlife.h5ad
**SoundLife Single-Cell**
Single-cell RNA-seq. Longitudinal PBMC cohort from the SoundLife study (96 donors, ages 25–67; multi-ethnic: African American, Asian, Caucasian, Other; Hispanic/Non-Hispanic). Flu vaccination study with timepoints at Day 0, 7, 90 across up to 3 flu years, plus Immune Variation visits. Includes CMV status, BMI, and vaccination metadata per donor.
Cells: 13,789,548 | Genes: 13,164
obs columns: AIFI_L1, AIFI_L1_score, AIFI_L2, AIFI_L2_original, AIFI_L2_score, AIFI_L3, AIFI_L3_score, Major_CT, Major_CT_original, Sub_CT, Sub_CT_original, age, barcodes, batch_id, bulk_group, cell_name, chip_id, cohort.cohortGuid, dataset, day, donor_age, donor_id, doublet_score, n_genes, n_genes_by_counts, n_reads, n_umis, pct_counts_mito, pct_counts_mt, pool_id, predicted_AIFI_L1, predicted_AIFI_L2, predicted_AIFI_L3, race, sample.drawYear, sample.sampleKitGuid, sample.subjectAgeAtDraw, sample.visitName, sex, subject.ageAtFirstDraw, subject.ageGroup, subject.biologicalSex, subject.birthYear, subject.bmi, subject.cmv, subject.ethnicity, subject.race, subject.subjectGuid, total_counts, total_counts_mito, total_counts_mt, vaccinated, vaccine_year, visitName, well_id, year
Major_CT: B, CD4T, CD8T, MONO, NK
Sub_CT: CD8a/a, CD16_NK, Classic_MONO, MAIT, Memory_B, Naive_B, NonClassic_MONO, Plasma_B, Tcm_Naive_CD4, Tcm_Naive_CD8, Tem_Effector_CD4, Tem_Trm_CD8, Treg
visitName values: Flu Year 1/2/3 Day 0/7/90/Stand-Alone; Immune Variation Day 0/7/90

## bulk/soundlife.h5ad
**SoundLife Bulk**
Pseudobulked from soundlife_sc by donor_id x Major_CT x visitName — NOT one-row-per-donor; a donor
with multiple flu-year/visit timepoints has multiple rows here. Collapse to a single row per donor
(e.g. filter to one visitName such as baseline/Day 0) yourself if that's what the analysis needs.
Major_CT: B, CD4T, CD8T, MONO, NK
