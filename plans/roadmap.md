# Agentic Immunology — Roadmap

> Goal: Build a complete, publishable agentic system for immunology research — integrating curated omics data, modular tools, and demonstrated applications.

---
## Summary Stats
- Precomputed signatures for new diseases (RA, IBD, MS, COVID)
- Precomputed CCC signatures for diseases/aging

## Data Gaps to Fill

### 1.1 Disease Coverage 
- **Rheumatoid Arthritis (RA)** — scRNA-seq PBMC/synovial (e.g., Zhang et al. 2023 Nature)
- **IBD / Crohn's** — intestinal immune scRNA-seq
- **Multiple Sclerosis (MS)** — CSF + blood scRNA-seq
- **COVID-19 / Infection** — acute vs resolved PBMC (e.g., Wilk et al., COMBAT cohort)
- **Type 1 Diabetes (T1D)** — islet-infiltrating immune cells
- Add disease TF/gene-expression summary stats for each (mirroring existing SLE stats)

### 1.2 Multi-Omics
- **ATAC-seq** — chromatin accessibility in aging/disease (e.g., CATLAS, Calderon et al.)
- **Proteomics** — plasma proteome aging (SomaScan/Olink, e.g., Lehallier et al.)
- **Metabolomics** — immune metabolic aging markers
- **eQTL / colocalization** — GTEx immune cell eQTLs to link GWAS → causal genes

### 1.3 Repertoire Data
- **TCR-seq** — clonotype diversity 
- **BCR-seq** — B cell repertoire 

### 1.4 Spatial & Tissue-Resident Immunity
- Spatial transcriptomics (Visium/Xenium) of lymph node / spleen
- Tissue-resident immune cells: lung, gut, liver (for beyond-PBMC analysis)

### 1.5 Longitudinal Data
- At least one cohort with repeated sampling (vaccination, therapy) to enable temporal modeling

---

## Tool Gaps to Fill

### 2.1 Repertoire Analysis
- `analyze_tcr_repertoire` — clonotype diversity, clonal expansion, V(D)J usage, aging metrics
- `analyze_bcr_repertoire` — somatic hypermutation, class switching, clonal topology

### 2.2 Trajectory & Differentiation
- `infer_pseudotime` — RNA velocity / diffusion pseudotime (scVelo, Diffusion Maps)
- `infer_cell_fate` — lineage tracing, differentiation state scoring

### 2.3 Cell-Cell Communication
- `infer_ccc_liana` — wrapper around LIANA for L-R inference (add to CIIM tools, expose cleanly)
- `compare_ccc_conditions` — differential CCC across age/disease/drug conditions

### 2.4 Multi-Omics Integration
- `integrate_atac_rna` — WNN or MOFA+ for joint embedding
- `motif_activity_from_atac` — chromVAR TF motif activity from ATAC
- `integrate_proteomics` — correlation/regression of plasma proteins with scRNA TF activity

### 2.5 Deconvolution
- `deconvolve_bulk_rna` — CIBERSORTx / BLADE for cell-type fractions from bulk tissue RNA

### 2.6 Genetic & Colocalization
- `run_eqtl_coloc` — colocalization of eQTL and GWAS signals at immune loci
- `run_mendelian_randomization` — causal inference for immune aging traits

---

## Benchmark
### Previous benchmarks
- general immunology quesions -
### Recovery questions
#### Immune aging and disease
recover main findings of hiara

---

## Case application
Each code.py should be stored for reproducibility. 

### Immune aging clocks


### Characterize immune aging and disease
- map aging TFs to cellular functions 

### Multi-Disease Immune Atlas
- 

### Drug Repurposing for Immune disease and aging
- 

### Disease/aging target discovery and prioritization
- 



## Skills
- `tcr_bcr_analysis.md` — repertoire analysis workflow
- `multi_omics_integration.md` — ATAC + RNA joint analysis
- `genetic_analysis.md` — eQTL, GWAS colocalization, MR
- `trajectory_analysis.md` — pseudotime, RNA velocity

## Tests
- Add integration tests for all new tools (mirror existing `test_*.sh` pattern)
- Add a smoke-test script that runs the full drug screening pipeline end-to-end on a small subset

