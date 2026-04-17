# CIIM Dataset Overview

All data lives under `/vol/projects/CIIM/`.


## 🆕 On Disk — Not Yet in Datalake

### scRNA-seq — Healthy

| Dataset | Location | Donors | Cells | Notes |
|---|---|---|---|---|
| **Healthy mega-atlas (4M)** | `Healthy_Single_Cell_Data/output/processed_data/processed_data_4Mcells.h5ad` | ~1,500+ | ~4,000,000 | Merged from 12 cohorts (OneK1K, COVID-19-UK, IAV, BCG, Pbmc_ageing, MS-Zhang, HCA1M, 1M-scBloodNL, etc.); 273 GB |
| Per-cell-type atlases | `Healthy_Single_Cell_Data/output/processed_data/processed_data_per_celltype/` | — | — | Individual h5ad per major and minor cell type |
| TrajDynamics data | `Healthy_Single_Cell_Data/output/TrajDynamics_data/` | — | — | Processed per cohort for trajectory analysis |

### scRNA-seq — Disease (processed, ready to use)

| Dataset | File | Disease | Source |
|---|---|---|---|
| MS | `Diseased_Single_Cell_Data/processed_data/ms_processed2.h5ad` | Multiple Sclerosis | GSE144744 |
| T1D | `Diseased_Single_Cell_Data/processed_data/t1d_processed2.h5ad` | Type 1 Diabetes | Synapse:syn53641849 |
| IBD | `Diseased_Single_Cell_Data/processed_data/ibd_processed2.h5ad` | Inflammatory Bowel Disease | — |
| PSA | `Diseased_Single_Cell_Data/processed_data/psa_processed2.h5ad` | Psoriatic Arthritis | GSE194315 |
| ME-CFS | `Diseased_Single_Cell_Data/processed_data/mecfs_processed2.h5ad` | ME/Chronic Fatigue Syndrome | GSE214284 |
| HCV | `Diseased_Single_Cell_Data/processed_data/hcv_processed2.h5ad` | Hepatitis C | — |
| HDV/HBV | `Diseased_Single_Cell_Data/processed_data/hdv_hbv_processed2.h5ad` | Hepatitis D/B | — |
| Long COVID | `Diseased_Single_Cell_Data/processed_data/lc_processed2.h5ad` | Long COVID | — |
| Gout | `Diseased_Single_Cell_Data/processed_data/gout_processed2.h5ad` | Gout | GSE217561 |
| Acute Gout | `Diseased_Single_Cell_Data/processed_data/ag_processed2.h5ad` | Acute Gout | — |
| SLE (2nd cohort) | `Diseased_Single_Cell_Data/processed_data/sle_processed2.h5ad` | SLE | GSE135779 |
| RA | `Diseased_Single_Cell_Data/initial_data_downloaded/RA/ac9c13da-7134-4d09-8086-d0933cbdba41.h5ad` | Rheumatoid Arthritis | CellxGene |
| JDM | `Diseased_Single_Cell_Data/initial_data_downloaded/JDM/` | Juvenile Dermatomyositis | CellxGene |
| Large-scale COVID | `Diseased_Single_Cell_Data/initial_data_downloaded/LargeScaleCovid/` | COVID-19 | GSE158055 |

### Multiome (scRNA-seq + scATAC-seq)

| Cohort | Location | Disease | Donors | Cells | Age | Sex | Paired RNA+ATAC | Stimulation | Modalities | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **IBD multiome** | `cohorts/IBD/multiome_processed/` | Crohn's Disease + Ulcerative Colitis | 79 sample visits (subset of 221 donors in phenotype) | 120,361 | 18–74 (median 36.5) | Mixed (F > M) | ✅ Yes (10x Multiome, same cells) | LPS, S. salmonella, RPMI (unstimulated) | RNA (`rna.h5ad`, 24,978 genes) + ATAC (`atac.h5ad`, 182,416 peaks) + Seurat (`seurat.rds`); clinical metadata in `phenotype.xlsx` | ✅ Ready |
| **Long COVID multiome** | `cohorts/LongCovid/multiome_processed/` | Long COVID + Psoriatic Arthritis (PA) | ~36 (9 pools × 4 donors; genotype README: 25 LC + 6 healthy) | — | — | — | ✅ Yes (10x Multiome) | With/without ex-vivo stimulation | Seurat RDS only (`bothCohorts_annotated_4Mods_WithLinkedPeaks.rds`, `stim_lc_peak_chromvar_alllinks_clinic.rds`); no h5ad | ⚠️ R/Seurat only |
| **DSolve/HDV multiome** | `cohorts/Dsolve_HDV/scATACseq_processed/` + `scRNAseq_processed/` | Hepatitis D/B (HDV/HBV) + 6 Healthy-IBD controls | 106 total (100 HDV, 6 Healthy-IBD); 93 with both RNA+ATAC assigned | — | — | — | ⚠️ Separate pipelines (RNA and ATAC processed independently) | None (longitudinal: 6 visit timepoints) | Count folders only; no merged h5ad | ⚠️ Raw counts only |

