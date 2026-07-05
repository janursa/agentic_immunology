# 📊 Data Lake 
## omics
*OMICs*
Raw omics data

### hiara
*HIaRA*
PBMC gene expression data (single-cell and pseudobulk) across healthy aging cohorts, disease conditions (SLE), drug perturbations (op dataset), cytokine perturbations (parsebioscience dataset), and a longitudinal flu vaccination cohort (soundlife), which is also an aging cohort.
Files are listed in `datalake/omics/hiara/list.md`
### incentive
*INCENTIVE*
PBMC multiome data (scRNA-seq + scATAC-seq, paired) from an elderly influenza vaccine cohort. 37 donors (age 60–76 y; 80 male / 68 female sample entries), 4 longitudinal timepoints (V2–V5). Responder categories: DR, TR, QR, QNR. Includes influenza antibody titres (H1N1, H3N2, B/Washington, B/Phuket) at D0 and D28. Clinical + demultiplexing metadata in `demultiplexedDonorMetadata.csv`.
- scRNA-seq (raw per-pool count matrices, not merged, not cell-type-annotated, no pseudobulk available): `/vol/projects/CIIM/processed/scRNAseq/INCENTIVE/`
- scATAC-seq (per-pool processed peak/fragment counts, not cell-type-annotated, no pseudobulk available): `/vol/projects/CIIM/cohorts/INCENTIVE/scATACseq_processed/` and `/vol/projects/CIIM/processed/scATACseq/INCENTIVE/`
- **Before any cell-type-resolved or pseudobulk analysis**: cell-type annotation + pseudobulking must be run first (no ready-made `_bulk`/`_bulk_minor` files exist for this cohort, unlike `hiara`). Budget this as its own step when planning to use INCENTIVE.

### IBD 
*IBD*
PBMC multiome data (scRNA-seq + scATAC-seq, paired) from IBD patients (Crohn's disease and ulcerative colitis). 120,361 cells; no healthy controls. 3 stimulation conditions: LPS, RPMI (control), *S. salmonella*. 5 major cell types (CD4 T, Monocytes, B, CD8 T, NK) and 10 subtypes (Naïve CD4 T, Memory CD4 T, Macrophages, Tregs, MAIT, Plasmablasts, etc.).
- **Disease:** CD (62,385 cells) + UC (57,976 cells)
- **Assays:** RNA (24,978 genes), ATAC (182,416 peaks)
- Raw Seurat object: `/vol/projects/CIIM/IBD/Functional_Multiome_2023/data/Seurat.rds`
- Processed h5ad: `datalake/omics/IBD/rna.h5ad`, `datalake/omics/IBD/atac.h5ad`
- Pseudobulk RNA: `datalake/omics/IBD/rna_bulk.h5ad` — 395 pseudo-samples × 24,978 genes; grouped by (celltype, donorID, stimulation); `.X` = CPM log1p normalized (no `.layers`); `.obs`: `celltype`, `donorID`, `stimulation`, `disease`, `gender`, `n_cells`

### kummerlowe
*Kummerlowe*
Compressed phenotypic drug screen on primary human PBMCs (1 healthy donor). 90 small-molecule compounds from the Broad Drug Repurposing Hub (known MOA), tested under 3 stimulation conditions: Control (DMSO), IFNβ (4h), and LPS (4h). Compressed design: 6 drugs pooled per well, 3 replicate wells per drug — individual drug assignment requires cNMF deconvolution. 120,174 cells × 15,313 genes after QC.  
Files are listed in `datalake/omics/Kummerlowe/list.md`

**90 compounds:** A-366, ABT-737, AMG 900, AMG 925, APY0201, AZ 191, AZD2014, AZD7545, Andarine, Apratastat, BI-78D3, BIO, BIX02188, BLU9931, BMS 564929, BMS 566419, BX-912, CHIR-99021, CP 724714, CPI-0610, Carmustine, Dothiepin hydrochloride, EPZ015666, FR 180204, Filanesib, Filgotinib, GDC-0879, GNF 5, GSK J4, GSK2334470, GW 3965 hydrochloride, GW 5074, Halopemide, Homochlorcyclizine 2HCl, Hydroxyzine (dihydrochloride), ICG-001, IOX 2, Ispinesib, KH-CB19, Ketotifen (fumarate), Lenvatinib, Linsitinib, MK-5108, ML 298 hydrochloride, ML-323, ML324, Maprotiline HCl, Merimepodib, NVP-AEW541, NVS-PAK1-1, Neflamapimod, Neratinib, Niraparib, ORPHENADRINE CITRATE, P005091, PD 198306, PF 477736, PFI-1, PHYSCION, PNU-74654, Pomalidomide, Ponatinib, Purmorphamine, RG-7112, RGFP966, Rapamycin, Romidepsin, Rosuvastatin calcium, Ruxolitinib, SAG, SCH900776, SGC 707, SGX-523, SHP 99.00, SU 3327, SU11274, Skepinone-L, T 0901317, THZ1, UNC0642, Valrubicin, Veliparib, WZ4003, XL413 (hydrochloride), delta-Tocotrienol, selumetinib, (2Z)-2-butenedioic acid compound with N,N-dimethyl-2-{3-[(1S)-1-(2-pyridinyl)ethyl]-1H-inden-2-yl}ethanamine (1:1), (3R)-6-chloro-3-methyl-1,5-dihydroimidazo[2,1-b]quinazolin-2(3H)-one, 2-((1H-pyrrolo[2,3-b]pyridin-5-yl)oxy)-4-(4-((4'-chloro-5,5-dimethyl-3,4,5,6-tetrahydro-[1,1'-biphenyl]-2-yl)methyl)piperazin-1-yl)-N-((3-nitro-4-(((tetrahydro-2H-pyran-4-yl)methyl)amino)phenyl)sulfonyl)benzamide, 3,6-diamino-10-methylacridinium chloride compound with 3,6-acridinediamine (1:1)

