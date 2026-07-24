# LongCovid — Long COVID Multiome Cohort — File List

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
