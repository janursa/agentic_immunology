# Agents index

Single index of the role-specialized subagents in this folder. **Read only this file to learn what agents exist and what each does — do not read the individual `*_agent.md` files** (the harness loads an agent's full definition automatically when you delegate to it by name via the Agent tool). Open an individual agent file only if you must inspect its internal methodology, which is rare.

Delegate to an agent by its `name` (the `subagent_type`). Each runs in its own fresh context and returns a concise summary plus absolute output paths.

| Agent (name) | Model | Tools | What it does |
|---|---|---|---|
| `study_designer_agent` | sonnet | Read, Write, Grep, Glob, WebSearch, WebFetch | Designs the study plan — the numbered plan, checkpoints, and evaluation procedure — at the start of every task, plus design-review revisions and post-results delta re-designs. |
| `peer_reviewer_agent` | opus | Read, Write, Grep, Glob, WebSearch, WebFetch | Critical referee with three modes. METHOD-REVIEW (user-triggered, post-analysis): audits actual code for correctness, leakage, batch handling, stats, reproducibility; returns PASS/REVISE. DESIGN-REVIEW (complex tasks, pre-execution): sanity-checks `study_designer_agent`'s draft design; returns APPROVE/REVISE-DESIGN. RESULTS-REVIEW (default, per cycle): evaluates results against the criteria, writes `peer_review.md`, returns ACCEPT/REVISE/CANNOT-MEET. |
| `data_analyst_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch | All omics (scRNA-seq, ATAC-seq, multi-omics, TF activity, GRN), genetics (eQTL, GWAS, colocalization, MR, CRISPR), disease/aging implication (8-pillar evidence synthesis), drug repurposing (signature reversal, TxGNN, safety → ranked evidence table), and literature grounding. |
| `data_download_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob | Downloads public datasets (URL/accession/DOI/paper) to datalake or temp, uses SLURM for large files, optionally registers in `docs/datalake.md`/`list.md`. |
| `feedback_analyser` | sonnet | Read, Grep, Glob | On-demand only (user request, not part of the numbered loop). Reads `memory/memory_blob.jsonl` and surfaces recurring issues — entries describing the same underlying problem happening more than once. Never writes any file. |
| `curate_paper` | sonnet | Read, Write, Grep, Glob | On-demand. Reads a full-text paper (tex/text) and curates open-ended questions, findings, and methodology into `{author-year}_curated.md` (given path, else `temp/`). |
| `evaluate` | opus | Read, Write, Grep, Glob | On-demand, two modes. DESIGN-REVIEW: checks `design.md` against knowhow docs. REPORT-REVIEW: checks `design.md` + `report.md` against the CASE-CARD (curated source paper) on both methodology and findings. Writes `evaluation.md`. |
| `echo_stub_agent` | haiku | Read | **TEST ONLY** — never delegate a real task to it. Tier 1 benchmarking stub (see `tests/tier1_probes.md`): echoes the exact task prompt it receives so a probe can check the orchestrator assembled it correctly. |

[`knowhow/output_conventions.md`](knowhow/output_conventions.md) is **not an agent** — it is the shared output-convention text appended verbatim to every analysis subagent's task prompt.

