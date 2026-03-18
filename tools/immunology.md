# Immunology — Function Reference

> Module: `biomni.tool.immunology`
> Import: `from biomni.tool.immunology import <function_name>`

**10 functions** — ATAC-seq, TCR/BCR analysis, immune cell phenotyping, cytokine modeling

---

### `analyze_atac_seq_differential_accessibility`
Perform ATAC-seq peak calling and differential accessibility analysis using MACS2.

**Required:** `treatment_bam` (str), `control_bam` (str)
**Optional:** `output_dir='./atac_results'` (str), `genome_size='hs'` (str), `q_value=0.05` (float), `name_prefix='atac'` (str)

### `analyze_bacterial_growth_curve`
Analyzes bacterial growth curve data to determine growth parameters such as doubling time, growth rate, and lag phase.

**Required:** `time_points` (List or numpy.ndarray), `od_values` (List or numpy.ndarray), `strain_name` (str)
**Optional:** `output_dir='.'` (str)

### `isolate_purify_immune_cells`
Simulates the isolation and purification of immune cells from tissue samples.

**Required:** `tissue_type` (str), `target_cell_type` (str)
**Optional:** `enzyme_type='collagenase'` (str), `macs_antibody=None` (str), `digestion_time_min=45` (int)

### `estimate_cell_cycle_phase_durations`
Estimate cell cycle phase durations using dual-nucleoside pulse labeling data and mathematical modeling.

**Required:** `flow_cytometry_data` (dict), `initial_estimates` (dict)
**Optional:** —

### `track_immune_cells_under_flow`
Track immune cells under flow conditions and classify their behaviors.

**Required:** `image_sequence_path` (str)
**Optional:** `output_dir='./output'` (str), `pixel_size_um=1.0` (float), `time_interval_sec=1.0` (float), `flow_direction='right'` (str)

### `analyze_cfse_cell_proliferation`
Analyze CFSE-labeled cell samples to quantify cell division and proliferation.

**Required:** `fcs_file_path` (str)
**Optional:** `cfse_channel='FL1-A'` (str), `lymphocyte_gate=None` (tuple or None)

### `analyze_cytokine_production_in_cd4_tcells`
Analyze cytokine production (IFN-γ, IL-17) in CD4+ T cells after antigen stimulation.

**Required:** `fcs_files_dict` (dict)
**Optional:** `output_dir='./results'` (str)

### `analyze_ebv_antibody_titers`
Analyze ELISA data to quantify EBV antibody titers in plasma/serum samples.

**Required:** `raw_od_data` (dict), `standard_curve_data` (dict), `sample_metadata` (dict)
**Optional:** `output_dir='./'` (str)

### `analyze_cns_lesion_histology`
Analyzes histological images of CNS lesions to quantify immune cell infiltration, demyelination, and tissue damage.

**Required:** `image_path` (str)
**Optional:** `output_dir='./output'` (str), `stain_type='H&E'` (str)

### `analyze_immunohistochemistry_image`
Analyzes immunohistochemistry images to quantify protein expression and spatial distribution.

**Required:** `image_path` (str)
**Optional:** `protein_name='Unknown'` (str), `output_dir='./ihc_results/'` (str)
