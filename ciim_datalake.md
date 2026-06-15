# CIIM Datalake
Datasets physically present under `/vol/projects/CIIM/`. Access them directly via the paths below.

---

## SI — Senior Individuals (multiomics cohort)

**Base path:** `/vol/projects/CIIM/cohorts/SI/`

279 donors with full phenotype data (651 sample entries across visits); N=531 used in QTL mapping (genotype + cytokine overlap).
- **Age:** 22–85 y (mean 63.8 y)
- **Sex:** 187 Male / 92 Female
- **Ethnicity:** predominantly Caucasian (273/279; ~98%)

| Modality | Status | Notes |
|---|---|---|
| **ATACseq** | raw | `ATACseq_raw/` |
| **RNAseq** | raw + processed | 205 donors; baseline (99 samples) + 21 stimulation conditions at 24h (LPS n=271, NS n=202, Pam3Cys n=182, CpG n=154, polyIC n=154; plus smaller sets: influenza/varilrix/shingrix/ns-antigen n=10 each) and 7d (NS n=138, VZV-oka n=141, CMV/HSV/HSV-peptide/influenza/VZV/VZV-peptide/CoV-N/CoV-C/CoV-ctrl n=35–39); ~13,107 genes after filtering; CPM-normalized per stimulation at `RNAseq_processed/counts/2-norm/filter/{stim}_cpm.tsv`; raw tximport RDS at `RNAseq_processed/counts/` (baseline/24h/7d) — do not use the batch-corrected version. |
| **Cytokines** | raw + processed | ~47 cytokines × 15 stimulations (LPS, polyIC, pam3cys, CpG, RPMI, varilrix, flu, HSV, VZV, CMV, CoV-N/C/ctrl) at 24h and 7d → ~500+ phenotypes; log2 + z-score at `cytokines_processed/` |
| **Flow cytometry** | raw | `flowcytometry_raw/` |
| **Genotype** | raw + imputed | imputed VCFs at `genotype_processed/imputed_vcf/` |
| **Metabolomics** | raw | `metabolomics_raw/` |
| **Methylation** | raw + processed | `methylation_processed/` |
| **Microbiome** | raw | `microbiome_raw/` |
| **Phenotype** | processed | comorbidity data, review paper |

QTL results (5 layers: cQTL, eQTL, eQTL-24h, meQTL, metabQTL) at `/vol/projects/CIIM/meta_cQTL/out/SI-senior/`; each layer has per-chr full stats, genome-wide, study-wide, and nominal outputs.

---



## BCG_prime / BCG_Prime — BCG Prime cohort 
#TOEVAL: process and merge datasets?
The BCG-PRIME trial — a randomized controlled trial in elderly individuals (>60 years) testing whether BCG vaccination reduces morbidity/adverse events.

- **Disease / context:** Aging; BCG vaccination RCT (BCG vs placebo)
- **Population:** Elderly (>60 yrs), predominantly Caucasian
- **Sample size:** 6,112 participants total; 471 with genomics
- **Long-term follow-up:** BCG-LT component includes participants from both PRIME and the BCG-CORONA-ELDERLY trial
- **Phenotypes:** demographics, comorbidities, adverse events, COVID events, vaccines
- **scRNAseq status:** Raw demultiplexed counts only (87+ pools in `BCG_Prime/scRNAseq_processed/`); no merged/processed h5ad
- **scATACseq status:** Raw demultiplexed (in `BCG_Prime/scATACseq_processed/`); no merged/processed h5ad

