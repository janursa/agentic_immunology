# Pharmacology — Function Reference

> Module: `tool.pharmacology`
> Import: `from tool.pharmacology import <function_name>`

**25 functions** — DiffDock docking, ADMET prediction, drug scoring, target interaction

```python
import sys
sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools')
from tool.pharmacology import <function_name>
```

---

### `run_diffdock_with_smiles`
Run DiffDock molecular docking using a protein PDB file and a SMILES string for the ligand, executing the process in a Docker container.

**Required:** `pdb_path` (str), `smiles_string` (str), `local_output_dir` (str)
**Optional:** `gpu_device=0` (int), `use_gpu=True` (bool)

### `docking_autodock_vina`
Performs molecular docking using AutoDock Vina to predict binding affinities between small molecules and a receptor protein.

**Required:** `smiles_list` (List[str]), `receptor_pdb_file` (str), `box_center` (List[float]), `box_size` (List[float])
**Optional:** `ncpu=1` (int)

### `run_autosite`
Runs AutoSite on a PDB file to identify potential binding sites and returns a research log with the results.

**Required:** `pdb_file` (str), `output_dir` (str)
**Optional:** `spacing=1.0` (float)

### `retrieve_topk_repurposing_drugs_from_disease_txgnn`
Computes TxGNN model predictions for drug repurposing and returns the top predicted drugs with their scores for a given disease.

**Required:** `disease_name` (str), `data_lake_path` (str)
**Optional:** `k=5` (int)

### `predict_admet_properties`
Predicts ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) properties for a list of compounds using pretrained models.

**Required:** `smiles_list` (List[str])
**Optional:** `ADMET_model_type='MPNN'` (str)

### `predict_binding_affinity_protein_1d_sequence`
Predicts binding affinity between small molecules and a protein sequence using pre-trained deep learning models.

**Required:** `smiles_list` (List[str]), `amino_acid_sequence` (str)
**Optional:** `affinity_model_type='MPNN-CNN'` (str)

### `analyze_accelerated_stability_of_pharmaceutical_formulations`
Analyzes the stability of pharmaceutical formulations under accelerated storage conditions.

**Required:** `formulations` (List[dict]), `storage_conditions` (List[dict]), `time_points` (List[int])
**Optional:** —

### `run_3d_chondrogenic_aggregate_assay`
Generates a detailed protocol for performing a 3D chondrogenic aggregate culture assay to evaluate compounds' effects on chondrogenesis.

**Required:** `chondrocyte_cells` (dict), `test_compounds` (list of dict)
**Optional:** `culture_duration_days=21` (int), `measurement_intervals=7` (int)

### `grade_adverse_events_using_vcog_ctcae`
Grade and monitor adverse events in animal studies using the VCOG-CTCAE standard.

**Required:** `clinical_data_file` (str)
**Optional:** —

### `analyze_radiolabeled_antibody_biodistribution`
Analyze biodistribution and pharmacokinetic profile of radiolabeled antibodies.

**Required:** `time_points` (List[float] or numpy.ndarray), `tissue_data` (dict)
**Optional:** —

### `estimate_alpha_particle_radiotherapy_dosimetry`
Estimate radiation absorbed doses to tumor and normal organs for alpha-particle radiotherapeutics using the Medical Internal Radiation Dose (MIRD) schema.

**Required:** `biodistribution_data` (dict), `radiation_parameters` (dict)
**Optional:** `output_file='dosimetry_results.csv'` (str)

### `perform_mwas_cyp2c19_metabolizer_status`
Perform a Methylome-wide Association Study (MWAS) to identify CpG sites significantly associated with CYP2C19 metabolizer status.

**Required:** `methylation_data_path` (str), `metabolizer_status_path` (str)
**Optional:** `covariates_path=None` (str), `pvalue_threshold=0.05` (float), `output_file='significant_cpg_sites.csv'` (str)

