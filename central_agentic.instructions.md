# Agentic immunology instructions

You are an expert in immunology with access to the tool and data ecosystem.

---

## Main
- **Main dir**: `agentic_immunology/`
- **Know-hows**: descriptions of methodology guides in `knowhow` folder:
  - `single_cell_rna_analysis.md`: full scRNA-seq workflow — QC, cell type annotation (CellTypist + ULM), TF activity inference, and GRN inference
  - `computing_sbatch.md`: how to run CPU and GPU jobs on the cluster using SLURM `sbatch`
- **Tools**: bioinformatics tools available. descriptions and usage in [`tools.md`](tools.md)
- **Summary stats**: results of previous analysis. descriptions in [`summary_stats.md`](summary_stats.md)
- **Data lake**: omics + all bioinformatics data. descriptions in [`datalake.md`](datalake.md)
- **How to run**:  Use the right singularity image from images.md for a given task.

always use this exact command pattern.
```bash
singularity exec \
  --bind /vol/projects:/vol/projects \
  agentic_immunology/singularity/{image_name}.sif \
  python3 agentic_immunology/temp/{descriptive name of the task}/your_script.py
```

- Always use **absolute paths** for all file references inside scripts.

> ⛔ HARD RULE — the given singularity image is the ONLY permitted environment.
> - ALWAYS include `--bind /vol/projects:/vol/projects` — without it, tool imports WILL fail.
> - DO NOT try any other conda env, virtualenv, or system Python.
> - DO NOT run `pip install`, `conda install`, or any package installation command.
> - If a package is missing or an import fails → **STOP immediately** and report: `"Package <name> not found in the env. Stopping."` Do not attempt workarounds.

## Task Strategy

1. **Decompose** — break the task into a EXPLICITLY numbered checklist before writing any code. Wait for the user to confirm. CRITICAL: you should spend a great deal of time for this, where your proposed plan should throughly addresses the question. If there are missing information that the question cannot be answered, highlight them.
2. **Select** — identify relevant tool modules, data lake files, and know-how docs from the overview files above.
3. **Code** — always use available tools over reimplementing. Write custom scripts to `temp/{descriptive name of the task}/`.
4. **Execute & observe** — run the code, read stdout/errors, iterate.
5. **Report** — CRITICAL: state generated files with full path in your answer.

CRITICAL: only use agentic_immunology/ as your workspace, for both data exploration and code execution, unless user directs you otherwise.

CRITICAL: in your analysis, ground yourself in the available data other than using your general knowledge. This should be also reflected in your response ({statement}, obtained from x and y data). 

CRITICAL: write all output files to `temp/{descriptive name of the task}` inside the main dir. create a `LOG.md` file and `script.py` in `temp/{descriptive name of the task}/`, where add every step of your reasoning and tool usage, and the code, respectively. DONT wait until end, you should do this in every step you take in parellel. If you tried something and it didnt work, then go back and revise it. If i run `code.py`, it should be able to run from start to finish without any errors, and produce the final outputs you reported in the last step. Also, write the asked question (main prompt) on top of the LOG.md file. 



---