## ciim
Datasets physically present under `/vol/projects/CIIM/`. Access them directly via the paths below.

### SI — Senior Individuals (multiomics cohort)

**Base path:** `/vol/projects/CIIM/cohorts/SI/`

279 donors with full phenotype data (651 sample entries across visits); N=531 used in QTL mapping (genotype + cytokine overlap).
- **Age:** 22–85 y (mean 63.8 y) — ⚠️ skewed toward seniors despite the wide range; check the actual age histogram before using for a young-vs-old contrast, name-as-"SI" notwithstanding
- **Sex:** 187 Male / 92 Female
- **Ethnicity:** predominantly Caucasian (273/279; ~98%)

| Modality | Status | Notes |
|---|---|---|
| **ATACseq** | raw | `ATACseq_raw/` |
| **RNAseq** | raw + processed | 205 donors; baseline (99 samples) + 21 stimulation conditions at 24h (LPS n=271, NS n=202, Pam3Cys n=182, CpG n=154, polyIC n=154; plus smaller sets: influenza/varilrix/shingrix/ns-antigen n=10 each) and 7d (NS n=138, VZV-oka n=141, CMV/HSV/HSV-peptide/influenza/VZV/VZV-peptide/CoV-N/CoV-C/CoV-ctrl n=35–39); ~13,107 genes after filtering; CPM-normalized per stimulation at `RNAseq_processed/counts/2-norm/filter/{stim}_cpm.tsv`; raw tximport RDS at `RNAseq_processed/counts/` (baseline/24h/7d) — do not use the batch-corrected version. |
| **Cytokines** | raw + processed | ~47 cytokines × 15 stimulations (LPS, polyIC, pam3cys, CpG, RPMI, varilrix, flu, HSV, VZV, CMV, CoV-N/C/ctrl) at 24h and 7d → ~500+ phenotypes; log2 + z-score at `cytokines_processed/` |
| **Flow cytometry** | raw | `flowcytometry_raw/` |
| **Genotype** | raw + imputed | imputed VCFs at `genotype_processed/imputed_vcf/` |
| **Metabolomics** | raw | `metabolomics_raw/` |
| **Methylation** | raw + processed | `methylation_processed/` |
| **Microbiome** | raw | `microbiome_raw/` |
| **Phenotype** | processed | comorbidity data, review paper |

QTL results (5 layers: cQTL, eQTL, eQTL-24h, meQTL, metabQTL) at `/vol/projects/CIIM/meta_cQTL/out/SI-senior/`; each layer has per-chr full stats, genome-wide, study-wide, and nominal outputs.


### BCG_prime / BCG_Prime — BCG Prime cohort 
#TOEVAL: process and merge datasets?
The BCG-PRIME trial — a randomized controlled trial in elderly individuals (>60 years) testing whether BCG vaccination reduces morbidity/adverse events.

Base dir: `/vol/projects/CIIM/`