### `calculate_physicochemical_properties`
Calculate key physicochemical properties of a drug candidate molecule.

**Required:** `smiles_string` (str)
**Optional:** —

### `analyze_xenograft_tumor_growth_inhibition`
Analyze tumor growth inhibition in xenograft models across different treatment groups.

**Required:** `data_path` (str), `time_column` (str), `volume_column` (str), `group_column` (str), `subject_column` (str)
**Optional:** `output_dir='./results'` (str)

### `analyze_pixel_distribution`
Analyze western blot or DNA electrophoresis images and return pixel distribution statistics including intensity statistics, percentiles, and brightness distribution. Use this to determine appropriate threshold values for find_roi_from_image.

**Required:** `image_path` (str)
**Optional:** —

### `find_roi_from_image`
Find the ROIs (regions of interest) of protein bands from a Western blot or DNA electrophoresis image using threshold-based blob detection. Returns annotated image path and list of ROI coordinates. Use analyze_pixel_distribution first to determine appropriate threshold values. The returned ROI list can be converted to target_bands format for analyze_western_blot.

**Required:** `image_path` (str), `lower_threshold` (int), `upper_threshold` (int), `number_of_bands` (int)
**Optional:** `debug=True` (bool)

### `analyze_western_blot`
Performs densitometric analysis of Western blot images to quantify relative protein expression.

**Required:** `blot_image_path` (str), `target_bands` (list of dict), `loading_control_band` (dict), `antibody_info` (dict)
**Optional:** `output_dir='./results'` (str)

### `query_drug_interactions`
Query drug-drug interactions from DDInter database to identify potential interactions, mechanisms, and severity levels between specified drugs.

**Required:** `drug_names` (List[str])
**Optional:** `interaction_types=None` (List[str]), `severity_levels=None` (List[str]), `data_lake_path=None` (str)

### `check_drug_combination_safety`
Analyze safety of a drug combination for potential interactions using DDInter database with comprehensive risk assessment and clinical recommendations.

**Required:** `drug_list` (List[str])
**Optional:** `include_mechanisms=True` (bool), `include_management=True` (bool), `data_lake_path=None` (str)

### `analyze_interaction_mechanisms`
Analyze interaction mechanisms between two specific drugs providing detailed mechanistic insights and clinical significance assessment.

**Required:** `drug_pair` (Tuple[str, str])
**Optional:** `detailed_analysis=True` (bool), `data_lake_path=None` (str)

### `find_alternative_drugs_ddinter`
Find alternative drugs that don't interact with contraindicated drugs using DDInter database for safer therapeutic substitutions.

**Required:** `target_drug` (str), `contraindicated_drugs` (List[str])
**Optional:** `therapeutic_class=None` (str), `data_lake_path=None` (str)

### `query_fda_adverse_events`
Query FDA adverse event reports for specific drugs from the OpenFDA database to identify potential safety signals, reaction patterns, and regulatory intelligence.

**Required:** `drug_name` (str)
**Optional:** `date_range=None` (Tuple[str, str]), `severity_filter=None` (List[str]), `outcome_filter=None` (List[str]), `limit=100` (int)

### `get_fda_drug_label_info`
Retrieve FDA drug label information including indications, contraindications, warnings, and dosage information from the OpenFDA database.

**Required:** `drug_name` (str)
**Optional:** `sections=None` (List[str])

### `check_fda_drug_recalls`
Check for FDA drug recalls and enforcement actions from the OpenFDA database to identify safety concerns and regulatory actions.

**Required:** `drug_name` (str)
**Optional:** `classification=None` (List[str]), `date_range=None` (Tuple[str, str])

### `analyze_fda_safety_signals`
Analyze safety signals across multiple drugs using OpenFDA adverse event data to identify patterns and comparative risk profiles.

**Required:** `drug_list` (List[str])
**Optional:** `comparison_period=None` (Tuple[str, str]), `signal_threshold=2.0` (float)
