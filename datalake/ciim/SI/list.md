# SI — Senior Individuals Aging Cohort — File List

Physically stored under `/vol/projects/CIIM/cohorts/SI/` — not mirrored into `datalake/`.

**Base path:** `/vol/projects/CIIM/cohorts/SI/`

279 donors with full phenotype data (651 sample entries across visits); N=531 used in QTL mapping (genotype + cytokine overlap).
- **Age:** 22–85 y (mean 63.8 y) — ⚠️ skewed toward seniors despite the wide range; check the actual age histogram before using for a young-vs-old contrast, name-as-"SI" notwithstanding
- **Sex:** 187 Male / 92 Female
- **Ethnicity:** predominantly Caucasian (273/279; ~98%)

| Modality | Status | Notes |
|---|---|---|
| **ATACseq** | raw | `ATACseq_raw/` |
| **RNAseq** | raw + processed | 205 donors; baseline (99 samples) + 21 stimulation conditions at 24h (LPS n=271, NS n=202, Pam3Cys n=182, CpG n=154, polyIC n=154; plus smaller sets: influenza/varilrix/shingrix/ns-antigen n=10 each) and 7d (NS n=138, VZV-oka n=141, CMV/HSV/HSV-peptide/influenza/VZV/VZV-peptide/CoV-N/CoV-C/CoV-ctrl n=35–39); ~13,107 genes after filtering; CPM-normalized per stimulation at `RNAseq_processed/counts/2-norm/filter/{timepoint}_{stim}_cpm.tsv` (e.g. `24h_lps_cpm.tsv`); raw tximport RDS at `RNAseq_processed/counts/` (baseline/24h/7d) — do not use the batch-corrected version. |
| **Cytokines** | raw + processed | ~47 cytokines × 15 stimulations (LPS, polyIC, pam3cys, CpG, RPMI, varilrix, flu, HSV, VZV, CMV, CoV-N/C/ctrl) at 24h and 7d → ~500+ phenotypes; log2 + z-score at `cytokines_processed/` |
| **Flow cytometry** | raw | `flowcytometry_raw/` |
| **Genotype** | raw + imputed | imputed VCFs at `genotype_processed/imputed_vcf/` |
| **Metabolomics** | raw | `metabolomics_raw/` |
| **Methylation** | raw + processed | `methylation_processed/` |
| **Microbiome** | raw | `microbiome_raw/` |
| **Phenotype** | processed | comorbidity data, review paper; donor age at `phenotype_processed/SI_Review_paper/Code_For_processing/individual_info.tsv` |

QTL results (5 layers: cQTL, eQTL, eQTL-24h, meQTL, metabQTL) at `/vol/projects/CIIM/meta_cQTL/out/SI-senior/`; each layer has per-chr full stats, genome-wide, study-wide, and nominal outputs.
