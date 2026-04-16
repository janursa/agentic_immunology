## 📊 Data Lake 
### omics
*OMICs*
### hiara
*HIaRA*
PBMC gene expression data (single-cell and pseudobulk) across healthy aging cohorts, disease conditions (SLE), drug perturbations (op dataset), and cytokine perturbations (parsebioscience dataset).
Files are listed in `datalake/omics/list.md`

### prior
*Prior*
Curated reference files: immune cell type marker genes (major + minor levels) and a list of 1,638 human transcription factors.  
Files are listed in `datalake/prior/list.md`

### omnipath
*OmniPath*
Signaling network data pulled from the OmniPath REST API. Covers directed protein interactions, kinase-substrate phosphorylation edges, ligand-receptor interactions, intercellular role annotations, and DoRothEA TF regulons.  
Files are listed in `datalake/omnipath/list.md`

### biomni
*Biomni*
Large collection of general biomedical reference databases sourced from Biomni: drug binding affinities, CRISPR gene effect screens, gene-disease associations, protein-protein interactions, GWAS, gene sets (MSigDB, MouseMine, GO), TCR sequences, miRNA targets, and more.  
Files are listed in `datalake/biomni/list.md`

### virtualbiotech
*VirtualBiotech*
Data from the Virtual Biotech study (bioRxiv 2024, harrisongzhang/TheVirtualBiotech). Contains single-cell expression features for 1,511 human target genes (tau, bimodality, AE-risk scores derived from Tabula Sapiens), ChEMBL clinical trial–target–disease mappings, and LLM-labelled outcomes for 56,707 clinical trials.  
Files are listed in `datalake/virtualbiotech/list.md`

### dice
*DICE*
Gene expression (TPM) and cis-eQTL data across 15 primary human immune cell subtypes from 91 healthy donors (Schmiedel et al. 2018, *Cell*). Cell types cover the full T cell compartment (naive CD4/CD8, activated, Th1/2/17/Tfh/Treg) plus B cells, NK cells, and monocytes. eQTLs provide cell-type-specific causal regulatory anchors; resting vs. activated pairs provide built-in perturbation comparisons for TCR activation programs.  
Files are listed in `datalake/dice/list.md`

### kg
*Knowledge graphs*
Large-scale knowledge graphs for biomedical reasoning and drug repurposing. Currently contains PrimeKG (Chandak et al. 2023, *Scientific Data*), a multiplex knowledge graph integrating 20 databases across 10 biological scales: genes/proteins, drugs, diseases, phenotypes, pathways, GO terms, anatomy, and exposures. 8.1M edges.  
Files are listed in `datalake/kg/list.md`

### nichenet
*NicheNet*
NicheNet v2 prior model networks (Browaeys et al. 2020, *Nature Methods*; Zenodo doi:10.5281/zenodo.7074291). General-purpose cell-cell communication tool providing empirically calibrated edge weights connecting extracellular ligands end-to-end to target gene expression via intracellular signaling and TF regulation. Contains ligand-receptor pairs (4,986), weighted signaling network (3.9M edges), weighted gene regulatory network (4.6M edges), ligand→TF matrix (33K×1.2K), and ligand→target matrix (34M long-format rows). Files available as both `.rds` (original R) and `.parquet` (Python-ready).  
Files are listed in `datalake/nichenet/list.md`



