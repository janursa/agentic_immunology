# Task levels — Reference

Every task is classified L0–L3 by the orchestrator. The level is defined by **what must exist before
execution starts** — which is the same thing as what `#### Checkpoint` in `design.md` must contain.
That makes the level auditable from `design.md` rather than an assertion nobody can check.

| level | what it is | must exist before execution | gates | who executes |
|---|---|---|---|---|
| L0 | closed retrieval/computation, verifiable answer | nothing | none | orchestrator, directly |
| L1 | fixed goal, open path | a falsifiable checkpoint | design review + user | phase loop |
| L2 | open goal in a bounded frame | a weighted rubric | design review + user | phase loop |
| L3 | open frame — the objective itself is open | a user-chosen objective, then L2's rubric | objective choice by user, then as L2 | phase loop |

## Per-level rules

**L0** — orchestrator does it itself. No `study_designer_agent`, no `peer_reviewer_agent` (hook-enforced).
Utility agents (`data_download_agent`, `curate_paper`) are still allowed.

**L1** — full phase loop. The checkpoint is a concrete pass/fail test against the stated goal.
No rubric — inventing weighted criteria for a question with a single right answer is decoration.

**L2** — full phase loop. The checkpoint is a weighted rubric: named criteria, their weights, and what
evidence scores each one. The user sees it at the pre-execution design gate.

**L3** — before any design, the orchestrator proposes 2–3 candidate objectives and the user picks one
(`STAGE: INTERPRETATION`). After that it is an L2 run against the chosen objective.

## Classification is not final

`study_designer_agent` may return `LEVEL-MISMATCH: L{n} — {reason}` when the level it was handed makes
no sense for the question (most often: an L2 rubric demanded for something with a falsifiable answer).
The orchestrator then reclassifies, or takes it to the user if the change is material.

Distinct from that: `CANNOT-MEET` from the planner means no evaluation is constructible with the
available data, at any level. Stop and return to the user — do not burn a phase to rediscover it.

## Persistence

Not a level. L0–L3 classify one request; cross-session accumulation of findings is an orthogonal axis
and is not implemented today.
