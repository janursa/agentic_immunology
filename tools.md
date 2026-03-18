# Tools — Overview

This folder contains function reference docs for the retained biomni tool modules and their Python source files under `tool/`.

**How to use a tool:**
```python
import sys
sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools')
from tool.<module_name> import <function_name>
result = <function_name>(required_arg, optional_kwarg=value)
```

> All tools run inside the `biomni_e1` conda environment:
> `conda run -n biomni_e1 python3 temp/script.py`

---

## Retained Modules

| Module | Description | Reference |
|--------|-------------|-----------|
| `database` | Queries 30+ biomedical REST APIs (UniProt, Ensembl, PDB, KEGG, ClinVar, GnomAD, ChEMBL, etc.) using natural language or direct endpoints. | [database.md](tools/database.md) |
| `genetics` | Liftover of genomic coordinates, CRISPR editing analysis, fine-mapping, TF binding site identification, and phylogenetic analysis. | [genetics.md](tools/genetics.md) |
| `genomics` | Single-cell RNA-seq cell type annotation, batch integration (Harmony/scVI), gene set enrichment, ChIP-seq peak calling, and embedding generation. | [genomics.md](tools/genomics.md) |
| `immunology` | ATAC-seq differential accessibility, TCR/BCR analysis, immune cell phenotyping, cytokine assays, and flow cytometry analysis. | [immunology.md](tools/immunology.md) |
| `literature` | PubMed/arXiv/Scholar search, paper/supplementary retrieval, web search, and PDF extraction. | [literature.md](tools/literature.md) |
| `pharmacology` | Molecular docking (DiffDock, Vina), ADMET prediction, drug-drug interaction analysis (DDInter), FDA adverse events, and drug repurposing (TxGNN). | [pharmacology.md](tools/pharmacology.md) |
