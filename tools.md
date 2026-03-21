# Tools — Overview


```python
import sys
sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools/{base or ciim}/code')
from <module_name> import <function_name>   
```

---

## Singularity Images

| Image | Path | Use for |
|-------|------|---------|
| `biomni_full.sif` | `/vol/projects/BIIM/agentic_central/singularity/biomni_full.sif` | Default — full bio stack (genomics, pharmacology, ML, NLP) |
| `ciim.sif` | `/vol/projects/BIIM/agentic_central/singularity/ciim.sif` | CIIM tasks — single-cell immunology + immune aging clock |
| `rapids.sif` | `/vol/projects/BIIM/agentic_central/singularity/rapids.sif` | GPU-accelerated tasks (RAPIDS, CellTypist GPU) |

**`ciim.sif` key packages:** `scanpy`, `anndata`, `decoupler`, `celltypist`, `scikit-learn`, `scipy`, `harmonypy`, `scrublet`, `umap-learn`, `grnimmuneclock` (CD4T + CD8T immune aging clocks)

---

## Base modules

| Module | Description | Reference |
|--------|-------------|-----------|
| `database_base` | Queries 30+ biomedical REST APIs (UniProt, Ensembl, PDB, KEGG, ClinVar, GnomAD, ChEMBL, etc.) using natural language or direct endpoints. | [database_base.md](tools/database_base.md) |
| `genetics_base` | Liftover of genomic coordinates, CRISPR editing analysis, fine-mapping, TF binding site identification, and phylogenetic analysis. | [genetics_base.md](tools/genetics_base.md) |
| `genomics_base` | Single-cell RNA-seq cell type annotation, batch integration (Harmony/scVI), gene set enrichment, ChIP-seq peak calling, and embedding generation. | [genomics_base.md](tools/genomics_base.md) |
| `immunology_base` | ATAC-seq differential accessibility, TCR/BCR analysis, immune cell phenotyping, cytokine assays, and flow cytometry analysis. | [immunology_base.md](tools/immunology_base.md) |
| `literature_base` | PubMed/arXiv/Scholar search, paper/supplementary retrieval, web search, and PDF extraction. | [literature_base.md](tools/literature_base.md) |
| `pharmacology_base` | Molecular docking (DiffDock, Vina), ADMET prediction, drug-drug interaction analysis (DDInter), FDA adverse events, and drug repurposing (TxGNN). | [pharmacology_base.md](tools/pharmacology_base.md) |

## CIIM modules

| Module | Description | Reference |
|--------|-------------|-----------|
| `genomics` | Raw counts detection (`identify_counts_layer`), CellTypist annotation with Leiden-based majority voting (`annotate_celltype_celltypist`), marker-based pseudobulk ULM annotation (`annotate_celltype_ulm`), consensus GRN loader (`get_immune_grn`), GRN inference (`infer_grn_spearman`), single-cell QC (`qc_sc_transcriptomics`), cluster annotation quality (`analyze_cluster_celltype_annotation_quality`), TF activity inference (`infer_tf_activity`). | [genomics.md](tools/ciim/genomics.md) |
| `aging` | GRN-based immune age prediction (`predict_immune_age_grn_clock` — CD4T/CD8T, requires `ciim.sif`). Immune TF signatures: aging multi-cohort (`immune_aging_tf_signatures_major_celltypes`, `immune_aging_tf_signatures_minor_celltypes`), SLE (`sle_tf_signatures_major_celltypes`), drug Ruxolitinib (`drug_tf_signatures_major_celltypes`), cytokine IL-10 (`cytokine_tf_signatures_major_celltypes`). | [aging.md](tools/ciim/aging.md) |
