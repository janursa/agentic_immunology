Curated methodology knowledge. `knowhow_audit` grades design.md/report.md against these — the planner,
reviewer, and analyst are blocked from reading them (`.claude/hooks/restrict_knowhow_access.py`).
Operational specs (sbatch, graphs, reporting, plotting) live in `docs/`.

  - `aging_clocks.md`: available aging clocks, hard rules, per-clock usage patterns, and output format
  - `drug_repurposing.md`: signature reversal, TxGNN, safety filtering → ranked evidence table
  - `safety_druggability.md`: target safety & tractability assessment (Open Targets buckets, gnomAD constraint, essentiality, safety liabilities)
  - `single_cell_rna_analysis.md`: scRNA-seq QC, annotation, and differential/compositional analysis
