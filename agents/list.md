# Agents index

Single index of the role-specialized subagents in this folder. **Read only this file to learn what agents exist and what each does — do not read the individual `*_agent.md` files** (the harness loads an agent's full definition automatically when you delegate to it by name via the Agent tool). Open an individual agent file only if you must inspect its internal methodology, which is rare.

Delegate to an agent by its `name` (the `subagent_type`). Each runs in its own fresh context and returns a concise summary plus absolute output paths.

| Agent (name) | Model | Tools | What it does |
|---|---|---|---|
| `peer_reviewer_agent` | opus | Read, Write, Grep, Glob, WebSearch, WebFetch | Critical referee with three modes. METHOD-REVIEW (user-triggered, post-analysis): audits actual code for correctness, leakage, batch handling, stats, reproducibility; returns PASS/REVISE. DESIGN-REVIEW (complex tasks, pre-execution): sanity-checks the orchestrator's draft design. RESULTS-REVIEW (default, per cycle): evaluates results against the criteria, writes `peer_review.md`, returns ACCEPT/REVISE/CANNOT-MEET. |
| `data_analyst_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch | All omics (scRNA-seq, ATAC-seq, multi-omics, TF activity, GRN), genetics (eQTL, GWAS, colocalization, MR, CRISPR), disease/aging implication (8-pillar evidence synthesis), drug repurposing (signature reversal, TxGNN, safety → ranked evidence table), and literature grounding. Reads relevant knowhow files before coding. |
| `data_download_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob | Downloads public datasets (URL/accession/DOI/paper) to datalake or temp, uses SLURM for large files, optionally registers in `datalake.md`/`list.md`. |

`output_conventions.md` (in this folder) is **not an agent** — it is the shared output-convention text appended verbatim to every analysis subagent's task prompt.
