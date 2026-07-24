# SI GRN Analysis — rs11867200 allele × GRN comparison

**Question**: Do the 16 TFs (13 ChIP-seq + 3 motif-LOSS) change their regulatory relationship with CCL2 depending on rs11867200 allele in elderly (age>60) SI cohort donors?  
**Approach (v4)**: Infer one full GRN per allele group (GRN_REF, GRN_Carrier) using `infer_grn_spearman` (LPS + RPMI pooled, age>60), then compare TF–CCL2 edge weights with Fisher Z-tests (BH FDR).

---

## Change log

### v4 (current) — one GRN per allele, full GRN comparison
- Replaced per-group Spearman correlation approach with `infer_grn_spearman` to build genome-wide GRNs
- GRN_REF: REF allele (dosage ≤ 0.5), age > 60, LPS + RPMI pooled
- GRN_Carrier: Carrier (dosage > 0.5), age > 60, LPS + RPMI pooled
- New outputs: `grn_ref.csv`, `grn_carrier.csv`, `grn_global_comparison.csv`, `grn_ccl2_comparison.csv`
- New plots: `grn_ccl2_comparison.png`, `grn_ccl2_scatter.png`, `grn_delta_rho.png`
- `post.ipynb` rebuilt: global overlap bar, CCL2 barplot, scatter, Δρ barplot, Fisher table, heatmap

### v3 (previous) — jackknife SE, 4 per-group Spearman correlations
- Manual Spearman per group (REF_RPMI, Carrier_RPMI, REF_LPS, Carrier_LPS)
- Jackknife leave-one-out SE, Fisher Z LPS REF vs Carrier

---

## Data Sources

- **Genotype**: `/vol/projects/CIIM/cohorts/SI/genotype_processed/dosage/chr17.txt`  
  SNP: `chr17:34248950:C:T;rs11867200` (lead cQTL for pbmc_24h_mcp1_lps, p=4.43×10⁻⁹)
- **Covariates**: `/vol/projects/CIIM/meta_cQTL/data/SI/covariates.tsv` (659 samples, includes age)
- **RNA-seq NS**: `/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_ns_cpm.tsv` (202 samples)
- **RNA-seq LPS**: `/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_lps_cpm.tsv` (271 samples)

---

## TFs

- **13 ChIP-seq TFs** (bind near CCL2 locus): CEBPB, FOS, FOSL2, GATA2, GATA3, JUN, JUND, MAX, MEF2A, MYC, NFIC, PBX3, TCF12
- **3 Motif-LOSS TFs** (bind rs11867200 REF allele, disrupted by ALT): SPI1 (100%), SPIB (95%), ETV6 (64%)

---

## Methods

### Allele grouping
- **REF/REF**: continuous dosage ≤ 0.5
- **Carrier (HET + ALT/ALT)**: continuous dosage > 0.5
- HET and ALT pooled as "Carriers" to ensure adequate statistical power (strict ALT/ALT n=7–11)

### Age filter
- Age > 60 applied from covariates

### GRN method (v2 — bootstrap-robust)
- **Observed GRN**: Spearman rank correlation ρ(TF expression, CCL2 expression) on the full sample per group
- **Bootstrap GRNs**: 10 bootstrap GRNs per group (sample with replacement, n = group size, seed=42); per-TF SD reported as error bars
- RNA-seq CPM values used as TF activity proxy (no TF proteomics in SI cohort)
- **Bonferroni correction**: 16 TFs × 4 groups = 64 tests → α = 7.81×10⁻⁴ (applied to observed ρ)

### LPS allele significance test
- **Fisher Z-transformation test** per TF: compares ρ(REF_LPS) vs ρ(Carrier_LPS) using sample sizes n=130 and n=122
  - Z = (arctanh(ρ₁) − arctanh(ρ₂)) / √(1/(n₁−3) + 1/(n₂−3))
- **BH FDR correction** over 16 TFs

---

## Sample Sizes

| Group       | n   | Status |
|-------------|-----|--------|
| REF_RPMI    | 98  | ✓ OK   |
| Carrier_RPMI| 87  | ✓ OK   |
| REF_LPS     | 130 | ✓ OK   |
| Carrier_LPS | 122 | ✓ OK   |

All groups well-powered (n ≥ 87). No low-N warnings.

---

## Results

### Bonferroni-significant associations (p < 7.81×10⁻⁴)

