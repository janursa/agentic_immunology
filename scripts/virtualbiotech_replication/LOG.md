# Virtual Biotech Replication — LOG

## Source
Paper: "The Virtual Biotech" (bioRxiv 2026.02.23.707551)
Repo: https://github.com/harrisongzhang/TheVirtualBiotech

## Data Downloaded
All 4 files from the public GitHub repo into `datalake/virtualbiotech/`:
- `clinical_trial_labels.csv` — 56,707 LLM-curated trial outcome labels
- `chembl_clinical_nct_data.parquet` — NCT↔targetId (Ensembl) mapping
- `comprehensive_features_aggregated_v2_optimized.parquet` — precomputed SC features for 1,511 genes
- `tahoe_efficacy_features_long.parquet` — Tahoe-100M perturbation features (not used here)

## Analysis
Script: `run_analysis.py` — adapted from `figure2_virtualbiotech_analysis.py`

### What we run (Sections A–E):
- **A** Phase progression: Phase II+, III+, IV
- **B** Stopped status: Terminated, Withdrawn, Suspended
- **C** Stop reasons: Negative, Safety, Enrollment, etc. (11 categories)
- **D** Endpoint results: Primary/Secondary/Either Positive
- **E** Phase 1 → Phase 2 progression

### What we skip:
- **Section F** (AE betareg): requires rpy2/R betareg, not in biomni_full.sif

### Key steps:
1. Merge clinical_trial_labels → ChEMBL NCT-target map → SC features (Ensembl ID join)
2. Aggregate to trial level: MIN across all targets per trial (worst-target assumption)
3. Univariate logistic regression per feature per outcome
4. BH FDR correction

## Results
- 56,555 trials after QC
- 33 non-expr features tested; 192 FDR-significant associations
- 62 cell-type-specific expr features; 403 FDR-sig (fold-change), 398 (adjusted)

### Top signals (FDR < 0.05, sorted by p-value):
| Feature | Outcome | OR | Interpretation |
|---|---|---|---|
| bimodality_score | Phase III+ | 1.36 | Cell-type bimodality → more likely to reach Phase III |
| tau_cell_type_max | Phase III+ | 1.34 | High max tau → Phase III progression |
| tissue_tau | Phase III+ | 1.32 | Tissue specificity → phase progression |
| bimodality_score | Terminated | 0.81 | High bimodality → LESS likely terminated |
| tau_cell_type | Phase 2 Progression | 1.27 | Cell-type tau → Phase I→II success |

**Core finding replicated**: cell-type-specific (high tau) and bimodal targets are consistently
enriched in successful trials and depleted in terminated/withdrawn trials.

## Output Files
- `figure2_all_results.csv` — non-expr features × all outcomes (192 FDR-sig rows)
- `figure2_expr_results.csv` — cell-type expr features × outcomes (fold-change + adjusted)
