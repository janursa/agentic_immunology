## Singularity Images

| Image | Path | Use for |
|-------|------|---------|
| `biomni_full.sif` | `/vol/projects/BIIM/agentic_central/singularity/biomni_full.sif` | Default — full bio stack (genomics, pharmacology, ML, NLP) |
| `ciim.sif` | `/vol/projects/BIIM/agentic_central/singularity/ciim.sif` | CIIM tasks — single-cell immunology + immune aging clock |
| `rapids.sif` | `/vol/projects/BIIM/agentic_central/singularity/rapids.sif` | GPU-accelerated tasks (RAPIDS, CellTypist GPU) |

**`ciim.sif` key packages:** `scanpy`, `anndata`, `decoupler`, `celltypist`, `scikit-learn`, `scipy`, `harmonypy`, `scrublet`, `umap-learn`, `grnimmuneclock` (CD4T + CD8T immune aging clocks)

---