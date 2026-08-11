# Single-cell atlas of healthy human blood unveils age-related loss of NKG2C+GZMB–CD8+ memory T cells and accumulation of type 2 memory T cells (Terekhova et al., 2023) — Question 2

## Question
Does healthy aging drive a coordinated functional shift toward type 2 (IL-4-associated) immunity across both the CD4+ and CD8+ memory T cell compartments, and does this transcriptional bias translate into an altered functional (cytokine-producing) capacity?

## Label
L1 — Fixed goal, open path. The goal is fixed (test whether a coordinated type-2/IL-4 skewing exists across CD4+ and CD8+ memory compartments and whether it is functionally consequential), but the path to it was open (subset discovery, cross-compartment correlation, orthogonal cytometry validation, and an independent ex vivo stimulation assay). Falsifiable checkpoints exist at each stage (significant cross-compartment correlation, cytometric confirmation of the two subsets, and a measurable stimulated cytokine difference between young and old).

## Findings
- Th2 memory CD4+ T cells (CCR4+CCR6–, GATA3+) significantly accumulated with age.
- Th2 memory CD4+ T cells showed the largest magnitude increase among all CD4+ memory subpopulations validated by cytometry.
- A CCR4+ CD8+ central memory (Tcm) subpopulation was identified that selectively expressed IL4 and IL2 transcripts.
- This CCR4+ CD8+ Tcm subpopulation was enriched for IL4/IL13 signaling pathways and a Th2 transcriptional signature (IL4R, GATA3, CCR4, ANXA1, XBP1), distinguishing it from the CCR4– Tcm subset.
- Both CCR4+ and CCR4– CD8+ Tcm subsets accumulated with age, but CCR4+ Tcm expanded faster.
- The CCR4+/CCR4– Tcm ratio was a robust correlate of age, analogous to the CD4+/CD8+ ratio; this was independently confirmed by spectral cytometry.
- The percentage of CD8+ Tcm CCR4+ cells correlated strongly and positively with the percentage of CD4+ Th2 memory cells across the cohort, indicating coordinated, cross-compartment functional skewing of memory T cells with age.
- A further notable cross-compartment correlation was found between CD8+ GZMK+ Tem and CD4+ Th1/Th17 frequencies.
- A further notable cross-compartment correlation was found between CD8+ GZMB+ Tem and CD4+ Temra frequencies.
- Baseline plasma levels of IL-4, IL-5, IL-13, and IgE did not differ across age groups, consistent with a healthy (non-inflamed) cohort.
- Upon ex vivo aCD3/aCD28 stimulation, sorted CD8+ T cells from older donors produced significantly more IL-4 than cells from younger donors.
- Upon ex vivo aCD3/aCD28 stimulation, sorted CD8+ T cells from older donors also produced more IL-9, IL-5, and IL-13 (to a lesser extent than IL-4) than cells from younger donors, indicating an age-associated functional predisposition toward type 2 cytokine production that is inducible rather than present at steady state.
- This ex vivo cytokine production bias was specific to CD8+ T cells and not observed in CD4+ T cells in the same experiment.

## Methodology

### Datasets
- ABF300 cohort scRNA-seq/FB dataset: CD4+ T cell subclusters (901,152 cells; Th2 memory cluster 7) and CD8+ T cell subclusters (313,343 non-MAIT cells; CCR4+/CCR4– Tcm clusters), from 317 samples/166 donors across 5 age groups (A–E).
- Spectral cytometry validation cohort (30-color panel, 26 donors: 13 young, 13 old; Table S4/S8) — used to validate Th2 CD4+ Tmem and CCR4+ CD8+ Tcm accumulation.
- Plasma samples from the ABF300 cohort (first-visit) submitted for multiplex cytokine (IL-4/IL-5/IL-13) and IgE profiling.
- Ex vivo functional stimulation cohort: CD8+ T cells sorted from young and elderly individuals, stimulated with aCD3+aCD28 beads (paired unstimulated controls).

### Analytics
- Chemokine-receptor-based subclustering and marker gene/transcription factor annotation (CCR4, IL4, IL2, GATA3, IL4R, ANXA1, XBP1) to define Th2 CD4+ Tmem and CCR4+ CD8+ Tcm clusters — uses ABF300 scRNA-seq dataset.
- Kruskal-Wallis/Dunn's post hoc test (Bonferroni-adjusted) and linear regression against age for cluster frequency and CCR4+/CCR4– Tcm ratio — uses ABF300 scRNA-seq dataset.
- GSEA (fgsea, MSigDB/Hallmark) for IL4/IL13 pathway and Th2 gene signature enrichment in CCR4+ Tcm cluster — uses ABF300 scRNA-seq dataset.
- Pearson correlation analysis of CD4+ and CD8+ subpopulation frequencies across donors (heatmap, hierarchical clustering; scatterplot with linear regression) — uses ABF300 scRNA-seq dataset (donor-level cluster proportions).
- Wilcoxon rank-sum test comparing young vs. old cytometry subgroups for CCR4+ Tcm and Th2 CD4+ Tmem proportions — uses spectral cytometry validation cohort.
- Multiplex bead-based immunoassay quantification of baseline plasma IL-4/IL-5/IL-13/IgE across age groups — uses ABF300 cohort plasma samples.
- Ex vivo stimulation assay with intracellular/secreted cytokine measurement (IL-4, IL-5, IL-9, IL-13) comparing unstimulated vs. stimulated, young vs. old, CD8+ (and CD4+) T cells — uses ex vivo functional stimulation cohort.
