# Planned Datasets

Datasets present on disk under `/vol/projects/CIIM/processed/` but **not yet integrated** into the agentic datalake (`datalake/omics/`) or fully documented in `ciim_dataset.md`.

All paths are relative to `/vol/projects/CIIM/`.

---

## scRNA-seq

### CXCL9_TI (Trained Immunity)
**Path:** `processed/scRNAseq/CXCL9_TI_OrderID_25_0014/`  
**Disease / Condition:** Aging / Trained Immunity  
**Donors:** 7 (aging cohort, pools AG1–AG16)  
**Cells:** not yet aggregated (raw counts per pool)  
**Age:** not in demux key  
**Sex:** not in demux key  
**Stimulation:** unknown (CXCL9-related stimulation inferred from name)  
**Modality:** scRNA-seq only  
**Status:** raw counts + SoupOrCell demultiplexed; no merged h5ad  
**Notes:** New CXCL9 experiment separate from `CXCL9_sc.h5ad` already in datalake. Demux key: `CXCL9_TI_demultiplexingKey.csv`

---

### EuropeanAfricnAsian_COVIAV (Multi-ethnic COVID Vaccine)
**Path:** `processed/scRNAseq/EuropeanAfricnAsian_COVIAV/`  
**Disease / Condition:** COVID-19 vaccine response  
**Donors:** multi-ethnic cohort (European, African, Asian); exact n not in local metadata  
**Cells:** available in Seurat RDS (`seurat_Wholedata.rds`) + raw count matrix  
**Age:** not in local metadata  
**Sex:** not in local metadata  
**Stimulation:** none (vaccine response, not ex-vivo)  
**Modality:** scRNA-seq + ADT (CITE-seq; `filtered_ADT_count_matrix` in raw folder)  
**Source:** Nature 2023, doi:[10.1038/s41586-023-06422-9](https://doi.org/10.1038/s41586-023-06422-9), Quintana-Murci lab  
**PI:** Lluis Quintana-Murci  
**Status:** Processed Seurat RDS + raw count matrices; no h5ad  
**Notes:** Public dataset. Multi-ethnic comparison of innate immune variation after COVID vaccination.

---

### HCV_KI (HCV NK cells — Karolinska)
**Path:** `processed/scRNAseq/HCV_KI/`  
**Disease / Condition:** Hepatitis C Virus (HCV) — NK cell focus  
**Donors:** not in local metadata (analysis outputs only)  
**Cells:** analysis outputs only (no raw h5ad or counts folder)  
**Modality:** scRNA-seq (NK-focused)  
**PI:** Chengjian Xu  
**Status:** Analysis results only (`results/` with DEG tables, PDFs); no raw data locally  
**Notes:** Separate from `HCV_sc.h5ad` already in `Diseased_Single_Cell_Data`. Three conditions: screen, follow-up, healthy. Includes pySCENIC regulon analysis.

---

### INCENTIVE (Influenza Vaccine — Elderly)
**Path:** `processed/scRNAseq/INCENTIVE/`  
**Disease / Condition:** Influenza vaccine response (seasonal)  
**Donors:** 37 unique donors  
**Cells:** raw counts (countsFolder); not yet merged  
**Age:** 60–76 years (elderly cohort)  
**Sex:** 80 Male samples / 68 Female samples (across visits)  
**Stimulation:** none (longitudinal vaccine study)  
**Visits:** 4 timepoints: V2, V3, V4, V5  
**Responder categories:** DR (double responder), QR (quadruple responder), TR (triple responder), QNR (non-responder)  
**Modality:** scRNA-seq only (ATAC also in `processed/scATACseq/INCENTIVE/`)  
**Status:** raw counts + demultiplexed donor metadata; no merged h5ad  
**Notes:** Listed in `ciim_dataset.md` only for scATAC. Demux + clinical metadata: `demultiplexedDonorMetadata.csv`. Includes influenza antibody titres (H1N1, H3N2, B/Washington, B/Phuket) at D0 and D28.

---

### InfluenzaVaccination_RA (Influenza Vaccine — RA patients)
**Path:** `processed/scRNAseq/InfluenzaVaccination_RA/`  
**Disease / Condition:** Rheumatoid Arthritis (RA), seasonal influenza vaccination  
**Donors:** 36 unique donors  
**Cells:** raw counts (28 pools); not yet merged  
**Age:** not in demux key  
**Sex:** Female-heavy (138F / 78M sample entries across visits)  
**Stimulation:** LPS and RPMI (ex-vivo, paired conditions)  
**Seasons:** 2018/2019 and 2020/2021  
**Modality:** scRNA-seq (paired scATAC also in `processed/scATACseq/InfluenzaVaccination_RA/`)  
**Status:** raw counts + demux key (`poolInfo_merge_DemultiplexingKey.xlsx`); no merged h5ad  
**Notes:** Longitudinal flu vaccine response in RA patients across two seasons. LPS vs RPMI stimulation design.

---

### LiverCancer_Order_ID_24-0182 (2nd HCC)
**Path:** `processed/scRNAseq/LiverCancer_Order_ID_24-0182/`  
**Disease / Condition:** Hepatocellular Carcinoma — 2nd HCC (recurrence)  
**Donors:** 8 (H1–H8)  
**Cells:** raw counts; not yet merged  
**Age:** not in demux key  
**Sex:** not in demux key  
**Stimulation:** none  
**Modality:** scRNA-seq only (CITE-seq arm listed separately in `ciim_dataset.md` as `cohorts/LiverCancer_Order_ID-24-0182/CITEseq_raw/`)  
**Status:** raw counts + demux key (`LiverCancer_demultiplexingKey.csv`); no merged h5ad  
**Notes:** 2nd/recurrent HCC cohort. Different from `Liver_cancer` below.

---

### Liver_cancer (Liver Cancer — Yang Li lab)
**Path:** `processed/scRNAseq/Liver_cancer/`  
**Disease / Condition:** Liver Cancer (Hepatocellular Carcinoma)  
**Donors:** unknown  
**Cells:** Seurat RData object (`LC.RData`)  
**Age:** not in local metadata  
**Sex:** not in local metadata  
**Stimulation:** none  
**Modality:** scRNA-seq  
**PI:** Prof. Yang Li, Prof. Thomas Wirth  
**Status:** Seurat RData only; no h5ad  
**Notes:** Older liver cancer dataset. Possibly overlaps with or predates LiverCancer_Order_ID_24-0182.

---

### LongCovid_SimonSamples (Long COVID — Simon cohort)
**Path:** `processed/scRNAseq/LongCovid_SimonSamples/`  
**Disease / Condition:** Long COVID  
**Donors:** 8 patients  
**Cells:** raw counts (countsFolder); not yet merged  
**Age:** 21–63 years  
**Sex:** 5 Female, 3 Male  
**Stimulation:** none  
**Modality:** scRNA-seq  
**Status:** raw counts + patient metadata (`PatientInformation_LC_SimonSamples.xlsx`, `finalMetadata.csv`); no h5ad  
**Notes:** Small cohort with detailed clinical phenotyping — fatigue scores, pulmonary function (FeNo), walking distance (6-min test), pulse, concentration tests, clinical phenotype narratives. Separate from the main `LongCovid` multiome cohort.

---

### Lyme_cohort (Lyme Disease)
**Path:** `processed/scRNAseq/Lyme_cohort/`  
**Disease / Condition:** Lyme disease  
**Donors:** 5 (donor_7, donor_8, donor_9, donor_11, donor_13)  
**Cells:** raw counts (5 pools); SoupX-corrected RDS available (`soupx_rds/`)  
**Age:** not in demux key  
**Sex:** not in demux key  
**Stimulation:** none  
**Modality:** scRNA-seq  
**Status:** raw counts + SoupX RDS + demux key (`Lyme_demultiplexingKey.csv`); no merged h5ad  
**Notes:** Small cohort; genotype also available in combined Bonn 2024 batch (see Genotype section).

---

### Pan_Vaccine (Pan-Vaccine Study)
**Path:** `processed/scRNAseq/Pan_Vaccine/`  
**Disease / Condition:** Multi-vaccine response (pan-vaccine)  
**Donors:** ~36 pools of pooled donors; ~39 soupOrCell outputs; estimated ~815,000 total cells  
**Cells:** ~815,115 estimated across 36 pools (`all_metrics_summary.csv`)  
**Age:** not in local metadata  
**Sex:** not in local metadata  
**Stimulation:** none (vaccine response study)  
**Modality:** scRNA-seq (paired scATAC also in `processed/scATACseq/Pan_Vaccine/`)  
**Status:** raw counts; no merged h5ad  
**Notes:** Large cohort by cell count. Paired RNA+ATAC. Genotype available in `processed/genotype/RA_and_PanVaccine/` (127 samples).

---

## scATAC-seq (unpaired / no scRNA counterpart listed)

### InfluenzaVaccination_RA — ATAC arm
**Path:** `processed/scATACseq/InfluenzaVaccination_RA/`  
**Notes:** ATAC arm of the InfluenzaVaccination_RA scRNA cohort (see above). Raw counts only; no processed ATAC object.

### Pan_Vaccine — ATAC arm
**Path:** `processed/scATACseq/Pan_Vaccine/`  
**Notes:** ATAC arm of Pan_Vaccine scRNA cohort (see above). SoupOrCell demultiplexing scripts present; one pool (PVT1) processed. Paired with RNA.

---

## Genotype Batches

### RA_and_PanVaccine Genotype
**Path:** `processed/genotype/RA_and_PanVaccine/`  
**Samples:** 127 (PLINK .fam)  
**Format:** PLINK bed/bim/fam + VCF  
**Notes:** Combined genotype batch for RA (InfluenzaVaccination_RA) and Pan_Vaccine cohorts.

### INCENTIVE Genotype
**Path:** `processed/genotype/incentive/`  
**Samples:** 38 (PLINK .fam)  
**Format:** PLINK bed/bim/fam + VCF  
**Notes:** Genotype for INCENTIVE influenza vaccine elderly cohort.

### HDV_CCL9_2ndHCC_8longCOVID_Lyme_Healthy_Bonn2024
**Path:** `processed/genotype/HDV_CCL9_2ndHCC_8longCOVID_Lyme_Healthy_Bonn2024/`  
**Samples:** 23 (from `chr_d31_map.txt`)  
**Format:** VCF (imputed, GRCh38)  
**Notes:** Combined 2024 Bonn genotype batch covering HDV, CXCL9 TI, 2nd HCC, 8 Long COVID, Lyme, and healthy samples. Used for demultiplexing across multiple cohorts.

### CMV_knockout Genotype
**Path:** `processed/genotype/CMV_knockout/`  
**Samples:** unknown (VCF only, no .fam)  
**Format:** VCF (`allchr.vcf.gz`, `allchr_relabelled.vcf.gz`)  
**Notes:** Genotype for CMV knockout experiment. No .fam file; sample count not directly readable without decompressing.

---

## Integration Priority

| Priority | Dataset | Reason |
|---|---|---|
| 🔴 | INCENTIVE (scRNA) | Large cohort with paired ATAC + genotype; rich clinical metadata (responders); elderly immune response |
| 🔴 | InfluenzaVaccination_RA | Paired RNA+ATAC+genotype; disease (RA) + stimulation (LPS/RPMI); two seasons |
| 🔴 | Pan_Vaccine | ~815K cells; paired RNA+ATAC+genotype (127 samples) |
| 🟡 | EuropeanAfricnAsian_COVIAV | Public Nature paper; multi-ethnic; ADT+RNA; directly usable |
| 🟡 | Lyme_cohort | New disease type; SoupX RDS available; small but ready |
| 🟡 | LongCovid_SimonSamples | Detailed clinical phenotypes; complements main LongCovid multiome |
| 🟡 | LiverCancer_Order_ID_24-0182 (scRNA arm) | Paired with CITE-seq already noted; complete the modality |
| 🟢 | CXCL9_TI | Complements existing CXCL9 perturbation dataset in datalake |
| 🟢 | HCV_KI | Analysis-only; would need raw data access to integrate |
| 🟢 | Liver_cancer | Older dataset; overlap with newer HCC cohort unclear |
