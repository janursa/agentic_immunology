# Database — Function Reference

> Module: `tool.database`
> Import: `from tool.database import <function_name>`

**40 functions** — UniProt, GWAS Catalog, Ensembl, ClinVar, dbSNP, GnomAD, GEO, PubChem, DrugBank


---

### `query_uniprot`
*UniProt Query*
Query the UniProt REST API using either natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=5` (int)

### `query_alphafold`
*AlphaFold Structures*
Query the AlphaFold Database API for protein structure predictions or metadata; optionally download structures.

**Required:** `uniprot_id` (str)
**Optional:** `endpoint='prediction'` (str), `residue_range=None` (str), `download=False` (bool), `output_dir=None` (str), `file_format='pdb'` (str), `model_version='v4'` (str), `model_number=1` (int)

### `query_interpro`
*InterPro Domains*
Query the InterPro REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=3` (int)

### `query_pdb`
*PDB Structure Search*
Query the RCSB PDB database using natural language or a direct structured query.

**Required:** `prompt` (str)
**Optional:** `query=None` (dict), `max_results=3` (int)

### `query_pdb_identifiers`
*PDB Data Retrieval*
Retrieve detailed data and/or download files for PDB identifiers.

**Required:** `identifiers` (List[str])
**Optional:** `return_type='entry'` (str), `download=False` (bool), `attributes=None` (List[str])

### `query_kegg`
*KEGG Pathways*
Take a natural language prompt and convert it to a structured KEGG API query.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_stringdb`
*STRING Interactions*
Query the STRING protein interaction database using natural language or direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `download_image=False` (bool), `output_dir=None` (str), `verbose=True` (bool)

### `query_iucn`
*IUCN Red List*
Query the IUCN Red List API using natural language or a direct endpoint.

**Required:** `token` (str)
**Optional:** `prompt=None` (str), `endpoint=None` (str), `verbose=True` (bool)

### `query_paleobiology`
*Paleobiology DB*
Query the Paleobiology Database (PBDB) API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_jaspar`
*JASPAR TF Profiles*
Query the JASPAR REST API for transcription factor binding profiles.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_worms`
*Marine Species DB*
Query the World Register of Marine Species (WoRMS) REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_cbioportal`
*cBioPortal Cancer*
Query the cBioPortal REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_clinvar`
*ClinVar Variants*
Convert a natural language prompt into a structured ClinVar search query and run it.

**Required:** `prompt` (str)
**Optional:** `search_term=None` (str), `max_results=3` (int)

### `query_geo`
*GEO Expression DB*
Query the NCBI GEO database (GDS/GEOPROFILES) using natural language or direct search term.

**Required:** `prompt` (str)
**Optional:** `search_term=None` (str), `max_results=3` (int)

### `query_dbsnp`
*dbSNP Variants*
Query the NCBI dbSNP database using natural language or direct search term.

**Required:** `prompt` (str)
**Optional:** `search_term=None` (str), `max_results=3` (int)

### `query_ucsc`
*UCSC Genome Browser*
Query the UCSC Genome Browser API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_ensembl`
*Ensembl REST API*
Query the Ensembl REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_opentarget`
*OpenTargets Platform*
Query the OpenTargets Platform API using natural language or a direct GraphQL query.

**Required:** `prompt` (str)
**Optional:** `query=None` (str), `variables=None` (dict), `verbose=False` (bool)

### `query_monarch`
*Monarch Disease DB*
Query the Monarch Initiative API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=2` (int), `verbose=False` (bool)

### `query_openfda`
*OpenFDA Drug Data*
Query the OpenFDA API using natural language or direct parameters.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=100` (int), `verbose=True` (bool), `search_params=None` (dict), `sort_params=None` (dict), `count_params=None` (str), `skip_results=0` (int)

### `query_gwas_catalog`
*GWAS Catalog*
Query the GWAS Catalog API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=3` (int)

### `query_gnomad`
*GnomAD Variants*
Query gnomAD for variants in a gene using natural language or direct gene symbol.

**Required:** `prompt` (str)
**Optional:** `gene_symbol=None` (str), `verbose=True` (bool)

### `blast_sequence`
*NCBI BLAST Search*
Identify a DNA or protein sequence using NCBI BLAST.

**Required:** `sequence` (str), `database` (str), `program` (str)
**Optional:** —

### `query_reactome`
*Reactome Pathways*
Query the Reactome database using natural language or a direct endpoint; optionally download pathway diagrams.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `download=False` (bool), `output_dir=None` (str), `verbose=True` (bool)

### `query_regulomedb`
*RegulomeDB Elements*
Query the RegulomeDB database using natural language or direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=False` (bool)

### `query_pride`
*PRIDE Proteomics*
Query the PRIDE proteomics database using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=3` (int)

### `query_gtopdb`
*GtoPdb Pharmacology*
Query the Guide to PHARMACOLOGY (GtoPdb) database using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_remap`
*ReMap TF Binding*
Query the ReMap database for regulatory elements and transcription factor binding.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_mpd`
*Mouse Phenome DB*
Query the Mouse Phenome Database (MPD) using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_emdb`
*EMDB Cryo-EM*
Query the Electron Microscopy Data Bank (EMDB) using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_synapse`
*Synapse Datasets*
Query Synapse REST API for biomedical datasets/files using natural language or structured search parameters. Supports optional authentication via SYNAPSE_AUTH_TOKEN.

**Required:** `prompt` (str)
**Optional:** `query_term=None` (str|list[str]), `return_fields=['name', 'node_type', 'description']` (list[str]), `max_results=20` (int), `query_type='dataset'` (str), `verbose=True` (bool)

### `query_pubchem`
*PubChem Compounds*
Query the PubChem PUG-REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=5` (int), `verbose=True` (bool)

### `query_chembl`
*ChEMBL Drug DB*
Query the ChEMBL REST API via natural language, direct endpoint, or identifiers (chembl_id, smiles, molecule_name).

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `chembl_id=None` (str), `smiles=None` (str), `molecule_name=None` (str), `max_results=20` (int), `verbose=True` (bool)

### `query_unichem`
*UniChem Cross-Refs*
Query the UniChem 2.0 REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_clinicaltrials`
*Clinical Trials DB*
Query the ClinicalTrials.gov API v2 using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=10` (int), `verbose=True` (bool)

### `query_dailymed`
*DailyMed Drug Labels*
Query the DailyMed RESTful API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `format='json'` (str), `verbose=True` (bool)

### `query_quickgo`
*QuickGO Ontology*
Query the QuickGO API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=25` (int), `verbose=True` (bool)

### `query_encode`
*ENCODE Genomics*
Query the ENCODE Portal API to locate functional genomics data (experiments, files, biosamples, datasets).

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=25` (int|str), `verbose=True` (bool)

### `region_to_ccre_screen`
*SCREEN cCRE Regions*
Given genomic coordinates, retrieve intersecting ENCODE SCREEN cCREs.

**Required:** `coord_chrom` (str), `coord_start` (int), `coord_end` (int)
**Optional:** `assembly='GRCh38'` (str)

### `get_genes_near_ccre`
*Genes Near cCRE*
Given a cCRE accession, return k nearest genes sorted by distance.

**Required:** `accession` (str), `assembly` (str), `chromosome` (str)
**Optional:** `k=10` (int)
