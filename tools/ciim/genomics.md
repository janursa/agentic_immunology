# Genomics — Custom Extensions

**7 functions** — consensus GRN loader, GRN inference, TF activity inference, cell-cell communication, CellxGene Census access

scRNA-seq QC, CellTypist annotation, ULM annotation, and annotation-quality assessment now live in the `scAnnotAgent` submodule — see [`scAnnotAgent/SKILL.md`](../../scAnnotAgent/SKILL.md) and [`knowhow/single_cell_rna_analysis.md`](../../knowhow/single_cell_rna_analysis.md).

### `get_immune_grn`
*Immune GRN Loader*
Load pre-computed consensus immune GRN(s) for one or more major immune cell types (CD4T, CD8T, NK, B, MONO). Returns edges from the HIARA multi-cohort consensus networks (minDegree2 filtered). Optionally restrict to promoter-supported edges, filter by edge weight, or look up a specific TF source or target gene.

**Required:** *(none — all parameters optional)*

**Optional:**
- `cell_type=None` (str or list) — filter by cell type: `'CD4T'`, `'CD8T'`, `'NK'`, `'B'`, `'MONO'`
- `promotor_based_only=False` (bool) — if True, return only promoter-supported edges
- `min_weight=None` (float) — keep edges where `|weight| >= min_weight`
- `source=None` (str or list) — filter by TF source gene(s)
- `target=None` (str or list) — filter by target gene(s)

**Returns:** `pd.DataFrame` with columns `source`, `target`, `weight`, `cell_type`, `promotor_based`

---

### `infer_grn_spearman`
*Spearman GRN Inference*
Infer a gene regulatory network (GRN) from expression data (single-cell or bulk) using pairwise Spearman correlation. Applies Benjamini-Hochberg FDR correction, filters edges to known transcription factors (TFs) from `data_lake/ciim/tf_all.csv`, and optionally annotates promoter-based edges. Returns a directed edge list CSV with columns `source`, `target`, `weight` (Spearman rho), and `promotor_based` (bool, if skeleton file present).

**Required:** `adata_path` (str), `output_file` (str)
**Optional:** `data_type='sc'` (str, `'sc'` or `'bulk'`), `group_col=None` (str — obs column for subsetting, e.g. `'Major_CT'`), `group=None` (str — value to keep, e.g. `'CD4T'`), `tf_list_path=None` (str), `p_value_filter=True` (bool), `top_n_edges=100_000` (int), `min_cells_per_gene=10` (int), `min_genes_per_cell=10` (int), `layer_norm=None` (str — layer name with pre-normalised expression; skips all normalisation), `layer_count=None` (str — layer name with raw counts to normalise; ignored if `layer_norm` set)

---

### `cellxgene_query_obs`
*CellxGene Census — Cell Metadata Query*
Query cell-level metadata from the CellxGene Census (~70M cells, ~900 datasets) without downloading any expression data. Returns a DataFrame of obs rows matching the given filters. Fast — streams only metadata columns.

**Optional:** `cell_type` (str or list), `tissue` (str or list), `disease` (str or list), `sex` (str), `organism='homo_sapiens'` (str), `extra_filter` (str — raw TileDB filter appended with AND), `columns` (list[str] — subset of obs columns to return), `census_version='stable'` (str)

**Returns:** `pd.DataFrame` — one row per cell. Key columns: `soma_joinid`, `dataset_id`, `cell_type`, `tissue`, `disease`, `sex`, `donor_id`, `development_stage`, `assay`, `self_reported_ethnicity`.

**Example:**
```python
from genomics import cellxgene_query_obs
obs = cellxgene_query_obs(
    cell_type=["CD4-positive, alpha-beta T cell", "CD8-positive, alpha-beta T cell"],
    tissue="blood", disease="normal",
    columns=["soma_joinid", "dataset_id", "cell_type", "donor_id", "sex"],
)
# 690,855 cells · 38 datasets · 1,374 donors
```

---

### `cellxgene_get_anndata`
*CellxGene Census — AnnData Retrieval*
Fetch a subsampled AnnData slice (raw counts) from the CellxGene Census. Efficiently caps cell count by sampling `soma_joinid`s **before** downloading the expression matrix — avoids streaming the full matching set. Compatible with the `scAnnotAgent` QC and annotation pipeline (see [`scAnnotAgent/SKILL.md`](../../scAnnotAgent/SKILL.md)).

**Optional:** `cell_type` (str or list), `tissue` (str or list), `disease` (str or list), `sex` (str), `genes` (list[str] — HGNC symbols; None = all genes, very large), `organism='homo_sapiens'` (str), `extra_filter` (str), `census_version='stable'` (str), `max_cells=10_000` (int — subsample cap), `seed=42` (int)

**Returns:** `AnnData` — obs × var, `X` = raw counts (sparse). `obs` carries full Census metadata; `var` has `feature_name` (HGNC symbol) and `feature_id` (Ensembl ID).

**Example:**
```python
from genomics import cellxgene_get_anndata
adata = cellxgene_get_anndata(
    cell_type="CD4-positive, alpha-beta T cell",
    tissue="blood", disease="normal",
    genes=["CD4", "FOXP3", "IL2RA", "GZMB", "IFNG"],
    max_cells=5000,
)
# (5000, 5) — pass directly into the scAnnotAgent QC/annotation pipeline
```

---

### `cellxgene_list_datasets`
*CellxGene Census — Dataset Listing*
List datasets available in the Census with optional tissue/disease filters. Useful for identifying which studies contribute cells to a query before downloading expression data.

**Optional:** `tissue` (str), `disease` (str), `organism='homo_sapiens'` (str), `census_version='stable'` (str)

**Returns:** `pd.DataFrame` with `dataset_id`, `dataset_title`, `dataset_cell_count`, and other collection-level metadata.

---

### `cellxgene_get_schema`
*CellxGene Census — Schema / Valid Filter Values*
Return valid values for `cell_type`, `tissue`, and `disease` obs fields, plus all available obs column names. Use this to discover correct filter strings before calling `cellxgene_query_obs` or `cellxgene_get_anndata`.

**Optional:** `organism='homo_sapiens'` (str), `census_version='stable'` (str)

**Returns:** `dict` with keys `obs_columns` (list), `unique_cell_types` (list), `unique_tissues` (list), `unique_diseases` (list).

---

### `infer_tf_activity`
*TF Activity Inference*
Infer TF activity from expression data using decoupler. Works with any AnnData (single-cell, pseudobulk, or bulk) — no assumptions about data type. Caller provides log-normalised expression in `adata.X` and the regulatory network.

**Required:**
- `adata` (AnnData) — obs × genes, `adata.X` should be log-normalised
- `net` (pd.DataFrame) — network with columns `source` (TF), `target` (gene), optionally `weight` (defaults to 1.0). Typically from `get_immune_grn()`

**Optional:**
- `method='ulm'` (str) — enrichment method: `'ulm'`, `'waggr'`, or `'mlm'`
- `use_raw=False` (bool) — use `adata.raw.X` instead of `adata.X`
- `min_n=2` (int) — minimum targets per TF (TFs with fewer are dropped)
- `verbose=False` (bool) — print decoupler progress

**Returns:** `pd.DataFrame` — activity score matrix (obs × TFs), index = `adata.obs_names`

**Example:**
```python
from genomics import get_immune_grn, infer_tf_activity
net = get_immune_grn(cell_type='CD8T')
tf_scores = infer_tf_activity(adata, net=net)           
```
