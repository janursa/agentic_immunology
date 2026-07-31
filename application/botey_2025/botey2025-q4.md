# Genetic and molecular landscape of comorbidities in people living with HIV (Botey-Bataller & van Unen et al., 2025) — Question 4

## Question
How does host genetic variation at the NLRP12 locus regulate the inflammasome pathway across multiple omics layers in PLHIV, and how does this relate to systemic inflammation and carotid plaque formation?

## Findings
- QTL mapping of the 21 MOFA latent factors (LFs) against genome-wide genotype data identified 4 study-wide-significant (SWs) loci associated with 4 LFs; the strongest association was between LF6 (the inflammasome-related, carotid-plaque-associated factor, see Question 1) and the NLRP12 locus, which was already known as a pQTL hotspot.
- The missense variant rs34436714 (in near-perfect LD, R² > 0.99, with the lead NLRP12-locus variant) showed significant, validation-cohort-replicated associations with 2 genes, 2 metabolites and 292 proteins — despite NLRP12 having previously been dismissed as a likely pQTL artifact in a healthy-population study, this work demonstrates its genuine pleiotropic effects.
- The G allele of rs34436714 was positively associated with NLRP3 inflammasome protein concentrations but negatively associated with transcription of the corresponding inflammasome genes (a gene expression/protein discordance despite an overall positive correlation between the two levels).
- Two metabolites associated with the NLRP12 locus, AMP and taurine, were positively correlated with the inflammasome score at both the gene-expression and protein level.
- LF6 (the NLRP12-regulated inflammasome factor) correlated with monocyte subpopulation proportions (classical and intermediate monocytes), linking the genetic/molecular inflammasome signature to a specific immune cell phenotype.
- Overall conclusion: the NLRP12 locus systemically regulates the inflammasome pathway across transcriptomic, proteomic and metabolomic layers, and this pathway drives systemic inflammation and contributes to carotid plaque formation in PLHIV.

## Methodology

### Datasets
- 2000HIV discovery and validation cohort multi-omics and genotype data (same as Questions 1–2): gene expression, plasma proteins, metabolites, and the MOFA-derived LFs (specifically LF6).
- Immune cell proportion data: whole-blood immunophenotyping by flow cytometry (three panels, 17–20 markers each), yielding monocyte subpopulation proportions.
- Inflammasome gene sets from the Molecular Signatures Database (MSigDB): GOBP_POSITIVE_REGULATION_OF_INFLAMMASOME_MEDIATED_SIGNALING_PATHWAY, REACTOME_INFLAMMASOMES, GOCC_CANONICAL_INFLAMMASOME_COMPLEX, REACTOME_THE_NLRP3_INFLAMMASOME, GOCC_NLRP3_INFLAMMASOME_COMPLEX.

### Analytics
- LF-genotype QTL mapping (MatrixEQTL, same covariate-adjusted linear model as Question 2's QTL mapping) — uses genotype data plus MOFA LFs; identifies the NLRP12 locus–LF6 association as the strongest of 4 SWs loci-LF associations.
- Replication of the missense variant rs34436714 association across omics layers: genome-wide significant (P < 5 × 10⁻⁸) hits in the discovery cohort tested for replication (P < 0.05) in the validation cohort, tallied per omics layer (2 genes, 2 metabolites, 292 proteins) — uses genotype plus gene expression/protein/metabolite datasets.
- Inflammasome score calculation: average of covariate-corrected expression/abundance values across each MSigDB inflammasome gene set, computed separately at the transcriptomic (PBMC gene expression) and proteomic (plasma) level — uses gene expression and protein datasets.
- Statistical association testing: two-sided pairwise Wilcoxon rank-sum test (rs34436714 genotype groups vs. inflammasome score), Pearson's correlation (AMP/taurine metabolite abundance vs. inflammasome score; LF6 vs. monocyte subpopulation proportions), and Spearman correlation (gene-expression vs. protein-level inflammasome scores, cross-checked across gene-set definitions).
