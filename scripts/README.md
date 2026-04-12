# Analysis

## target_clinical_signal_screen
Broad Repurposing Hub target screen using clinical phase labels to compare positive vs withdrawn drugs.
## virtualbiotech_replication

Replication of Virtual Biotech (Zhang et al. 2026) Figure 2 analysis: SC target features (tau, bimodality) vs clinical trial outcomes across 56K trials. Data from their public GitHub repo.

### What is Virtual Biotech about?

#### The core question

Can you predict whether a drug will succeed in clinical trials — before running the trial — just by looking at the biology of its target?

#### The insight

When a drug fails in trials, it's often because the target is expressed in many tissues/cell types you don't want (causing side effects), or it's expressed uniformly everywhere (so blocking it causes collateral damage).

The hypothesis: targets that are *specifically* expressed in just the right cell type — like a receptor expressed only on cancer cells, not on heart cells — should make better drugs.

They measured this "specificity" using single-cell RNA-seq (Tabula Sapiens healthy human atlas — **not** from trial patients; this is healthy tissue to characterise the gene's normal biology):

- `tau` — how cell-type specific is expression? (0 = everywhere, 1 = one cell type only)
- `bimodality_score` — is expression bimodal? (cells are either ON or OFF, not a gradual gradient — suggests a cleaner on/off biological switch)

#### What they did

- Collected 56,707 clinical trials from ClinicalTrials.gov
- Used LLMs to label each trial outcome: Did it progress? Was it terminated? Did endpoints succeed?
- For each trial, looked up the drug's target gene(s) and pulled the tau/bimodality scores
- Asked: do trials targeting more specific genes succeed more often?

#### What they found (and we confirmed)

Yes — strongly:

| If your target has high... | Effect |
|---|---|
| `bimodality_score` | 36% more likely to reach Phase III |
| `tau_cell_type` | 27–34% more likely to progress Phase I→II |
| `tissue_tau` | 31% more likely to succeed in Phase I→II |
| `bimodality_score` | 19% *less* likely to be terminated |

In plain terms: drugs against targets that are expressed specifically in one cell type, in an on/off fashion, are systematically more successful in clinical trials.

#### Why does this matter for us?

We can now score any target gene on these features and get a data-driven prior on its clinical tractability — before investing in a drug program. A target with low tau (expressed everywhere) is a red flag. A target with high bimodality and tissue specificity is a green flag.

This is complementary to our earlier Broad Hub screen (which used drug-phase labels) — that screen told us *which* targets appeared in more successful drugs; Virtual Biotech tells us *why* those targets are better at the molecular level.

### Data from the paper

All four files are publicly available in the paper's GitHub repo (`harrisongzhang/TheVirtualBiotech`) and were added to our data lake at `datalake/virtualbiotech/`:

| File | Description |
|---|---|
| `clinical_trial_labels.csv` | 56,707 trials with LLM-curated outcome labels (phase, status, stop reason, endpoint result, Phase I→II progression) |
| `chembl_clinical_nct_data.parquet` | NCT ID ↔ Ensembl target ID mapping from ChEMBL (76,925 trials) |
| `comprehensive_features_aggregated_v2_optimized.parquet` | Precomputed SC features (tau, bimodality, expression stats) for 1,511 target genes derived from Tabula Sapiens |
| `tahoe_efficacy_features_long.parquet` | Tahoe-100M perturbation efficacy features per gene (downloaded, not yet used) |

### Script

`virtualbiotech_replication/run_analysis.py` — adapted from the paper's `figure2_virtualbiotech_analysis.py`.

Steps:
1. Merge trial labels → ChEMBL NCT-target map → SC features (join on Ensembl ID)
2. Aggregate to trial level: MIN across all targets per trial (worst-target assumption)
3. Univariate logistic regression per feature × outcome (21 outcomes across Sections A–E)
4. BH FDR correction

Sections covered: A (phase progression), B (stopped status), C (stop reasons), D (endpoint results), E (Phase I→II progression).
Section F (adverse event betareg) is skipped — requires R's `betareg` via rpy2, not available in the singularity image.

Outputs: `figure2_all_results.csv` (192 FDR-sig associations), `figure2_expr_results.csv` (401+ FDR-sig cell-type expr hits).
