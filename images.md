## Singularity Images

| Image | Path | Use for |
|-------|------|---------|
| `biomni_full.sif` | `agentic_immunology/singularity/biomni_full.sif` | Default — full bio stack (genomics, pharmacology, ML, NLP) |
| `ciim.sif` | `agentic_immunology/singularity/ciim.sif` | CIIM tasks — single-cell immunology + immune aging clock |
| `rapids.sif` | `agentic_immunology/singularity/rapids.sif` | GPU-accelerated tasks (RAPIDS, CellTypist GPU) |
| `ldsc.sif` | `agentic_immunology/singularity/ldsc.sif` | LD Score Regression — S-LDSC cell-type heritability enrichment |
| `ciim_R_base.sif` | `agentic_immunology/singularity/ciim_R_base.sif` | R bioinformatics tasks — Seurat v5 + Signac single-cell/multiome (R/Seurat `.rds` objects, e.g. LongCovid multiome) |
| `aging_clocks_py.sif` | `agentic_immunology/singularity/aging_clocks_py.sif` | **Aging clocks (Python)** — `aging_clock_agent` only: `pyaging` (BiTAge bulk RNA-seq; OcampoATAC1/2 bulk ATAC-seq) |
| `aging_clocks_R.sif` | `agentic_immunology/singularity/aging_clocks_R.sif` | **Aging clocks (R)** — `aging_clock_agent` only: `scImmuAging` (single-cell immune aging, CD4T/CD8T/NK/B/Monocyte) |

**`ciim.sif` key packages:** `scanpy`, `anndata`, `decoupler`, `celltypist`, `scikit-learn`, `scipy`, `harmonypy`, `scrublet`, `umap-learn`, `grnimmuneclock` (CD4T + CD8T immune aging clocks), `liana` 1.7.1 (cell-cell communication)

**`ldsc.sif` key packages:** everything in `ciim.sif` + `ldsc` (Python 3 port — `ldsc.py`, `munge_sumstats.py`, `make_annot.py`)

**`ciim_R_base.sif` key packages:** R 4.4.1 (rocker/r-ver); `Seurat` (v5), `SeuratObject`, `Signac` (single-cell/multiome RNA+ATAC); `tidyverse`, `ggplot2`, `ggrepel`, `patchwork`, `cowplot`, `pheatmap`, `ComplexHeatmap`, `RColorBrewer`, `viridis`; `Matrix`, `igraph`, `data.table`, `hdf5r`, `R.utils`, `optparse`; Bioconductor: `GenomicRanges`, `Rsamtools`, `SingleCellExperiment`, `SummarizedExperiment`, `AUCell`, `limma`, `edgeR`. Run with `Rscript` (the `%runscript`).

**`aging_clocks_py.sif` key packages:** everything in `ciim.sif` + `pyaging` (58-clock compendium, PyTorch-backed). Clocks used: `ocampoatac1`/`ocampoatac2` (bulk ATAC-seq, `chr:start-end` peaks); `horvath2013`, `hannum`, `grimage2`, `dunedinpace` (DNA methylation, Illumina 450K/EPIC `cg*` CpG IDs). Tested on GSE40279 (n=656 whole blood). Run with `python3`.

**`aging_clocks_R.sif` key packages:** everything in `ciim_R_base.sif` + `glmnet`, `ggpubr`, `infotheo`, `ggridges`, `biomaRt` + `scImmuAging` (CiiM-Bioinformatics-group). Run with `Rscript`.

---

## How to run

```bash
singularity exec \
  --bind /vol/projects:/vol/projects \
  agentic_immunology/singularity/{image_name}.sif \
  python3 agentic_immunology/temp/{task}/code/script.py
```
(Swap `python3 ... script.py` for `Rscript ... script.R` for R images.)

> ⛔ HARD RULES:
> - These images are the ONLY permitted environments. ALWAYS include `--bind /vol/projects:/vol/projects`.
> - DO NOT use any other env, conda, or virtualenv.
> - DO NOT `pip install` or `conda install`. If a package is missing → STOP: `"Package <name> not found in the env. Stopping."`
> - Singularity scratch: `/tmp/` only; all persistent outputs go to the task folder.
> - Always use **absolute paths** inside scripts.

---