# Genetic and molecular landscape of comorbidities in people living with HIV (Botey-Bataller & van Unen et al., 2025) — Question 3

## Question
Which circulating molecules (transcripts, proteins and metabolites) are causally linked to ex vivo cytokine production capacity upon stimulation with inactivated pathogens in PLHIV, using host genetic variation as instruments?

## Findings
- Mendelian randomization (MR) identified 313 genes, 55 proteins and 14 metabolites causally associated with cytokine responses to stimulation (386 molecules across three omics modalities overall).
- Six genes were causally linked with at least six different cytokine-stimulation pairs; LINC00173 (a lncRNA) had the highest number of causal links (11 cytokine-stimulation pairs), with higher LINC00173 expression associated with lower cytokine responses, most notably lower IL-1Ra production — consistent with prior evidence that LINC00173 is regulated during HIV infection and modulates cytokine responses.
- Six circulating plasma proteins were causally associated with at least three cytokine-stimulation pairs. IL-17D was causally linked to HIV-envelope-stimulated responses: higher IL-17D concentration was associated with lower CCL3 (MIP-1α) and IL-1β production, suggesting a potential immunomodulatory role reducing persistent immune activation.
- For CCL3 (MIP-1α) response to HIV envelope specifically: two genes (RP11-128N14.4, a lncRNA, and TRAPPC9), one metabolite and one protein (IL-17D) causally downregulated the response, while two genes (CAPS2, MYLK4) and one protein (MEGF10) causally upregulated it.
- These findings provide a catalog of candidate immune modulators (genes, proteins, metabolites) with causal relationships to cytokine production capacity in PLHIV, relevant to identifying potential drug targets/stratification markers for immunomodulatory therapy.

## Methodology

### Datasets
- 2000HIV discovery and validation cohort genotype data (same QC'd/imputed genotype dataset as Question 2), used to derive genetic instruments for exposures.
- Exposure datasets: baseline gene expression (eQTL summary statistics), plasma protein levels (pQTL) and metabolite levels (mQTL) from the 2000HIV discovery/validation cohorts.
- Outcome dataset: ex vivo cytokine production responses (cQTL summary statistics) to the 13-stimulant panel described in Question 1/2's methods.

### Analytics
- Two-sample Mendelian randomization (R package TwoSampleMR), inverse-variance weighted (IVW) method as the primary estimator — uses exposure QTL (gene expression, protein, metabolite) and outcome QTL (cytokine response) summary statistics.
- Instrument selection: SNPs strongly associated with the exposure in the discovery cohort (P < 1 × 10⁻⁵), validated as at least nominally significant in the validation cohort (P < 0.05), MAF ≥ 0.05, excluding SNPs associated with more than four other traits within the same exposure (excess pleiotropy); stringent LD clumping (r² = 0.001, 10,000 kb window); MR performed only when ≥3 independent SNPs remained.
- Sensitivity analyses for MR results with significant IVW (P < 0.05): tests for horizontal pleiotropy, heterogeneity and leave-one-out analysis.
- Bidirectional MR performed to exclude results with a significant reverse-direction causal effect (also passing sensitivity checks), removing likely confounded/reverse-causal associations.
