
# Summary Stats — Overview

Location: `summary_stats/`

All signature files are loaded via the unified `retrieve_summary_stats(context, ...)` function in `tools/ciim/code/hiara.py`, except GRNs which use `get_immune_grn()` in `tools/ciim/code/genomics.py`.

```python
import sys
sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools/ciim/code')
from hiara import retrieve_summary_stats
```

---

## hiara

### `immune_aging_tf_signatures_major_celltypes.csv`
*Aging TF Signatures — Major*

Per-TF aging statistics across 5 major immune cell types (CD4T, CD8T, NK, B, MONO) from multi-cohort TF activity analysis (cohorts: onek1k, abf300, aida, perez_sle; healthy donors only).

**Load:** `retrieve_summary_stats('aging')`

---

### `immune_aging_tf_signatures_minor_celltypes.csv`
*Aging TF Signatures — Minor*

Per-TF aging statistics across 11 minor (sub) immune cell types (CD16_NK, Classic_MONO, MAIT, Memory_B, Naive_B, NonClassic_MONO, Tcm_Naive_CD4, Tcm_Naive_CD8, Tem_Effector_CD4, Tem_Temra_CD8, Tem_Trm_CD8) from multi-cohort TF activity analysis (cohorts: onek1k, abf300, aida, perez_sle; healthy donors only).

**Load:** `retrieve_summary_stats('aging', cell_resolution='minor')`

---

### `immune_aging_gene_expression_signatures_major_celltypes.csv`
*Aging Gene Expression Signatures*

Per-gene aging statistics across 5 major immune cell types from multi-cohort bulk gene expression analysis (cohorts: onek1k, abf300, aida, perez_sle; healthy donors only).

**Load:** `retrieve_summary_stats('aging', feature_type='gene_expression')`

---

### `immune_aging_ccc_signatures_major_celltypes.csv`
*Aging Cell-Cell Communication*

Cell-cell communication (L-R pair) aging statistics across major immune cell types (LIANA rank_aggregate). The `gene` column encodes interactions as `source_ct__ligand__target_ct__receptor` (double underscore) — parse in your analysis.

**Load:** `retrieve_summary_stats('aging', feature_type='ccc')`

---

### `sle_tf_signatures_major_celltypes.csv`
*SLE TF Signatures*

Differential TF activity statistics for SLE vs healthy across 5 major immune cell types (Perez cohort).

**Load:** `retrieve_summary_stats('sle')`

---

### `drug_tf_signatures_major_celltypes.csv`
*Drug TF Signatures*

146 drugs (vs DMSO) differential TF activity from the OP ex-vivo drug study across 5 major immune cell types.

**Load:** `retrieve_summary_stats('drug')`

---

### `cytokine_tf_signatures_major_celltypes.csv`
*Cytokine TF Signatures*

90 cytokines (vs PBS) differential TF activity from the ParseBioscience ex-vivo cytokine stimulation study across 5 major immune cell types.

**Load:** `retrieve_summary_stats('cytokine')`

---

### `immune_gene_regulatory_networks_major_cts.csv`
*Immune GRN Models*

GRN models for 5 major immune cell types (CD4T, CD8T, NK, B, MONO) inferred from aging cohorts of AIDA, ABF300, OneK1K, and Perez_SLE.

**Load:** `get_immune_grn()` from `tools/ciim/code/genomics.py`