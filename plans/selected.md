## Cohorts (`/vol/projects/CIIM/cohorts/`)

### SI — Senior Individuals
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
### QTL Results
`/vol/projects/CIIM/meta_cQTL/out/SI-senior/`

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

### BCG_prime — BCG Prime cohort 
the BCG-PRIME trial — a randomized controlled trial in elderly individuals (>60 years) testing whether BCG vaccination reduces morbidity/adverse events. It's an aging cohort (6,112 participants; 471 with genomics). 

It has:

 - A long-term follow-up component (BCG-LT), which includes participants from both PRIME and the BCG-CORONA-ELDERLY trial
 - Phenotypes: demographics, comorbidities, adverse events, COVID events, vaccines
 - Omics: cytokines, genotype, methylation, metabolomics, proteomics

So it is an aging cohort (elderly, >60 yrs), specifically designed around BCG vaccination as an intervention. 

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

