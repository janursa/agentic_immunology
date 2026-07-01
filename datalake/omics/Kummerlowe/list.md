# Kummerlowe Drug Perturbation — File List

All files located in `datalake/omics/Kummerlowe/`.  
**Reference:** Kummerlowe et al., *Nat Biotechnol* 42, 1693–1703 (2024). DOI: 10.1038/s41587-024-02403-z  
**Source:** Single Cell Portal SCP2622

---

## scp2622_val_sc.h5ad
**SCP2622 Compressed Drug Screen — Single-Cell**
Primary human PBMC drug perturbation screen (1 healthy donor). 90 small-molecule compounds (Broad Drug Repurposing Hub, known MOA) tested under Control (DMSO), IFNβ, and LPS stimulation. Compressed screen design: 6 drugs pooled per well, 3 replicate wells per drug. Individual drug assignment requires cNMF deconvolution.  
Cells: 120,174 | Genes: 15,313  
obs columns: sample_id, stimulation, is_assigned, well_id, dest_row, dest_col, drug_pool, is_control, CT_Major, CT_Minor, CT_Major_percell, CT_Minor_percell, leiden, n_genes_by_counts, total_counts, pct_counts_mt, disease, organ, sex  
layers: lognorm (normalize_total 1e4 + log1p)  
obsm: X_pca, X_umap  
Stimulation conditions: S1–S6 = Control · M1–M6 = IFNβ · W1–W6 = LPS
