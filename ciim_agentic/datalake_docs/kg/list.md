# KG -- File List

All files located in `${CIIM_DATALAKE_DIR}/kg/`. Contains large-scale knowledge graphs for biomedical applications.

---

## PrimeKG.csv
**PrimeKG — Precision Medicine Knowledge Graph**  
**Reference**: Chandak et al. 2023, *Scientific Data* (doi:10.1038/s41597-023-01960-3)  
**Source**: Harvard Dataverse (doi:10.7910/DVN/IXA7BM) | **License**: MIT  
**Size**: 8.1M rows | **Build**: December 2023 (includes full OMIM coverage)

A multiplex biomedical knowledge graph integrating 20 high-quality databases across 10 biological scales.

**Columns**: `relation`, `display_relation`, `x_index`, `x_id`, `x_type`, `x_name`, `x_source`, `y_index`, `y_id`, `y_type`, `y_name`, `y_source`

**Node types** (x_type / y_type):

| Node type | Count | Description |
|---|---|---|
| `gene/protein` | 2,631,229 rows | Human genes and proteins (NCBI) |
| `drug` | 2,805,696 rows | Approved + investigational drugs (DrugBank, ChEMBL) |
| `anatomy` | 1,566,154 rows | Anatomical entities (Uberon) |
| `disease` | 341,244 rows | 17,080 diseases (MONDO, OMIM, DOID) |
| `effect/phenotype` | 257,096 rows | HPO phenotype terms |
| `biological_process` | 252,202 rows | GO biological process |
| `molecular_function` | 96,723 rows | GO molecular function |
| `cellular_component` | 93,102 rows | GO cellular component |
| `pathway` | 47,716 rows | Reactome pathways |
| `exposure` | 9,336 rows | Environmental exposures |

**Edge/relation types** (top by frequency):

| Relation | Count | Meaning |
|---|---|---|
| `anatomy_protein_present` | 3,036,406 | Gene expressed in anatomy (GTEx, PROTEOMICS_DB) |
| `drug_drug` | 2,672,628 | Drug-drug interactions (DRUGBANK) |
| `protein_protein` | 642,150 | Protein-protein interactions |
| `disease_phenotype_positive` | 300,634 | Disease → phenotype associations |
| `bioprocess_protein` | 289,610 | GO BP → gene membership |
| `disease_protein` | 160,822 | Disease → gene associations (OMIM, ClinVar, DisGeNET) |
| `drug_effect` | 129,568 | Drug → side effect |
| `drug_protein` | 51,306 | Drug → protein target |
| `indication` | 18,776 | Drug approved indication |
| `contraindication` | 61,350 | Drug contraindication |

**Primary use cases**:
- Drug repurposing via GNN link prediction
- Disease–gene–drug path traversal
- Multi-hop reasoning across biological scales (e.g., gene → disease → drug → side effect)
