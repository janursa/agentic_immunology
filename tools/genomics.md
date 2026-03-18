# Genomics — Function Reference

### `annotate_celltype_scRNA`
Annotate cell types based on gene markers and transferred labels using LLM. After leiden clustering, annotate clusters using differentially expressed genes and optionally incorporate transferred labels from reference datasets.

**Required:** `adata_filename` (str), `data_dir` (str), `data_info` (str), `data_lake_path` (str)
**Optional:** `cluster='leiden'` (str), `llm='claude-3-5-sonnet-20241022'` (str), `composition=None` (pd.DataFrame)

### `annotate_celltype_with_panhumanpy`
Perform cell type annotation of single-cell RNA-seq data using Panhuman Azimuth Neural Network. This function implements the Panhuman Azimuth workflow for cell type annotation using the panhumanpy package, providing hierarchical cell type labels for tissues across the human body. 

**Required:** `adata_path` (str)
**Optional:** `feature_names_col=None` (str), `refine=True` (bool), `umap=True` (bool), `output_dir='./output'` (str)

### `create_scvi_embeddings_scRNA`
Create scVI and scANVI embeddings for single-cell RNA-seq data, saving the results to an AnnData object.

**Required:** `adata_filename` (str), `batch_key` (str), `label_key` (str), `data_dir` (str)
**Optional:** —

### `create_harmony_embeddings_scRNA`
Performs batch integration on single-cell RNA-seq data using Harmony and saves the integrated embeddings.

**Required:** `adata_filename` (str), `batch_key` (str), `data_dir` (str)
**Optional:** —

### `get_uce_embeddings_scRNA`
Generate UCE embeddings for single-cell RNA-seq data and map them to a reference dataset for cell type annotation.

**Required:** `adata_filename` (str), `data_dir` (str)
**Optional:** `DATA_ROOT='/dfs/project/bioagentos/data/singlecell/'` (str), `custom_args=None` (List[str])

### `map_to_ima_interpret_scRNA`
Map cell embeddings from the input dataset to the Integrated Megascale Atlas reference dataset using UCE embeddings.

**Required:** `adata_filename` (str), `data_dir` (str)
**Optional:** `custom_args=None` (dict)

### `get_rna_seq_archs4`
Given a gene name, fetch RNA-seq expression data showing the top K tissues with highest transcripts-per-million (TPM) values.

**Required:** `gene_name` (str)
**Optional:** `K=10` (int)

### `get_gene_set_enrichment_analysis_supported_database_list`
Returns a list of supported databases for gene set enrichment analysis.

**Required:** —
**Optional:** —

### `gene_set_enrichment_analysis`
Perform enrichment analysis for a list of genes, with optional background gene set and plotting functionality.

**Required:** `genes` (list)
**Optional:** `top_k=10` (int), `database='ontology'` (str), `background_list=None` (list), `plot=False` (bool)

### `analyze_chromatin_interactions`
Analyze chromatin interactions from Hi-C data to identify enhancer-promoter interactions and TADs.

**Required:** `hic_file_path` (str), `regulatory_elements_bed` (str)
**Optional:** `output_dir='./output'` (str)

### `analyze_comparative_genomics_and_haplotypes`
Perform comparative genomics and haplotype analysis on multiple genome samples. Aligns genome samples to a reference, identifies variants, analyzes shared and unique genomic regions, and determines haplotype structure.

**Required:** `sample_fasta_files` (List[str]), `reference_genome_path` (str)
**Optional:** `output_dir='./output'` (str)

### `perform_chipseq_peak_calling_with_macs2`
Perform ChIP-seq peak calling using MACS2 to identify genomic regions with significant binding.

**Required:** `chip_seq_file` (str), `control_file` (str)
**Optional:** `output_name='macs2_output'` (str), `genome_size='hs'` (str), `q_value=0.05` (float)

### `find_enriched_motifs_with_homer`
Find DNA sequence motifs enriched in genomic regions using the HOMER motif discovery software.

**Required:** `peak_file` (str)
**Optional:** `genome='hg38'` (str), `background_file=None` (str), `motif_length='8,10,12'` (str), `output_dir='./homer_motifs'` (str), `num_motifs=10` (int), `threads=4` (int)

### `analyze_genomic_region_overlap`
Analyze overlaps between two or more sets of genomic regions.

**Required:** `region_sets` (list)
**Optional:** `output_prefix='overlap_analysis'` (str)

