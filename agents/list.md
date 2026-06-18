# Agents index

Single index of the role-specialized subagents in this folder. **Read only this file to learn what agents exist and what each does — do not read the individual `*_agent.md` files** (the harness loads an agent's full definition automatically when you delegate to it by name via the Agent tool). Open an individual agent file only if you must inspect its internal methodology, which is rare.

Delegate to an agent by its `name` (the `subagent_type`). Each runs in its own fresh context and returns a concise summary plus absolute output paths.

| Agent (name) | Model | Tools | What it does |
|---|---|---|---|
| `study_designer_agent` | sonnet | Read, Grep, Glob | Lays out the study: numbered plan + subagent assignments, checkpoints, and the evaluation/benchmark procedure (success criteria + validation tier). Used at task start and for every re-design/delta pass. No analysis, no user interaction. |
| `peer_reviewer_agent` | opus | Read, Write, Grep, Glob | Critical referee. DESIGN-REVIEW mode (complex tasks, pre-execution): sanity-checks the draft design. RESULTS-REVIEW mode (default, per cycle): evaluates results against the criteria, writes `peer_review.md`, returns ACCEPT/REVISE/CANNOT-MEET. |
| `method_reviewer_agent` | opus | Read, Grep, Glob | Reviews the actual CODE/methods of a finished step (not just inputs/outputs): correctness, data leakage, batch/confounder handling, multiple-testing correction, reproducibility. Returns PASS/REVISE with file/line-referenced issues. |
| `omics_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob | All omics analysis (scRNA-seq QC, annotation, DE, TF activity, GRN, etc.). Hand it a fully-specified, pre-confirmed task with data paths and expected outputs. |
| `genetics_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob | Genetic analyses (eQTL, GWAS, colocalization, MR, etc.). Hand it a fully-specified task with gene/locus/disease identifiers and expected outputs. |
| `literature_agent` | sonnet | Read, Write, Bash, Grep, Glob, WebSearch, WebFetch | Literature search, evidence synthesis, novelty/grounding checks (PubMed/arXiv/Scholar/web). Hand it the question and what evidence is needed. |
| `disease_implication_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob, Agent | Assesses whether a gene/feature is causally implicated in a disease/aging phenotype and evaluates safety/tractability (evidence-pillar synthesis). May delegate to `omics_agent`/`literature_agent`/`genetics_agent`. |
| `drug_repurposing_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob, Agent | Drug repurposing in immune aging/disease: signature reversal, KG repurposing scores, aging-clock prediction, safety annotation → ranked evidence table. May delegate to `aging_clock_agent`. |
| `aging_clock_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob | Aging-clock prediction (age acceleration/deceleration). Receives data paths only — does not access the datalake or tool ecosystem. Needs metadata with chronological ages, design, desired clocks. |
| `data_download_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob | Downloads public datasets (URL/accession/DOI/paper) to datalake or temp, uses SLURM for large files, optionally registers in `datalake.md`/`list.md`. |
| `reporting_agent` | sonnet | Read, Write, Glob | Writes the final user-facing markdown report after peer_reviewer_agent ACCEPTs. Takes the original question, grounded findings + paths, and the peer-review record. No analysis. |

`output_conventions.md` (in this folder) is **not an agent** — it is the shared output-convention text appended verbatim to every analysis subagent's task prompt.
