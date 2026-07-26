# Systemic dysregulation and molecular insights into poor influenza vaccine response in the aging population (Kumar et al., 2024) — Question 1

## Question
How does the vaccination response differ, at the systems (transcriptome, proteome, metabolome) level, between responders (high responders/HRs, triple responders/TRs) and poor responders (low responders/LRs, nonresponders/NRs) among vaccinated individuals >65 years old?

## Findings
- Prevaccination proteomes and metabolomes did not differ significantly between HRs/LRs or TRs/NRs, but clear differences emerged in the *longitudinal* (post-vaccination) dynamics: responders (HRs, TRs) mounted time-dependent changes in plasma proteins and metabolites that were absent or blunted in poor responders (LRs, NRs).
- Proteome: HRs/TRs up-regulated TNFRSF13B (TACI), CCL3, IFNLR1, SLAMF7, CD48, SIGLEC10, GZMA, and HLA-E at day 7 and/or day 35 post-vaccination; these changes did not reach significance in LRs, and NRs instead up-regulated a distinct set (PARP1, EGLN1, SERPINB8) linked to inflammation/hypoxia rather than adaptive immune activation.
- Metabolome: HRs/TRs showed consistent post-vaccination up-regulation of amino acids (methionine, arginine, tyrosine, and organic acids) and down-regulation of fatty acyls/lipids (including bile acids), plus HR-specific up-regulation of 4-pyridoxic acid (vitamin B6 metabolite) and tyramine; NRs lacked the sustained amino acid increase seen in TRs, indicating metabolic dysregulation.
- Transcriptome: NRs showed a persistent inflammatory/monocyte-driven signature (elevated inflammatory and TLR signaling BTMs) at all time points including prevaccination, whereas TRs showed transient antiviral/interferon activation at day 3 followed by a strong, specific transcriptional response (cell cycle, plasma cell, immunoglobulin, T-cell activation modules) peaking at day 7 that resolved by day 35; NRs showed no statistically significant DEGs at any post-vaccination time point.
- Cellular deconvolution and flow cytometry (replication cohort) showed TRs had higher T- and B-cell/plasma-cell proportions at day 7 (consistent with clonal expansion), while NRs had higher neutrophil proportions and higher activated NK-cell proportions/activity; NK/CD8 T-cell activation modules were more strongly associated with immune activation BTMs in NRs than TRs, and Treg proportions were negatively associated with immune activation BTMs in NRs (suggesting an attempted but insufficient anti-inflammatory brake).
- Genome-wide antibody QTL mapping (MAGMA gene-set analysis) showed the transcriptional modules separating TRs from NRs (plasma cell/Ig and myeloid/inflammatory modules) were suggestively enriched for genetic association with antibody response, and top MAGMA-ranked genes overlapped with genes differentially expressed between TRs and NRs, anchoring the transcriptomic signature at the genetic level.
- Multiomics integration (MOFA) identified a latent factor (factor 3, ~18% variance) spanning transcriptome, proteome, and metabolome that separated TRs from NRs independent of time; top contributing molecules (CCL25, CCL3 proteins; arginine, methionine metabolites) were consistently higher in TRs, and arginine/methionine were positively associated with pro-inflammatory cytokine (IL-1β, IL-6, TNFα) production capacity upon influenza stimulation in an independent healthy cohort, linking these amino acids to functional immune competence.
- An integrative network combining proteome, metabolome and transcriptome BTMs showed transcriptome and proteome were tightly interconnected while the metabolome was more loosely connected; TR-associated nodes (e.g., arginine, TNFRSF13B, IFNLR1, CCL3) linked to B-cell/plasma-cell and T-cell modules, whereas NR-associated nodes (e.g., xanthosine, glyceric acid 1,3-bisphosphate) linked to immune activation/inflammatory modules.

## Methodology

### Datasets
- Discovery cohort: 200 vaccinees (>65 years), influenza season 2015/2016, longitudinal blood/plasma samples (day 0, 1, 3, 6/7, 21, 70).
- Replication cohort: 34 vaccinees, influenza season 2014/2015 (non-overlapping donors), same longitudinal design (used for replication of proteome/metabolome/flow cytometry findings).
- Serology: HAI and MN titers against H1N1, H3N2, and B strains, pre- and post-vaccination, used to classify donors as HR/LR (per strain, >4-fold vs <4-fold rise) and TR (N=71)/NR (N=10)/Other.
- Plasma proteome: Olink Explore Inflammation panel, up to 311 high-quality proteins, 702 samples (three time points x 234 individuals).
- Plasma/serum metabolome: untargeted LC-MS (flow-injection MS), 192 endogenous metabolites (HMDB-annotated, drug/xenobiotic-filtered), plus targeted amino acid panel (AbsoluteIDQ p180) for validation.
- Whole blood bulk transcriptome: subset of 10 TRs and 10 NRs, 5 time points each (baseline, day 1/3, day 6/7, day 21/35, day 60/70); RNA-seq (Salmon quantification).
- Complete blood counts: all 200 discovery-cohort donors, prevaccination.
- Genotype data: Illumina Infinium Global Screening Array, imputed against HRC1.1 reference panel, 176 individuals (~54.1M SNPs after QC), used for antibody QTL mapping.
- Replication-cohort flow cytometry: human PBMCs (season 2014/2015 donors) stained for NK/T markers.
- Independent cohort (500FG): 500 healthy individuals with cytokine production data (IL-1β, IL-6, TNFα) after 24h influenza stimulation of PBMCs, and single-cell RNA-seq reference of human PBMCs.

### Analytics
- Serological classification (HR/LR per strain; TR/NR/Other overall) — uses serology data.
- Longitudinal differential protein abundance (limma/linear mixed models: protein ~ strainresponse_time + age + sex + 1|donor, and time_responder models for TR/NR), day 7 vs day 0 and day 35 vs day 0 — uses plasma proteome.
- Longitudinal differential metabolite abundance (analogous linear mixed models) plus metabolite class/pathway over-representation analysis (IMPALA) — uses metabolome.
- Bulk RNA-seq differential expression (limma-voom, gene ~ responder/time + age + sex + 1|donor) between TRs and NRs and across time points — uses transcriptome.
- Gene set enrichment analysis (GSEA) using Blood Transcriptome Modules (BTMs) on ranked DEG statistics — uses transcriptome.
- Cellular deconvolution (CIBERSORT, LM22 signature) of transcriptome samples, associated with BTM pathway activity via linear mixed models (cell proportion ~ BTM_score + age + sex + 1|donor) — uses transcriptome + CBC (validation).
- Flow cytometry validation of NK-cell frequencies in replication cohort — uses PBMC flow cytometry data.
- Genome-wide antibody QTL mapping (linear regression of rank-normalized log fold-change titers on imputed genotypes, adjusted for age/sex) and MAGMA gene-set/BTM-level aggregation — uses genotype + serology + transcriptome-derived BTMs.
- Multiomics factor analysis (MOFA), unsupervised integration of transcriptome (1560 top variable genes), proteome (279 proteins), metabolome (158 metabolites) across day 0/7/35 in 10 TR + 10 NR subset — uses transcriptome, proteome, metabolome.
- Association of MOFA factor-3 top proteins/metabolites (CCL25, CCL3, arginine, methionine) with cytokine production capacity after influenza stimulation (partial correlation, age/sex-adjusted) — uses proteome/metabolome + 500FG cohort.
- Cross-omics network construction (linear mixed models linking proteins/metabolites to transcriptome BTM activity; Cytoscape visualization) — uses transcriptome, proteome, metabolome jointly.
