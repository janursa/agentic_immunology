# Genomics — Custom Extensions

**6 functions** — counts detection, CellTypist annotation, consensus GRN loader, GRN inference, single-cell QC, annotation quality assessment


### `identify_counts_layer`
*Raw Counts Detection*
Identify which slot in an AnnData object holds raw integer counts. Checks `adata.layers['counts']`, then `adata.layers['count']`, then tests `adata.X` for non-negative integer values. Raises `ValueError` if none found.

**Required:** `adata` (AnnData)

**Returns:** `str` — `'counts'`, `'count'`, or `'X'`

---

### `annotate_celltype_celltypist`
*CellTypist Annotation*
Annotate immune cell types using CellTypist with Leiden-based majority voting. Receives the AnnData directly (no file loading).

**Pipeline:**
1. Auto-detects raw counts via `identify_counts_layer`
2. Normalizes to 10k CPM + log1p; stores in `adata.layers['scaledlognom']`
3. Pre-clusters at **two** Leiden resolutions (HVG → scale → PCA → kNN → Leiden):
   - GPU (`rapids_singlecell`) if `adata.n_obs >= gpu_cell_threshold` and importable; otherwise CPU (scanpy)
   - Stores `adata.obs['leiden_major']` and `adata.obs['leiden_minor']`
   - `leiden_res_minor=None` auto-selects resolution following CellTypist's over-clustering scale: 5 / 10 / 15 / 20 / 25 / 30 for <5k / <20k / <40k / <100k / <200k / ≥200k cells
   - Copies `X_pca`, `connectivities`, `distances`, `neighbors` to `adata`
4. Runs CellTypist **twice** (`majority_voting=False`):
   - `model_major` (`Immune_All_Low.pkl`) → coarse per-cell predictions
   - `model_minor` (`Immune_All_High.pkl`) → fine per-cell predictions
5. Majority voting per Leiden cluster:
   - `adata.obs['CT_Major']` — vote on `leiden_major` with low-res predictions, collapsed via broad cell type mapping
   - `adata.obs['CT_Minor']` — vote on `leiden_minor` with high-res predictions, raw CellTypist labels preserved

**Required:** `adata` (AnnData — raw counts auto-detected)
**Optional:** `model_major='Immune_All_Low.pkl'` (str), `model_minor='Immune_All_High.pkl'` (str), `leiden_res_major=0.3` (float), `leiden_res_minor=None` (float or None — auto from cell count), `n_neighbors=10` (int), `n_pcs=50` (int), `gpu_cell_threshold=200_000` (int)

**Returns:** AnnData (modified in-place) with `leiden_major`, `leiden_minor`, `CT_Major`, `CT_Minor` added to `.obs`

---

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

### `qc_sc_transcriptomics`
*scRNA QC Filter*
Apply the standard single-cell RNA-seq QC protocol to a raw-count AnnData object. Flags mitochondrial genes, filters low-quality / dying cells, removes lowly expressed genes, sanity-checks that `adata.X` contains raw integer counts, and writes the filtered AnnData to disk.

**Required:** `adata_path` (str), `output_path` (str)
**Optional:** `group_col=None` (str — `obs` column for donor×condition groups, used to set the per-gene min-cells threshold: `max(n_groups × 10, 10)`), `min_genes=100` (int), `max_genes=5000` (int), `max_pct_mt=20.0` (float)

---

### `analyze_cluster_celltype_annotation_quality`
*Annotation Quality*
Assess the quality of cell type annotations at the cluster level. For each cluster (e.g. Leiden), computes dominant label, consistency score (fraction of cells carrying the dominant label), Shannon entropy of the label distribution, and cell count across one or more annotation columns. Flags clusters with consistency below threshold as ambiguous or heterogeneous. Saves a full stats CSV, a flagged-clusters CSV, a consistency heatmap, and a per-annotation entropy bar plot.

**Required:** `adata_or_path` (AnnData or str — pass a loaded AnnData object or a path to an `.h5ad` file), `output_dir` (str)
**Optional:** `cluster_key='leiden'` (str — `obs` column with cluster assignments), `annotation_keys=None` (list of str — defaults to `['Major_CT', 'Sub_CT', 'celltypist_label']` if present), `consistency_threshold=0.8` (float — clusters below this are flagged)

**Outputs:**
- `cluster_annotation_stats.csv` — per-cluster × per-annotation stats table
- `flagged_clusters.csv` — flagged cluster rows with dominant label, consistency, entropy, and 2nd-most-common label
- `consistency_heatmap.png` — RdYlGn heatmap of consistency scores (clusters × annotation keys)
- `entropy_barplot_<annotation>.png` — Shannon entropy bar chart per annotation key (red = flagged)

---

### `annotate_celltype_ulm`
*ULM Pseudobulk Annotation*
Annotate cell types using decoupler ULM on **pseudobulk profiles per cluster**. Receives the AnnData directly (no file loading). Uses Leiden cluster columns already computed by `annotate_celltype_celltypist` — does **not** re-cluster.

**Pipeline:**
1. Auto-detects raw counts via `identify_counts_layer`
2. Builds pseudobulk per cluster: sums raw counts per Leiden cluster, normalizes to CPM + log1p
3. Builds decoupler network from `marker_dict` (cell_type → marker genes)
4. Runs `dc.mt.ulm()` on the pseudobulk matrix (clusters × genes) — not per cell
5. Assigns each cluster the cell type with the highest ULM score
6. Propagates cluster labels back to all cells in `adata.obs`

**Required:** `adata` (AnnData), `output_dir` (str), `marker_dict` (dict — nested: `{'Major': {'CD8T': ['CD8A', ...], ...}, 'Minor': {...}}`)
**Optional:** `leiden_key_major='leiden_major'` (str), `leiden_key_minor='leiden_minor'` (str), `major_key='Major'` (str), `minor_key='Minor'` (str), `min_cells_per_cluster=10` (int)

**Returns:** str (log). Adds `adata.obs['ulm_Major_ct']` and `adata.obs['ulm_Minor_ct']`.

**Outputs (in `output_dir`):**
- `ulm_cluster_summary_<level>.csv` — per-cluster ULM scores + assigned label + cell count
- `ulm_activity_heatmap_<level>.png` — heatmap of ULM scores (clusters × cell types)

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
