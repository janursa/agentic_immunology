
### `predict_immune_age_grn_clock`
*GRN Immune Age Clock*
Predict biological age of immune cells using the GRN-based immune aging clock (GRNimmuneClock). Runs on a pseudobulk AnnData (samples × genes) and adds predicted ages to `adata.obs['predicted_age']`. Supported cell types: CD4T, CD8T.

IMAGE to use: ciim.sif

**Required:**
- `adata` (AnnData) — pseudobulk AnnData, rows = donors/samples, columns = genes. Expression should be log-normalised (CPM + log1p).
- `cell_type` (str) — cell type for the clock: `'CD4T'` or `'CD8T'`

**Optional:**
- `output_dir=None` (str) — if provided, saves `predicted_ages_{cell_type}.csv` to this directory

**Returns:** `str` log of steps. Predicted ages written to `adata.obs['predicted_age']` in-place.

**Example:**
```python
log = predict_immune_age_grn_clock(adata_cd4t, cell_type='CD4T', output_dir='/my/output/')
print(adata_cd4t.obs['predicted_age'])
```

---

### `retrieve_summary_stats`
*Immune Summary Stats*

Unified loader for all immune summary statistics. Selects the right dataset via `context`, with optional filters.

**Required:**
- `context` (str) — which dataset to load:
  - `'aging'`    : multi-cohort aging signatures (healthy donors; onek1k, abf300, aida, perez_sle)
  - `'sle'`      : SLE vs healthy TF differential activity (Perez cohort)
  - `'drug'`     : Ruxolitinib vs DMSO TF differential activity (OP ex-vivo)
  - `'cytokine'` : IL-10 vs PBS TF differential activity (ParseBioscience ex-vivo)

**Optional (context='aging'):**
- `feature_type='tf_activity'` (str) — `'tf_activity'` (default), `'gene_expression'`, or `'ccc'`
  - `'ccc'`: `gene` column encodes `source_ct__ligand__target_ct__receptor` (double underscore) — parse in your analysis
- `cell_resolution='major'` (str) — `'major'` (CD4T/CD8T/NK/B/MONO) or `'minor'` (11 sub-types)
- `trend=None` (str or list) — `'Increase in aging'`, `'Decrease in aging'`, `'Inconsistent'`
- `dataset=None` (str or list) — `'onek1k'`, `'abf300'`, `'aida'`, `'perez_sle'`

**Optional (all contexts):**
- `cell_type=None` (str or list) — filter by cell type (not applicable for `feature_type='ccc'`)
- `p_adj_threshold=None` (float) — significance filter:
  - `context='aging'`: filters `meta_p_adj`
  - `context` in `('sle', 'drug', 'cytokine')`: filters `p_value_adj`

**Optional (context='sle'/'drug'/'cytokine'):**
- `direction=None` (str or list):
  - `'sle'`: `'Increase in SLE'`, `'Decrease in SLE'`
  - `'drug'` / `'cytokine'`: `'Increase'`, `'Decrease'`
- `age_group=None` (str or list) — [`'sle'` only] e.g. `'Both age groups'`

**Returns:** `pd.DataFrame` — columns depend on context (see docstring for details)

**Examples:**
```python
# Significant TFs increasing with age in CD8T (major cell types)
df = retrieve_summary_stats('aging', cell_type='CD8T', trend='Increase in aging', p_adj_threshold=0.05)

# TF aging signatures in minor cell types
df = retrieve_summary_stats('aging', cell_resolution='minor', cell_type='Tem_Temra_CD8', p_adj_threshold=0.05)

# Gene expression aging signatures
df = retrieve_summary_stats('aging', feature_type='gene_expression', cell_type='CD4T', p_adj_threshold=0.05)

# CCC aging signatures (parse gene column for components)
df = retrieve_summary_stats('aging', feature_type='ccc', p_adj_threshold=0.05, dataset='abf300')
parts = df['gene'].str.split('__', expand=True)
df['source_ct'], df['ligand'], df['target_ct'], df['receptor'] = parts[0], parts[1], parts[2], parts[3]

# SLE TFs in B cells
df = retrieve_summary_stats('sle', cell_type='B', direction='Increase in SLE', p_adj_threshold=0.05)

# Ruxolitinib drug signatures
df = retrieve_summary_stats('drug', cell_type='CD4T', p_adj_threshold=0.05)

# IL-10 cytokine signatures
df = retrieve_summary_stats('cytokine', cell_type='B', direction='Increase', p_adj_threshold=0.05)
```

