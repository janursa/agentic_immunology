# Database — Function Reference

> Module: `tool.database`
> Import: `from tool.database import <function_name>`

**40 functions** — UniProt, GWAS Catalog, Ensembl, ClinVar, dbSNP, GnomAD, GEO, PubChem, DrugBank

```python
import sys
sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools')
from tool.database import <function_name>
```

---

### `query_uniprot`
Query the UniProt REST API using either natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=5` (int)

### `query_alphafold`
Query the AlphaFold Database API for protein structure predictions or metadata; optionally download structures.

**Required:** `uniprot_id` (str)
**Optional:** `endpoint='prediction'` (str), `residue_range=None` (str), `download=False` (bool), `output_dir=None` (str), `file_format='pdb'` (str), `model_version='v4'` (str), `model_number=1` (int)

### `query_interpro`
Query the InterPro REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=3` (int)

### `query_pdb`
Query the RCSB PDB database using natural language or a direct structured query.

**Required:** `prompt` (str)
**Optional:** `query=None` (dict), `max_results=3` (int)

### `query_pdb_identifiers`
Retrieve detailed data and/or download files for PDB identifiers.

**Required:** `identifiers` (List[str])
**Optional:** `return_type='entry'` (str), `download=False` (bool), `attributes=None` (List[str])

### `query_kegg`
Take a natural language prompt and convert it to a structured KEGG API query.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_stringdb`
Query the STRING protein interaction database using natural language or direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `download_image=False` (bool), `output_dir=None` (str), `verbose=True` (bool)

### `query_iucn`
Query the IUCN Red List API using natural language or a direct endpoint.

**Required:** `token` (str)
**Optional:** `prompt=None` (str), `endpoint=None` (str), `verbose=True` (bool)

### `query_paleobiology`
Query the Paleobiology Database (PBDB) API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_jaspar`
Query the JASPAR REST API for transcription factor binding profiles.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_worms`
Query the World Register of Marine Species (WoRMS) REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_cbioportal`
Query the cBioPortal REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_clinvar`
Convert a natural language prompt into a structured ClinVar search query and run it.

**Required:** `prompt` (str)
**Optional:** `search_term=None` (str), `max_results=3` (int)

### `query_geo`
Query the NCBI GEO database (GDS/GEOPROFILES) using natural language or direct search term.

**Required:** `prompt` (str)
**Optional:** `search_term=None` (str), `max_results=3` (int)

### `query_dbsnp`
Query the NCBI dbSNP database using natural language or direct search term.

**Required:** `prompt` (str)
**Optional:** `search_term=None` (str), `max_results=3` (int)

### `query_ucsc`
Query the UCSC Genome Browser API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_ensembl`
Query the Ensembl REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_opentarget`
Query the OpenTargets Platform API using natural language or a direct GraphQL query.

**Required:** `prompt` (str)
**Optional:** `query=None` (str), `variables=None` (dict), `verbose=False` (bool)

### `query_monarch`
Query the Monarch Initiative API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=2` (int), `verbose=False` (bool)

### `query_openfda`
Query the OpenFDA API using natural language or direct parameters.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=100` (int), `verbose=True` (bool), `search_params=None` (dict), `sort_params=None` (dict), `count_params=None` (str), `skip_results=0` (int)

### `query_gwas_catalog`
Query the GWAS Catalog API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=3` (int)

### `query_gnomad`
Query gnomAD for variants in a gene using natural language or direct gene symbol.

**Required:** `prompt` (str)
**Optional:** `gene_symbol=None` (str), `verbose=True` (bool)

### `blast_sequence`
Identify a DNA or protein sequence using NCBI BLAST.

**Required:** `sequence` (str), `database` (str), `program` (str)
**Optional:** —

### `query_reactome`
Query the Reactome database using natural language or a direct endpoint; optionally download pathway diagrams.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `download=False` (bool), `output_dir=None` (str), `verbose=True` (bool)

### `query_regulomedb`
Query the RegulomeDB database using natural language or direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=False` (bool)

### `query_pride`
Query the PRIDE proteomics database using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=3` (int)

### `query_gtopdb`
Query the Guide to PHARMACOLOGY (GtoPdb) database using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_remap`
Query the ReMap database for regulatory elements and transcription factor binding.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_mpd`
Query the Mouse Phenome Database (MPD) using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_emdb`
Query the Electron Microscopy Data Bank (EMDB) using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_synapse`
Query Synapse REST API for biomedical datasets/files using natural language or structured search parameters. Supports optional authentication via SYNAPSE_AUTH_TOKEN.

**Required:** `prompt` (str)
**Optional:** `query_term=None` (str|list[str]), `return_fields=['name', 'node_type', 'description']` (list[str]), `max_results=20` (int), `query_type='dataset'` (str), `verbose=True` (bool)

### `query_pubchem`
Query the PubChem PUG-REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=5` (int), `verbose=True` (bool)

### `query_chembl`
Query the ChEMBL REST API via natural language, direct endpoint, or identifiers (chembl_id, smiles, molecule_name).

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `chembl_id=None` (str), `smiles=None` (str), `molecule_name=None` (str), `max_results=20` (int), `verbose=True` (bool)

### `query_unichem`
Query the UniChem 2.0 REST API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `verbose=True` (bool)

### `query_clinicaltrials`
Query the ClinicalTrials.gov API v2 using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=10` (int), `verbose=True` (bool)

### `query_dailymed`
Query the DailyMed RESTful API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `format='json'` (str), `verbose=True` (bool)

### `query_quickgo`
Query the QuickGO API using natural language or a direct endpoint.

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=25` (int), `verbose=True` (bool)

### `query_encode`
Query the ENCODE Portal API to locate functional genomics data (experiments, files, biosamples, datasets).

**Required:** `prompt` (str)
**Optional:** `endpoint=None` (str), `max_results=25` (int|str), `verbose=True` (bool)

### `region_to_ccre_screen`
Given genomic coordinates, retrieve intersecting ENCODE SCREEN cCREs.

**Required:** `coord_chrom` (str), `coord_start` (int), `coord_end` (int)
**Optional:** `assembly='GRCh38'` (str)

### `get_genes_near_ccre`
Given a cCRE accession, return k nearest genes sorted by distance.

**Required:** `accession` (str), `assembly` (str), `chromosome` (str)
**Optional:** `k=10` (int)