- **Disease / context:** Aging; BCG vaccination RCT (BCG vs placebo)
- **Population:** Elderly (>60 yrs), predominantly Caucasian
- **Sample size:** 6,112 participants total; 471 with genomics
- **Long-term follow-up:** BCG-LT component includes participants from both PRIME and the BCG-CORONA-ELDERLY trial
- **Phenotypes:** demographics, comorbidities, adverse events, COVID events, vaccines
- **scRNAseq status:** Raw demultiplexed counts only (87+ pools in `BCG_Prime/scRNAseq_processed/`); no merged/processed h5ad
- **scATACseq status:** Raw demultiplexed (in `BCG_Prime/scATACseq_processed/`); no merged/processed h5ad

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

---

### 2000HIV 
PBMC multi-omics cohort of People Living with HIV (PLHIV).
Base dir: `/vol/projects/CIIM/`

- **Disease:** HIV (all PLHIV; no healthy controls in scRNAseq)
- **Population:** Multi-ethnic (White, Black, Mixed, Asian, Hispanic); multi-center (EMC, OLV, ETZ, RUMC; Netherlands)
- **scRNAseq donors:** 290 total in h5ad (224 in final selection/metadata file)
- **scRNAseq cells:** 698,742 cells × 29,021 genes
- **Age range:** 23–77 years
- **Sex:** ~77% male (536,821), ~23% female (161,921)
- **Cell types (lvl0):** T cells (381,950), Monocytes (193,438), B/Plasma (55,619), NK (47,537), DCs (17,842), other (2,356)
- **CMV split:** `2000HIV_PLHIV_CMV.h5ad` available for CMV+/− stratified analyses
- **scRNAseq metadata:** `240318_Selection_scRNAseq_FINALMetadata.n=224.xlsx`

| Modality | Status | n samples | Details |
|---|---|---|---|
| RNAseq | processed | — | bulk PBMC; DESeq2 object + raw/normalized count RDS; batch-correct for season, sex, center |
| Cytokines | raw | 1,793 samples | PBMC 24h; 13 cytokines (IL-1β, IL-6, IL-8, IL-10, IL-17, IL-22, IL-1RA, IFN-γ, TNF-α, MCP-1, MIP-1α, IL-5, all-cyt); 15 stimulations (RPMI, LPS, polyIC, MTB, CMV, HIV env, Candida, E.coli, S.aureus, S.pneumoniae, PHA, IMQ, IL-1α, Candida hyphae, all-stim) |
| Flow cytometry | processed | 1,423–1,434 samples | 3 panels; ABS (1,423 × 415 vars), PER/MFI (1,434 × 356/521 vars); centers: EMC, ETZ, FAM, OLV, RAD |
| Genotype | raw | 1,356 samples | array-genotyped; all-ethnicities + per-ancestry splits (European, African) in PLINK bed format |
| Methylation | raw + processed | 1,914 samples | EPIC 850k array; discovery (n=1,592) + validation (n=322); M-values in `methylation_processed/Combined/` |
| Proteomics | raw + processed | 1,910 samples | Olink Explore 3072; 2,367 proteins; bridging-normalized; also older panel (641 × 1,463 proteins) |
| **scRNAseq** | processed | 290 donors / 698,742 cells | `2000HIV_PLHIV.h5ad` (29,021 genes); CMV split: `2000HIV_PLHIV_CMV.h5ad`; metadata: `240318_Selection_scRNAseq_FINALMetadata.n=224.xlsx` |

---

### LongCovid — Long COVID multiome cohort

Multimodal Long COVID cohort. In-house modalities (multiome, flow cytometry, proteomics, genotype, metabolomics) plus processed RDS objects of public data (Mayo/GSE263817).

**path**: `/vol/projects/CIIM/processed/multiome/LongCovid/`; other modalities under `/vol/projects/CIIM/cohorts`

