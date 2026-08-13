# IBD — File List

All files located in `${CIIM_DATALAKE_DIR}/omics/IBD/`.

PBMC multiome data (scRNA-seq + scATAC-seq, paired) from IBD patients (Crohn's disease and ulcerative colitis). 120,361 cells; no healthy controls. 3 stimulation conditions: LPS, RPMI (control), *S. salmonella*. 5 major cell types (CD4 T, Monocytes, B, CD8 T, NK) and 10 subtypes (Naïve CD4 T, Memory CD4 T, Macrophages, Tregs, MAIT, Plasmablasts, etc.).

- **Disease:** CD (62,385 cells) + UC (57,976 cells)
- **Assays:** RNA (24,978 genes), ATAC (182,416 peaks)
- Raw Seurat object: `/vol/projects/CIIM/IBD/Functional_Multiome_2023/data/Seurat.rds`
- Processed h5ad: `${CIIM_DATALAKE_DIR}/omics/IBD/rna.h5ad`, `${CIIM_DATALAKE_DIR}/omics/IBD/atac.h5ad`
- Pseudobulk RNA: `${CIIM_DATALAKE_DIR}/omics/IBD/rna_bulk.h5ad` — 395 pseudo-samples × 24,978 genes; grouped by (celltype, donorID, stimulation); `.X` = CPM log1p normalized (no `.layers`); `.obs`: `celltype`, `donorID`, `stimulation`, `disease`, `gender`, `n_cells`
