# Single-cell atlas of healthy human blood unveils age-related loss of NKG2C+GZMB–CD8+ memory T cells and accumulation of type 2 memory T cells (Terekhova et al., 2023) — Question 1

## Question
Using ABF300 cohort, investigate how immune cell subpopulations remodel compositionally and transcriptionally with healthy aging? ()

## Label
L1 — Fixed goal, open path. The goal is fixed (characterize age-associated compositional and transcriptional change across PBMC subpopulations in a named cohort) while the path is open (clustering resolution, statistical model, validation strategy). A falsifiable checkpoint is constructible before execution: subpopulation frequencies and cluster-wise expression tested against age, significant after multiple-testing correction and reproduced by an orthogonal assay. No weighted rubric is needed — every validated age association is part of the answer, so candidate answers are never ranked against one another.

## Findings

### Compositional
- Profiling of ~2 million PBMCs from 317 samples (166 donors) resolved 55 biologically distinct immune subpopulations.
- 12 of these 55 subpopulations showed statistically significant age-associated frequency changes.
- Overall CD4+ T cell proportion did not change with age.
- Conventional (non-MAIT) CD8+ T cells decreased with age, producing the well-known age-associated rise in the CD4+/CD8+ T cell ratio.
- MAIT cells declined after ~55 years.
- Th2 memory CD4+ cells significantly accumulated with age.
- A novel HLA-DR+ CD4+ Tmem population significantly accumulated with age.
- Naive Treg cells decreased with age while memory Treg cells increased, with total Treg proportion stable.
- Naive CD4+ T cells showed only a slight, non-significant decrease with age.
- GZMK+ CD8+ effector memory cells strongly and gradually accumulated with age (~9% to ~20% of CD8+ cells).
- Naive CD8+ T cells declined with age.
- CCR4+ and CCR4– CD8+ central memory (Tcm) subsets both accumulated with age, with CCR4+ Tcm expanding faster.
- CD8+ Temra, Tem-GZMB, and tissue-resident memory (Trm) subsets showed no significant age dependence.
- NK cells showed no significant age-associated compositional change overall, though a trend of CD56bright loss and accumulation of higher-CD57 CD56dim subsets was noted.
- gd T cells showed age-related compositional restructuring restricted to naive and Vd1 GZMB+ subsets.
- B cells (9 clusters) showed limited compositional change with age; the most prominent age effect in B cells was BCR repertoire (clonal) restructuring rather than subpopulation frequency shifts.
- Myeloid subpopulations (classical/non-classical monocytes, pDCs, cDCs) remained proportionally static with age.

### Transcriptional
- Naive CD4+ T cells are the principal site of age-associated transcriptional remodeling: despite a stable proportion they showed strong differential expression between young and old donors — composition and transcription decouple in this subpopulation.
- Hallmark enrichment in aged naive CD4+ T cells highlighted two axes: active cytokine signaling and metabolic modification.
- IL2-STAT5 signaling, including its members IL2RA and IL2RB, was among the most strongly elevated pathways in aged naive CD4+ T cells.
- The IL2-STAT5/IL2RA transcriptional signal was confirmed at protein level: naive CD4+ T cells from old donors showed a greater increase in surface CD25 than those from young donors, interpreted as enhanced homeostatic proliferation relying on minute quantities of circulating IL2.
- Explicit negative control for the above: classical T cell activation signatures showed no positive enrichment in aged naive CD4+ T cells, ruling out activation as the explanation for elevated CD25.
- TCA cycle pathways were enriched in elderly donors across Th2, HLA-DR+ memory, Tfh, Th1/Th17 and naive Treg cells, read as mitochondrial dysfunction generating reactive oxygen species and contributing to inflammaging.
- Rho GTPase cycle pathways were enriched in young donors across those same CD4+ memory subsets.
- In the CD8+ compartment, a small naive CD8+ T cell cluster was enriched in interferon signatures.
- That same naive CD8+ T cell cluster was also enriched for TCA cycle pathways.
- Negative result: myeloid subpopulations showed no age-associated transcriptional change.
- Negative result: gd T cells showed no transcriptional age dependence despite their compositional restructuring.
- Cell-cell communication analysis detected age-related differences in SEMA4D (myeloid–T cell) signaling.
- Cell-cell communication analysis detected age-related differences in FLT3 (progenitor–T cell) signaling.

### Validation
- Spectral cytometry (30-color panel, 26 donors: 13 young/13 old) independently confirmed naive CD4+ T cell proportional stability.
- Spectral cytometry independently confirmed HLA-DR+ CD4+ Tmem accumulation with age.
- Spectral cytometry independently confirmed Th2 CD4+ Tmem accumulation with age.
- A composite PCA built from the top 10 age-associated features showed strong concordance with donor age.
- Similar age-related shifts (e.g., GZMK+ Tem, HLA-DR+ CD4+, Th2 accumulation) were reproduced in independent public scRNA-seq cohorts (healthy/psoriasis, supercentenarian datasets).

## Methodology

### Datasets
- ABF300 cohort: 317 PBMC samples from 166 healthy, Caucasian, non-obese (BMI<30) adults aged 25–85 (WashU IRB-201804084), collected 2018–2021, cross-sectional plus short-term longitudinal (annual) sampling; excluded donors with cancer, chronic inflammatory disease, blood-borne infection, smoking, or recent illness.
- scRNA-seq/scTCR-seq/scBCR-seq with 20-antibody feature barcoding (FB), generated in 14 sequencing batches; ~2 million cells after QC, ~6,000 cells/sample, ~1,300 genes/cell.
- Donors split into 5 age groups (10-year bins): A (25–34), B (35–44), C (45–54), D (55–64), E (65+); n=96/53/41/54/73 in scRNA-seq cohorts, n=47/30/22/30/37 in blood-panel cohort.
- Clinical blood panel data (hs-CRP, LDH, creatine kinase, cholesterol/triglycerides, cortisol, insulin, glucose, liver/kidney markers, DHEA-S, TSH, RBC/hemoglobin) for all donors.
- 30-color spectral cytometry validation cohort: 26 individuals (13 young, 13 old; Table S8), custom 30-marker panel (Table S4).
- Public reference datasets: Azimuth human PBMC reference (Hao et al. 2021; GEO GSE164378/Zenodo 4546839); Liu et al. 2022 healthy-vs-psoriasis scRNA-seq dataset; Hashimoto et al. 2019 supercentenarian scRNA-seq dataset.

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