### `unsupervised_celltype_transfer_between_scRNA_datasets`
Transfer cell type labels from an annotated reference scRNA-seq dataset to an unannotated query dataset using popV. Loads both AnnData .h5ad files, prepares count layers for scVI, processes the query against the reference, and runs selected annotation methods (default: SCANVI_POPV). Saves predictions to 'output_folder/popv_output/predictions.csv'. This function allows you to use different annotaiton methods i.e. CELLTYPIST, KNN_BBKNN, KNN_HARMONY, KNN_SCANORAMA, KNN_SCVI, ONCLASS, Random_Forest, SCANVI_POPV, Support_Vector, XGboost. Based on you transfer task you can select the multiple best annotation methods. Beware each annotation method adds computational requirements for running the tool. By default it uses SCANVI_POPV method.

**Required:** `path_to_annotated_h5ad` (str), `path_to_not_annotated_h5ad` (str), `ref_labels_key` (str)
**Optional:** `query_batch_key=None` (str), `ref_batch_key=None` (str), `CELLTYPIST=False` (bool), `KNN_BBKNN=False` (bool), `KNN_HARMONY=False` (bool), `KNN_SCANORAMA=False` (bool), `KNN_SCVI=False` (bool), `ONCLASS=False` (bool), `Random_Forest=False` (bool), `SCANVI_POPV=True` (bool), `Support_Vector=False` (bool), `XGboost=False` (bool), `n_jobs=1` (int), `output_folder='./tmp/'` (str), `n_samples_per_label=10` (int)

### `generate_embeddings_with_state`
Generate State embeddings for single-cell RNA-seq data using the SE-600M model. This function downloads the SE-600M model from Hugging Face, installs required dependencies (git-lfs, uv, arc-state), and generates embeddings for the input AnnData object. The SE-600M model is a state-of-the-art embedding model for single-cell data that can capture complex biological patterns and cell states. Features include real-time streaming output, automatic retry with reduced batch size on failure, GPU detection and warnings, and input validation.

**Required:** `adata_filename` (str), `data_dir` (str), `model_folder` (str)
**Optional:** `output_filename=None` (str), `checkpoint=None` (str), `embed_key='X_state'` (str), `protein_embeddings=None` (str), `batch_size=500` (int)

### `interspecies_gene_conversion`
Convert ENSEMBL gene IDs between different species using BioMart homology mapping. This function converts a list of ENSEMBL gene IDs from one species to their homologous counterparts in another species using the Ensembl BioMart database. The conversion is based on one-to-one ortholog mappings between species.

**Required:** `gene_list` (list[str]), `source_species` (str), `target_species` (str)
**Optional:** —

### `generate_gene_embeddings_with_ESM_models`
Generate average protein embeddings for a list of Ensembl gene IDs using ESM (Evolutionary Scale Modeling) protein language models. This function fetches all protein isoform sequences for each gene, computes embeddings for each isoform using the specified ESM model and layer, then averages the embeddings across all isoforms to create a single representative embedding per gene. The embeddings are saved as PyTorch tensors for future use. Memory-friendly implementation with rolling averages, small batch processing, and automatic memory management. Automatically handles GPU/CPU device selection and includes error recovery for out-of-memory situations by falling back to single-sequence processing.

**Required:** `ensembl_gene_ids` (List[str])
**Optional:** `model_name='esm2_t6_8M_UR50D'` (str), `layer=6` (int), `save_path=None` (str), `batch_size=1` (int), `max_sequence_length=1024` (int)

### `generate_transcriptformer_embeddings`
Generate Transcriptformer embeddings for single-cell RNA-seq data. This function downloads model checkpoints, prepares the AnnData object with required fields (ensembl_id, raw counts, assay metadata), and runs inference to generate cell or gene embeddings. Transcriptformer is a transformer-based model that can learn rich representations of single-cell gene expression data. The function automatically handles Ensembl ID pattern detection, model downloading, data preprocessing, and creates missing assay metadata columns with 'unknown' values if needed.

**Required:** `adata_filename` (str), `data_dir` (str)
**Optional:** `output_filename=None` (str), `model_type='tf-sapiens'` (str), `checkpoint_path=None` (str), `batch_size=8` (int), `precision='16-mixed'` (str), `clip_counts=30` (int), `embedding_layer_index=-1` (int), `num_gpus=1` (int), `n_data_workers=0` (int), `gene_col_name='ensembl_id'` (str), `pretrained_embedding=None` (str), `filter_to_vocabs=True` (bool), `use_raw='None'` (str), `emb_type='cell'` (str), `remove_duplicate_genes=False` (bool), `oom_dataloader=False` (bool)
