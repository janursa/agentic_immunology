"""Quick exploration of Perez SLE bulk data structure."""
import anndata as ad
import numpy as np

BULK_PATH = "/vol/projects/BIIM/agentic_immunology/datalake/omics/hira/perez_sle_bulk.h5ad"
BULK_MINOR_PATH = "/vol/projects/BIIM/agentic_immunology/datalake/omics/hira/perez_sle_bulk_minor.h5ad"

print("=== MAJOR CELL TYPES ===")
adata = ad.read_h5ad(BULK_PATH)
print(f"Shape: {adata.shape}")
print(f"obs columns: {list(adata.obs.columns)}")
print(f"\nMajor_CT values: {sorted(adata.obs['Major_CT'].unique())}")
print(f"condition values: {sorted(adata.obs['condition'].unique())}")
if 'disease_state' in adata.obs.columns:
    print(f"disease_state values: {sorted(adata.obs['disease_state'].dropna().unique())}")
print(f"\nCCL2 in var: {'CCL2' in adata.var_names}")
if 'CCL2' in adata.var_names:
    mono_mask = adata.obs['Major_CT'].str.upper().str.contains('MONO')
    print(f"Monocyte samples: {mono_mask.sum()}")
    print(f"Monocyte condition counts:\n{adata.obs.loc[mono_mask, 'condition'].value_counts()}")

print("\n=== MINOR CELL TYPES ===")
adata_minor = ad.read_h5ad(BULK_MINOR_PATH)
print(f"Shape: {adata_minor.shape}")
print(f"obs columns: {list(adata_minor.obs.columns)}")
print(f"\nMajor_CT values: {sorted(adata_minor.obs['Major_CT'].unique())}")
if 'Sub_CT' in adata_minor.obs.columns:
    mono_minor = adata_minor.obs['Major_CT'].str.upper().str.contains('MONO')
    print(f"\nMonocyte Sub_CT:\n{adata_minor.obs.loc[mono_minor, 'Sub_CT'].value_counts()}")
print(f"\nCCL2 in var: {'CCL2' in adata_minor.var_names}")
