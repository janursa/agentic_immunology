# Omics Analysis — Reference

Reference for omics analyses in the platform: tools, images, and workflow. For detailed single-cell methodology, see `knowhow/single_cell_rna_analysis.md`.

---

## Tools

Prefer the platform's existing tools (`tools.md`) over reimplementing methods yourself.

Key tool modules:
- `tools/ciim/genomics.md` — `get_immune_grn`, `infer_grn_spearman`, `infer_tf_activity`, and other CIIM genomics utilities.
- `tools/ciim/hiara.md` — `retrieve_summary_stats` (unified loader for precomputed aging, disease, drug, cytokine signatures).

---

## Know-hows (methodology guides)

- `knowhow/single_cell_rna_analysis.md` — full scRNA-seq workflow: QC, cell-type annotation (CellTypist + ULM), TF activity inference, GRN inference. **Use `backed_r=True` for any exploratory analysis.**
- `knowhow/computing_sbatch.md` — running CPU/GPU jobs on the cluster via SLURM `sbatch` (use for heavy/long jobs).

---

## Image Selection

Pick from `images.md` based on task:
- `ciim.sif` — single-cell immunology, immune aging clocks, LIANA, CIIM tool imports.
- `biomni_full.sif` — default; general bioinformatics, pharmacology tools.
- `rapids.sif` — GPU acceleration, CellTypist GPU (use at ≥200k cells).
- `ldsc.sif` — stratified LDSC / S-LDSC.
- `ciim_R_base.sif` — Seurat/Signac R tasks.

```bash
singularity exec \
  --bind /vol/projects:/vol/projects \
  agentic_immunology/singularity/{image_name}.sif \
  python3 agentic_immunology/temp/{task}/code/script.py
```

> ⛔ HARD RULES:
> - ALWAYS include `--bind /vol/projects:/vol/projects`.
> - DO NOT use any other env, conda, or virtualenv.
> - DO NOT `pip install` or `conda install`. If a package is missing → STOP: `"Package <name> not found in the env. Stopping."`
> - Singularity scratch: `/tmp/` only; all persistent outputs go to the task folder.
> - Always use **absolute paths** inside scripts.

---

## Workflow

1. **Select** — identify the relevant tool modules, data-lake entries, and knowhow docs for the task.
2. **Code** — write a self-contained `code/script.py` to `temp/{task}/code/`. Must run start-to-finish inside the singularity image with no manual steps.
3. **Execute & observe** — run it, read stdout/errors, iterate. If something fails, revise and rerun.
4. **Report** — return key findings (grounded in data) and **absolute paths** of every output file.

## Grounding
Ground every claim in the available data — e.g. "{statement}, obtained from {x} and {y} data." Report failures and skipped steps faithfully.
