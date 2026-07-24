# TFA Analysis — rs11867200 / CCL2 locus (SI cohort)

**Question:** Infer a GRN from REF-allele (C, dosage ≤ 0.5) elderly (age > 60) SI cohort donors using both LPS and NS 24h RNA-seq pooled. Then calculate per-sample TF activity (decoupler ULM) for ALL genotyped samples (REF + Carrier allele, both conditions, all ages) using that GRN.

---

## Data Sources

- **Genotype**: `/vol/projects/CIIM/cohorts/SI/genotype_processed/dosage/chr17.txt`
  SNP: `chr17:34248950:C:T;rs11867200`
- **Covariates (age)**: `/vol/projects/CIIM/meta_cQTL/data/SI/covariates.tsv`
- **RNA-seq NS**: `/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_ns_cpm.tsv`
- **RNA-seq LPS**: `/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_lps_cpm.tsv`

---

## Methods

### GRN inference
- Samples: REF allele (dosage ≤ 0.5) + age > 60, LPS + NS pooled into one matrix
- Expression: log1p(CPM)
- Tool: `infer_grn_spearman` (bulk, BH FDR < 0.05, top 100k edges by |ρ|)
- Output: directed TF→gene edge list

### TF activity inference
- Samples: ALL genotyped samples (REF + Carrier, LPS + NS, all ages)
- Expression: log1p(CPM)
- GRN: from the inference step above
- Tool: `infer_tf_activity` (decoupler ULM, min_n=2)
- Output: per-sample ULM activity scores (samples × TFs)

---

## Steps

### Step 1 — 2026-05-28
- [x] Script written: `tfa_analysis/script.py`
- [x] LOG created
- [x] Ran via singularity ciim.sif

### Bug fixes during run
1. `PRIOR_DIR` undefined in `genomics.py` → fixed: added `from datalake import DATALAKE_DIR` and `PRIOR_DIR = os.path.join(DATALAKE_DIR, 'prior')` at module level.
2. Negative CPM values → `np.log1p` produced NaN → fixed: `np.clip(..., 0, None)` before log1p.

### Execution results

**GRN (Step 3)**
- Input: 228 samples (REF, age > 60, LPS + NS pooled) × 12,834 genes
- After Spearman + BH FDR < 0.05 + top 100k edges: 100,000 edges
- Unique TF sources: 528 | Target genes: 5,210

**TF activity (Step 5)**
- Decoupler ULM fit on 456 samples × 12,834 genes with the 528-TF network
- Output matrix: 456 samples × 467 TFs (TFs with ≥ 2 targets in data)

**Sample counts per group**
| Group | n |
|---|---|
| REF_LPS | 136 |
| Carrier_LPS | 126 |
| REF_NS | 104 |
| Carrier_NS | 90 |

**Candidate TFs (16) in GRN**: 13/16 recovered — CEBPB, FOS, FOSL2, GATA2, GATA3, JUND, MAX, MEF2A, NFIC, PBX3, SPI1, SPIB, ETV6. Missing from top 100k edges: JUN, MYC, TCF12.

---

## Output Files

| File | Description |
|---|---|
| `results/grn.csv` | Inferred GRN (100k edges: source TF, target gene, weight ρ) |
| `results/grn_adata.h5ad` | AnnData used for GRN inference (228 × 12834) |
| `results/tf_activity.tsv` | Per-sample ULM TF activity scores (456 × 467) |
| `results/sample_metadata.tsv` | Sample metadata (condition, allele, age, group) |
| `images/fig1_heatmap_candidate_tfs.png` | Group-mean heatmap — 13 candidate TFs |
| `images/fig2_heatmap_top50.png` | Group-mean heatmap — top 50 TFs by cross-group variance |
| `images/fig3_boxplots_candidate_tfs.png` | Boxplots per candidate TF × group |
| `images/fig4_pca_tf_activity.png` | PCA of TF activity space, coloured by group |
| `images/fig5_allele_delta_lps.png` | Δ median ULM (Carrier − REF) under LPS per candidate TF |
| `images/fig6_allele_dist_candidate_tfs.png` | Violin+strip plots REF vs Carrier per TF (LPS & NS), with significance brackets |
| `results/allele_tfa_stats.csv` | Mann-Whitney U + BH FDR stats for REF vs Carrier per TF × condition |

---

## Step 2 — Allele distribution analysis (2026-05-28)

**Script**: `script_allele_dist.py`

**Question**: For the 13 recovered candidate TFs, compare TF activity distributions between REF and Carrier allele (Mann-Whitney U, BH FDR correction across 26 tests: 13 TFs × 2 conditions).

**Result**: No TF reaches statistical significance after BH FDR correction.

Notable trends (raw p < 0.15, all ns after FDR):
| TF | Condition | raw p | FDR |
|---|---|---|---|
| SPIB | NS | 0.041 | 0.483 |
| MEF2A | LPS | 0.091 | 0.483 |
| ETV6 | NS | 0.094 | 0.483 |
| GATA2 | LPS | 0.105 | 0.483 |
| MEF2A | NS | 0.121 | 0.483 |

**Interpretation**: At the bulk PBMC transcriptome level, the rs11867200 T allele does not significantly alter the inferred activity of the 13 candidate TFs. This is consistent with the prior RNA co-expression analysis (SI_grn_analysis) which also found no allele-driven difference in TF–CCL2 co-expression. The cQTL effect may operate through subtle changes in TF binding affinity at the enhancer (as suggested by motif analysis) rather than wholesale shifts in TF activity measurable by ULM in bulk tissue.
