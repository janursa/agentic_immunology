# Agentic immunology instructions

You are an expert in immunology with access to the tool and data ecosystem.

CRITICAL: only use agentic_immunology/ as your workspace, for both data exploration and code execution, unless user directs you otherwise.
---

## Main
- **Main dir**: `agentic_immunology/`
- **Know-hows**: descriptions of methodology guides in `knowhow` folder. Only use this when you need to perform a task and want to check if there is a guide for it. Key guides:
  - `single_cell_rna_analysis.md`: full scRNA-seq workflow — QC, cell type annotation (CellTypist + ULM), TF activity inference, and GRN inference
  - `computing_sbatch.md`: how to run CPU and GPU jobs on the cluster using SLURM `sbatch`
- **Tools**: bioinformatics tools available. descriptions and usage in [`tools.md`](tools.md)
- **Summary stats**: pre-computed results — **start here for any question requiring data analysis**. Contains aging/disease/perturbation signatures, and GRN models as well as target expression features and target clinical success stats. Full descriptions and load instructions in [`summary_stats.md`](summary_stats.md)
- **Data lake**: omics + all bioinformatics data. descriptions in [`datalake.md`](datalake.md)
- **How to run**:  Use the right singularity image from images.md for a given task.
available images:
- `biomni_full.sif`: the default image for all tasks, with all tools
- `rapid.sif`: uses GPU based RAPID tools

always use this exact command pattern.
```bash
singularity exec \
  --bind /vol/projects:/vol/projects \
  agentic_immunology/singularity/{image_name}.sif \
  python3 agentic_immunology/temp/{descriptive name of the task}/your_script.py
```
- Scripts must import tools like this:
```python
import sys
sys.path.insert(0, '{abs_path_of_repo}/tools/code')
from genomics import annotate_celltype_scRNA  # example
```
- Always use **absolute paths** for all file references inside scripts.

> ⛔ HARD RULE — the given singularity image is the ONLY permitted environment.
> - ALWAYS include `--bind /vol/projects:/vol/projects` — without it, tool imports WILL fail.
> - DO NOT try any other conda env, virtualenv, or system Python.
> - DO NOT run `pip install`, `conda install`, or any package installation command.
> - If a package is missing or an import fails → **STOP immediately** and report: `"Package <name> not found in the env. Stopping."` Do not attempt workarounds.

## Task Strategy

1. **Decompose** — break the task into a EXPLICITLY numbered checklist before writing any code. Wait for the user to confirm.
2. **Select** — identify relevant tool modules, data lake files, and know-how docs from the overview files above.
3. **Code** — prefer biomni tools over reimplementing. Write custom scripts to `temp/{descriptive name of the task}/`.
4. **Execute & observe** — run the code, read stdout/errors, iterate.
5. **Report** — state file paths for any saved outputs (plots, tables).

CRITICAL: write all output files to `temp/{descriptive name of the task}` inside the main dir. create a `LOG.md` file and `script.py` in `temp/{descriptive name of the task}/`, where add every step of your reasoning and tool usage, and the code, respectively. DONT wait until end, you should do this in every step you take in parellel. If you tried something and it didnt work, then go back and revis it. If i run `code.py`, it should be able to run from start to finish without any errors, and produce the final outputs you reported in the last step.

## How to create overview map (agentic_map.html)
The code to generate should be in `scripts/generate_map.py`. It should plot from the major categories to all the way minor data and function. For example, datalake -> omics -> hiara -> op_sc.h5ad. 
Each node should be shown with its pretty name (*pretty name* under each section in md files). 
Important: all the modules/datasets/methods should be shown on the graph. For the leafs (the most dowstram nodes), they should be shown with a option of having a + on their mother node -> if the plus hit, they should be shown on the graph, if not, they should be hidden.
---
