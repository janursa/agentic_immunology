# Virtual Biotech -- File List

All files located in `${CIIM_DATALAKE_DIR}/virtualbiotech/`. All four files are publicly available from the paper's GitHub repo (`harrisongzhang/TheVirtualBiotech`, `trials_analysis/data/`). Source: Zhang et al. 2026, "The Virtual Biotech" (bioRxiv 2026.02.23.707551).

---

## clinical_trial_labels.csv
**Clinical Trial Outcome Labels**
56,707 clinical trials from ClinicalTrials.gov with LLM-curated outcome labels. The most valuable piece of the dataset — extracting these from raw trial text is what the paper's main contribution is. Columns include trial phase, status (Active/Terminated/Withdrawn/Suspended), stop reason and category, primary/secondary endpoint result (POSITIVE/NEGATIVE/MIXED/NA), Phase I→II progression flag, and adverse event rates by organ system.

## chembl_clinical_nct_data.parquet
**ChEMBL NCT–Target Mapping**
488,361 rows mapping NCT trial IDs to drug targets (Ensembl gene IDs) and diseases (EFO IDs + disease name) via ChEMBL. The bridge between trial labels and gene-level biology. Key columns: `nct_id`, `targetId` (Ensembl), `diseaseId` (EFO), `disease_name`, `drugId` (ChEMBL), `phase`, `status`, `mechanism_of_action`.

## comprehensive_features_aggregated_v2_optimized.parquet
**SC Target Features**
Precomputed single-cell expression features for 1,511 human target genes derived from the Tabula Sapiens healthy human atlas. 127 columns covering cell-type and tissue specificity (tau), bimodality, cell-type-specific expression per 62 cell types, predicted AE risk per organ system, and composite attrition/safety risk scores. This is the gene-level feature table used in all regression analyses — see `summary_stats/virtualbiotech/target_sc_features.csv` for a leaner version with the key columns only.

## tahoe_efficacy_features_long.parquet
**Tahoe-100M Drug Efficacy Features**
2.9M rows of functional drug efficacy scores from the Tahoe-100M perturbation atlas — drugs tested across cancer cell lines at multiple concentrations. Long-format: one row per drug × cell line × concentration × feature. Feature types include functional scores (apoptosis, proliferation suppression, cell cycle arrest, DNA damage, stress response) and scores stratified by mutation context (KRAS/TP53/PIK3CA/BRAF mutant vs wild-type). 
