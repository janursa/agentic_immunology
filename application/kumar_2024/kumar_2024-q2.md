# Systemic dysregulation and molecular insights into poor influenza vaccine response in the aging population (Kumar et al., 2024) — Question 2

## Question
Which prevaccination (baseline) plasma protein and metabolite biomarkers correlate with, and mechanistically explain, the antibody response to influenza vaccination in the aging population?

## Findings
- Partial least-squares regression (PLSR) of prevaccination plasma proteome against antibody fold change (all three strains) in the discovery cohort identified components explaining ~40% of covariation; TNFSF13 (APRIL) and IL-15 were the top proteins negatively associated with antibody fold change across all three influenza strains, while most other prioritized proteins showed strain-specific (contrasting) associations.
- The negative association of prevaccination IL-15 with antibody response was replicated in the smaller replication cohort (for two of three strains) and corroborated at the transcriptome level (elevated IL15 expression in NRs prevaccination); single-cell RNA-seq reference data showed monocytes are the primary source of plasma IL-15.
- Because IL-15 drives NK-cell proliferation/maturation, and NRs showed higher activated NK-cell frequencies (from bulk transcriptome deconvolution and replication-cohort flow cytometry), the authors experimentally tested the IL-15–NK cell axis: IL15RA-/- mice (reduced NK cells) immunized with OVA showed increased CD4 T cells, T follicular helper (TFH) and germinal-center (GC) B cells in draining lymph nodes, a significantly higher TFH/Tfr ratio, and significantly higher OVA-specific IgG1 titers than IL15RA+/+ controls under two immunization protocols (OVA-Alum and OVA-IFA) — mechanistically confirming that high IL-15/NK-cell activity suppresses germinal-center responses and antibody production.
- PLSR of prevaccination plasma metabolome against antibody fold change (8 components, ~40% variance explained) identified malic acid and citric acid (component 1) as top negative predictors of antibody response across all three strains, and betaine as a top positive predictor.
- Malic acid showed strong negative associations with TNFα, IL-6, and IL-1β production upon influenza stimulation in an independent cohort of 500 healthy individuals; citric acid was negatively associated with specific CD4+ T-cell and immature neutrophil subsets in another independent cohort.
- PLSR component 2 of the metabolome highlighted unsaturated long-chain fatty acids (LCFAs, e.g., palmitoleic/hypogeic acid) and the odd-chain fatty acid pentadecanoic acid as predictors of antibody response; these LCFAs were negatively associated with prevaccination IL-15 abundance and, as a class, negatively associated with inflammatory proteins in the aging (>65) cohort but not in a younger (<65, 500FG) cohort, suggesting an age-dependent anti-inflammatory role for LCFAs.
- Together, findings support a model in which high prevaccination IL-15 (from monocytes, amplified by chronic low-grade inflammation) drives NK-cell activation and suppresses germinal-center/antibody responses, while a subset of LCFAs and odd-chain fatty acids may counteract this inflammatory state and could represent pharmacologically modulable biomarkers of poor vaccine response.

## Methodology

### Datasets
- Discovery cohort: 200 vaccinees (>65 years, season 2015/2016), prevaccination (day 0) plasma proteome and metabolome data used for PLSR biomarker discovery.
- Replication cohort: 34 vaccinees (season 2014/2015) for validating IL-15/TNFSF13 associations.
- Plasma proteome: Olink Explore Inflammation panel (up to 311 proteins), prevaccination timepoint.
- Plasma/serum metabolome: untargeted LC-MS panel of 192 endogenous metabolites, prevaccination timepoint.
- Whole blood bulk transcriptome (10 TR + 10 NR subset) — prevaccination IL15 expression comparison.
- Single-cell RNA-seq reference of human PBMCs (published dataset, ref. 58) — cell-type source of IL-15.
- Mouse experimental dataset: sex-matched IL15RA-/- and IL15RA+/+ C57BL/6 mice (10–12 weeks), immunized with OVA-IFA or OVA-Alum; spleen/lymph node flow cytometry (B/T/NK cell subsets, TFH, Tfr, GC B cells) and serum anti-OVA IgG1 ELISA, day 11 post-immunization.
- Independent cohort 1 (500FG): 500 healthy individuals with influenza-stimulated PBMC cytokine production data (IL-1β, IL-6, TNFα) — for metabolite/IL-15–cytokine associations and LCFA age-dependence comparison.
- Independent cohort 2 (~300 healthy individuals, deep immune phenotyping cohort): immune cell subset counts — for citric acid associations.

### Analytics
- Partial least-squares regression (PLSR, R `pls` package, 100 iterations, 10-fold cross-validation) of prevaccination proteome on antibody fold change (all 3 strains jointly) — uses discovery-cohort proteome + serology.
- Rank-product analysis over PLSR iterations to identify top 30 predictor proteins per component, followed by directionality (t-test statistic) assessment against each strain's antibody fold change — uses proteome.
- Replication of top protein associations (IL-15, TNFSF13) in the smaller replication cohort — uses replication-cohort proteome.
- Comparison of prevaccination IL15 transcript levels between TRs and NRs — uses bulk transcriptome.
- Single-cell RNA-seq cell-type expression analysis of IL-15 in PBMCs — uses external scRNA-seq reference.
- In vivo mouse experiment: immunization of IL15RA-/- vs IL15RA+/+ mice, flow cytometric quantification of splenic/lymph-node B, T, NK, TFH, Tfr, GC-B cell populations, and ELISA-based anti-OVA IgG1 titer quantification; group comparisons via Wilcoxon rank-sum test — uses mouse experimental dataset.
- PLSR (same design as proteome) of prevaccination metabolome on antibody fold change — uses discovery-cohort metabolome + serology.
- Rank-product analysis of PLSR components to identify top metabolite predictors (malic acid, citric acid, betaine, LCFAs) — uses metabolome.
- Partial correlation analysis (age/gender-corrected) of prioritized metabolites (malic acid, citric acid) with cytokine production and immune cell subset frequencies — uses metabolome + independent 500FG/300-donor cohorts.
- Partial correlation analysis of LCFAs with prevaccination IL-15 abundance, and of LCFA class with inflammatory protein abundance, compared between the aging cohort and a younger (500FG) cohort — uses proteome + metabolome + 500FG cohort.
