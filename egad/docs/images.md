## Singularity Images

`.sif` images live at `${CIIM_SINGULARITY_DIR}` (set in `.env`, echoed at install time);
their `.def` build recipes are git-tracked in `singularity_docs/` (see `singularity_docs/build.sh`).

| Image | Path | Use for |
|-------|------|---------|
| `biomni_full.sif` | `${CIIM_SINGULARITY_DIR}/biomni_full.sif` | Default — full bio stack (genomics, pharmacology, ML, NLP); `genetics_biomni`, `pharmacology_biomni`, and direct-API CIIM genetics functions (`phewas_opengwas`, `query_gwas_catalog`, `query_opentarget_platform`, `get_disease_credible_sets`) |
| `genotype.sif` | `${CIIM_SINGULARITY_DIR}/genotype.sif` | `run_coloc` and `run_mr` (R 4.5, `coloc`, `susieR`, `plink`) |
| `ciim.sif` | `${CIIM_SINGULARITY_DIR}/ciim.sif` | CIIM tasks — single-cell immunology + immune aging clock |
| `rapids.sif` | `${CIIM_SINGULARITY_DIR}/rapids.sif` | GPU-accelerated tasks (RAPIDS, CellTypist GPU) |
| `ldsc.sif` | `${CIIM_SINGULARITY_DIR}/ldsc.sif` | LD Score Regression — S-LDSC cell-type heritability enrichment |
| `ciim_R_base.sif` | `${CIIM_SINGULARITY_DIR}/ciim_R_base.sif` | R bioinformatics tasks — Seurat v5 + Signac single-cell/multiome (R/Seurat `.rds` objects, e.g. LongCovid multiome) |
| `aging_clocks_py.sif` | `${CIIM_SINGULARITY_DIR}/aging_clocks_py.sif` | **Aging clocks (Python)** — `aging_clock_agent` only: `pyaging` (BiTAge bulk RNA-seq; OcampoATAC1/2 bulk ATAC-seq) |
| `aging_clocks_R.sif` | `${CIIM_SINGULARITY_DIR}/aging_clocks_R.sif` | **Aging clocks (R)** — `aging_clock_agent` only: `scImmuAging` (single-cell immune aging, CD4T/CD8T/NK/B/Monocyte) |

**`ciim.sif` key packages:** `scanpy`, `anndata`, `decoupler`, `celltypist`, `scikit-learn`, `scipy`, `harmonypy`, `scrublet`, `umap-learn`, `grnimmuneclock` (CD4T + CD8T immune aging clocks), `liana` 1.7.1 (cell-cell communication), `statsmodels`.

**`ldsc.sif` key packages:** everything in `ciim.sif` + `ldsc` (Python 3 port — `ldsc.py`, `munge_sumstats.py`, `make_annot.py`)

**`ciim_R_base.sif` key packages:** R 4.4.1 (rocker/r-ver); `Seurat` (v5), `SeuratObject`, `Signac` (single-cell/multiome RNA+ATAC); `tidyverse`, `ggplot2`, `ggrepel`, `patchwork`, `cowplot`, `pheatmap`, `ComplexHeatmap`, `RColorBrewer`, `viridis`; `Matrix`, `igraph`, `data.table`, `hdf5r`, `R.utils`, `optparse`, `metafor`; Bioconductor: `GenomicRanges`, `Rsamtools`, `SingleCellExperiment`, `SummarizedExperiment`, `AUCell`, `limma`, `edgeR`. Run with `Rscript` (the `%runscript`).

**`aging_clocks_py.sif` key packages:** everything in `ciim.sif` + `pyaging` (58-clock compendium, PyTorch-backed). Clocks used: `ocampoatac1`/`ocampoatac2` (bulk ATAC-seq, `chr:start-end` peaks); `horvath2013`, `hannum`, `grimage2`, `dunedinpace` (DNA methylation, Illumina 450K/EPIC `cg*` CpG IDs). Tested on GSE40279 (n=656 whole blood). Run with `python3`.

**`aging_clocks_R.sif` key packages:** everything in `ciim_R_base.sif` + `glmnet`, `ggpubr`, `infotheo`, `ggridges`, `biomaRt` + `scImmuAging` (CiiM-Bioinformatics-group). Run with `Rscript`.

---

## How to run

```bash
env -u SSL_CERT_FILE -u SSL_CERT_DIR singularity exec \
  --bind /vol/projects:/vol/projects \
  ${CIIM_SINGULARITY_DIR}/{image_name}.sif \
  python3 ${CIIM_TEMP_DIR}/{task}/code/script.py
```
(Swap `python3 ... script.py` for `Rscript ... script.R` for R images.)

> `env -u SSL_CERT_FILE -u SSL_CERT_DIR` is required: singularity passes host env vars into the
> container by default, and the host's `SSL_CERT_FILE` points at a path
> (`/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem`) that doesn't exist inside these images,
> which crashes any tool doing its own TLS context setup (e.g. `query_scholar`'s `httpx`/`scholarly`
> stack) before it makes a request. Unsetting lets the container fall back to its own trust store.

> ⛔ HARD RULES:
> - These images are the ONLY permitted environments. ALWAYS include `--bind /vol/projects:/vol/projects`.
> - DO NOT use any other env, conda, or virtualenv.
> - DO NOT `pip install` or `conda install`. If a package is missing → STOP: `"Package <name> not found in the env. Stopping."`
> - Singularity scratch: `/tmp/` only; all persistent outputs go to the task folder.
> - Always use **absolute paths** inside scripts.
> - Additional rule for `run_mr` in `opengwas` mode: the OpenGWAS JWT token must be in `.env` as `OPENGWAS_TOKEN=<jwt>`. If missing/expired → report and stop (or use `exposure_file`/`outcome_file` if pre-fetched files are available).

---

