# Single-Cell RNA-seq Analysis

Covers the full scRNA-seq workflow: QC → Cell Type Annotation → TF Activity → GRN Inference.

USE `backed_r=True` for any exploratory analysis.

---

## 1. Quality Control (QC)

Apply QC **before** normalization, on raw counts using `qc_sc_transcriptomics`.

### Notes
- `group_col` should point to a donor × condition column; controls the per-gene min-cells threshold (`n_groups × 10`). If omitted, threshold is fixed at 10.
- Always run on raw counts — do **not** normalize before calling this tool.

---

## 2. Cell Type Annotation

1. Run QC (Section 1) first.

2. **Identify raw counts** using `identify_counts_layer(adata)` — checks `layers['counts']`, `layers['count']`, then `adata.X` for integer values.

3. **CellTypist annotation** via `annotate_celltype_celltypist(adata)`:
   - Normalizes internally (10k CPM + log1p); stores result in `adata.layers['scaledlognom']`
   - Pre-clusters with a single Leiden partition before running CellTypist:
     - Uses GPU (`rapid.sif`) if `n_obs ≥ 200k`; otherwise CPU (scanpy, `biomni_full.sif`)
     - `leiden_res` auto-scales with cell count: res 5→30 for <5k→≥200k cells
     - Stores `adata.obs['leiden']`
   - Runs `Immune_All_High.pkl` (32 coarse types) → `CT_Major`, `Immune_All_Low.pkl` (98 fine subtypes) → `CT_Minor`

4. **Marker-based annotation** via `annotate_celltype_ulm(adata, output_dir, marker_dict)`:
   - Load marker genes from `data_lake/ciim/marker_genes.json` (10 major lineages, 15 minor subtypes)
   - Uses existing `leiden` clusters — does **not** re-cluster
   - Pseudobulks raw counts per cluster, normalizes, runs decoupler ULM
   - Assigns top ULM-scored cell type to `adata.obs['ulm_Major_ct']` and `adata.obs['ulm_Minor_ct']`
   - Pass `leiden_key_major='leiden'` and `leiden_key_minor='leiden'`

5. **Cluster consistency assessment** via `analyze_cluster_celltype_annotation_quality(adata, output_dir)`:
   - Pass `cluster_key='leiden'` and `annotation_keys=['CT_Major', 'CT_Minor', 'ulm_Major_ct', 'ulm_Minor_ct']`
   - Clusters with consistency < 0.8 are flagged
   - Outputs: `cluster_annotation_stats.csv`, `flagged_clusters.csv`, `consistency_heatmap.png`

6. **Reporting**: summarize flagged clusters. Do **not** automatically modify annotations — ask the user for guidance (re-clustering, manual relabeling, or acceptance).

---

## 3. TF Activity Inference

Infer transcription factor activity per cell (or pseudobulk/bulk donor) using `infer_tf_activity` from decoupler.

**Input**: log-normalized expression in `adata.X` (log1p CPM). Raw counts also work but give noisier results.

```python
from genomics import get_immune_grn, infer_tf_activity

# Load a cell-type-specific GRN as the regulatory network
net = get_immune_grn(cell_type='CD8T')  # or 'CD4T', etc.

# Infer TF activity per cell
tf_scores = infer_tf_activity(adata, net=net)  # returns obs × TFs DataFrame

# For pseudobulk/bulk donors
tf_scores = infer_tf_activity(adata_bulk, net=net, method='ulm')
```

### Parameters
| Parameter | Default | Notes |
|-----------|---------|-------|
| `method` | `'ulm'` | One of `'ulm'`, `'waggr'`, `'mlm'` |
| `use_raw` | `False` | Use `adata.raw.X` instead of `adata.X` |
| `min_n` | `2` | Min targets per TF; TFs with fewer are dropped |

### Output
- Returns a `pd.DataFrame` (obs × TFs) with activity scores
- Also stored in `adata.obsm[f'score_{method}']`

### Notes
- TF coverage depends on overlap between `net` targets and `adata.var_names` — check for warnings about dropped TFs
- For immune data, pair with `get_immune_grn` to use curated immune-specific networks

---

## 4. GRN Inference

Infer gene regulatory networks per cell type using Spearman correlation via `infer_grn_spearman`.

```python
from genomics import infer_grn_spearman

log = infer_grn_spearman(
    adata_path='/data/pbmc.h5ad',
    output_file='/output/grn_CD4T.csv',
    cell_type_key='cell_type',
    cell_type='CD4T',
)
```

Result CSV columns: `source` (TF), `target` (gene), `weight` (Spearman ρ), `promotor_based` (bool).

### Pipeline Steps

1. **Load & subset** — optionally subset to a single cell type; run GRN inference per cell type separately
2. **QC filtering** — remove low-detection genes (`min_cells_per_gene`) and low-quality cells (`min_genes_per_cell`)
3. **Normalisation** — library-size normalisation + log1p (single-cell only; set `data_type='bulk'` to skip)
4. **Zero-variance removal** — exclude genes with zero std across samples
5. **Spearman correlation** — all pairwise ρ and p-values via `scipy.stats.spearmanr`
6. **FDR correction** — Benjamini-Hochberg; keep edges with adj. p-value < 0.05
7. **TF filter** — restrict `source` to 1,638 human TFs in `data_lake/ciim/tf_all.csv`
8. **Promoter annotation** — flag edges supported by `data_lake/ciim/skeleton_promotor.csv`
9. **Top-N selection** — keep top 100,000 edges by |ρ| (configurable)

### Running Per Cell Type

```python
for ct in adata.obs['Major_CT'].unique():
    infer_grn_spearman(
        adata_path='/data/pbmc.h5ad',
        output_file=f'/output/grn_{ct}.csv',
        group_col='Major_CT',
        group=ct,
    )
```

### Notes
- Spearman correlation is most reliable with ≥ 200 samples per cell type
- Positive ρ → co-activation; negative ρ → repression
- Transcriptomics only 

### Prior Files (`data_lake/ciim/`)

| File | Description |
|------|-------------|
| `tf_all.csv` | 1,638 human TFs — restricts GRN source nodes |
| `skeleton_promotor.csv` | TF–gene pairs with promoter-region evidence |