| Modality | Status | n samples | Details |
|---|---|---|---|
| Cytokines | raw | 674 samples | whole blood, 48h; 7 cytokines (IFN-α/γ, IL-1β, IL-1RA, IL-6, IL-10, TNF-α); 9 stimulations (RPMI, LPS, R848, S.aureus, Candida, Wuhan/Delta/Omicron spike, influenza) |
| Flow cytometry | raw | — | `flowcytometry_raw/` |
| Genotype | raw + processed | 661 samples | raw PLINK bed (`BCG_prime_combined`); TOPMed-imputed (`genotype_processed/`) |
| Metabolomics | raw | 499 (LUMC) + 315 (RADN) | 172 metabolites per site (NMR lipoprotein panel) |
| Methylation | raw + processed | 383 samples | EPIC 850k array; M-values in `methylation_processed/BCG_prime_Mval.rdata` |
| Proteomics | raw | 675 (RADN T1) + 107 (RADB) | Olink (92 proteins per panel); `olink_RADN_T1.tsv`, `olink_RADB.tsv` |
| Phenotype | raw | 6,112 total | `PRIME_studydata.xlsx`, AE data, LT follow-up |
| **scRNAseq** | raw (demultiplexed) | ~87 pools | `BCG_Prime/scRNAseq_processed/`; no merged h5ad yet |
| **scATACseq** | raw (demultiplexed) | — | `BCG_Prime/scATACseq_processed/`; no merged h5ad yet |

---

## 2000HIV 
PBMC multi-omics cohort of People Living with HIV (PLHIV).

- **Disease:** HIV (all PLHIV; no healthy controls in scRNAseq)
- **Population:** Multi-ethnic (White, Black, Mixed, Asian, Hispanic); multi-center (EMC, OLV, ETZ, RUMC; Netherlands)
- **scRNAseq donors:** 290 total in h5ad (224 in final selection/metadata file)
- **scRNAseq cells:** 698,742 cells × 29,021 genes
- **Age range:** 23–77 years
- **Sex:** ~77% male (536,821), ~23% female (161,921)
- **Cell types (lvl0):** T cells (381,950), Monocytes (193,438), B/Plasma (55,619), NK (47,537), DCs (17,842), other (2,356)
- **CMV split:** `2000HIV_PLHIV_CMV.h5ad` available for CMV+/− stratified analyses
- **scRNAseq metadata:** `240318_Selection_scRNAseq_FINALMetadata.n=224.xlsx`

| Modality | Status | n samples | Details |
|---|---|---|---|
| RNAseq | processed | — | bulk PBMC; DESeq2 object + raw/normalized count RDS; batch-correct for season, sex, center |
| Cytokines | raw | 1,793 samples | PBMC 24h; 13 cytokines (IL-1β, IL-6, IL-8, IL-10, IL-17, IL-22, IL-1RA, IFN-γ, TNF-α, MCP-1, MIP-1α, IL-5, all-cyt); 15 stimulations (RPMI, LPS, polyIC, MTB, CMV, HIV env, Candida, E.coli, S.aureus, S.pneumoniae, PHA, IMQ, IL-1α, Candida hyphae, all-stim) |
| Flow cytometry | processed | 1,423–1,434 samples | 3 panels; ABS (1,423 × 415 vars), PER/MFI (1,434 × 356/521 vars); centers: EMC, ETZ, FAM, OLV, RAD |
| Genotype | raw | 1,356 samples | array-genotyped; all-ethnicities + per-ancestry splits (European, African) in PLINK bed format |
| Methylation | raw + processed | 1,914 samples | EPIC 850k array; discovery (n=1,592) + validation (n=322); M-values in `methylation_processed/Combined/` |
| Proteomics | raw + processed | 1,910 samples | Olink Explore 3072; 2,367 proteins; bridging-normalized; also older panel (641 × 1,463 proteins) |
| **scRNAseq** | processed | 290 donors / 698,742 cells | `2000HIV_PLHIV.h5ad` (29,021 genes); CMV split: `2000HIV_PLHIV_CMV.h5ad`; metadata: `240318_Selection_scRNAseq_FINALMetadata.n=224.xlsx` |

---

## LongCovid — Long COVID multiome cohort

Multimodal Long COVID cohort. In-house modalities (multiome, flow cytometry, proteomics, genotype, metabolomics) plus processed RDS objects of public data (Mayo/GSE263817).

**path**: `/vol/projects/CIIM/processed/multiome/LongCovid/`; other modalities under `/vol/projects/CIIM/cohorts`

