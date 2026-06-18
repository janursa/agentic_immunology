# Aging Clocks — Reference

This file is the canonical reference for aging-clock work done by `data_analyst_agent`. It covers available clocks, hard rules, execution commands, per-clock usage patterns, and the mandatory output format.

---

## Available Clocks

| Clock | Modality | Cell types / tissue | Image | Input format |
|---|---|---|---|---|
| **GRNimmuneClock** | scRNA-seq pseudobulk | CD4T, CD8T | `ciim.sif` | AnnData (samples × genes), CPM + log1p |
| **scImmuAging** | scRNA-seq (single-cell) | CD4T, CD8T | `aging_clocks_R.sif` | Seurat object; `.obs` must have `donor_id` + `age` |
| **OcampoATAC1/2** | Bulk ATAC-seq | Peripheral blood | `aging_clocks_py.sif` | DataFrame (samples × peaks in `chr:start-end` format), 80,400 features |
| **Horvath2013** | DNA methylation (450K/EPIC) | Multi-tissue | `aging_clocks_py.sif` | DataFrame (samples × CpGs in `cg*` format); 353 CpGs |
| **Hannum** | DNA methylation (450K/EPIC) | Whole blood | `aging_clocks_py.sif` | DataFrame (samples × CpGs in `cg*` format); 69 CpGs |
| **GrimAge2** | DNA methylation (450K/EPIC) | Blood | `aging_clocks_py.sif` | DataFrame (samples × CpGs in `cg*` format); 1,030 CpGs |
| **DunedinPACE** | DNA methylation (450K/EPIC) | Blood | `aging_clocks_py.sif` | DataFrame (samples × CpGs in `cg*` format); 20,000 CpGs |
| **PhenoAge** | DNA methylation (EPIC only) | Blood | `aging_clocks_py.sif` | DataFrame (samples × CpGs in `cg*` format); needs EPIC array |

All images: `agentic_immunology/singularity/{image}.sif`

---

## Hard Rules

**1. Feature coverage — hard fail at >20% missing.**
Before running any clock, check what fraction of the clock's required features are absent from the input. If >20% missing → **STOP**: `"HARD FAIL: {N}% of {clock} features missing in input ({missing}/{total}). Threshold is 20%. Stopping."` If ≤20%, proceed and log the missing fraction in output.

**2. pyaging downloads model weights at first use.**
OcampoATAC1/2 weights (~600 MB) download from S3 on first call and cache in the `dir` argument. Always pass `dir` to a persistent path (e.g. the task output folder). Run with SSL cert binding:
```bash
--bind /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem:/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
```

**3. Use age acceleration, not absolute age, for transcriptomics and ATAC-seq clocks.**
Absolute predicted age alone can suffer from batch effects. Always compute acceleration relative to a control from the same data.

**4. OcampoATAC1/2 are bulk models.**
If pseudobulked scATAC-seq is provided, add a mandatory note: `"OcampoATAC clocks are trained on bulk ATAC-seq. Pseudobulk scATAC-seq is a reasonable approximation but may carry additional variance. Interpret with caution."`

---

## How to Run

**Python clocks (GRNimmuneClock, OcampoATAC):**
```bash
singularity exec \
  --bind /vol/projects:/vol/projects \
  /vol/projects/BIIM/agentic_immunology/singularity/{ciim|aging_clocks_py}.sif \
  python3 /vol/projects/BIIM/agentic_immunology/temp/{task}/code/script.py
```

**R clocks (scImmuAging):**
```bash
singularity exec \
  --bind /vol/projects:/vol/projects \
  /vol/projects/BIIM/agentic_immunology/singularity/aging_clocks_R.sif \
  Rscript /vol/projects/BIIM/agentic_immunology/temp/{task}/code/script.R
```

> ⛔ These images are the ONLY permitted environments. Always include `--bind /vol/projects:/vol/projects`. DO NOT `pip install`, `conda install`, or install anything. If a package is missing → STOP: `"Package <name> not found in image. Stopping."` Use absolute paths for all file references. Singularity scratch: `/tmp/` only; all persistent outputs go to the task folder.

---

## Per-Clock Usage

### GRNimmuneClock (`ciim.sif`)
```python
import sys
sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools/ciim/code')
from hiara import predict_immune_age_grn_clock
# adata: pseudobulk AnnData (samples × genes), log-normalised CPM+log1p
# adata.obs must contain 'age' (chronological)
log = predict_immune_age_grn_clock(adata, cell_type='CD4T', output_dir='/output/')
# predicted age → adata.obs['predicted_age']
```

### scImmuAging (`aging_clocks_R.sif`)

Three compatibility patches are **required** (image has Seurat v5 and glmnet 5.0; scImmuAging was written for v4/4.x):