| Group         | TF    | ρ      | p-value    | motif-LOSS? |
|---------------|-------|--------|------------|-------------|
| Carrier_RPMI  | JUN   | +0.710 | 1.41×10⁻¹⁴ | No |
| REF_RPMI      | JUN   | +0.613 | 1.90×10⁻¹¹ | No |
| Carrier_RPMI  | MYC   | +0.579 | 4.38×10⁻⁹  | No |
| Carrier_RPMI  | CEBPB | +0.529 | 1.39×10⁻⁷  | No |
| Carrier_LPS   | MEF2A | +0.432 | 6.73×10⁻⁷  | No |
| Carrier_RPMI  | MAX   | -0.487 | 1.70×10⁻⁶  | No |
| REF_RPMI      | MYC   | +0.456 | 2.33×10⁻⁶  | No |
| REF_RPMI      | CEBPB | +0.456 | 2.36×10⁻⁶  | No |
| REF_LPS       | MEF2A | +0.381 | 7.92×10⁻⁶  | No |
| REF_LPS       | **ETV6**  | +0.359 | 2.80×10⁻⁵  | **YES** |
| REF_RPMI      | PBX3  | -0.388 | 8.06×10⁻⁵  | No |
| Carrier_RPMI  | PBX3  | -0.400 | 1.23×10⁻⁴  | No |
| Carrier_LPS   | **ETV6**  | +0.317 | 3.70×10⁻⁴  | **YES** |

### Key observations

1. **JUN–CCL2** is the strongest association in both groups under RPMI, with the Carrier group showing an even stronger correlation (ρ=0.71 vs 0.61). JUN is a known AP-1 factor and major regulator of CCL2 transcription.

2. **ETV6** (motif-LOSS TF) is significantly correlated with CCL2 in both REF and Carrier groups under LPS, suggesting ETV6–CCL2 co-regulation is present regardless of allele — but ETV6's binding to the rs11867200 locus in REF carriers may additionally modulate local chromatin access.

3. **SPI1 and SPIB** (the other two motif-LOSS TFs) show no significant correlation with CCL2 expression in any group. This may indicate their effect on CCL2 is mediated through chromatin accessibility at the rs11867200 locus rather than co-expression at the RNA level.

4. **MAX** shows a uniquely *negative* correlation with CCL2 in Carrier_RPMI (ρ=−0.49), not seen in REF_RPMI, suggesting the ALT allele context may alter the direction of MAX's relationship with CCL2.

5. **CEBPB, MYC** associations are broadly consistent across REF and Carrier groups, indicating stable regulatory relationships.

---

## LPS REF vs Carrier — Fisher Z-test Results

No TF reaches FDR significance (all FDR > 0.84). Largest Δρ observed:

| TF    | ρ_REF_LPS | ρ_Carrier_LPS | Δρ     | p(Fisher) | FDR   |
|-------|-----------|---------------|--------|-----------|-------|
| PBX3  | −0.195    | −0.366        | −0.171 | 0.178     | 0.844 |
| TCF12 | +0.095    | −0.070        | −0.165 | 0.196     | 0.844 |
| JUND  | +0.152    | +0.311        | +0.159 | 0.204     | 0.844 |
| FOSL2 | +0.145    | +0.302        | +0.157 | 0.218     | 0.844 |
| ETV6  | +0.359    | +0.317        | −0.041 | 0.714     | 0.844 |

**Interpretation**: ETV6 (motif-LOSS) shows similar ρ in both LPS allele groups (Δρ=−0.04, p=0.71), indicating its CCL2 co-expression is allele-independent. No TF shows a statistically distinguishable allele-driven change in TF–CCL2 correlation under LPS, suggesting the cQTL effect on CCL2 protein levels operates through mechanisms not detectable at the RNA co-expression level in this n=130/122 cohort.

---

## Output Files

- **Results TSV**: `results/grn_results.tsv`
- **Bootstrap raw**: `results/grn_bootstrap_raw.tsv`
- **Bootstrap summary**: `results/grn_bootstrap_summary.tsv`
- **LPS comparison**: `results/lps_comparison_fisher.tsv`
- **Heatmap**: `images/heatmap_spearman.png`
- **Barplot RPMI** (with bootstrap SD): `images/barplot_RPMI.png`
- **Barplot LPS** (with bootstrap SD): `images/barplot_LPS.png`
- **LPS allele comparison (Δρ)**: `images/lps_allele_comparison.png`

---

## Environment

- Singularity: `ciim.sif`
- Script: `script.py`