### scATAC-seq only

| Cohort | Location | Notes |
|---|---|---|
| CGD | `cohorts/CGD/ATACseq_raw/` | Chronic Granulomatous Disease |
| 20HSCs | `cohorts/20HSCs_project/scATACseq_processed/` | Hematopoietic stem cells |
| SI | `cohorts/SI/ATACseq_raw/` | Systemic inflammation cohort |
| INCENTIVE | `cohorts/INCENTIVE/scATACseq_processed/` | — |

### CITE-seq (Protein + RNA)

| Cohort | Location | Notes |
|---|---|---|
| HDV | `cohorts/HDV/CITEseq_processed/` | Hepatitis D |
| HDV pilot | `cohorts/HDV_pilot/CITEseq_raw/` | — |
| Liver Cancer | `cohorts/LiverCancer_Order_ID-24-0182/CITEseq_raw/` | — |

### Spatial Transcriptomics (Visium)

| Project | Location | Tissue / Disease |
|---|---|---|
| MTB Granuloma | `Spatial_Transcriptomics_Projects/MTB_Granuloma/` | Granuloma — Tuberculosis |
| Skin HSV | `Spatial_Transcriptomics_Projects/Skin_HSV/` | Skin — Herpes Simplex |
| Tendinopathy | `cohorts/Tendinopathy_From_Tran/spatial_raw/` | Tendon |
| DL_ST_SC | `DL_ST_SC/` | In progress |

### Proteomics (Olink / SomaScan)

| Cohort | Location | Notes |
|---|---|---|
| 2000HIV | `cohorts/2000HIV/proteomics_processed/` | HIV cohort |
| BCG prime | `cohorts/BCG_prime/proteomics_raw/` | BCG vaccination |
| D-Solve | `cohorts/D-Solve/proteomics_raw/` | — |
| Olink LongCovid & PA | `cohorts/Olink_LongCovidandPA/proteomics_raw/` | NPX format (wide + long), ready to use |
| Flu Vaccine (Portugal) | `cohorts/FluVaccine_autoImmune_Portugal/proteomics_raw/` | Vaccine response |
| Fatigue | `cohorts/Fatigue/proteomics_raw/` | ME/CFS-related fatigue |
| LongCovid + HDV | `cohorts/LongCovid_and_HDV_Dec2024/proteomics_raw/` | — |

### Metabolomics

| Cohort | Location | Notes |
|---|---|---|
| D-solve | `cohorts/D-solve/metabolomics_raw/` | — |
| BCG prime | `cohorts/BCG_prime/` | — |
| Long COVID | `cohorts/LongCOVID/metabolomics_raw/` | — |
| NOURISHED IBD | `cohorts/NOURISHED_IBD/metabolomics_raw/` | IBD metabolomics |
| SI | `cohorts/SI/metabolomics_raw/` | MS2 fragmentation results |
| Fatigue | `cohorts/Fatigue/metabolomics_raw/` | — |

### DNA Methylation

| Cohort | Location | Notes |
|---|---|---|
| 2000HIV | `cohorts/2000HIV/methylation_processed/` | Processed methylation array |
| BCG prime | `cohorts/BCG_prime/methylation_processed/` | — |
| iMED | `cohorts/iMED/methylation_processed/` | — |
| Monocytes uric acid | `cohorts/monocytes_uric_acid/methylation_raw/` | Gout-related |
| HDV | `cohorts/HDV/methylation_raw/` | — |
| HFGP & SI | `cohorts/HFGP_and_SI/methylation_raw/` | — |