```R
library(scImmuAging); library(Seurat); library(dplyr); library(purrr)

# Patch 1: glmnet 5.0 — predict.cv.glmnet S3 dispatch broken
patched_pre_fun <- function(model, selected, final_mtx, preprocessed_df) {
    testPredictions <- glmnet:::predict.glmnet(
        model$glmnet.fit, newx = as.matrix(final_mtx), s = model$lambda.min
    )
    data.frame(donor_id=preprocessed_df[,1], age=preprocessed_df[,2],
               Prediction=testPredictions[,1])
}
assignInNamespace("pre_fun", patched_pre_fun, ns="scImmuAging")

# Patch 2: Seurat v5 — force v3/v4-style Assay before CreateSeuratObject()
options(Seurat.object.assay.version = "v3")

# Patch 3: use beta rownames as feature set (not all_features)
data_path <- system.file("data", package = "scImmuAging")
all_model  <- readRDS(file.path(data_path, "all_model.RDS"))

seurat_obj <- CreateSeuratObject(counts = counts, meta.data = meta)
seurat_obj <- NormalizeData(seurat_obj, verbose = FALSE)

cell_type  <- "CD4T"   # one of: CD4T, CD8T, MONO, NK, B
beta_genes <- rownames(all_model[[cell_type]]$glmnet.fit$beta)

preprocessed   <- PreProcess(seurat_obj, cell_type=cell_type,
                              model=all_model[[cell_type]], marker_gene=beta_genes)
preds_per_cell <- AgingClockCalculator(preprocessed_df=preprocessed,
                                        model=all_model[[cell_type]], marker_gene=beta_genes)
donor_ages     <- Age_Donor(preds_per_cell)
donor_ages$age_acceleration <- donor_ages$predicted - donor_ages$age
```

> Feature counts per cell type: CD4T: 1000 | CD8T: 700 | MONO: 880 | NK: 700 | B: 1100

### OcampoATAC (`aging_clocks_py.sif`)
```python
import pandas as pd, pyaging as pya
# df: samples × peaks — peaks MUST be chr:start-end format (e.g. 'chr1:817100-817691')
# 80,400 features; ≤20% missing allowed. Add 'age' column for age-acceleration.
adata = pya.preprocess.df_to_adata(df, metadata_cols=['age'], verbose=False)
pya.pred.predict_age(adata, clock_names=['ocampoatac1', 'ocampoatac2'],
                     dir='/path/to/cache/', verbose=False)
age_accel = adata.obs['ocampoatac1'] - adata.obs['age']
```
> **BiTAge note**: available in pyaging but uses C. elegans gene IDs — NOT suitable for human PBMC RNA-seq.

### DNA Methylation Clocks (`aging_clocks_py.sif`)

Input: samples × CpGs DataFrame with `cg*` column names (β-values in [0,1]) + an `age` column. Requires 450K or EPIC array — WGBS/RRBS use genomic coordinates and are incompatible.

```python
import pandas as pd, pyaging as pya
cpg_cols = [c for c in df.columns if c.startswith("cg")]
adata = pya.preprocess.df_to_adata(df[cpg_cols + ["age"]], metadata_cols=["age"], verbose=False)
clock_names = [...]  # fill from task specification
pya.pred.predict_age(adata, clock_names=clock_names, dir="/path/to/cache/", verbose=False)

rows = []
for clock in clock_names:
    for sample in adata.obs.index:
        rows.append({
            "sample_id": sample, "cell_type": "bulk",
            "chronological_age": adata.obs.loc[sample, "age"],
            "predicted_age": adata.obs.loc[sample, clock],
            "age_acceleration": adata.obs.loc[sample, clock] - adata.obs.loc[sample, "age"],
            "clock": clock, "missing_features_pct": missing_pct, "notes": "",
        })
pd.DataFrame(rows).to_csv("/path/to/predicted_ages.csv", index=False)
```

**Clock selection:**
| Clock | Best use case | r vs chron. age (whole blood) |
|---|---|---|
| `horvath2013` | Multi-tissue; classic reference | 0.92 |
| `hannum` | Whole blood; highest correlation | 0.95 |
| `grimage2` | Mortality/morbidity prediction | 0.34* |
| `dunedinpace` | Rate of aging (not absolute age) | 0.14* |
| `phenoage` | Biological age vs clinical outcomes; **EPIC only** | — |

*Low correlation with chronological age is expected — these predict health outcomes, not calendar age. Compare age acceleration across groups.

**Feature requirements:**
- `horvath2013`: 353 CpGs (fully covered by 450K)
- `hannum`: 69 CpGs (fully covered by 450K)
- `grimage2`: 1,030 CpGs (958/1030 present in 450K)
- `dunedinpace`: 20,000 CpGs (fully covered by 450K)
- `phenoage`: EPIC-only CpGs, not present on 450K

**pyaging clock name convention** (exact strings): `horvath2013`, `hannum`, `phenoage`, `grimage2`, `dunedinpace`

---

## Standardised Output

Every task must produce `temp/{task}/results/predicted_ages.csv`:

| Column | Description |
|---|---|
| `sample_id` | Donor or sample identifier |
| `cell_type` | Cell type (or `'bulk'` for OcampoATAC) |
| `chronological_age` | Known biological age (years) |
| `predicted_age` | Clock output |
| `age_acceleration` | `predicted_age − chronological_age` |
| `clock` | Clock name (e.g. `GRNimmuneClock_CD4T`, `ocampoatac1`) |
| `missing_features_pct` | % of clock features absent from input |
| `notes` | Warnings (missing genes, compat notes, bulk-model note, etc.) |

Stack all clocks/cell types into one long-format CSV.
