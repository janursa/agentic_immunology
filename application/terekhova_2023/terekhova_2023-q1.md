# Single-cell atlas of healthy human blood unveils age-related loss of NKG2C+GZMB–CD8+ memory T cells and accumulation of type 2 memory T cells (Terekhova et al., 2023) — Question 1

## Question
Using ABF300 cohort, investigate how immune cell subpopulations remodel compositionally and transcriptionally with healthy aging?

## Findings
- Profiling of ~2 million PBMCs from 317 samples (166 donors) resolved 55 biologically distinct immune subpopulations; 12 of these subpopulations showed statistically significant age-associated frequency changes.
- Overall CD4+ T cell proportion did not change with age, while conventional (non-MAIT) CD8+ T cells decreased, producing the well-known age-associated rise in the CD4+/CD8+ T cell ratio; MAIT cells declined after ~55 years.
- Within CD4+ memory subsets, Th2 memory cells and a novel HLA-DR+ CD4+ Tmem population significantly accumulated with age; naive Treg cells decreased while memory Treg cells increased, with total Treg proportion stable; naive CD4+ T cells showed only a slight, non-significant decrease but underwent strong transcriptional remodeling (IL2-STAT5/CD25 upregulation, metabolic/TCA pathway shifts) without classical activation signatures.
- Within CD8+ T cells, GZMK+ effector memory cells strongly and gradually accumulated with age (~9% to ~20% of CD8+ cells), and naive CD8+ T cells declined; CCR4+ and CCR4– central memory (Tcm) subsets both accumulated, with CCR4+ Tcm expanding faster; Temra, Tem-GZMB, and tissue-resident memory (Trm) subsets showed no significant age dependence.
- Myeloid subpopulations (classical/non-classical monocytes, pDCs, cDCs) remained transcriptionally and proportionally static with age; cell-cell communication analysis detected age-related differences in SEMA4D (myeloid-T cell) and FLT3 (progenitor-T cell) signaling.
- NK cells showed no significant age-associated compositional change overall, though a trend of CD56bright loss and accumulation of higher-CD57 CD56dim subsets was noted; gd T cells showed age-related restructuring restricted to naive and Vd1 GZMB+ subsets, without transcriptional age-dependence.
- B cells (9 clusters) showed limited compositional change with age; the most prominent age effect in B cells was BCR repertoire (clonal) restructuring rather than subpopulation frequency shifts.
- Spectral cytometry (30-color panel, 26 donors: 13 young/13 old) independently confirmed the scRNA-seq findings for naive CD4+ T cell stability, HLA-DR+ CD4+ Tmem accumulation, and Th2 CD4+ Tmem accumulation with age.
- A composite PCA built from the top 10 age-associated features showed strong concordance with donor age, and similar age-related shifts (e.g., GZMK+ Tem, HLA-DR+ CD4+, Th2 accumulation) were reproduced in independent public scRNA-seq cohorts (healthy/psoriasis, supercentenarian datasets).

## Methodology

### Datasets
- ABF300 cohort: 317 PBMC samples from 166 healthy, Caucasian, non-obese (BMI<30) adults aged 25–85 (WashU IRB-201804084), collected 2018–2021, cross-sectional plus short-term longitudinal (annual) sampling; excluded donors with cancer, chronic inflammatory disease, blood-borne infection, smoking, or recent illness.
- scRNA-seq/scTCR-seq/scBCR-seq with 20-antibody feature barcoding (FB), generated in 14 sequencing batches; ~2 million cells after QC, ~6,000 cells/sample, ~1,300 genes/cell.
- Donors split into 5 age groups (10-year bins): A (25–34, n=96 cells cohort/ n=47 blood-panel cohort), B (35–44), C (45–54), D (55–64), E (65+, n=73/n=37).
- Clinical blood panel data (hs-CRP, LDH, creatine kinase, cholesterol/triglycerides, cortisol, insulin, glucose, liver/kidney markers, DHEA-S, TSH, RBC/hemoglobin) for all donors.
- 30-color spectral cytometry validation cohort: 26 individuals (13 young, 13 old; Table S8), custom 30-marker panel (Table S4).
- Public reference datasets: Azimuth human PBMC reference (Hao et al. 2021; GEO GSE164378 / Zenodo 4546839); Liu et al. 2022 healthy-vs-psoriasis scRNA-seq dataset (GEO GSE194315); Hashimoto et al. 2019 supercentenarian scRNA-seq dataset.

### Analytics
- Batch harmonization of count data across 14 libraries using Harmony — uses ABF300 scRNA-seq dataset.
- Hierarchical clustering (major lineage identification followed by subclustering; resolution matched to known signatures from Monaco et al. and Azimuth) to define 55 PBMC subpopulations — uses ABF300 scRNA-seq dataset.
- Kruskal-Wallis test across 5 age groups with post hoc Dunn's test (Bonferroni-adjusted) for subpopulation frequency comparisons (primarily A vs. E) — uses ABF300 scRNA-seq dataset (age-group-labeled cluster frequencies).
- Linear regression of subpopulation frequency against continuous donor age, as confirmatory analysis — uses ABF300 scRNA-seq dataset.
- Differential gene expression analysis (limma, t-statistic ranking) between age groups within each cluster, followed by Hallmark/MSigDB gene set enrichment analysis (GSEA via fgsea) — uses ABF300 scRNA-seq dataset.
- Cell-cell communication analysis (CellChat) comparing youngest vs. oldest age groups — uses ABF300 scRNA-seq dataset.
- Spectral flow cytometry gating and statistical comparison (two-sided Wilcoxon rank-sum test) between young and old subgroups — uses spectral cytometry validation cohort.
- Principal component analysis (PCA) on the top 10 age-associated subpopulation features, with locally estimated scatterplot smoothing (LOESS) of PC1 against age — uses ABF300 scRNA-seq dataset.
- Cross-cohort validation: gene signature/cluster transfer and PCA reproduction in independent public scRNA-seq datasets — uses Azimuth PBMC reference, Liu et al. psoriasis dataset, and Hashimoto et al. supercentenarian dataset.