| Modality | Status | Path | Details |
|---|---|---|---|
| **Multiome (snRNA+snATAC)** | processed | `processed/multiome/LongCovid/withoutStim/bothCohorts_annotated_4Mods_WithLinkedPeaks.rds` (9.96 GB) | 10x Multiome, 117,598 cells (discovery 87,138 + replication 30,460), 4 assays RNA/ATAC/peaks(171,844)/chromvar; metadata `CellType`, `TimePointAll` (HC/T1–T5), `RecovStatus`, `highestWHOscore`/`visitWHOscore`. |
| Multiome — stim subset | processed | `processed/multiome/LongCovid/withStim/stim_lc_peak_chromvar_alllinks_clinic.rds` (13 GB) | *P. aeruginosa*-stimulated functional subset (12 donors: LCAM7+LCAS5+RLC6, T1/T2/T4/T5); embeds clinical columns `fas_score`, `blood_gases_po2`, `score_mmrc` (now also available cohort-wide in the metadata table below). |
| **Clinical metadata table** | processed | `datalake/covid/metadataBothDiscoveryReplicationCohort_toUseForAnalysis_withDyspnea.xlsx` | Full-cohort per-visit clinical table, **50 patients / 83 patient-visits, T1–T5, both discovery + replication**. Join key `PatientID`/`TimePoint` (also `PatientID_TP`). Columns: `Age`, `Sex`, `HighestWHOscore`/`VisitWHOscore` (→ multiome `highestWHOscore`/`visitWHOscore`), lung function `TLC%`/`DLCO%`/`FEV%`/`FVCEX%`/`ResVol%`, blood gases `pCO2`/`pO2` (=`blood_gases_po2`), `FA_Score`+`FA_Score_Category` (=`fas_score`), `score_mmrc (Dyspnoe)` (=`score_mmrc`), `Recovered` (Yes/No). |

| Flow cytometry | raw | `cohorts/LongCovid/flowcytometry_raw/AGLi/` | 11-protein Sony ID7000; Panel 1/2/3, per-sample; numeric sample IDs (e.g. 4896, BL44, 2314). No clinical labels attached. |
| Proteomics | raw | `cohorts/Olink_LongCovidandPA/proteomics_raw/` + `cohorts/LongCovid_and_HDV_Dec2024/proteomics_raw/` | plasma Olink NPX (LC + PA; LC + HDV Dec-2024 batch). |
| Genotype | processed | `cohorts/LongCovid/genotype_processed/` | genotype array; used for Souporcell demultiplexing of the multiome. |
| Metabolomics | raw | `cohorts/LongCOVID/metabolomics_raw/` | plasma metabolomics. |

(`cohorts/LongCovid/multiome_processed/withoutStim|withStim/` mirrors the `processed/multiome/LongCovid/` objects.)

> **Note — dataset linkage.** The subsection groups one cohort profiled across modalities; the multiome is the anchor. Three tiers of linkage:
> - **Mechanically coupled to the multiome:** *Genotype* is used for Souporcell demultiplexing of the pooled multiome (assigns nuclei → donor). The *stim subset* is a 12-donor subset of the multiome itself (the only object carrying clinical columns).
> - **Same cohort, donor-level (join intended, not yet on disk):** *Flow cytometry* (numeric sample IDs, no clinical labels — ID crosswalk to multiome donors pending), *Proteomics* (plasma Olink), *Metabolomics* (plasma).
> - **Not the same individuals:** the two `VirginiaData/` objects are public Mayo/GSE263817 data (metadata key `PASC_cat`, distinct from the in-house `TimePointAll`/`RecovStatus`) — co-located in the folder for comparison only, not cohort donors.

> **Note — clinical phenotype columns.** Per-visit clinical scores (`fas_score`, `score_mmrc`, `blood_gases_po2`) are now available cohort-wide in `datalake/covid/metadataBothDiscoveryReplicationCohort_toUseForAnalysis_withDyspnea.xlsx` (50 patients / 83 visits, T1–T5; join on `PatientID`/`TimePoint`), in addition to the 12-donor stim subset object. Controlled-access (EGAS50000000142/143).
> ✅ RESOLVED (2026-06-15): full-cohort clinical table received and stored under `datalake/covid/`.
> 🕓 STILL PENDING: ID crosswalk from the multiome `PatientID`s to the flow-cytometry sample IDs (`4896`/`BL44`/…) — not provided by this table.

## prior
*Prior*
Curated reference files: 
- immune cell type marker genes (major + minor levels)
- a list of 1,638 human transcription factors
- SLE prior drug targets (141 drugs / 129 targets from OpenTargets Platform, all clinical phases + approved).  
Files are listed in `datalake/prior/list.md`

## omnipath
*OmniPath*
Signaling network data pulled from the OmniPath REST API. Covers directed protein interactions, kinase-substrate phosphorylation edges, ligand-receptor interactions, intercellular role annotations, and DoRothEA TF regulons.  
Files are listed in `datalake/omnipath/list.md`

