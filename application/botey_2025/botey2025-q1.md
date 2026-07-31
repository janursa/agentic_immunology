# Genetic and molecular landscape of comorbidities in people living with HIV (Botey-Bataller & van Unen et al., 2025) — Question 1

## Question
Which multi-omic latent factors (integrating epigenomics, transcriptomics, proteomics, metabolomics and ex vivo cytokine production) capture the inter-individual variation among people living with HIV (PLHIV), and which of these factors are linked to non-AIDS comorbidities and systemic inflammation?

## Findings
- Multi-omics factor analysis (MOFA) yielded 21 latent factors (LFs), each explaining 1–20% of total variance, predominantly composed of features from all five data modalities.
- 19 of 21 LFs were significantly correlated (FDR < 0.05) with systemic inflammation, measured via IL-1β production capacity, IL-1β plasma concentration or IL1B gene expression — indicating IL-1β-driven inflammation is a major axis of inter-individual variation.
- Only 5 significant LF associations (FDR < 0.05) were found with HIV-related phenotypes (rapid progressors, CD8+ and CD4+ T cell counts), suggesting molecular variation is driven more by non-HIV-related factors.
- LF6 (5.19% variance explained, dominated by plasma proteins) was significantly higher in PLHIV with a documented carotid plaque and captured innate immune activation and NF-κB activation signatures at the protein and gene-expression level.
- LF8 (3.89% variance explained, dominated by metabolomics and proteomics) was negatively associated with cardiovascular disease (myocardial infarction, hypertension) and endocrine disorders; key contributing metabolites included indoxyl sulphate and DHEA-S; LF8 also captured variation in IL-10 and IL-1β cytokine responses and RNA-mediated mitosis/intracellular transport pathways.
- LF11 was positively associated with COPD and correlated with CD8+ T cell counts; it was characterized by lower B-cell-related proteins/transcripts together with higher interferon activity and chemokine/T cell function.
- LF20, dominated by DNA methylation, was significantly associated with rapid progressors (individuals with a sharp CD4+ T cell decline after infection); SKAP1 showed lower expression (gene expression and protein) in rapid progressors, with enrichment for inositol metabolism (gene expression) and immune activation (protein).

## Methodology

### Datasets
- 2000HIV cohort: 1,342 virally suppressed PLHIV (2000HIV Human Functional Genomics Partnership Program), split into a discovery cohort (N = 1,075, 3 Dutch clinical centers) and a validation cohort (N = 267, 1 separate center); 89% male, median age 54, median HIV duration 10 years.
- Epigenomics: Illumina EPIC methylation array; top 20,000 most variable CpG probes used.
- Transcriptomics: bulk RNA sequencing of PBMCs (17,741 genes after processing).
- Proteomics: Olink Explore 3072 targeted panel; 2,367 proteins after QC.
- Metabolomics: General Metabolics untargeted mass-spectrometry platform; 851 endogenous metabolites (per HMDB annotation).
- Cytokine production: ex vivo PBMC stimulation with 13 stimulants (poly I:C, LPS, imiquimod, IL-1a, HIV envelope, CMV, S. pneumoniae, E. coli, S. aureus, M. tuberculosis, C. albicans conidia/hyphae, PHA); 77 cytokine-response features.
- Clinical/comorbidity data: cardiovascular, endocrine, gastrointestinal and respiratory disease diagnoses, plus HIV phenotypes (rapid progressor status, CD4/CD8 T cell counts) from the cohort database.

### Analytics
- MOFA (R `run_mofa`, 30 factors, view scaling, default parameters) — integrates epigenomics, transcriptomics, proteomics, metabolomics and cytokine-production datasets (genomics excluded); each modality pre-corrected for age, sex and collection institute via linear-model residuals; artifact factors (correlated >0.6 with cross-modality feature averages) discarded; factors retained if explaining >1% of variance — yields 21 LFs.
- LF–clinical association testing: Wilcoxon rank-sum test (binary variables), Kruskal–Wallis test (categorical variables), Pearson's correlation (continuous variables), all FDR-corrected — uses LFs plus clinical/comorbidity and HIV-phenotype data.
- LF–inflammation correlation: Pearson's correlation of each LF with normalized/scaled IL-1β protein, gene-expression and cytokine (24-hour stimulation average "IL-1β score") values, FDR-corrected — uses LFs plus cytokine, protein and gene-expression datasets.
- Molecular profiling of LFs: significant feature weights extracted per factor/modality (top/bottom 1% under a standard-normal assumption); enrichment testing via MOFA2's `run_enrichment` (principal-component gene-set enrichment) against blood transcriptome modules (methylation, gene expression, protein) and cytokine stimulation/cytokine groupings — uses LF weight matrices.
- Validation: LFs projected onto the validation cohort by matrix multiplication of preprocessed validation data with discovery-derived significant weights, confirming robustness of LF definitions — uses validation cohort omics data.
