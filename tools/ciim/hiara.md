
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

