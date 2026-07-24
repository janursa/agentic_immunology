# GWAS -- File List

Full genome-wide summary statistics and LD reference panel for Mendelian Randomization, colocalization, and fine-mapping analyses.

Three items: `GCST003156_SLE_Bentham2015.h.tsv.gz` (SLE GWAS full summary stats), `1kg/` (1000 Genomes Phase 3 LD reference panel, all 5 superpopulations), and `ldsc_grch38/` (LDSC baseline LD score files, GRCh37 + GRCh38, for partitioned heritability / stratified LDSC).

---

## GCST003156_SLE_Bentham2015.h.tsv.gz
**SLE GWAS — full summary statistics**

**Reference**: Bentham et al. 2015, *Nat Genet* (doi:10.1038/ng.3434) | GWAS Catalog ID: GCST003156  
**Genome build**: GRCh38 (harmonised `hm_*` columns); original columns are GRCh37  
**Sample size**: 5,201 European ancestry cases + 9,066 European ancestry controls (n ≈ 14,267)  
**Variants**: ~7.9M total; ~6.7M with valid harmonisation (filter to `hm_code` ∈ {10, 11})  
**Compressed size**: 474 MB | Source: EBI GWAS Catalog harmonised FTP

Full genome-wide imputed summary statistics for systemic lupus erythematosus. The largest European ancestry SLE GWAS on the EBI GWAS Catalog with full summary statistics deposited. Used as the **outcome dataset** in cis-MR and the GWAS input for colocalization against DICE eQTLs.

**Columns**:

| Column | Description |
|--------|-------------|
| `hm_variant_id` | GRCh38 variant ID (`chr_pos_ref_alt`) |
| `hm_rsid` | rsID — use this for cross-dataset matching |
| `hm_chrom` / `hm_pos` | GRCh38 chromosome and position |
| `hm_effect_allele` / `hm_other_allele` | Strand-harmonised alleles |
| `hm_beta` | log(OR) on harmonised strand |
| `hm_odds_ratio` | Odds ratio |
| `hm_effect_allele_frequency` | Effect allele frequency |
| `hm_code` | Harmonisation quality: 10 = direct match, 11 = palindromic resolved; exclude all others |
| `p_value` | GWAS p-value |
| `standard_error` | SE of beta — required for MR and coloc |

**Usage note**: Match to DICE eQTL data by `hm_rsid` (rsID-based, build-agnostic). DICE is GRCh37; the 1000G LD panel is also GRCh37 — only the GWAS harmonised columns are GRCh38.

---

## 1kg/
**1000 Genomes Phase 3 — LD reference panel, all superpopulations**

**Reference**: 1000 Genomes Project Consortium 2015, *Nature* | Source: MRC IEU fileserver (`1kg.v3.tgz`, May 2020)  
**Genome build**: GRCh37 — matches DICE eQTL coordinates directly  
**Format**: plink binary (`.bed` / `.bim` / `.fam`) per superpopulation | Tool: `genotype.sif` (plink v1.9 and plink2)

Genome-wide genotype matrices used to compute in-locus LD for SuSiE fine-mapping, SuSiE-coloc, and plink-based IV clumping in multi-SNP MR. All three files per population are required by plink and cannot be used independently. Select the population matching your GWAS ancestry (EUR for Bentham 2015 SLE).

**Usage**: `bfile = "/vol/projects/BIIM/agentic_immunology/datalake/gwas/1kg/{POP}"` where `{POP}` is one of EUR, AFR, AMR, EAS, SAS.

| Population | Samples | Variants | .bed size |
|---|---|---|---|
| AFR | 661 | ~13.6M | 2.3 GB |
| AMR | 347 | ~8.9M | 811 MB |
| EAS | 504 | ~8.0M | 908 MB |
| EUR | 503 | ~8.6M | 1.1 GB |
| SAS | 489 | ~9.3M | 1.1 GB |

### {POP}.bed
**Binary genotype matrix**  
Bit-packed genotype calls (0/1/2 per allele) for all samples × variants. Not human-readable; requires `.bim` and `.fam` to be interpreted.

### {POP}.bim
**SNP manifest**  
One row per variant: chromosome, rsID, genetic distance (cM), GRCh37 base-pair position, allele 1, allele 2.

### {POP}.fam
**Sample manifest**  
One row per individual: family ID, sample ID, father ID, mother ID, sex, phenotype.
