# Regulatory network remodeling defines human immune aging and reveals modifiable immune states (Nourisa et al., 2026)

## Question 3
Does the GRN-informed immune-aging framework capture clinically relevant deviations from physiological aging — specifically, does autoimmune activation in systemic lupus erythematosus (SLE) engage the same regulatory programs as physiological aging, and is this effect age-dependent?

**Findings:**
- Both CD4+ and CD8+ T cells from SLE patients show significantly elevated predicted biological age (via the GRN-informed clocks) compared with age-matched healthy controls.
- The effect is most pronounced in younger patients: in CD8+ T cells of individuals <50 years, predicted age increases by ~+6 years (FDR = 1×10⁻¹¹); no significant increase is seen in older individuals — paralleling clinical patterns where hyperactivation dominates early SLE and exhaustion/comorbidity dominate later disease.
- SLE induces widespread TF activity shifts across immune lineages, with the highest concordance between CD4+ and CD8+ T cells.
- Pathway-level changes in SLE mirror physiological aging: upregulation of IL-2/STAT5, interferon-α/γ, and TNF-α/NF-κB signaling, and downregulation of Wnt–β-catenin signaling.
- Nearly all age-associated TFs shift in the same direction in SLE as they do with physiological aging, in both CD4+ and CD8+ T cells — except in older (>50y) SLE CD8+ T cells, where this concordance is not observed, consistent with the aging-clock results.
- The 15 most central age-associated TFs reproduce the same directional shifts in SLE as in normal aging, across cell types and age groups (again excluding the older CD8+ T group).
- Example: LEF1 (naive T-cell maintenance regulator) is prematurely downregulated in young SLE patients, such that ~30-year-old SLE patients resemble ~50-year-old healthy controls at the LEF1 activity level.
- Overall, autoimmune activation in SLE appears to pathologically re-engage the regulatory programs of physiological immune aging, most strongly in younger adults and within CD8+ T cells.

**Methodology:**

### Datasets
- Perez SLE cohort (CELLxGENE): 261 individuals total (162 SLE cases, 99 healthy controls), balanced group sizes, predominantly female donors, ages 20–80 (same cohort whose healthy subset served as a discovery cohort in Question 1).

### Analytics
- **Biological age estimation**: the pre-trained GRN-informed cell type-specific aging clocks (from Question 2) applied to CD4+ and CD8+ T cell pseudobulk profiles of SLE vs. healthy donors.
- **Age-acceleration testing**: Wilcoxon rank-sum test on predicted age (SLE vs. healthy) with FDR correction; acceleration defined as significant (FDR<0.05) increase in predicted age; analysis run for all ages combined and separately for young/old subgroups using two age thresholds (40 and 50 years) for robustness.
- **Differential TF activity analysis**: Mann–Whitney U test comparing TF activity between SLE and healthy samples per cell type, with multiple-testing correction within each cell type.
- **Gene set enrichment analysis** (GSEApy, MSigDB Hallmark 2020) on SLE-associated TFs, separated by direction and cell type.
- **Cross-referencing** of SLE-associated TF signatures (direction of change, and centrality-ranked top TFs) against the physiological age-associated TF signatures from Question 1, stratified by patient age group.
