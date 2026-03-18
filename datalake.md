

## 📊 Data Lake (76 files)

`DATA_LAKE = '/vol/projects/BIIM/agentic_central/agentic/data_lake'`

```python
import pandas as pd, os, pickle

DATA_LAKE = '/vol/projects/BIIM/agentic_central/agentic/data_lake'

# Parquet
df = pd.read_parquet(os.path.join(DATA_LAKE, '<filename>.parquet'))

# CSV
df = pd.read_csv(os.path.join(DATA_LAKE, '<filename>.csv'))

# Pickle
with open(os.path.join(DATA_LAKE, '<filename>.pkl'), 'rb') as f:
    obj = pickle.load(f)
```

| File | Description |
|------|-------------|
| `affinity_capture-ms.parquet` | Protein-protein interactions detected via affinity capture and mass spectrometry. |
| `affinity_capture-rna.parquet` | Protein-RNA interactions detected by affinity capture. |
| `BindingDB_All_202409.tsv` | Measured binding affinities between proteins and small molecules for drug discovery. |
| `broad_repurposing_hub_molecule_with_smiles.parquet` | Molecules from Broad Institute's Drug Repurposing Hub with SMILES annotations. |
| `broad_repurposing_hub_phase_moa_target_info.parquet` | Drug phases, mechanisms of action, and target information from Broad Institute. |
| `co-fractionation.parquet` | Protein-protein interactions from co-fractionation experiments. |
| `czi_census_datasets_v4.parquet` | Datasets from the Chan Zuckerberg Initiative's Cell Census. |
| `DepMap_CRISPRGeneDependency.csv` | Gene dependency probability estimates for cancer cell lines, including all DepMap models. |
| `DepMap_CRISPRGeneEffect.csv` | Genome-wide CRISPR gene effect estimates for cancer cell lines, including all DepMap models. |
| `DepMap_Model.csv` | Metadata describing all cancer models/cell lines which are referenced by a dataset contained within the DepMap portal. |
| `DepMap_OmicsExpressionProteinCodingGenesTPMLogp1.csv` | Gene expression in TPMs for cancer cell lines, including all DepMap models. |
| `ddinter_alimentary_tract_metabolism.csv` | Drug-drug interactions for alimentary tract and metabolism drugs from DDInter 2.0 database. |
| `ddinter_antineoplastic.csv` | Drug-drug interactions for antineoplastic and immunomodulating agents from DDInter 2.0 database. |
| `ddinter_antiparasitic.csv` | Drug-drug interactions for antiparasitic products from DDInter 2.0 database. |
| `ddinter_blood_organs.csv` | Drug-drug interactions for blood and blood forming organs drugs from DDInter 2.0 database. |
| `ddinter_dermatological.csv` | Drug-drug interactions for dermatological drugs from DDInter 2.0 database. |
| `ddinter_hormonal.csv` | Drug-drug interactions for systemic hormonal preparations from DDInter 2.0 database. |
| `ddinter_respiratory.csv` | Drug-drug interactions for respiratory system drugs from DDInter 2.0 database. |
| `ddinter_various.csv` | Drug-drug interactions for various drugs from DDInter 2.0 database. |
| `DisGeNET.parquet` | Gene-disease associations from multiple sources. |
| `dosage_growth_defect.parquet` | Gene dosage changes affecting growth. |
| `enamine_cloud_library_smiles.pkl` | Compounds from Enamine REAL library with SMILES annotations. |
| `evebio_assay_table.csv` | Assay metadata with one row per assay from EveBio pharmome mapping. |
| `evebio_bundle_table.csv` | Target subfamily bundles used for screening-to-profiling progression. |
| `evebio_compound_table.csv` | Compound metadata with common identifiers from EveBio screening. |
| `evebio_control_table.csv` | Control datapoints for all screening and profiling plates. |
| `evebio_detailed_result_table.csv` | Expanded results on evebio_summary_result_table with curve fit parameters and phase categories. |
| `evebio_observed_points_table.csv` | Raw observed datapoints from all screening and profiling experiments. |
| `evebio_summary_result_table.csv` | Succinct summary of results for each assay-compound combination. |
| `evebio_target_table.csv` | Target metadata with common identifiers from EveBio screening. |
| `genebass_missense_LC_filtered.pkl` | Filtered missense variants from GeneBass. |
| `genebass_pLoF_filtered.pkl` | Predicted loss-of-function variants from GeneBass. |
| `genebass_synonymous_filtered.pkl` | Filtered synonymous variants from GeneBass. |
| `gene_info.parquet` | Comprehensive gene information. |
| `genetic_interaction.parquet` | Genetic interactions between genes. |
| `go-plus.json` | Gene ontology data for functional gene annotations. |
| `gtex_tissue_gene_tpm.parquet` | Gene expression (TPM) across human tissues from GTEx. |
| `gwas_catalog.pkl` | Genome-wide association studies (GWAS) results. |
| `hp.obo` | Official HPO release in obographs format |
| `kg.csv` | Precision medicine knowledge graph with 17,080 diseases and 4+ million relationships across biological scales. |
| `marker_celltype.parquet` | Cell type marker genes for identification. |
| `McPAS-TCR.parquet` | T-cell receptor sequences and specificity data from McPAS database. |
| `miRDB_v6.0_results.parquet` | Predicted microRNA targets from miRDB. |
| `miRTarBase_microRNA_target_interaction.parquet` | Experimentally validated microRNA-target interactions from miRTarBase. |
| `miRTarBase_microRNA_target_interaction_pubmed_abtract.txt` | PubMed abstracts for microRNA-target interactions in miRTarBase. |
| `miRTarBase_MicroRNA_Target_Sites.parquet` | Binding sites of microRNAs on target genes from miRTarBase. |
| `mousemine_m1_positional_geneset.parquet` | Positional gene sets from MouseMine. |
| `mousemine_m2_curated_geneset.parquet` | Curated gene sets from MouseMine. |
| `mousemine_m3_regulatory_target_geneset.parquet` | Regulatory target gene sets from MouseMine. |
| `mousemine_m5_ontology_geneset.parquet` | Ontology-based gene sets from MouseMine. |
| `mousemine_m8_celltype_signature_geneset.parquet` | Cell type signature gene sets from MouseMine. |
| `mousemine_mh_hallmark_geneset.parquet` | Hallmark gene sets from MouseMine. |
| `msigdb_human_c1_positional_geneset.parquet` | Human positional gene sets from MSigDB. |
| `msigdb_human_c2_curated_geneset.parquet` | Curated human gene sets from MSigDB. |
| `msigdb_human_c3_regulatory_target_geneset.parquet` | Regulatory target gene sets from MSigDB. |
| `msigdb_human_c3_subset_transcription_factor_targets_from_GTRD.parquet` | Transcription factor targets from GTRD/MSigDB. |
| `msigdb_human_c4_computational_geneset.parquet` | Computationally derived gene sets from MSigDB. |
| `msigdb_human_c5_ontology_geneset.parquet` | Ontology-based gene sets from MSigDB. |
| `msigdb_human_c6_oncogenic_signature_geneset.parquet` | Oncogenic signatures from MSigDB. |
| `msigdb_human_c7_immunologic_signature_geneset.parquet` | Immunologic signatures from MSigDB. |
| `msigdb_human_c8_celltype_signature_geneset.parquet` | Cell type signatures from MSigDB. |
| `msigdb_human_h_hallmark_geneset.parquet` | Hallmark gene sets from MSigDB. |
| `omim.parquet` | Genetic disorders and associated genes from OMIM. |
| `proteinatlas.tsv` | Protein expression data from Human Protein Atlas. |
| `proximity_label-ms.parquet` | Protein interactions via proximity labeling and mass spectrometry. |
| `reconstituted_complex.parquet` | Protein complexes reconstituted in vitro. |
| `sgRNA_KO_SP_mouse.txt` | sgRNA knockout data for mouse. |
| `sgRNA_KO_SP_human.txt` | sgRNA knockout data for human. |
| `synthetic_growth_defect.parquet` | Synthetic growth defects from genetic interactions. |
| `synthetic_lethality.parquet` | Synthetic lethal interactions. |
| `synthetic_rescue.parquet` | Genetic interactions rescuing phenotypes. |
| `two-hybrid.parquet` | Protein-protein interactions detected by yeast two-hybrid assays. |
| `variant_table.parquet` | Annotated genetic variants table. |
| `Virus-Host_PPI_P-HIPSTER_2020.parquet` | Virus-host protein-protein interactions from P-HIPSTER. |
| `txgnn_name_mapping.pkl` | Name mapping for TXGNN. |
| `txgnn_prediction.pkl` | Prediction data for TXGNN. |

---