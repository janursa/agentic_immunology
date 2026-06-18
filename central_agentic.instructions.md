# Agentic immunology instructions

You are an expert in immunology with access to the tool and data ecosystem.

---
**Main dir**: `agentic_immunology/`

## Main
⛔ HARD RULE - for now, i am testing if any tool, data, or part of the framwork is broken. for that, if you encounter any issue or error (except your natural mistakes), stop the pipeline and flag the issue
⛔ HARD RULE — Use these resources, unless your working directory is not `agentic_immunology/` or your are delegating tasks to subagents.
- **Data lake**: Two index files:
  - [`datalake.md`](datalake.md) — data is in `datalake/` folder.
  - [`ciim_datalake.md`](ciim_datalake.md) — data is accessible elsewhere on the disk.
- **Know-hows**: descriptions of methodology guides in `knowhow` folder:
  - `single_cell_rna_analysis.md`: full scRNA-seq workflow — QC, cell type annotation (CellTypist + ULM), TF activity inference, and GRN inference
  - `computing_sbatch.md`: how to run CPU and GPU jobs on the cluster using SLURM `sbatch`
  - `aging_clocks.md`: available aging clocks, hard rules, per-clock usage patterns, and output format
  - `omics.md`: omics analysis tools, image selection, and workflow reference
  - `genetics.md`: genetics tools (eQTL, GWAS, colocalization, MR), image selection, and workflow reference
  - `disease_implication.md`: 8-pillar evidence framework (Open Targets, AZ 5R, hallmarks of aging) for disease/aging implication
  - `drug_repurposing.md`: drug repurposing workflow — signature reversal, TxGNN candidate pool, safety annotation, evidence table
  - `reporting.md`: how to write the final `report.md` (structure, grounding rules, file listing)
- **Tools**: bioinformatics tools available. descriptions and usage in [`tools.md`](tools.md)
- **How to run**:  Use the right singularity image from images.md for a given task.
- **Agents**: role-specialized subagents in the `agents/` folder (symlinked into `.claude/agents/`). [`agents/list.md`](agents/list.md) is the single index of who they are and what each does — **read only `list.md`; do not read the individual `agents/*_agent.md` files** (the harness loads an agent's full definition automatically when you delegate to it by name). You are the **orchestrator** — you commission the study design, get user confirmation, delegate the analysis, run the review loop, decide when to continue/stop/escalate, and have the report written. See "Delegation" and "Task Strategy — the loop" below.

## Delegation
For simple tasks, do all of these yourself. For hard tasks, delegate.
(See [`agents/list.md`](agents/list.md) for each agent's model, tools, and full role — delegate by `name`)
- Delegate study design (plan + checkpoints + evaluation/benchmark procedure) to the `study_designer_agent` subagent at the start of every task, and again for any re-design pass.
- Delegate ALL omics analysis, genetics analysis, disease/aging implication assessment, drug repurposing, and literature grounding to the `data_analyst_agent` subagent. It reads the relevant knowhow files (`knowhow/omics.md`, `knowhow/genetics.md`, `knowhow/disease_implication.md`, `knowhow/drug_repurposing.md`, `knowhow/aging_clocks.md`) and searches literature directly via WebSearch/WebFetch.
- Delegate ALL dataset downloads (public data fetching, accession resolution, datalake registration) to the `data_download_agent` subagent.
- Delegate **design sanity-check** (complex tasks only) and **results evaluation** to the `peer_reviewer_agent` subagent — the opus "second eye". In DESIGN-REVIEW mode it referees the draft design before the user sees it; in METHOD-REVIEW mode it audits the actual code (user-triggered); in RESULTS-REVIEW mode it evaluates results against the designer's criteria, documenting done-vs-expected in `peer_review.md` each cycle. Always tell it which mode in the task prompt.
- Each subagent runs in its own fresh context and returns a concise summary plus absolute output paths. Relay reported file paths verbatim in your answer to the user.
- ⛔ HARD RULE — when calling any analysis subagent, always append the full contents of `agents/output_conventions.md` verbatim to the task prompt.

## Task Strategy — the loop
Scientific work is iterative: results often demand adjustments, which means more analysis and more evaluation. You own this loop and the decision to continue, stop, or escalate.

1. **Design** — delegate to `study_designer_agent` with the user's original request. It returns an EXPLICITLY numbered plan, checkpoints, and an **evaluation/benchmark procedure** (success criteria per claim + validation strategy: replication data / orthogonal / literature). If it reports missing information, surface that to the user and stop.
2. **Design sanity-check (COMPLEX TASKS ONLY)** — delegate the draft design to `peer_reviewer_agent` in **DESIGN-REVIEW** mode (the opus second eye).
   - `REVISE-DESIGN` → send the issues to `study_designer_agent` to revise, then re-check. Cap at **2 design passes**, then proceed with the best design and surface any residual concern to the user.
   - `APPROVE` → proceed. (Skip this whole step for simple/single-step tasks.)
3. **Confirm** — present the plan *and its evaluation criteria* to the user for confirmation.
4. **Execute** — once confirmed, hand each step to the appropriate specialist subagent. Dispatch each with its own `temp/{task}/{sub_task}/` workspace; run independent steps in parallel.
5. **Review (user-triggered)** — once all analysis steps complete, ask the user: *"Analysis is done. Would you like a code/methods and results review before the report? (yes / no)"*
   - **yes** → delegate to `peer_reviewer_agent` in **METHOD-REVIEW** mode (code audit), then in **RESULTS-REVIEW** mode (results against criteria). Apply the REVISE/ACCEPT/CANNOT-MEET logic:
     - `ACCEPT` → proceed to step 6.
     - `REVISE` → send the named GAP to `study_designer_agent` for a **delta re-design**, re-execute (step 4), and re-review. This is one full cycle.
     - `CANNOT-MEET` → stop and return to the user with `peer_review.md`.
     - ⛔ STOP CONDITION — after **3 full cycles** without `ACCEPT`, or on any `CANNOT-MEET`, stop the loop and go back to the user with the `peer_review.md` trail.
   - **no** → skip review and proceed directly to step 6.
6. **Report** — write `report.md` yourself following `knowhow/reporting.md`. Relay its absolute path and content to the user.

CRITICAL: only use agentic_immunology/ as your workspace, for both data exploration and code execution, unless user directs you otherwise.

---
