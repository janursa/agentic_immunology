# 📊 Data Lake 
## summary_stats
*Summary stats*
Results of our own analysis. 

- Immune cell TF activity and gene expression signatures for aging (5 major + 11 minor cell types, 4 cohorts) and SLE (5 major + 14 sub cell types, Perez cohort); drug TF signatures (145 compounds, OP dataset); cytokine TF signatures (90 cytokines, ParseBio study); immune GRN models (5 major cell types). 

- Virtual Biotech target-level SC expression features and clinical trial outcome rates. 

Files are listed in `datalake/summary_stats/list.md`

## omics
*OMICs*
Raw omics data

### hiara
*HIaRA*
PBMC gene expression data (single-cell and pseudobulk) across healthy aging cohorts, disease conditions (SLE), drug perturbations (op dataset), and cytokine perturbations (parsebioscience dataset).
Files are listed in `datalake/omics/hiara/list.md`
### kummerlowe
*Kummerlowe*
Compressed phenotypic drug screen on primary human PBMCs (1 healthy donor). 90 small-molecule compounds from the Broad Drug Repurposing Hub (known MOA), tested under 3 stimulation conditions: Control (DMSO), IFNβ (4h), and LPS (4h). Compressed design: 6 drugs pooled per well, 3 replicate wells per drug — individual drug assignment requires cNMF deconvolution. 120,174 cells × 15,313 genes after QC.  
Files are listed in `datalake/omics/Kummerlowe/list.md`

**90 compounds:** A-366, ABT-737, AMG 900, AMG 925, APY0201, AZ 191, AZD2014, AZD7545, Andarine, Apratastat, BI-78D3, BIO, BIX02188, BLU9931, BMS 564929, BMS 566419, BX-912, CHIR-99021, CP 724714, CPI-0610, Carmustine, Dothiepin hydrochloride, EPZ015666, FR 180204, Filanesib, Filgotinib, GDC-0879, GNF 5, GSK J4, GSK2334470, GW 3965 hydrochloride, GW 5074, Halopemide, Homochlorcyclizine 2HCl, Hydroxyzine (dihydrochloride), ICG-001, IOX 2, Ispinesib, KH-CB19, Ketotifen (fumarate), Lenvatinib, Linsitinib, MK-5108, ML 298 hydrochloride, ML-323, ML324, Maprotiline HCl, Merimepodib, NVP-AEW541, NVS-PAK1-1, Neflamapimod, Neratinib, Niraparib, ORPHENADRINE CITRATE, P005091, PD 198306, PF 477736, PFI-1, PHYSCION, PNU-74654, Pomalidomide, Ponatinib, Purmorphamine, RG-7112, RGFP966, Rapamycin, Romidepsin, Rosuvastatin calcium, Ruxolitinib, SAG, SCH900776, SGC 707, SGX-523, SHP 99.00, SU 3327, SU11274, Skepinone-L, T 0901317, THZ1, UNC0642, Valrubicin, Veliparib, WZ4003, XL413 (hydrochloride), delta-Tocotrienol, selumetinib, (2Z)-2-butenedioic acid compound with N,N-dimethyl-2-{3-[(1S)-1-(2-pyridinyl)ethyl]-1H-inden-2-yl}ethanamine (1:1), (3R)-6-chloro-3-methyl-1,5-dihydroimidazo[2,1-b]quinazolin-2(3H)-one, 2-((1H-pyrrolo[2,3-b]pyridin-5-yl)oxy)-4-(4-((4'-chloro-5,5-dimethyl-3,4,5,6-tetrahydro-[1,1'-biphenyl]-2-yl)methyl)piperazin-1-yl)-N-((3-nitro-4-(((tetrahydro-2H-pyran-4-yl)methyl)amino)phenyl)sulfonyl)benzamide, 3,6-diamino-10-methylacridinium chloride compound with 3,6-acridinediamine (1:1)


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




