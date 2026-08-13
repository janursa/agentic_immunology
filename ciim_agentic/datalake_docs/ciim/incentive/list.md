# INCENTIVE — File List

Physically stored under `/vol/projects/CIIM/` — not mirrored into `${CIIM_DATALAKE_DIR}/`.

PBMC multiome data (scRNA-seq + scATAC-seq, paired) from an elderly influenza vaccine cohort. 37 donors (age 60–76 y; 80 male / 68 female sample entries), 4 longitudinal timepoints (V2–V5). Responder categories: DR, TR, QR, QNR. Includes influenza antibody titres (H1N1, H3N2, B/Washington, B/Phuket) at D0 and D28. Clinical + demultiplexing metadata in `demultiplexedDonorMetadata.csv`.

- scRNA-seq (raw per-pool count matrices, not merged, not cell-type-annotated, no pseudobulk available): `/vol/projects/CIIM/processed/scRNAseq/INCENTIVE/`
- scATAC-seq (per-pool processed peak/fragment counts, not cell-type-annotated, no pseudobulk available): `/vol/projects/CIIM/cohorts/INCENTIVE/scATACseq_processed/` and `/vol/projects/CIIM/processed/scATACseq/INCENTIVE/`
- **Before any cell-type-resolved or pseudobulk analysis**: cell-type annotation + pseudobulking must be run first (no ready-made `_bulk`/`_bulk_minor` files exist for this cohort, unlike `hira`). Budget this as its own step when planning to use INCENTIVE.
