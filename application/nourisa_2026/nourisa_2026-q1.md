# Regulatory network remodeling defines human immune aging and reveals modifiable immune states (Nourisa et al., 2026)

## Question 1
What regulatory architecture (transcription-factor/gene-regulatory-network activity changes) organizes immune aging across human immune cell types and individuals, and is it shared or lineage-specific?

**Findings:**
- More than 600 transcription factors (TFs) show age-associated changes in inferred activity across immune lineages, involving both gains and losses of activity — i.e., bidirectional network remodeling rather than a uniform decline.
- The most extensive rewiring occurs in T cells: ~350 age-associated TFs in CD8+ T cells and ~120 in CD4+ T cells.
- In CD8+ T cells, naive/stem-like regulators lose activity with age (TCF7, LEF1, FOXO1, BACH2, BCL11B, MYB), while effector-differentiation regulators gain activity (TBX21, PRDM1, ZEB2, RUNX3, EOMES, BATF, IRF4, STAT4) — a coordinated shift from naive to effector programs.
- Age-associated TFs are enriched for inflammatory/effector pathways (TNF-α via NF-κB, IL-2/STAT5, interferon-γ response), while Wnt–β-catenin signaling activity declines with age, consistent with loss of naive T-cell maintenance.
- Age-associated TFs tend to occupy highly central (hub) positions within their cell type-specific GRNs, implying aging perturbs core regulatory circuitry.
- PRDM1, TBX21, and KLF6 increase with age across T and NK cells; LEF1, TCF7, and BACH2 decrease — patterns consistent with known effector vs. naive/regulatory TF roles.
- Overlap of age-associated TFs across CD4+ T and CD8+ T, and NK cells; 10 TFs are shared across all three, some with conserved trends (e.g., SATB1 declines everywhere) and others with lineage-divergent direction (e.g., GATA3 increases in T cells but decreases in NK cells).

**Methodology:**

### Datasets
- Discovery cohorts (used to derive age-TF associations, meta-analyzed): OneK1K (CELLxGENE; 981 healthy European individuals), ABF300 (Synapse syn49637038; 166 healthy Caucasian individuals, 25–85 yrs), AIDA Freeze v1 (CELLxGENE; ~1.26M cells, 619 healthy donors, 5 Asian countries), and healthy samples from the Perez SLE cohort (CELLxGENE) — together ~1,900 donors.
- Validation cohort: SoundLife (96 donors, 25–35 and 55–65 yrs, longitudinal PBMC scRNA-seq, ~12M cells).
- Overall: >18 million single-cell PBMC transcriptomes from >2,000 donors aged 20–90, spanning 5 cohorts and multiple ancestries, processed through a harmonized QC/pseudobulk pipeline (CellTypist coarse annotation into CD4+ T, CD8+ T, NK, B, monocyte; pseudobulk aggregation per cell type/donor; shifted-log normalization).

### Analytics
- **GRN inference** (per cell type, per discovery cohort): pairwise Spearman correlation between genes restricted to a curated TF list, FDR<0.05, top 100,000 TF–gene edges retained
- **Consensus GRN construction**: TF–gene edges retained only if present in ≥2 cohorts with consistent regulatory-weight direction (60,000–90,000 edges per cell type).
- **TF activity inference**: dot product of consensus GRN adjacency matrix with pseudobulk expression, using decoupleR's univariate linear model.
- **TF–age association**: Spearman correlation of TF activity vs. chronological age per cohort/cell type; meta-analysis across discovery cohorts via Fisher's method; significance = concordant direction across cohorts, meta-FDR<0.05, |Spearman ρ|>0.1 across cohorts.
- **Validation**: same correlation/FDR/ρ thresholds applied independently in the SoundLife cohort.
- **Network centrality analysis** of age-associated TFs within consensus 
- **Gene set enrichment analysis** (GSEApy, MSigDB Hallmark 2020) on age-increasing vs. age-decreasing TF target sets, per cell type.
