# Tools — Overview


```python
import sys
sys.path.insert(0, '/vol/projects/BIIM/agentic_central/tools/{biomni or ciim}/code')
from <module_name> import <function_name>   
```

Two major modules: biomni, ciim



## biomni

### `database_biomni`
*Biomedical DB APIs*

Queries 30+ biomedical REST APIs using natural language or direct endpoints. → [database_biomni.md](tools/biomni/database_biomni.md)

`query_uniprot` · `query_alphafold` · `query_interpro` · `query_pdb` · `query_pdb_identifiers` · `query_kegg` · `query_stringdb` · `query_iucn` · `query_paleobiology` · `query_jaspar` · `query_worms` · `query_cbioportal` · `query_clinvar` · `query_geo` · `query_dbsnp` · `query_ucsc` · `query_ensembl` · `query_opentarget` · `query_monarch` · `query_openfda` · `query_gwas_catalog` · `query_gnomad` · `blast_sequence` · `query_reactome` · `query_regulomedb` · `query_pride` · `query_gtopdb` · `query_remap` · `query_mpd` · `query_emdb` · `query_synapse` · `query_pubchem` · `query_chembl` · `query_unichem` · `query_clinicaltrials` · `query_dailymed` · `query_quickgo` · `query_encode` · `region_to_ccre_screen` · `get_genes_near_ccre`

---

### `genetics_biomni`
*Genetics & CRISPR*

Liftover, fine-mapping, CRISPR analysis, TF binding site identification, phylogenetic analysis. → [genetics_biomni.md](tools/biomni/genetics_biomni.md)

`liftover_coordinates` · `bayesian_finemapping_with_deep_vi` · `analyze_cas9_mutation_outcomes` · `analyze_crispr_genome_editing` · `simulate_demographic_history` · `identify_transcription_factor_binding_sites` · `fit_genomic_prediction_model` · `perform_pcr_and_gel_electrophoresis` · `analyze_protein_phylogeny`

---

### `genomics_biomni`
*Single-Cell Genomics*

scRNA-seq cell type annotation, batch integration, gene set enrichment, ChIP-seq, embeddings. → [genomics_biomni.md](tools/biomni/genomics_biomni.md)

`annotate_celltype_scRNA` · `annotate_celltype_with_panhumanpy` · `create_scvi_embeddings_scRNA` · `create_harmony_embeddings_scRNA` · `get_uce_embeddings_scRNA` · `map_to_ima_interpret_scRNA` · `get_rna_seq_archs4` · `get_gene_set_enrichment_analysis_supported_database_list` · `gene_set_enrichment_analysis` · `analyze_chromatin_interactions` · `analyze_comparative_genomics_and_haplotypes` · `perform_chipseq_peak_calling_with_macs2` · `find_enriched_motifs_with_homer` · `analyze_genomic_region_overlap` · `unsupervised_celltype_transfer_between_scRNA_datasets` · `generate_embeddings_with_state` · `interspecies_gene_conversion` · `generate_gene_embeddings_with_ESM_models` · `generate_transcriptformer_embeddings` · `infer_grn_spearman` · `qc_sc_transcriptomics`

---

### `immunology_biomni`
*Immunology Assays*

ATAC-seq, immune cell phenotyping, cytokine assays, flow cytometry, histology. → [immunology_biomni.md](tools/biomni/immunology_biomni.md)

`analyze_atac_seq_differential_accessibility` · `analyze_bacterial_growth_curve` · `isolate_purify_immune_cells` · `estimate_cell_cycle_phase_durations` · `track_immune_cells_under_flow` · `analyze_cfse_cell_proliferation` · `analyze_cytokine_production_in_cd4_tcells` · `analyze_ebv_antibody_titers` · `analyze_cns_lesion_histology` · `analyze_immunohistochemistry_image`

---

### `literature_biomni`
*Literature Search*

PubMed/arXiv/Scholar search, paper/supplementary retrieval, web search, PDF extraction. → [literature_biomni.md](tools/biomni/literature_biomni.md)

`fetch_supplementary_info_from_doi` · `query_arxiv` · `query_scholar` · `query_pubmed` · `search_google` · `extract_url_content` · `extract_pdf_content` · `advanced_web_search_claude`

---

### `pharmacology_biomni`
*Drug & Pharmacology*

Molecular docking (DiffDock, Vina), ADMET prediction, drug-drug interactions (DDInter), FDA data, drug repurposing (TxGNN). → [pharmacology_biomni.md](tools/biomni/pharmacology_biomni.md)

`run_diffdock_with_smiles` · `docking_autodock_vina` · `run_autosite` · `retrieve_topk_repurposing_drugs_from_disease_txgnn` · `predict_admet_properties` · `predict_binding_affinity_protein_1d_sequence` · `analyze_accelerated_stability_of_pharmaceutical_formulations` · `run_3d_chondrogenic_aggregate_assay` · `grade_adverse_events_using_vcog_ctcae` · `analyze_radiolabeled_antibody_biodistribution` · `estimate_alpha_particle_radiotherapy_dosimetry` · `perform_mwas_cyp2c19_metabolizer_status` · `calculate_physicochemical_properties` · `analyze_xenograft_tumor_growth_inhibition` · `analyze_pixel_distribution` · `find_roi_from_image` · `analyze_western_blot` · `query_drug_interactions` · `check_drug_combination_safety` · `analyze_interaction_mechanisms` · `find_alternative_drugs_ddinter` · `query_fda_adverse_events` · `get_fda_drug_label_info` · `check_fda_drug_recalls` · `analyze_fda_safety_signals`

---

## CIIM

### `genomics`
*Genomics*

Raw counts detection, CellTypist annotation, ULM annotation, GRN loader & inference, scRNA QC, annotation quality, TF activity inference. → [genomics.md](tools/ciim/genomics.md)

`identify_counts_layer` · `annotate_celltype_celltypist` · `annotate_celltype_ulm` · `get_immune_grn` · `infer_grn_spearman` · `qc_sc_transcriptomics` · `analyze_cluster_celltype_annotation_quality` · `infer_tf_activity`

---

### `hiara`
*HIaRA*

GRN-based immune age prediction (CD4T/CD8T) and unified loader for all immune signatures (aging, SLE, drug, cytokine). → [hiara.md](tools/ciim/hiara.md)

`predict_immune_age_grn_clock` · `retrieve_summary_stats`

