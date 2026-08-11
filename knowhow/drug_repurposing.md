# Drug Repurposing — Reference

Methodology for drug repurposing in immune aging and disease contexts. Used by `data_analyst_agent` when running drug repurposing tasks.

---

## Tools

- [`tools/biomni/pharmacology_biomni.md`](../tools/biomni/pharmacology_biomni.md) — `retrieve_topk_repurposing_drugs_from_disease_txgnn`, `predict_admet_properties`, `query_fda_adverse_events`, `check_fda_drug_recalls`, `query_drug_interactions`, `analyze_fda_safety_signals`.

Always prefer these existing tools over reimplementing methods yourself.

## Image selection

| Step | Image |
|---|---|
| TxGNN, ADMET, FDA, DDInter | `biomni_full.sif` |
| Aging clock (if applicable) | see `knowhow/aging_clocks.md` |

---

## Workflow

### 1. Load signatures
Load from the file paths given in the task:
- **Disease/aging signature**: gene × signed effect size (log FC or z-score) for the condition and cell type(s).
- **Drug signatures**: drug × gene × signed effect size. Load for the same cell type(s) where available.

No precomputed signature set ships with the platform — if the task does not provide one, say so and stop.

### 2. Build candidate pool (TxGNN)
Run `retrieve_topk_repurposing_drugs_from_disease_txgnn(disease_name=context, k=50)` using `biomni_full.sif`. Any drug present in the drug signature dataset is also included regardless of TxGNN rank — TxGNN is one evidence layer, not a gate.

### 3. Signature reversal scoring
For each drug × cell_type pair, compute two complementary metrics against the disease/aging signature:

**Cosine similarity** (direction + magnitude):
- Restrict to genes present in both the drug and disease signatures.
- Compute cosine of the signed effect-size vectors.
- Negative value = reversal.

**Hit ratio** (coverage):
- Numerator: # disease/aging genes where the drug effect has the opposite sign.
- Denominator: total # genes in the disease/aging signature.

Both are required and reported separately. Save to `{WORK-DIR}/results/reversal_scores.csv` immediately after this step.

### 4. Aging clock (conditional)
If perturbation expression data is available for any candidate drug:
- Read `knowhow/aging_clocks.md` for clock selection, feature coverage rules, execution commands, and output format.
- Write and run the aging clock script inline (write to `{WORK-DIR}/code/clock_script.py`, execute in the correct singularity image per the knowhow).
- Add the returned predicted age delta per drug to the evidence table.
- If no suitable data exists, skip and mark the clock column as `NA` for all drugs.

### 5. Safety annotation
Run using `biomni_full.sif`:
- `predict_admet_properties(smiles_list)` → ADMET pass/fail per drug.
- `query_fda_adverse_events(drug_name)` → top adverse event signals.
- `check_fda_drug_recalls(drug_name)` → active recalls flag.
- `query_drug_interactions(drug_names)` → DDInter interaction flags.

Save to `{WORK-DIR}/results/safety_annotations.csv` immediately after this step.

### 6. Assemble evidence table
Merge all evidence into `{WORK-DIR}/results/evidence_table.csv`. Columns:

| drug | context | cell_type | cosine_reversal | hit_ratio | n_genes_overlap | txgnn_score | clock_age_delta | admet_pass | fda_adverse_flag | fda_recall_flag | ddi_flag | data_sources |

Save incrementally — update after each step, not only at the end.

### 7. Prioritization
Apply after all evidence is collected. No drug is dropped before this step.

Composite score (`composite_score`) from:
1. `evidence_count` — number of independent sources contributing.
2. `hit_ratio` — breadth of reversal.
3. `clock_age_delta` — clock-based reversal.
4. If multiple cell types, deprioritize drugs that rejuvenate one cell type but accelerate others.

Disqualifiers (flag, do not silently drop): failed ADMET, active FDA recall. Report disqualified drugs separately with reason.
