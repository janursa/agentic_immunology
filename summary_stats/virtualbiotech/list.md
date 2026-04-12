# Virtual Biotech -- File List

All files located in `summary_stats/virtualbiotech/`. Derived from the Virtual Biotech paper (Zhang et al. 2026) public data. Source repo: `harrisongzhang/TheVirtualBiotech`.

---

## target_sc_features.csv
**SC Target Features**
Single-cell expression features for 1,511 human target genes precomputed from the Tabula Sapiens healthy human atlas (not from trial patients). Includes cell-type and tissue specificity (tau), bimodality, predicted adverse event risk per organ system, and composite attrition risk scores per trial phase.

## target_clinical_success_overall.csv
**Clinical Success Rates per Target (Overall)**
Empirical trial outcome rates per target gene aggregated across all diseases, based on 56,707 ChEMBL-mapped trials. Reports % and count for: reaching Phase II+/III+, termination, withdrawal, positive endpoint (primary/secondary/either), and Phase I→II progression. Best used with `n_trials >= 5`.

## target_clinical_success_by_disease.csv
**Clinical Success Rates per Target × Disease**
Same outcome rates as above but stratified by `disease_name` from ChEMBL (95,498 target × disease combinations). Useful for disease-specific target queries. Most rows have `n_trials = 1`; filter to `n_trials >= 5` for meaningful rates.
