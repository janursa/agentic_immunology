# Genetic and molecular landscape of comorbidities in people living with HIV (Botey-Bataller & van Unen et al., 2025) — Question 2

## Question
What is the genetic architecture of molecular trait variation (gene expression, protein abundance, metabolite abundance and ex vivo cytokine production) in PLHIV, and how does this genetic regulation compare to that observed in individuals without HIV?

## Findings
- QTL mapping across four omics layers identified 5,962 molecular QTL at study-wide significance (SWs), with the highest counts in gene expression, followed by proteomics, metabolomics and immune/cytokine function.
- eQTL: of 17,741 genes tested, 10,642 genome-wide significant (GWs) eQTL were found for 8,591 genes (4,765 SWs eQTL for 4,920 genes). Comparison with GTEx and eQTLGen showed high concordance of effect direction (98.6% and 94.9%, respectively) and correlation (R² = 0.82 GTEx, R² = 0.68 eQTLGen); 42 cis-eQTL showed discordant effects versus both healthy datasets, suggesting disease-specific regulation.
- pQTL: of 2,367 proteins, 3,019 GWs pQTL were found for 1,427 proteins (1,646 SWs pQTL for 1,040 proteins, 43.93% of measured proteins), including a chromosome 19 hotspot with trans signals for 367 proteins. Comparison with UK Biobank Pharma Proteomics Project (UKB-PPP) showed 99.94% concordance in effect direction.
- mQTL: 171 GWs metabolite QTL for 159 metabolites (40 SWs); comparison to a healthy cohort (500FG) showed R² = 0.62 concordance — lower than for proteins/genes, possibly reflecting HIV/ART effects on metabolism.
- cQTL: 2 SWs and 13 GWs cytokine-response QTL, 12 of which were novel; highlighted the TLR1-6-10 and HLA loci. Two cis-acting loci regulating CCL2 (MCP-1) and CCL3 (MIP-1α) responses were identified; colocalization linked the CCL3 response locus to baseline CCL3 eQTL and neighboring CCL3L3/CCL4L2/CCL4, whereas CCL2 response regulation appeared specific to the stimulated setting (no association with baseline CCL2 protein or in external eQTL/pQTL data).
- Three loci harboring missense variants (NLRP12, TLR1, KLKB1) were found to regulate multiple omics layers simultaneously.
- Overall conclusion: genetic regulation of gene expression, protein and metabolite abundance in PLHIV is broadly concordant with that of healthy individuals, though disease-specific/discordant effects exist at a subset of loci.

## Methodology

### Datasets
- 2000HIV discovery cohort (genotype QC-imputed, n up to 1,003; molecular assays: gene expression n = 1,048, protein n = 1,064, metabolite n = 1,069, cytokine response n = 196–1,031 depending on stimulation) and validation cohort (genotype n = 257; gene expression n = 260, protein n = 266, metabolite n = 267, cytokine response n = 41–260).
- Genomics: Illumina Global Screening Array genotyping, QC'd with PLINK 1.90b/2.0, imputed to TOPMed Freeze 5 reference panel (GRCh38); 8,944,122 SNPs retained after QC in the European-ancestry subset used for QTL mapping.
- External comparison datasets: GTEx (whole-blood eQTL), eQTLGen (eQTL), UK Biobank Pharma Proteomics Project (UKB-PPP, pQTL) and 500 Functional Genomics Project (500FG, mQTL, healthy cohort).

### Analytics
- Genotype QC/imputation pipeline: PLINK-based variant/sample filtering (call rate, HWE, heterozygosity, MAF), liftOver GRCh37→GRCh38, TOPMed imputation server, BCFtools post-imputation filtering (imputation R², MAF) — uses genomics dataset.
- QTL mapping via MatrixEQTL, linear model of inverse-rank-transformed omics values (gene expression, protein, metabolite, cytokine response) against genotype, adjusted for age, sex, BMI, seasonality (sine/cosine terms), pre/post-COVID-pandemic inclusion, COVID vaccination status and recruitment center — uses genotype plus each respective omics dataset (discovery cohort primary, validation cohort for replication).
- Significance thresholds: genome-wide significance (P < 5 × 10⁻⁸) and study-wide significance (GWs threshold corrected by the number of effective independent tests, per Li & Ji 2005 eigenvalue method).
- Colocalization analysis (coloc R package) — uses cQTL summary statistics jointly with baseline eQTL/pQTL summary statistics at the CCL2–CCL3 locus.
- Cross-cohort concordance analysis — lead SNP effect estimates (direction and R²) from 2000HIV QTL compared against GTEx (eQTL), eQTLGen (eQTL), UKB-PPP (pQTL) and 500FG (mQTL) summary statistics.
