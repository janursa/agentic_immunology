## Singularity Images

| Image | Path | Use for |
|-------|------|---------|
| `biomni_full.sif` | `agentic_immunology/singularity/biomni_full.sif` | Default — full bio stack (genomics, pharmacology, ML, NLP) |
| `ciim.sif` | `agentic_immunology/singularity/ciim.sif` | CIIM tasks — single-cell immunology + immune aging clock |
| `rapids.sif` | `agentic_immunology/singularity/rapids.sif` | GPU-accelerated tasks (RAPIDS, CellTypist GPU) |
| `ldsc.sif` | `agentic_immunology/singularity/ldsc.sif` | LD Score Regression — S-LDSC cell-type heritability enrichment |
| `ciim_R_base.sif` | `agentic_immunology/singularity/ciim_R_base.sif` | R bioinformatics tasks — Seurat v5 + Signac single-cell/multiome (R/Seurat `.rds` objects, e.g. LongCovid multiome) |

**`ciim.sif` key packages:** `scanpy`, `anndata`, `decoupler`, `celltypist`, `scikit-learn`, `scipy`, `harmonypy`, `scrublet`, `umap-learn`, `grnimmuneclock` (CD4T + CD8T immune aging clocks), `liana` 1.7.1 (cell-cell communication)

**`ldsc.sif` key packages:** everything in `ciim.sif` + `ldsc` (Python 3 port — `ldsc.py`, `munge_sumstats.py`, `make_annot.py`)

**`ciim_R_base.sif` key packages:** R 4.4.1 (rocker/r-ver); `Seurat` (v5), `SeuratObject`, `Signac` (single-cell/multiome RNA+ATAC); `tidyverse`, `ggplot2`, `ggrepel`, `patchwork`, `cowplot`, `pheatmap`, `ComplexHeatmap`, `RColorBrewer`, `viridis`; `Matrix`, `igraph`, `data.table`, `hdf5r`, `R.utils`, `optparse`; Bioconductor: `GenomicRanges`, `Rsamtools`, `SingleCellExperiment`, `SummarizedExperiment`, `AUCell`, `limma`, `edgeR`. Run with `Rscript` (the `%runscript`).

---