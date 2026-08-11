# Tier 2 probe — end-to-end positive-control run

Companion to Tier 1 (`tier1_probes.md`, cheap structural checks) and Tier 0
(`test_memory_blob.py`, `check_report_completeness.py`). Where Tier 1 checks
that a delegation is *compliant* (right flags, right conventions), Tier 2
checks that a full L2 run through the real `ciim_agentic`
orchestrator is both **process-faithful** (right steps, right agents, right
artifacts) and **scientifically correct** (recovers a known biological
ground truth). Run periodically (e.g. monthly, or after any change to
`ciim_agentic.md`, `agents/*.md`, or `knowhow/*.md`) — not per-change.

## Why this scenario

The prompt below targets the `abf300` datalake cohort, which is the source
cohort of Terekhova et al., *Immunity* 2024 (confirmed by a live run of this
probe on 2026-07-16/17 — see `temp/tcell_aging_abf300/`). That paper
publishes 12 age-associated T cell subpopulation shifts for this exact
cohort, which gives this probe something Tier 1 can't have: a literature
ground truth to grade the *content* of the analysis against, not just its
shape. Keep this scenario fixed run over run — a fixed positive control is
what makes results comparable across runs; swap it only if the `abf300`
datalake entry is removed or the cohort ID is disproven.

## How to trigger

⚠️ **This probe must be run manually by a human, present and responsive in
real time — it cannot be handed to another agent to run unattended.** An
agent (including whichever agent launched `ciim_agentic`) cannot supply the
checkpoint consent on your behalf; only you can. See "Why this must be
manual" below for the mechanism.

