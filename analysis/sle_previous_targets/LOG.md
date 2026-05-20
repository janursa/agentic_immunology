# Task
Get all molecular targets of SLE (Systemic Lupus Erythematosus) from past clinical trials (any phase) and approved drugs.

## Strategy
1. Query OpenTargets Platform (EFO_0002690) `knownDrugs` via GraphQL — comprehensive source aggregating ChEMBL clinical trial data + FDA/EMA approvals.
2. Cross-check with ChEMBL direct query for SLE indication.
3. Output: clean target table with drug, phase, mechanism.

## Step 1 — OpenTargets Platform query (corrected)

- API: `https://api.platform.opentargets.org/api/v4/graphql`
- Correct disease ID: `MONDO_0007915` (not `EFO_0002690` — Platform API uses MONDO IDs)
- Correct field: `disease.drugAndClinicalCandidates` (not `knownDrugs` — schema changed)
- Targets extracted via `drug.mechanismsOfAction.rows[].targets`

## Results

- 141 drugs/candidates in SLE
- 129 unique molecular targets
- Approved drugs in SLE: 8 (ANIFROLUMAB, BELIMUMAB, hydroxychloroquine, glucocorticoids)
- Phase 3 targets include: JAK1 (8 drugs), TYK2 (6 drugs), JAK2 (5 drugs), TNFSF13B (5 drugs), JAK3 (4 drugs), BTK, CD20, CD22, IL-12, S1PR1

## Output files
- `sle_drug_targets.csv` — full table (255 rows): target_gene, target_name, drug_name, drug_type, max_phase_sle, is_approved_sle, moa, action_type
- `sle_targets_summary.csv` — 129 unique targets with max_phase, drug count, approved status, moas
