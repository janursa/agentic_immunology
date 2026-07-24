# Regulatory network remodeling defines human immune aging and reveals modifiable immune states (Nourisa et al., 2026)

## Question 4
Can age-associated immune regulatory states be shifted (accelerated or reversed) by defined extracellular signals or pharmacological perturbations, and can such candidate rejuvenating interventions be nominated and experimentally validated?

**Findings:**
- Applying the aging clocks to a systematic cytokine perturbation screen (90 cytokines) stratifies cytokines into age-accelerating vs. age-rejuvenating classes: age-accelerating cytokines are predominantly pro-inflammatory (IL-2, IL-4, IL-7, IL-15); age-rejuvenating cytokines are enriched for anti-inflammatory/immunoregulatory factors (IL-10, IL-22, IL-6, OSM).
- Type I interferons (IFN-β, IFN-ω) show cell type-specific, divergent effects: age-accelerating in CD4+ T cells but age-reducing in CD8+ T cells.
- IL-10 produces the strongest age-reducing effect among all cytokines tested: −4.9 years in CD4+ T cells and −2.0 years in CD8+ T cells (FDR<0.0001).
- IL-10 induces widespread TF activity remodeling, suppressing IL-2/STAT5 and interferon-α/γ pathways — directionally opposite to the changes seen in physiological aging and SLE (Questions 1 and 3).
- IL-10 reverses the activity of ~300 of ~370 age-associated TFs in CD8+ T cells, notably restoring naive/memory regulators LEF1 and TCF7.
- Applying the clocks to a drug perturbation screen (146 small molecules) reveals both age-accelerating compounds (e.g., CGM-097, an MDM2 inhibitor/p53 activator, consistent with p53's role in senescence) and age-reducing compounds.
- Ruxolitinib (a clinically approved JAK1/2 inhibitor) is prioritized as a top age-reversing hit: ~9-year predicted-age reduction in CD4+ T cells (FDR=0.023).
- Ruxolitinib broadly counteracts age-associated TF programs and suppresses TNF-α/NF-κB, IL-2/STAT5, and interferon-α/γ pathways in CD4+ T cells, showing high concordance with IL-10-induced TF changes, including shared shifts in core JAK-STAT regulators (STAT1, STAT2, STAT3, IRF1, IRF2, IRF7, IRF9, NFKB2).
- In newly generated ex vivo experiments (PBMCs from 7 healthy donors, ±LPS, ±ruxolitinib, 18h): LPS alone induces ~8 years of predicted age acceleration (P=1×10⁻¹⁶), consistent with prior findings that acute infection/inflammation accelerates immune age.
- Ruxolitinib reduces predicted age under baseline conditions (~2 years, P=0.048) and shows a directionally consistent, though not statistically significant, attenuation of LPS-induced age acceleration (~2.5 years, P=0.12).
- Transcriptionally, LPS induces aging-like TF signatures (e.g., increased STAT1, BATF activity), which ruxolitinib consistently opposes, particularly among the most central age-associated TFs.

**Methodology:**

### Datasets
- Cytokine perturbation dataset: ParseBioscience 10M PBMC dataset — PBMCs from 12 donors (6M/6F) exposed to 90 cytokines for 24h vs. PBS control; donor age obtained via direct communication with original authors (public dataset lacked age metadata).
- Drug perturbation dataset (OPSCA): from the 2023 Open Problems Single-Cell Perturbation NeurIPS competition — 144 (paper reports up to 146) compounds plus positive controls (Dabrafenib, Belinostat) and negative control (DMSO), tested across 3 donors on 96-well plates (6 plates total), Cell Ranger-processed by the competition organizers.
- Ex vivo validation dataset (newly generated): PBMCs from 7 healthy donors, cultured with 1 μM ruxolitinib ± 10 ng/mL LPS or RPMI control for 18h, scRNA-seq on Chromium X (10x Genomics GEM-X 3′ v4), sequenced on Illumina NovaSeq 6000; processed through the same QC/pseudobulk/normalization pipeline as other cohorts.

### Analytics
- **Biological age estimation under perturbation**: GRN-informed cell type-specific aging clocks (from Question 2) applied to pseudobulk expression of treated vs. untreated/control samples in each dataset.
- **Age-modifying effect testing**: mixed-effects models (perturbation as fixed effect, donor as random effect) comparing predicted age between treated and control samples per cytokine/compound; multiple-testing correction (FDR<0.05) applied per cell type; rejuvenation = significant decrease, acceleration = significant increase in predicted age.
- **Differential TF activity analysis**: same mixed-effects modeling framework applied to TF activity scores per perturbation and cell type, FDR-corrected.
- **Gene set enrichment analysis** (GSEApy, MSigDB Hallmark 2020) on perturbation-responsive TFs (IL-10, ruxolitinib), compared against Hallmark enrichment patterns from physiological aging (Question 1) and SLE (Question 3).
- **Cross-perturbation concordance analysis**: comparison of IL-10- vs. ruxolitinib-induced TF activity profiles to assess convergence on shared regulatory nodes.
- **Ex vivo statistical comparison**: predicted-age and TF-activity comparisons across RPMI/LPS/ruxolitinib conditions in the 7-donor ex vivo cohort (paired condition comparisons with reported P-values).