## gwas
*GWAS Summary Statistics + LD Reference*
- (1) SLE full summary stats — Bentham et al. 2015, Nat Genet, GCST003156, 7.9M variants, GRCh38 harmonised
- (2) 1000 Genomes Phase 3 all-ancestry LD reference (`1kg/`) — all 5 superpopulations (AFR/AMR/EAS/EUR/SAS), GRCh37, plink format.  

Files are listed in `datalake/gwas/list.md`

## biomni
*Biomni*
Large collection of general biomedical reference databases sourced from Biomni: drug binding affinities, CRISPR gene effect screens, gene-disease associations, protein-protein interactions, GWAS (lead SNPs only, not full summary stats), gene sets (MSigDB, MouseMine, GO), TCR sequences, miRNA targets, and more.  
Files are listed in `datalake/biomni/list.md`

## virtualbiotech
*VirtualBiotech*
Data from the Virtual Biotech study (bioRxiv 2024, harrisongzhang/TheVirtualBiotech). Contains single-cell expression features for 1,511 human target genes (tau, bimodality, AE-risk scores derived from Tabula Sapiens), ChEMBL clinical trial–target–disease mappings, and LLM-labelled outcomes for 56,707 clinical trials.  
Files are listed in `datalake/virtualbiotech/list.md`

## dice
*DICE*
Gene expression (TPM) and cis-eQTL data across 15 primary human immune cell subtypes from 91 healthy donors (Schmiedel et al. 2018, *Cell*). Cell types cover the full T cell compartment (naive CD4/CD8, activated, Th1/2/17/Tfh/Treg) plus B cells, NK cells, and monocytes. eQTLs provide cell-type-specific causal regulatory anchors; resting vs. activated pairs provide built-in perturbation comparisons for TCR activation programs. There is both filtered (sig) and unfiltered SNP-gene association results.
Files are listed in `datalake/dice/list.md`

## kg
*Knowledge graphs*
Large-scale knowledge graphs for biomedical reasoning and drug repurposing. Currently contains PrimeKG (Chandak et al. 2023, *Scientific Data*), a multiplex knowledge graph integrating 20 databases across 10 biological scales: genes/proteins, drugs, diseases, phenotypes, pathways, GO terms, anatomy, and exposures. 8.1M edges.  
Files are listed in `datalake/kg/list.md`

## cellxgene
*CellxGene Census*
Remote single-cell database (125.5M unique cells / 217.8M total records, ~900 datasets, snapshot 2025-11-08) streamed on demand via `cellxgene_get_anndata` / `cellxgene_query_obs` in `genomics.py` — no local files. Includes Tabula Sapiens (3.4M cells, 28 organs, healthy only, scRNA-seq), plus hundreds of other studies covering disease, perturbation, and development. Overview and Tabula Sapiens breakdown in [`datalake/cellxgene_overview.md`](datalake/cellxgene_overview.md)

## nichenet
*NicheNet*
NicheNet v2 prior model networks (Browaeys et al. 2020, *Nature Methods*; Zenodo doi:10.5281/zenodo.7074291). General-purpose cell-cell communication tool providing empirically calibrated edge weights connecting extracellular ligands end-to-end to target gene expression via intracellular signaling and TF regulation. Contains ligand-receptor pairs (4,986), weighted signaling network (3.9M edges), weighted gene regulatory network (4.6M edges), ligand→TF matrix (33K×1.2K), and ligand→target matrix (34M long-format rows). Files available as both `.rds` (original R) and `.parquet` (Python-ready).  
Files are listed in `datalake/nichenet/list.md`

## sQTL
*Splicing QTL*
Cis-sQTL summary statistics (leafcutter intron excision) across 14 immune cell types from three studies: **BLUEPRINT** (monocyte/neutrophil/CD4+ T cell, n=167–196), **DICE/Schmiedel_2018** (10 immune types, n=88–91), and **GTEx v8 whole blood** (n=670). All files are tabix-indexed `.cc.tsv.gz` from the eQTL Catalogue (r7). 
Files are listed in `datalake/sQTL/list.md`

## pQTL
*Plasma Protein QTL*
Cis-pQTL summary statistics for ~2,994 plasma proteins (SomaScan aptamers) from **Sun et al. 2018** (*Nature*, INTERVAL cohort, n=3,301). Tabix-indexed `.cc.tsv.gz` from the eQTL Catalogue (r7). `gene_id` column maps aptamers to Ensembl gene IDs.  
Files are listed in `datalake/pQTL/list.md`

