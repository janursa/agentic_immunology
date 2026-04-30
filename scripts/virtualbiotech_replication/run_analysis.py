#!/usr/bin/env python3
"""
Generate three target-level summary stat files from Virtual Biotech data.

File 1: target_sc_features.csv
    SC features (tau, bimodality, ae_risk, etc.) for all 1,511 genes.

File 2: target_clinical_success_overall.csv
    Clinical outcome rates per target gene across all trials/diseases.

File 3: target_clinical_success_by_disease.csv
    Same outcome rates but broken down by disease_name.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("datalake/virtualbiotech")
OUT_DIR  = Path("summary_stats/virtualbiotech")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading data...")
sc       = pd.read_parquet(DATA_DIR / "comprehensive_features_aggregated_v2_optimized.parquet")
chembl   = pd.read_parquet(DATA_DIR / "chembl_clinical_nct_data.parquet")
labels   = pd.read_csv(DATA_DIR / "clinical_trial_labels.csv")

print(f"  SC features:  {len(sc):,} genes")
print(f"  ChEMBL:       {len(chembl):,} rows, {chembl['nct_id'].nunique():,} unique NCTs")
print(f"  Trial labels: {len(labels):,} trials")

# ── FILE 1: SC features per gene ───────────────────────────────────────────────
print("\n[1] SC features per gene...")

sc_summary_cols = (
    ['ensembl_id'] +
    ['mean_expr', 'detection_rate', 'cv', 'p90_expr', 'donor_variance_ratio'] +
    ['tau_cell_type', 'tau_cell_type_max', 'tau_cell_type_min',
     'tau_cell_type_range', 'tau_cell_type_variance',
     'n_expressing_cell_types', 'cell_type_selectivity',
     'peak_cell_type_expr', 'dominant_peak_celltype'] +
    ['tissue_tau', 'tissue_entropy', 'n_tissues_expressing', 'n_tissues_high_tau'] +
    ['bimodality_score', 'bimodality_max_celltype', 'bimodality_mean_celltype',
     'n_bimodal_celltypes', 'variance_within_celltype_max', 'outlier_cell_fraction'] +
    [c for c in sc.columns if c.startswith('ae_risk_')] +
    ['overall_safety_risk', 'multi_system_ae_count',
     'attrition_risk_phase1', 'attrition_risk_phase2', 'attrition_risk_phase3',
     'rare_celltype_enrichment', 'critical_rare_expr_max']
)
sc_summary_cols = [c for c in sc_summary_cols if c in sc.columns]
file1 = sc[sc_summary_cols].copy()
out1 = OUT_DIR / "target_sc_features.csv"
file1.to_csv(out1, index=False)
print(f"  Saved: {out1}  ({len(file1):,} genes x {len(file1.columns)} columns)")

# ── Merge for files 2 & 3 ─────────────────────────────────────────────────────
print("\nMerging ChEMBL + labels for clinical success files...")

nct_target_disease = (
    chembl[['nct_id', 'targetId', 'disease_name', 'targetFromSourceId']]
    .drop_duplicates()
)

merged = nct_target_disease.merge(
    labels[['nct_id', 'phase', 'status',
            'primary_endpoint_result', 'secondary_endpoint_result',
            'phase2_progression']],
    on='nct_id', how='inner'
)
print(f"  Merged rows: {len(merged):,}  ({merged['nct_id'].nunique():,} unique trials, "
      f"{merged['targetId'].nunique():,} unique targets)")

# Binary outcomes
merged['reached_phase3']     = (merged['phase'] >= 3.0).astype(float)
merged['reached_phase2']     = (merged['phase'] >= 2.0).astype(float)
merged['terminated']         = (merged['status'] == 'Terminated').astype(float)
merged['withdrawn']          = (merged['status'] == 'Withdrawn').astype(float)
merged['endpoint_primary']   = (merged['primary_endpoint_result'] == 'POSITIVE').astype(float)
merged['endpoint_secondary'] = (merged['secondary_endpoint_result'] == 'POSITIVE').astype(float)
merged['endpoint_either']    = (
    (merged['primary_endpoint_result'] == 'POSITIVE') |
    (merged['secondary_endpoint_result'] == 'POSITIVE')
).astype(float)
merged['phase1_to_phase2']   = merged['phase2_progression'].map({'EVER': 1.0, 'NEVER': 0.0})

outcome_cols = ['reached_phase3', 'reached_phase2', 'terminated', 'withdrawn',
                'endpoint_primary', 'endpoint_secondary', 'endpoint_either',
                'phase1_to_phase2']

gene_map = chembl[['targetId','targetFromSourceId']].drop_duplicates('targetId')

def summarise_group(grp):
    n_trials = grp['nct_id'].nunique()
    row = {'n_trials': n_trials}
    for col in outcome_cols:
        valid = grp[col].dropna()
        row[f'pct_{col}'] = round(valid.mean() * 100, 1) if len(valid) else np.nan
        row[f'n_{col}']   = int(valid.sum()) if len(valid) else 0
    return pd.Series(row)

# ── FILE 2: Overall per target ─────────────────────────────────────────────────
print("\n[2] Clinical success overall per target...")
file2 = merged.groupby('targetId').apply(summarise_group).reset_index()
file2 = file2.merge(gene_map, on='targetId', how='left')
out2 = OUT_DIR / "target_clinical_success_overall.csv"
file2.to_csv(out2, index=False)
print(f"  Saved: {out2}  ({len(file2):,} targets)")
print(f"  Top 5 by n_trials:")
print(file2.sort_values('n_trials', ascending=False).head(5)[
    ['targetId','targetFromSourceId','n_trials','pct_reached_phase3','pct_terminated','pct_endpoint_either']
].to_string(index=False))

# ── FILE 3: Per target x disease ──────────────────────────────────────────────
print("\n[3] Clinical success per target x disease...")
file3 = merged.groupby(['targetId', 'disease_name']).apply(summarise_group).reset_index()
file3 = file3.merge(gene_map, on='targetId', how='left')
out3 = OUT_DIR / "target_clinical_success_by_disease.csv"
file3.to_csv(out3, index=False)
print(f"  Saved: {out3}  ({len(file3):,} target x disease combinations)")
print(f"  Top 5 by n_trials:")
print(file3.sort_values('n_trials', ascending=False).head(5)[
    ['targetId','targetFromSourceId','disease_name','n_trials','pct_reached_phase3','pct_terminated','pct_endpoint_either']
].to_string(index=False))

print("\nDone.")
