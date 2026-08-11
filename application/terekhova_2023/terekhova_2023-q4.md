# Single-cell atlas of healthy human blood unveils age-related loss of NKG2C+GZMB–CD8+ memory T cells and accumulation of type 2 memory T cells (Terekhova et al., 2023) — Question 4

## Question
Beyond previously described broad, bulk repertoire changes, how do TCR and BCR clonality and clonotype-sharing patterns change with age within specific transcriptionally defined memory T and B cell subpopulations, and what do these patterns reveal about the relationships between subpopulations?

## Label
L2 — Open goal in a bounded frame. The bounded frame is antigen-receptor (TCR/BCR) repertoire behavior within the already-defined subpopulations of the ABF300 atlas; the goal is open (survey clonality and clonotype-sharing across all subpopulations to discover which change with age and how they relate to each other) rather than a single fixed prediction, evaluated against multiple criteria (per-cluster clonality trend, pairwise sharing pattern, public-clone frequency, cross-checked against pseudotime-derived lineage relationships).

## Findings
- Among CD4+ T cells, cytotoxic subsets (Temra and TTE) were the most clonal overall and showed a tendency for clonality to increase with age, reaching significance in Temra.
- The CD4+ Th1/Th17 memory subset showed the most statistically significant age-associated clonality increase despite a lower absolute Gini coefficient than the cytotoxic subsets.
- CD4+ Temra, TTE, and Th1/Th17 clusters shared TCR clones with each other, suggesting a developmental relationship.
- Among CD8+ T cells, GZMK+ Tem and CCR4– Tcm populations showed strong, significant increases in TCR clonality with age.
- The CD8+ CCR4+ Tcm population's clonality did not change with age despite comparable overall clonality to CCR4– Tcm — reinforcing the distinct identity/lineage of the CCR4+ Tcm subset.
- CD8+ effector memory subsets (Tem-GZMB, Tem-GZMK, NKT-like, HLA-DR+, and proliferating cells) exhibited extensive TCR clonotype sharing with each other (70–90% of shared clones), and to a lesser extent with CCR4– Tcm cells; this sharing pattern was consistent across all age groups.
- In contrast, CD8+ CCR4+ Tcm cells lacked clonotype sharing with other memory populations, again pointing to their functional/developmental uniqueness (consistent with pseudotime placing CCR4+ Tcm on a separate branch).
- No public (donor-shared) TCR clonotypes were detected to change in frequency with age.
- In B cells, age-associated changes were most evident in BCR repertoire restructuring rather than subpopulation frequency shifts, particularly within the CD5+ B cell subset.
- Within the CD5+ B cell subset, clonality increased with age, and distinct patient-specific clones became dominant in individual old donors.
- The CD5+ B cell subset shared BCR clones with naive, non-switched, activated, and plasma cell B cell clusters.
- Two public BCR clonotype clusters were identified with strong homology to known antibodies: one to the SARS-CoV-2 spike protein (84% overlap) and one to the dengue virus envelope glycoprotein (89% overlap).

## Methodology

### Datasets
- ABF300 cohort scTCR-seq dataset: paired CD4+ and CD8+ T cell clusters with TCR alpha/beta chain sequences, from 317 samples/166 donors across 5 age groups (A–E).
- ABF300 cohort scBCR-seq dataset: 71,614 B cells across 9 transcriptional clusters with paired heavy/light chain BCR sequences, from the same cohort.
- Public antibody/clonotype reference database (SAbDab, structural antibody database) used to identify homology of expanded BCR clonotype clusters to known SARS-CoV-2 and dengue virus antibodies.

### Analytics
- Clonotype definition (identical V/J gene usage and CDR3) and Gini coefficient calculation (DescTools) per sample/cluster to quantify TCR and BCR clonality — uses ABF300 scTCR-seq and scBCR-seq datasets.
- Kruskal-Wallis/Dunn's post hoc test (Bonferroni-adjusted) and pairwise Wilcoxon rank-sum test (A vs. E groups) on clonality (Gini coefficient) across age groups — uses ABF300 scTCR-seq and scBCR-seq datasets.
- Clonotype-sharing analysis across CD4+ and CD8+ memory clusters (pairwise percentage of shared clonotypes) and across age groups — uses ABF300 scTCR-seq dataset.
- Immcantation framework (Change-O, SHazaM) for BCR lineage/clone assignment and repertoire analysis, including identification of patient-specific dominant clones in CD5+ B cells and public clonotype clusters — uses ABF300 scBCR-seq dataset.
- Sequence homology comparison of expanded/public BCR clonotypes against known antibody sequences — uses ABF300 scBCR-seq dataset and public antibody structural database.
- Pseudotime trajectory analysis (Monocle3) used to corroborate clonal-sharing-based relationships between CD8+ memory subpopulations (e.g., separate branch for CCR4+ Tcm) — uses ABF300 scRNA-seq/scTCR-seq datasets.
