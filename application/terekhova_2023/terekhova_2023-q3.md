# Single-cell atlas of healthy human blood unveils age-related loss of NKG2C+GZMB–CD8+ memory T cells and accumulation of type 2 memory T cells (Terekhova et al., 2023) — Question 3

## Question
What defines the novel NKG2C+(KLRC2+)GZMB– CD8+ memory T cell subpopulation transcriptionally and functionally, is it a reproducible biological entity rather than a clustering artifact, and why does it uniquely decrease with age in contrast to other CD8+ memory subsets that accumulate or remain stable?

## Label
L1 — Fixed goal, open path. The goal is fixed (characterize a specific candidate subpopulation and determine whether it is real and age-declining), and falsifiable checkpoints are explicit: cross-dataset signature matching to independent public references (must show significant, specific enrichment) and cytometric validation of the population's identity and age trend. The path to those checkpoints (which markers/trajectory/repertoire features to use) was open.

## Findings
- Unbiased clustering of non-MAIT CD8+ T cells identified a small (~1% of CD8+ T cells), transcriptionally distinct memory cluster marked by KLRC2 (encoding NKG2C) expression and lacking GZMB.
- This KLRC2+GZMB– cluster expresses XCL1, the only CD8+ subpopulation to do so (a ligand important for antigen cross-presentation by dendritic cells).
- This cluster co-expresses transcription factors associated with both central memory (LEF1, TCF7) and effector memory/NKT-like cells (ZNF683/Hobit, IKZF2/Helios), giving it a hybrid transcriptional identity not previously described in the literature.
- It is distinguishable from NKT-like and Temra CD8+ clusters (which also express NKG2C-related/effector markers) by the absence of GZMB and KLRF1 (NKp80) expression.
- Pseudotime trajectory analysis placed this subpopulation as a distinct terminal branch of CD8+ memory maturation, separate from the NKT-like and Temra branches.
- Cross-dataset signature matching showed this cluster strongly and specifically matched cluster 10 from Galletti et al. (a study specifically profiling memory CD8+ T cells), with statistically significant gene set enrichment.
- Cross-dataset signature matching also showed strong, specific matching to cluster CD8+ TEM_6 from the Azimuth human PBMC reference, with statistically significant gene set enrichment — together with the Galletti et al. match, confirming this is a robust, reproducible population rather than a technical artifact.
- Unlike most other CD8+ memory subsets (which accumulate or remain stable with age), this KLRC2+GZMB– population progressively and significantly decreased with age in the scRNA-seq data.
- Cytometry-based validation, gating on NKG2C+GZMB–NKp80– CD8+ T cells, confirmed this as a distinct subpopulation whose proportion differed significantly between young (28–35y) and old (68+y) donors, corroborating the age-associated decline.
- The subpopulation exhibited a highly diverse (non-clonally-restricted) TCR repertoire, distinguishing its clonal behavior from the highly clonal NKT-like and Temra subsets.

## Methodology

### Datasets
- ABF300 cohort scRNA-seq/scTCR-seq dataset: 313,343 non-MAIT CD8+ T cells subclustered into 12 subpopulations including the KLRC2+GZMB– Tmem cluster, from 317 samples/166 donors across 5 age groups (A–E).
- Public reference datasets for cross-validation: Galletti et al. 2020 memory CD8+ T cell scRNA-seq dataset (cluster 10 signature); Azimuth human PBMC reference (Hao et al. 2021; GEO GSE164378/Zenodo 4546839, CD8+ TEM_6 cluster).
- Spectral cytometry validation cohort (30-color panel, 26 donors; young 28–35y vs. old 68+y subgroups) gated for NKG2C+GZMB–NKp80– CD8+ T cells.

### Analytics
- Unsupervised subclustering and marker/transcription-factor-based annotation (KLRC2, GZMB, XCL1, LEF1, TCF7, ZNF683, IKZF2, KLRF1) to define and characterize the KLRC2+GZMB– cluster — uses ABF300 scRNA-seq dataset.
- Pseudotime trajectory analysis (Monocle3) of CD8+ memory maturation branches — uses ABF300 scRNA-seq dataset.
- Cross-dataset gene set enrichment analysis (GSEA) comparing cluster-defining marker genes between the KLRC2+ cluster and corresponding clusters in Galletti et al. and Azimuth reference datasets — uses ABF300 scRNA-seq dataset, Galletti et al. dataset, and Azimuth PBMC reference.
- Kruskal-Wallis/Dunn's post hoc test (Bonferroni-adjusted) and linear regression of cluster frequency against age (A vs. E comparison) — uses ABF300 scRNA-seq dataset.
- TCR repertoire diversity assessment (Gini coefficient via DescTools) for the KLRC2+ cluster compared with other CD8+ memory clusters — uses ABF300 scTCR-seq dataset.
- Flow/spectral cytometry gating strategy design and statistical comparison (Wilcoxon rank-sum test) of NKG2C+GZMB–NKp80– proportions between young and old donors — uses spectral cytometry validation cohort.
