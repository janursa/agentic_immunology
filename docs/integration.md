# Agentic Central — Change Log

## 2026-05-25

### IBD Pseudobulk RNA — `datalake/omics/IBD/rna_bulk.h5ad`
Pseudobulk AnnData derived from `rna.h5ad`. Cells grouped by `(celltype, donorID, stimulation)`; raw counts summed per group, then normalized with `normalize_total` (CPM) + `log1p`.
- 395 pseudo-samples × 24,978 genes
- `.X` — CPM log1p normalized (float64, sparse); no `.layers`
- `.obs` fields: `celltype`, `donorID`, `stimulation`, `disease`, `gender`, `n_cells`
- Script: `temp/ibd_pseudobulk/script.py`

---

## 2026-05-23

### IBD  Multiome — `datalake/omics/IBD/`
PBMC multiome (scRNA-seq + scATAC-seq) from CD and UC patients. Converted from Seurat.rds (`/vol/projects/CIIM/IBD/Functional_Multiome_2023/data/Seurat.rds`) using `genernbi` conda R + `ciim.sif` Python.
- 120,361 cells; CD (62,385) + UC (57,976); no healthy controls
- Stimulations: LPS, RPMI, *S. salmonella*
- `rna.h5ad` — 120,361 × 24,978 genes
- `atac.h5ad` — 120,361 × 182,416 peaks
- Key `.obs` fields: `disease`, `stimulation`, `celltype`, `celltype.l2`, `donorID`, `gender`

---

## 2026-05-19

- SLE prior drug targets retrieved from OpenTargets Platform (141 drugs, 129 targets, all phases + approved) → `datalake/prior/sle_targets/`; analysis in `analysis/sle_previous_targets/`

### genome_refs — `/vol/projects/jnourisa/genernbi/resources/supp_data/`
Shared hg38 reference files (not migrated, referenced in place):

### motif_databases — `/vol/projects/jnourisa/genernbi/resources/supp_data/databases/`
TF motif and binding site resources for GRN tools (not migrated, referenced in place):

### eQTL datasets added — `datalake/eQTL/`

Four cis-eQTL resources covering whole blood, 50 GTEx tissues, and 14–24 immune cell types:

#### eQTLGen — `eqtlgen/`
Whole-blood cis-eQTL meta-analysis (Võsa et al. 2021, *Nat Genet*), n=31,684, 37 cohorts, GRCh37:
- `sig/eQTLGen_cis_sig_FDR05.txt.gz` — significant pairs (FDR < 0.05), 308 MB
- `allpairs/eQTLGen_cis_allpairs.txt.gz` — all tested pairs, 3.7 GB

#### GTEx v10 — `gtex_v10/sig/`
Significant cis-eQTLs across 50 tissues (GRCh38, ~3 GB total). Per tissue: `.eGenes.txt.gz` (best variant per gene + permutation stats) and `.eQTLs.signif_pairs.parquet` (all significant pairs).

#### GTEx v8 / eQTL Catalogue — `gtex_v8_eqtl_catalogue/allpairs/`
All cis-eQTL pairs for spleen (3.3 GB) and whole blood (2.7 GB), n≈670. Tabix-indexed, eQTL Catalogue r7 schema — drop-in compatible with `run_coloc` (`generic_tsv` format).

#### OneK1K — `onek1k/sig/` and `onek1k_eqtl_catalogue/allpairs/`
PBMC eQTLs across immune cell types (Yazar et al. 2022, *Science*), n=982:
- `onek1k/sig/` — 14 cell types, direct download (GRCh37), significant pairs; `*_eqtl_table.tsv.gz` + `*_esnp_table.tsv.gz` per cell type
- `onek1k_eqtl_catalogue/allpairs/` — 10 cell types, tabix-indexed allpairs (eQTL Catalogue r7), drop-in compatible with `run_coloc`

All eQTL Catalogue allpairs files share the same column schema and are compatible with `run_coloc` and `run_MR`.

## 2026-05-18

### Multi-omic QTL datasets added

#### sQTL — `datalake/sQTL/`
Splicing QTL (leafcutter) from eQTL Catalogue r7, tabix-indexed. 14 immune cell types across 3 studies:
- `sQTL/blueprint/` — monocyte (260 MB, QTD000025), neutrophil (199 MB, QTD000030), CD4+ T cell (605 MB, QTD000035); Chen et al. 2016, n=167–196
- `sQTL/schmiedel_2018/` — 10 DICE immune cell types (13–24 MB each); Schmiedel et al. 2018, n=88–91
- `sQTL/gtex_v8/` — whole blood (576 MB, QTD000360); GTEx Consortium 2020, n=670

