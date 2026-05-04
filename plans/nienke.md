# Nienke's Multi-Omics Aging Cohorts

## Cohorts (`/vol/projects/CIIM/cohorts/`)

### SI — Senior Individuals (primary aging cohort)
Most complete multi-omics dataset. Relevant for aging QTL work.

| Modality | Notes |
|---|---|
| ATACseq | raw |
| RNAseq | raw + processed |
| Cytokines | ~47 cytokines × 15 stimulations (LPS, polyIC, pam3cys, CPG, RPMI, varilrix, flu, HSV, VZV, CMV, cov-N/C/ctrl) at **24h** and **7d** → ~500+ phenotypes. Processed: log2, z-score versions at `cytokines_processed/` |
| Flow cytometry | raw |
| Genotype | raw + imputed VCFs at `genotype_processed/imputed_vcf/` |
| Metabolomics | raw |
| Methylation | raw + processed |
| Microbiome | raw |
| Phenotype | processed (comorbidity data, review paper) |

### BCG_prime — BCG Prime cohort (small subset used)
| Modality | Notes |
|---|---|
| Cytokines | raw |
| Genotype | raw + processed |
| Metabolomics | raw |
| Methylation | raw + processed |
| Proteomics | raw |
| Phenotype | raw |

### 2000HIV 
HIV-positive individuals; useful for immune-aging comparisons.

| Modality | Notes |
|---|---|
| RNAseq | processed |
| Cytokines | raw |
| Flow cytometry | processed |
| Genotype | raw |
| Methylation | raw + processed |
| Proteomics | raw + processed |
| **scRNAseq** | `2000HIV_PLHIV.h5ad` (n=224) and `2000HIV_PLHIV_CMV.h5ad` (CMV split); metadata in `240318_Selection_scRNAseq_FINALMetadata.n=224.xlsx` |

---

## QTL Results (`/vol/projects/CIIM/meta_cQTL/out/SI-senior/`)

Full QTL mapping run on SI-senior for **5 omics layers**:

| QTL type | Stimulations | Approx phenotypes |
|---|---|---|
| **cQTL** (cytokines) | LPS, polyIC, pam3cys, CPG, varilrix, flu, CMV, VZV, CoV-N/C/ctrl, RPMI | ~500+ |
| **eQTL** (expression baseline) | baseline | transcriptome-wide |
| **eQTL 24h** | LPS, pam3cys, CPG (separate runs) | — |
| **meQTL** (methylation) | baseline | — |
| **metabQTL** (metabolomics) | baseline | — |

Each omics layer has a consistent output structure:
```
mapping/
  main/chr*.tsv          # full summary statistics (all tested SNPs per chr)
  main_genomewide.tsv    # genome-wide significant hits
  main_genomewide_loci.tsv     # lead SNP per locus (genome-wide)
  main_genomewide_loci_annot.tsv   # + nearest gene, cis-eQTL annotation, consequence
  main_studywide.tsv     # study-wide significant hits
  main_studywide_loci.tsv
  main_1e-5.tsv          # suggestive threshold hits
  main_nominal.tsv       # nominal results
```

---

## Locus of Interest — rs11867200

> Identified by Nienke; mostly negative follow-up results so far.

| Field | Value |
|---|---|
| Locus | 11 |
| CHR:BP | chr17:34,248,950 |
| REF/ALT | C / T |
| rsID | rs11867200 |
| Trait | `pbmc_24h_mcp1_lps` (MCP-1 / CCL2 after LPS stimulation) |
| β | −0.354 |
| t-stat | −5.97 |
| p-value | 4.4 × 10⁻⁹ |
| N | 531 |
| Consequence | intron_variant |
| Cis-eQTL gene | **CCL8** (Z=5.29, FDR=3.7×10⁻⁴) |

### Biological interpretation
The SNP sits in an intronic region on chr17 within the **CCL2/CCL7/CCL8 chemokine cluster**. It is simultaneously:
- A **cQTL** for MCP-1 (CCL2 protein) production after LPS
- A **cis-eQTL** for **CCL8** (MCP-2) gene expression

This suggests the variant may act through a **shared regulatory element** controlling multiple chemokines in the cluster. The most likely mechanism is allele-specific binding of a transcription factor regulating the entire locus, rather than a coding effect on a single gene — which may explain why targeted follow-up (focused on a single gene) was negative.

### Potential next steps
- Colocalization of the cQTL signal (MCP-1 LPS) with the CCL8 eQTL using full summary statistics from `main/chr17.tsv`
- Check if rs11867200 is a known GWAS hit (OpenGWAS / GWAS catalog) for inflammatory or immune traits
- Look at the chr17 chemokine locus in ATAC-seq (SI cohort) for accessible chromatin peaks overlapping the SNP position
