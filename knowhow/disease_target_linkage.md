Disease target discovery
The aim is to identify targets that play a causal role in disease pathology and are amenable to drug development. 
Causality of the target:
This highly depend on the available datasets and known biology of the disease. Common approach could include:
    -> genetic association studies (GWAS) to find genes associated with disease risk
    -> transcriptomic/proteomic analysis to find genes/proteins that are differentially expressed
    -> functional genomics screens (CRISPR, RNAi) to find genes that affect disease-relevant phenotypes
    -> multiomics integration to provide a more comprehensive view of the disease mechanisms and identify key drivers


an effective target treats the disease and does not cause side effects
two overal appraoches 
    -> ommics aprpaoch to find signature of aging
    -> targetted expression measurements (protein expression in clinical samples)
target related safety:
    -> pathways that are known to be safe 
    -> (evolutionary conservation) animal models/organoid models
    -> tissue specificalty of the expression of the target
technical feasibility of drug development:
    -> druggability 
    -> target family (member of a protein familty that is well established)
    -> drug with clear clinical biomarker


## OpenGWAS PheWAS (UK Biobank + published GWAS)
OpenGWAS (MRC IEU) indexes >10,000 GWAS studies including the full Neale Lab UKB (~4,000 phenotypes)
and Pan-UKBB (~7,200 phenotypes). Use this to look up SNPs across all phenotypes (PheWAS).

API: https://api.opengwas.io/api/
Auth: JWT token stored in agentic_immunology/.env as OPENGWAS_TOKEN
      Token must be passed as header: "X-Api-Token: <token>"
      Free registration at https://api.opengwas.io/ (token expires ~2 weeks)

Key endpoints:
  POST /associations  - body: {"variant_id": ["rsXXX", ...], "pval": 5e-8}
                        Returns all associations across all indexed GWAS studies
  GET  /gwasinfo       - list all available studies with metadata

UKB study ID prefixes in OpenGWAS:
  ukb-b-*   Neale Lab UKB GWAS (binary + continuous traits)
  ukb-d-*   IEU UKB GWAS (ICD10 disease endpoints)
  ieu-b-*   IEU curated studies

Batch query: send up to ~100 SNPs per POST request; use pval threshold to limit results.
Python snippet:
    import requests, json, os
    from dotenv import load_dotenv
    load_dotenv('agentic_immunology/.env')
    token = os.environ['OPENGWAS_TOKEN']
    r = requests.post('https://api.opengwas.io/api/associations',
                      headers={'X-Api-Token': token, 'Content-Type': 'application/json'},
                      json={'variant_id': snp_list, 'pval': 5e-8})
    hits = r.json()
