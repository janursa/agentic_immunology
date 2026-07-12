# BCG Prime — File List

Physically stored under `/vol/projects/CIIM/` — not mirrored into `datalake/`.

The BCG-PRIME trial — a randomized controlled trial in elderly individuals (>60 years) testing whether BCG vaccination reduces morbidity/adverse events.

Base dir: `/vol/projects/CIIM/`

- **Disease / context:** Aging; BCG vaccination RCT (BCG vs placebo)
- **Population:** Elderly (>60 yrs), predominantly Caucasian
- **Sample size:** 6,112 participants total; 471 with genomics
- **Long-term follow-up:** BCG-LT component includes participants from both PRIME and the BCG-CORONA-ELDERLY trial
- **Phenotypes:** demographics, comorbidities, adverse events, COVID events, vaccines
- **scRNAseq status:** Raw demultiplexed counts only (87+ pools in `BCG_Prime/scRNAseq_processed/`); no merged/processed h5ad
- **scATACseq status:** Raw demultiplexed (in `BCG_Prime/scATACseq_processed/`); no merged/processed h5ad

#TOEVAL: process and merge datasets?

| Modality | Status | n samples | Details |
|---|---|---|---|
| Cytokines | raw | 674 samples | whole blood, 48h; 7 cytokines (IFN-α/γ, IL-1β, IL-1RA, IL-6, IL-10, TNF-α); 9 stimulations (RPMI, LPS, R848, S.aureus, Candida, Wuhan/Delta/Omicron spike, influenza) |
| Flow cytometry | raw | — | `flowcytometry_raw/` |
| Genotype | raw + processed | 661 samples | raw PLINK bed (`BCG_prime_combined`); TOPMed-imputed (`genotype_processed/`) |
| Metabolomics | raw | 499 (LUMC) + 315 (RADN) | 172 metabolites per site (NMR lipoprotein panel) |
| Methylation | raw + processed | 383 samples | EPIC 850k array; M-values in `methylation_processed/BCG_prime_Mval.rdata` |
| Proteomics | raw | 675 (RADN T1) + 107 (RADB) | Olink (92 proteins per panel); `olink_RADN_T1.tsv`, `olink_RADB.tsv` |
| Phenotype | raw | 6,112 total | `PRIME_studydata.xlsx`, AE data, LT follow-up |
| **scRNAseq** | raw (demultiplexed) | ~87 pools | `BCG_Prime/scRNAseq_processed/`; no merged h5ad yet |
| **scATACseq** | raw (demultiplexed) | — | `BCG_Prime/scATACseq_processed/`; no merged h5ad yet |