### Bulk RNA-seq

| Cohort | Location | Disease / Condition |
|---|---|---|
| HINT GOUT | `cohorts/HINT_GOUT/RNAseq_processed/` | Gout |
| 100LPS Mono | `cohorts/100LPS_Mono/` | LPS stimulation, 100 donors, 2 timepoints |
| SI | `cohorts/SI/RNAseq_processed/` | Systemic inflammation |
| VZV | `cohorts/VZV/RNAseq_raw/` | Varicella-Zoster Virus |
| HSV | `cohorts/HSV/RNAseq_raw/` | Herpes Simplex Virus |
| FUSE SEPSIS | `cohorts/FUSE_SEPSIS/RNAseq_raw/` | Sepsis |
| Liver TX | `cohorts/liverTX/RNAseq_processed/` | Liver transplant |

### Cytokine Assays (ELISA / Luminex)

| Cohort | Location | Notes |
|---|---|---|
| 200FG | `cohorts/200FG/cytokines_raw/` | Trained immunity, 120 samples |
| BCG prime | `cohorts/BCG_prime/cytokines_raw/` | BCG vaccination |
| SI | `cohorts/SI/cytokines_processed/` + `cytokines_raw/` | — |
| HSV | `cohorts/HSV/cytokines_raw/` | — |
| VZV | `cohorts/VZV/cytokines_raw/` | — |
| IBD | `cohorts/IBD/cytokines_processed/` | — |

### Genotype / GWAS

Many cohorts have processed genotype data. Key ones:

| Cohort | Location |
|---|---|
| 200FG | `cohorts/200FG/genotype_processed/` |
| 2000HIV | `cohorts/2000HIV/genotype_raw/` |
| 600T1D | `cohorts/600T1D/genotype_processed/` |
| IBD | `cohorts/IBD/genotype_processed/` |
| LongCovid | `cohorts/LongCovid/genotype_processed/` |
| ALLIANCE | `cohorts/ALLIANCE/genotype_processed/` |
| sceQTLGen | `sceQTLGen/outputs/` | Single-cell eQTL results (WG1/WG2/WG3) |

### Perturb-seq (CRISPR screens)

| Dataset | Location | Cell type |
|---|---|---|
| Replogle K562 | `PerturbationDataset/Perturb_seq_dataset_Replogle_K562/replogle_train_sc.h5ad` | K562 (leukemia) |
| Xiara HCT116 | `PerturbationDataset/Perturb_seq_dataset_Xiara/HCT116_filtered_dual_guide_cells.h5ad` | Colon cancer |
| Xiara HEK293T | `PerturbationDataset/Perturb_seq_dataset_Xiara/HEK293T_filtered_dual_guide_cells.h5ad` | HEK cells |

### Flow Cytometry

| Cohort | Location |
|---|---|
| 2000HIV | `cohorts/2000HIV/flowcytometry_processed/` |
| Long COVID | `cohorts/LongCovid/fcsData_raw/` + `flowcytometry_raw/` |
| SI | `cohorts/SI/flowcytometry_raw/` |

### Microbiome

| Cohort | Location |
|---|---|
| SI | `cohorts/SI/microbiome_raw/` |
| Fatigue | `cohorts/Fatigue/microbiome_raw/` |

### ChIP-seq

| Cohort | Location |
|---|---|
| CMV chip | `cohorts/CMV_chip/ChIPseq_raw/` |

---

## Integration Priority for `agentic_central`

The following datasets are highest priority to process and add to `datalake/omics/` (TF activity + pseudobulk):

| Priority | Dataset | Reason |
|---|---|---|
| 🔴 | MS, RA, IBD, T1D, PSA (processed scRNA) | Disease TF signatures for multi-disease atlas |
| 🔴 | Long COVID scRNA | Acute vs. persistent immune dysregulation |
| 🟡 | IBD + LongCovid multiome | First ATAC+RNA joint analysis in the system |
| 🟡 | Olink LongCovid & PA proteomics | Protein-level validation of TF signatures |
| 🟡 | 200FG cytokines + genotype | Link innate immune responses to genetics |
| 🟢 | Spatial transcriptomics (MTB, HSV) | Tissue-context immune programs |
| 🟢 | Perturb-seq (Replogle) | Functional validation of TF targets |
