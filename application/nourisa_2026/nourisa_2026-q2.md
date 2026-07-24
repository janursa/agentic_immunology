# Regulatory network remodeling defines human immune aging and reveals modifiable immune states (Nourisa et al., 2026)

## Question 2
Can age-associated regulatory network remodeling be quantified in an interpretable, cell type-specific way (an "aging clock") that generalizes across independent cohorts and outperforms conventional transcriptome-wide clocks?

**Findings:**
- Cell type-specific "GRN-informed" aging clocks were built using only predicted GRN target genes (~4,000–5,000 per cell type, ~2,000 shared across cell types) as model features, rather than the full transcriptome.
- Ridge regression outperformed Gradient Boosting, Elastic Net, and MLP models, and single-cell (non-pseudobulked) models were less robust and more computationally costly.
- Clocks predicted chronological age with high accuracy in test cohorts: Spearman correlation ≈ 0.8 in both CD4+ and CD8+ T cells; lower and more variable performance in NK cells, monocytes, and B cells, mirroring weaker/heterogeneous age signals in those lineages (also seen in a prior transcriptome-wide clock).
- The GRN-informed clocks outperformed a previously published genome-wide expression-based clock evaluated on the same datasets.
- Clocks are computationally efficient (seconds per sample) and released as an open-source Python package.
- Clock feature genes are enriched for immune pathways (interferon-α/γ response, TNF-α/NF-κB, apoptosis), consistent with the age-associated TF pathway enrichment found in Question 1.
- Top-weighted clock features include established senescence/immune-aging markers (CD70, CDKN2A/p16INK4a, KLRC1/NKG2A); positively weighted genes increase with age, negatively weighted genes decrease.
- Mapping clock gene weights back through the GRN identified the TFs with strongest regulatory contribution to each clock's predictions: JUN, KLF6, GATA3, MAF, SOX4 in CD8+ T cells; SOX4, IRF4, RORC, SCML4, SATB1 in CD4+ T cells — most previously implicated in immune aging/senescence.
- RORC illustrates the added value of the clock-based (multivariate/conditional) view over marginal TF–age correlation: its activity increases with age (Question 1 finding), yet it has a negative regulatory coefficient in the CD4+ clock, suggesting a context-dependent or compensatory role.

**Methodology:**

### Datasets
- Training: pseudobulk transcriptomes from ~1,200 healthy donors pooled from the OneK1K and ABF300 cohorts.
- Testing/generalization: three independent cohorts — AIDA, (healthy) Perez, and Zhang et al. immune-aging atlas (Synapse syn61609846; 33 donors aged 20–90, used only for clock testing) — together >800 donors across multiple ancestries.
- Same QC/pseudobulk pipeline as Question 1 datasets.

### Analytics
- **Feature selection**: consensus GRN target genes per cell type (from Question 1's GRN inference).
- **Model training/selection**: Ridge regression, Gradient Boosting, Elastic Net, and MLP compared via leave-one-dataset-out cross-validation; Ridge chosen for best cross-validated and held-out test performance.
- **Performance evaluation**: Spearman correlation between predicted and chronological age in each held-out test cohort; benchmarked against a previously published transcriptome-wide clock (Li et al., Nat. Aging 2025) trained/tested on the same data.
- **Pathway enrichment** of clock feature genes (GSEApy, MSigDB Hallmark 2020).
- **TF regulatory-contribution mapping**: matrix multiplication of the GRN TF–target weight matrix by the clock's learned gene regression coefficients to obtain a per-TF contribution score (Aₘ) to predicted age, enabling upstream-regulator interpretation of clock predictions.
