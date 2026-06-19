# Study design

How to lay out a study — the role a PI plays when designing an experiment. The orchestrator does this directly (no delegation): at the start of every task, and again whenever a cycle needs re-design.

## Orientation
Check these resources before drafting a design:
- Data -> `datalake.md`, `ciim_datalake.md`
- Tools -> `tools.md`

**CRITICAL**: do not limit yourself to local resources. If a question requires additional data, check public databases via the enabled tools. If it requires a custom method, plan to develop it.

## What to produce
A design with two parts:

### 1. Plan
Numbered steps, with subagent assignments where analysis needs delegating.

### 2. Evaluation
- **Success criteria** — the concrete result that would confirm the claim, and what would falsify it
- **Validation strategy**
  1. **Replication** — an independent / held-out dataset or cohort
  2. **Orthogonal** — a different modality or method on the same samples
  3. **Literature concordance** — known biology / prior reports

## Design-review revision (pre-execution)
If `peer_reviewer_agent` (DESIGN-REVIEW mode) returns `REVISE-DESIGN` issues, fix the draft per those issues directly. This is a quick pre-execution tightening, not a re-run.

## Re-design pass (post-results)
When a results cycle returns `REVISE` (not a fresh request), read the existing plan and `peer_review.md`, and produce a **delta** — only the additional/changed numbered steps and any updated evaluation criteria needed to close that specific gap. Do not restart the whole study. Do not repeat analyses already recorded as done in `peer_review.md`.

## Keep it tight
`HARD RULE`: keep a design to ≤2000 words. If missing information blocks the study, surface that to the user and stop instead of guessing.
