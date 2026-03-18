# Genetics — Function Reference

> Module: `biomni.tool.genetics`
> Import: `from biomni.tool.genetics import <function_name>`

**9 functions** — Liftover, fine-mapping, CRISPR analysis, TF binding, PCR simulation

---

### `liftover_coordinates`
Perform liftover of genomic coordinates between hg19 and hg38 formats with detailed intermediate steps.

**Required:** `chromosome` (str), `position` (int), `input_format` (str), `output_format` (str), `data_path` (str)
**Optional:** —

### `bayesian_finemapping_with_deep_vi`
Performs Bayesian fine-mapping from GWAS summary statistics using deep variational inference to compute posterior inclusion probabilities and credible sets for putative causal variants.

**Required:** `gwas_summary_path` (str), `ld_matrix` (numpy.ndarray)
**Optional:** `n_iterations=5000` (int), `learning_rate=0.01` (float), `hidden_dim=64` (int), `credible_threshold=0.95` (float)

### `analyze_cas9_mutation_outcomes`
Analyzes and categorizes mutations induced by Cas9 at target sites.

**Required:** `reference_sequences` (dict), `edited_sequences` (dict)
**Optional:** `cell_line_info=None` (dict), `output_prefix='cas9_mutation_analysis'` (str)

### `analyze_crispr_genome_editing`
Analyzes CRISPR-Cas9 genome editing results by comparing original and edited sequences.

**Required:** `original_sequence` (str), `edited_sequence` (str), `guide_rna` (str)
**Optional:** `repair_template=None` (str)

### `simulate_demographic_history`
Simulate DNA sequences with specified demographic and coalescent histories using msprime.

**Required:** —
**Optional:** `num_samples=10` (int), `sequence_length=100000` (int), `recombination_rate=1e-08` (float), `mutation_rate=1e-08` (float), `demographic_model='constant'` (str), `demographic_params=None` (dict), `coalescent_model='kingman'` (str), `beta_coalescent_param=None` (float), `random_seed=None` (int), `output_file='simulated_sequences.vcf'` (str)

### `identify_transcription_factor_binding_sites`
Identifies binding sites for a specific transcription factor in a genomic sequence.

**Required:** `sequence` (str), `tf_name` (str)
**Optional:** `threshold=0.8` (float), `output_file=None` (str)

### `fit_genomic_prediction_model`
Fit a linear mixed model for genomic prediction using genotype and phenotype data.

**Required:** `genotypes` (numpy.ndarray), `phenotypes` (numpy.ndarray)
**Optional:** `fixed_effects=None` (numpy.ndarray), `model_type='additive'` (str), `output_file='genomic_prediction_results.csv'` (str)

### `perform_pcr_and_gel_electrophoresis`
Performs PCR amplification of a target transgene and visualizes results using agarose gel electrophoresis.

**Required:** `genomic_dna` (str)
**Optional:** `forward_primer=None` (str), `reverse_primer=None` (str), `target_region=None` (tuple), `annealing_temp=58` (float), `extension_time=30` (int), `cycles=35` (int), `gel_percentage=2.0` (float), `output_prefix='pcr_result'` (str)

### `analyze_protein_phylogeny`
Perform phylogenetic analysis on a set of protein sequences. This function aligns sequences, constructs a phylogenetic tree, and visualizes evolutionary relationships.

**Required:** `fasta_sequences` (str)
**Optional:** `output_dir='./'` (str), `alignment_method='clustalw'` (str), `tree_method='fasttree'` (str)
