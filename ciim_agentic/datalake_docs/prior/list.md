# Prior Knowledge -- File List

All files located in `${CIIM_DATALAKE_DIR}/prior/`.

---

## marker_genes.json
**Immune Marker Genes**
Curated immune cell type marker genes. Two levels:
- Major (10 lineages): CD4T, CD8T, NK, B, MONO, DC, HSC, Megakaryocyte, Erythroid, ILC
- Minor (22 subtypes): Tcm_Naive_CD4, Tem_Effector_CD4, Treg, Tcm_Naive_CD8, Tem_Temra_CD8, Tem_Trm_CD8, MAIT, CD8a/a, CD16_NK, NK, Naive_B, Memory_B, Aged_B, Bcells, Plasma_B, Plasmablasts_B, Classic_MONO, NonClassic_MONO, pDC, DC1, DC2, Platelet

## tf_all.csv
**Human TF List**
List of 1,638 human transcription factors.

## sle_targets/
**SLE Prior Drug Targets**
All molecular targets of SLE from clinical trials (any phase) and approved drugs, retrieved from OpenTargets Platform (MONDO_0007915) via `disease.drugAndClinicalCandidates`. 141 drugs, 129 unique targets.
- `sle_drug_targets.csv` — 255 rows: target_gene, target_name, target_id, drug_name, drug_id, drug_type, max_phase_sle, is_approved_sle, is_approved_any, moa, action_type, trial_statuses
- `sle_targets_summary.csv` — 129 rows: one per unique target; max_phase_sle, n_drugs, drugs, approved_in_sle, moas, action_types
Analysis: `analysis/sle_previous_targets/`