1. Launch the orchestrator as an isolated subagent (not inline in your own
   session — this is what's actually being tested):
   ```
   Agent(subagent_type: "ciim_agentic", prompt: "<PROMPT below>", run_in_background: true)
   ```
2. `ciim_agentic` serves a dashboard page (via `scripts/serve_dashboard.sh` + `scripts/render_review_artifact.py`) at each checkpoint and pauses. **You,
   the actual human, must answer directly** — via an `AskUserQuestion`
   prompt the subagent raises to you, or by interacting with it in a
   foreground session. Do **not** resume it by having another agent relay
   your comments over `SendMessage` — `ciim_agentic` correctly refuses to
   treat that as consent (confirmed 2026-07-17; see below). Expect two such
   checkpoints (after design peer review, and after results peer review);
   answer both, not just the first.
3. Give it real feedback at least once (don't just approve) — e.g. ask
   whether covariate collinearity was checked, or challenge a data-source
   claim. A run that never receives a substantive comment can't test
   whether feedback is actually incorporated.
4. The probe isn't finished until the orchestrator reaches a completed
   `report.md`. Only then grade it against the checklist below.

### Why this must be manual (found 2026-07-17)

`ciim_agentic` carries a harness-level rule that no message delivered via
the agent-to-agent `SendMessage` tool is ever treated as user consent —
regardless of who is actually behind it, including the very agent that
launched the run. This is a real anti-prompt-injection guardrail working
correctly, not a bug: if it trusted relayed "the user approved this"
messages, any compromised tool output or peer agent could spoof approval
the same way. The practical consequence is that a background `ciim_agentic`
run's checkpoints cannot be resumed by proxy — confirmed by trying it live
(the subagent held at the design-review checkpoint through two relayed
messages and explicitly named the missing first-party consent as the
reason). Only two channels count as genuine first-party input: the human
answering an `AskUserQuestion` prompt the subagent raises directly, or the
human interacting with the orchestrator in a foreground session rather than
through a spawned background `Agent` call. As of 2026-07-17 `ciim_agentic`
does not carry `AskUserQuestion` (removed deliberately in favor of
dashboard-only interaction) — restoring it for just the two checkpoint
moments is the open decision needed to make the background-run path usable
again; until then, foreground execution is the only way to complete this
probe.

### Prompt

```
Characterize age-associated changes in T cell subsets using the abf300 cohort.
```

Feed nothing else — no cohort hints, no method hints. Whether the
orchestrator chain correctly identifies `abf300` as the Terekhova 2024
cohort (via `study_designer_agent`'s literature step) is itself part of
what's being probed.

### Output location

`temp/tcell_aging_abf300/` is this probe's fixed output folder — it's the
probe, not a separate real-analysis fixture. Remove it before each rerun
(`rm -rf temp/tcell_aging_abf300/`) so the orchestrator starts clean; don't
diff against stale output from a prior run.

## What to check (manual walkthrough — no judge agent)

Grade by reading the transcript and the output directory directly. This is
a documented checklist, not an automated grader — `benchmark_judge.md` was
deliberately removed from this repo; don't reintroduce a grading agent here
without a separate explicit decision to do so.

**Process fidelity**
- [ ] First line of the orchestrator's first reply is `CANARY: ...`.
- [ ] Agent sequence matches `ciim_agentic.md` L1+ phase-loop steps in order:
      `study_designer_agent` → `peer_reviewer_agent` (DESIGN-REVIEW) →
      dashboard checkpoint → `data_analyst_agent` → `peer_reviewer_agent`
      (RESULTS-REVIEW) → dashboard checkpoint → report finalized.
- [ ] `memory_blob.py retrieve` was run before every dispatch, and the
      output appended verbatim as "Past lessons for you:" — or, if a
      retrieved lesson conflicts with this task's reviewed design, the
      conflict is flagged to the user rather than silently applied or
      silently dropped.
- [ ] Both dashboard checkpoints are reachable at the printed link and follow
      the fixed card format from `render_review_artifact.py` (see
      `ciim_agentic.md`'s "Interact with user"): one card per `##` section,
      each with its content and a Comment textarea, one page-level "Compile
      comments" button.
- [ ] Your injected comment (see trigger step 3) visibly changes something
      downstream — a design revision, a re-review, or an explicit answer —
      not just an acknowledgement.
- [ ] `report.md` exists early (checked after the first dashboard
      checkpoint, not only at the end) and gains sections as the run
      progresses, per the step-7 hard rule in `ciim_agentic.md`.
- [ ] Final `report.md` lists the absolute path of every generated file:
      `design.md`, `peer_review.md`, `LOG.md`, `code/`, `results/`
      (including `results/images/`).
- [ ] If any tool/data/framework error occurs (not the agent's own
      reasoning mistake), the run stops and flags it rather than routing
      around it, per the orchestrator's hard rule.

**Scientific correctness** (grade against Terekhova et al. 2024, *Immunity*)
- [ ] Cohort is identified as the Terekhova 2024 source cohort, with a
      citation, not just used blind.
- [ ] The 4 cohort-native positive controls (GZMK+CD8 up, NKG2C+GZMB-CD8
      down, HLA-DR+CD4 up, type-2/CCR4+ shift up) are explicitly tested and
      their recovery status (recovered / not recovered / sub-floor)
      reported — not silently dropped if inconvenient.
- [ ] Repeated-measures structure (`donor_id` recurs across visits) is
      accounted for in every statistical model, not treated as i.i.d. rows.
- [ ] Multiple-testing correction is applied per family, not pooled across
      unrelated test sets.
- [ ] A sensitivity check (e.g. baseline-visit-only refit) is run and its
      outcome reported, not just the primary model.

## Known first-run baseline (2026-07-16/17)

The live run that motivated this file recovered 7/8 positive controls;
control #2 (NKG2C+GZMB-CD8 decline) was not recovered, later found to be
because the analysis tested only single-gene (`KLRC2`) lineage-average
expression instead of a proper per-cell joint `KLRC2+/GZMB-` gate — a fixable
method-choice gap, not a data-availability limitation (`sc/abf300.h5ad` has
both genes at single-cell resolution). Future runs should recover control #2
correctly once that fix propagates through `data_analyst_agent`'s guidance;
if a future run still substitutes a single-gene proxy for a named
two-marker joint control, that's a regression worth flagging.