| Modality | Status | Path | Details |
|---|---|---|---|
| **Multiome (snRNA+snATAC)** | processed | `processed/multiome/LongCovid/withoutStim/bothCohorts_annotated_4Mods_WithLinkedPeaks.rds` (9.96 GB) | 10x Multiome, 117,598 cells (discovery 87,138 + replication 30,460), 4 assays RNA/ATAC/peaks(171,844)/chromvar; metadata `CellType`, `TimePointAll` (HC/T1–T5), `RecovStatus`, `highestWHOscore`/`visitWHOscore`. |
| Multiome — stim subset | processed | `processed/multiome/LongCovid/withStim/stim_lc_peak_chromvar_alllinks_clinic.rds` (13 GB) | *P. aeruginosa*-stimulated functional subset (12 donors: LCAM7+LCAS5+RLC6, T1/T2/T4/T5); embeds clinical columns `fas_score`, `blood_gases_po2`, `score_mmrc` (now also available cohort-wide in the metadata table below). |
| **Clinical metadata table** | processed | `datalake/covid/metadataBothDiscoveryReplicationCohort_toUseForAnalysis_withDyspnea.xlsx` | Full-cohort per-visit clinical table, **50 patients / 83 patient-visits, T1–T5, both discovery + replication**. Join key `PatientID`/`TimePoint` (also `PatientID_TP`). Columns: `Age`, `Sex`, `HighestWHOscore`/`VisitWHOscore` (→ multiome `highestWHOscore`/`visitWHOscore`), lung function `TLC%`/`DLCO%`/`FEV%`/`FVCEX%`/`ResVol%`, blood gases `pCO2`/`pO2` (=`blood_gases_po2`), `FA_Score`+`FA_Score_Category` (=`fas_score`), `score_mmrc (Dyspnoe)` (=`score_mmrc`), `Recovered` (Yes/No). |

| Flow cytometry | raw | `cohorts/LongCovid/flowcytometry_raw/AGLi/` | 11-protein Sony ID7000; Panel 1/2/3, per-sample; numeric sample IDs (e.g. 4896, BL44, 2314). No clinical labels attached. |
| Proteomics | raw | `cohorts/Olink_LongCovidandPA/proteomics_raw/` + `cohorts/LongCovid_and_HDV_Dec2024/proteomics_raw/` | plasma Olink NPX (LC + PA; LC + HDV Dec-2024 batch). |
| Genotype | processed | `cohorts/LongCovid/genotype_processed/` | genotype array; used for Souporcell demultiplexing of the multiome. |
| Metabolomics | raw | `cohorts/LongCOVID/metabolomics_raw/` | plasma metabolomics. |

(`cohorts/LongCovid/multiome_processed/withoutStim|withStim/` mirrors the `processed/multiome/LongCovid/` objects.)

> **Note — dataset linkage.** The subsection groups one cohort profiled across modalities; the multiome is the anchor. Three tiers of linkage:
> - **Mechanically coupled to the multiome:** *Genotype* is used for Souporcell demultiplexing of the pooled multiome (assigns nuclei → donor). The *stim subset* is a 12-donor subset of the multiome itself (the only object carrying clinical columns).
> - **Same cohort, donor-level (join intended, not yet on disk):** *Flow cytometry* (numeric sample IDs, no clinical labels — ID crosswalk to multiome donors pending), *Proteomics* (plasma Olink), *Metabolomics* (plasma).
> - **Not the same individuals:** the two `VirginiaData/` objects are public Mayo/GSE263817 data (metadata key `PASC_cat`, distinct from the in-house `TimePointAll`/`RecovStatus`) — co-located in the folder for comparison only, not cohort donors.

> **Note — clinical phenotype columns.** Per-visit clinical scores (`fas_score`, `score_mmrc`, `blood_gases_po2`) are now available cohort-wide in `datalake/covid/metadataBothDiscoveryReplicationCohort_toUseForAnalysis_withDyspnea.xlsx` (50 patients / 83 visits, T1–T5; join on `PatientID`/`TimePoint`), in addition to the 12-donor stim subset object. Controlled-access (EGAS50000000142/143).
> ✅ RESOLVED (2026-06-15): full-cohort clinical table received and stored under `datalake/covid/`.
> 🕓 STILL PENDING: ID crosswalk from the multiome `PatientID`s to the flow-cytometry sample IDs (`4896`/`BL44`/…) — not provided by this table.

