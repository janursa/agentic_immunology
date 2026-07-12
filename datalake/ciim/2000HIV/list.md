# 2000HIV — File List

Physically stored under `/vol/projects/CIIM/` — not mirrored into `datalake/`.

PBMC multi-omics cohort of People Living with HIV (PLHIV).
Base dir: `/vol/projects/CIIM/`

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