## mQTL
*Methylation QTL*
Cis-mQTL (FDR < 0.05) for 3 primary human immune cell types — **monocyte**, **neutrophil**, **T cell** — from **BLUEPRINT** (Chen et al. 2016, *Cell*). Methylation measured by 450k array (M-values). Stored as filtered significant pairs (full 26 GB files remain at EBI FTP for per-locus regional queries). GRCh37.  
Files are listed in `datalake/mQTL/list.md`

## eQTL
*Expression QTL*
Cis-eQTL summary statistics across four datasets:
- **eQTLGen** — whole-blood meta-analysis (n=31,684, 37 cohorts; Võsa et al. 2021, *Nat Genet*); significant (FDR < 0.05) and all-pairs files. GRCh37.
- **GTEx v10** — significant eQTLs across 50 tissues (GRCh38); per tissue: eGenes file + signif_pairs parquet. ~3 GB total.
- **GTEx v8 / eQTL Catalogue** — all cis-eQTL pairs for spleen and whole blood (n≈670); tabix-indexed, eQTL Catalogue r7 schema. Drop-in compatible with `run_coloc`.
- **OneK1K** — 14 immune cell types from 982 PBMC donors (Yazar et al. 2022, *Science*); significant pairs (GRCh37, direct download) and 10-cell-type allpairs (eQTL Catalogue r7, tabix-indexed).

Files are listed in `datalake/eQTL/list.md`

## genome_refs
*Reference Genome & Annotations*
Shared reference files for peak-calling, GRN inference, and multi-omics tools. All GRCh38/hg38.
Base path: `/vol/projects/jnourisa/genernbi/resources/supp_data/`

- `genome/genome.fa` — hg38 reference genome FASTA (3.1 GB)
- `gencode.v45.annotation.gtf.gz` — GENCODE v45 gene annotation
- `gencode.v47.annotation.gtf.gz` — GENCODE v47 gene annotation
- `tss_h38.bed` — transcription start site coordinates for hg38

## motif_databases
*TF Motif & Binding Site Databases*
Reference motif and TFBS resources for GRN inference or motif analysis.
Base path: `/vol/projects/jnourisa/genernbi/resources/supp_data/databases/`
- `granie/H12INVIVO/` — HOCOMOCO v12 H12INVIVO per-TF TFBS `.bed.gz` files (948 TFs, 1,442 files)
- `granie/PWMScan_HOCOMOCOv12_H12INVIVO.tar.gz` — PWMScan archive for the full HOCOMOCO v12 H12INVIVO motif set
- `celloracle/gimme.vertebrate.v5.0.pfm` — GIMME vertebrate v5.0 motif PFM database

- `scenicplus/db.regions_vs_motifs.rankings.feather` — cisTarget region-vs-motif rankings (feather)
- `scenicplus/db.regions_vs_motifs.scores.feather` — cisTarget region-vs-motif scores (feather)
- `scenicplus/motifs-v10-nr.hgnc-m0.00001-o0.0.tbl` — motif-to-TF annotation table (strict threshold, 1e-5)
- `scenicplus/hg38-blacklist.v2.bed` — ENCODE hg38 blacklist regions v2

- `scenic/hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather` — gene-vs-motif rankings, ±10 kb window
- `scenic/hg38_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather` — gene-vs-motif rankings, 500 bp up / 100 bp down window
- `scenic/motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl` — motif-to-TF annotation table (relaxed threshold, 1e-3)

- `scglue/JASPAR2022-hg38.bed.gz` — JASPAR2022 TF motif hits on hg38
- `scglue/ENCODE-TF-ChIP-hg38.bed.gz` — ENCODE TF ChIP-seq peaks on hg38

## xenium_breast_cancer_janesick2023_rep1
*Xenium Breast Cancer (Janesick et al. 2023) Rep1*
Canonical public 10x Genomics Xenium In Situ (imaging-based spatial transcriptomics) dataset profiling human breast cancer FFPE tissue (Replicate 1). Provides single-cell-resolution spatial gene expression, cell segmentation, and transcript-level coordinates, enabling immune cell characterization and mapping of the tumor microenvironment. Source: GEO GSE243280 / GSM7780153. Reference: Janesick et al. 2023, *Nature Communications* (doi:10.1038/s41467-023-43458-x).
Files are listed in `datalake/xenium_breast_cancer_janesick2023_rep1/list.md`




