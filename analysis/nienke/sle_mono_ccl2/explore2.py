"""Explore minor cell type structure."""
import anndata as ad

BULK_MINOR_PATH = "/vol/projects/BIIM/agentic_immunology/datalake/omics/hira/perez_sle_bulk_minor.h5ad"
adata_minor = ad.read_h5ad(BULK_MINOR_PATH)
print(f"obs columns: {list(adata_minor.obs.columns)}")
print(f"Sub_CT unique:\n{adata_minor.obs['Sub_CT'].value_counts()}")
print(f"\ncondition:\n{adata_minor.obs['condition'].value_counts()}")
print(f"CCL2 in var: {'CCL2' in adata_minor.var_names}")
