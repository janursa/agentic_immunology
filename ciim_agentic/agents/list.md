# Agents index (ciim_agentic core)

Single index of the role-specialized subagents that make up the ciim_agentic study-execution loop. **Read only this file to learn what agents exist and what each does — do not read the individual `*_agent.md` files** (the harness loads an agent's full definition automatically when you delegate to it by name via the Agent tool). Open an individual agent file only if you must inspect its internal methodology, which is rare.

Delegate to an agent by its `name` (the `subagent_type`). Each runs in its own fresh context and returns a concise summary plus absolute output paths.

For the host project's own on-demand evaluation/curation agents (`curate_paper`, `rubric_agent`, `knowhow_audit`, `feedback_analyser` — not shipped with ciim_agentic), see `${CIIM_MAIN_DIR}/agents/list.md`.

| Agent (name) | Model | Tools | What it does |
|---|---|---|---|
| `study_designer_agent` | sonnet | Read, Write, Bash, Grep, Glob, WebSearch, WebFetch | Designs the study plan — the numbered plan, checkpoints, and evaluation procedure — at the start of every task, plus design-review revisions and post-results delta re-designs. Downloads the plan's data into `${CIIM_TEMP_DIR}/{task}/raw_data/`. |
| `peer_reviewer_agent` | opus | Read, Write, Grep, Glob, WebSearch, WebFetch | Critical referee with two modes. DESIGN-REVIEW (complex tasks, pre-execution): sanity-checks `study_designer_agent`'s draft design; returns APPROVE/REVISE-DESIGN. RESULTS-REVIEW (default, per cycle): evaluates results against the criteria, writes `peer_review.md`, returns ACCEPT/REVISE-ANALYSIS/REVISE-DESIGN. |
| `data_analyst_agent` | sonnet | Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch | All omics (scRNA-seq, ATAC-seq, multi-omics, TF activity, GRN), genetics (eQTL, GWAS, colocalization, MR, CRISPR), disease/aging implication (8-pillar evidence synthesis), drug repurposing (signature reversal, TxGNN, safety → ranked evidence table), and literature grounding. |
| `echo_stub_agent` | haiku | Read | **TEST ONLY** — never delegate a real task to it. Tier 1 benchmarking stub (see `tests/tier1_probes.md`): echoes the exact task prompt it receives so a probe can check the orchestrator assembled it correctly. |
