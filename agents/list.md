# Agents index (host-only evaluation/curation agents)

On-demand agents specific to this host project's benchmark harness — not part of the portable `egad` package (see `egad/agents/list.md` for the core study-execution loop). They read/write `application/` and `memory/`, the host's own answer-key content.

| Agent (name) | Model | Tools | What it does |
|---|---|---|---|
| `feedback_analyser` | sonnet | Read, Grep, Glob | On-demand only (user request, not part of the numbered loop). Reads `memory/memory_blob.jsonl` and surfaces recurring issues — entries describing the same underlying problem happening more than once. Never writes any file. |
| `curate_paper` | sonnet | Read, Write, Grep, Glob | On-demand. Reads a full-text paper (tex/text) and curates open-ended questions, findings, and methodology into `{author-year}_curated.md` (given path, else `${CIIM_TEMP_DIR}/`). |
| `knowhow_audit` | opus | Read, Write, Grep, Glob, Bash | On-demand. Checks `design.md` (and `report.md` if run) against the curated knowhow docs and `memory/guardrail.md` — where the run followed or departed from prior methodology. Writes `consistency.md`, renders it, returns the URL. For a human expert judging work quality; no source paper involved. |
| `rubric_agent` | opus | Read, Write, Grep, Glob, Bash | On-demand. Scores a run against the source paper it reproduces: holistic comparison of the CASE-CARD's findings with `report.md`'s, giving recovered / missed / novel items, each tagged from `docs/evaluate_tags.json`. Writes `evaluation.md`, renders it for user review, and revises it from the user's comments before it is final. |