#### pQTL — `datalake/pQTL/`
Plasma protein QTL from eQTL Catalogue r7, tabix-indexed:
- `pQTL/sun_2018/plasma.cc.tsv.gz` — 207 MB, ~2,994 proteins (SomaScan), n=3,301 (INTERVAL); Sun et al. 2018, Nature

#### mQTL — `datalake/mQTL/`
BLUEPRINT immune cell methylation QTL (Chen et al. 2016, Cell). Filtered FDR < 0.05, streamed from EBI FTP (full files 26 GB/cell type not stored locally):
- `mQTL/blueprint/mono_meth_fdr05.tsv.gz` — monocyte
- `mQTL/blueprint/neut_meth_fdr05.tsv.gz` — neutrophil
- `mQTL/blueprint/tcel_meth_fdr05.tsv.gz` — T cell

All three modalities share the same column schema and are drop-in compatible with `run_coloc` (`generic_tsv` format) and `run_mr`.

---

---
## VirtualBiotech
### Data Downloaded
All 4 files from the public GitHub repo into `datalake/virtualbiotech/`:
- `clinical_trial_labels.csv` — 56,707 LLM-curated trial outcome labels
- `chembl_clinical_nct_data.parquet` — NCT↔targetId (Ensembl) mapping
- `comprehensive_features_aggregated_v2_optimized.parquet` — precomputed SC features for 1,511 genes
- `tahoe_efficacy_features_long.parquet` — Tahoe-100M perturbation features (not used here)

## 2026-04-15

### Datasets added

#### NicheNet 
All files under `datalake/nichenet/`

#### DICE 
`datalake_docs/dice/list.md` was written today covering the full DICE dataset (Schmiedel et al. 2018 *Cell*, DICE-DB 1, GRCh37.p19, 91 donors)
Both filtered (sig ones) and full summary stats (47 GB)
~220M SNP-gene pairs per cell type vs 347K in the filtered version

#### PrimeKG — documentation written *(file pre-existing since Feb 2026)*
`datalake_docs/kg/list.md` was written today documenting `PrimeKG.csv` (Chandak et al. 2023 *Scientific Data*, 8.1M rows, 20 source databases across 10 biological scales).

## 2026-05-10
### Cell * gene database API
added to ciim/genomics.md

### Kummerlowe
perturbation (drug) on human immune cells -> ~90 drugs, 1 donor

### gwas folder
Gwas summary stats for SLE -> GCST003156_SLE_Bentham2015.h.tsv
LD for different ancestry: gwas/1kg

## 2026-05-18

### S-LDSC reference data (GRCh38)
Cell-type heritability enrichment analysis for SLE.

Downloaded from Zenodo record 10515792 into `datalake/gwas/ldsc_grch38/`:
- `GRCh38.tgz` → `GRCh38/` — 1000G EUR plink files (GRCh38) + weights + baselineLD_v2.2
- `1000G_Phase3_baseline_v1.2_ldscores.tgz` → `baseline_v1.2/` — 97 baseline annotations aligned to **GRCh38** (the only baseline version on GRCh38; required for cell-type-specific heritability analysis per Finucane 2018)

### ldsc tool
Cloned `abdenlab/ldsc-python3` (Python 3 port of bulik/ldsc) to `tools/ldsc/`.
New singularity image: `singularity/ldsc.sif` — ciim + pip install ldsc. Provides `ldsc.py`, `munge_sumstats.py`, `make_annot.py`.

### S-LDSC analysis (SLE cell-type specificity)
Workspace: `temp/sle_ct_specificity/`
Runs: Perez scRNA-seq → SEGs per cell type → genomic annotations → S-LDSC with `--h2-cts` → enrichment p-value per immune cell type.

---

## 2026-05-13

### Colocalization pipeline 

GWAS × eQTL colocalization script (coloc.abf + coloc.susie) made modular and registered as a tool.

**Script:** `tools/ciim/code/coloc.R`
**Tool entry:** `tools/ciim/code/genetics.py` → `run_coloc()`
### MR pipeline 

MR in R 
**Script:** `tools/ciim/code/MR.R`
**Tool entry:** `tools/ciim/code/genetics.py` → `run_MR()`

