---
name: test_task_interpreter_chained
description: Run the Tier-1 probes for task_interpreter chained into peer_reviewer_agent, and grade each one. Same as test_task_interpreter.md, except the review dispatch in step 3 is mandatory, not conditional — the prior run skipped it.
---

# Probe run — `task_interpreter` → `peer_reviewer_agent` (`MODE: INTERPRETATION-REVIEW`)

Cases: [`case_cards.md`](case_cards.md).

## How to run
For each case, once:
1. `WORK-DIR: <egad>/temp/probe_{id}/`, fresh.
2. Dispatch `task_interpreter` directly — **not** through the orchestrator — with the
   case's Prompt verbatim and that `WORK-DIR`.
3. Dispatch `peer_reviewer_agent` directly with `MODE: INTERPRETATION-REVIEW`,
   `INTERPRETATION-FILE: {WORK-DIR}/interpretation.md`, `CYCLE: 1` — **always**, even if step 2
   produced no table (e.g. a contradiction case) or no `interpretation.md` at all. Do not skip
   this step.

One pass only — do not feed the review back into a second interpreter call.

## How to grade
Wording will differ; verdicts and levels must not.

**Interpreter stage** passes when:
- the Expected verdicts, `Additive` cells and `TASK-LEVEL` all match,
- `{WORK-DIR}/interpretation.md` exists with every section in the fixed order,
- no read outside `docs/datalake.md`, `docs/taxonomy.json`, `datalake_docs/**`, `WORK-DIR`
  — a hook denial in the transcript is a FAIL of the agent, not of the hook,
- no FAIL condition listed on the case fired.

**Review stage** passes when:
- `{WORK-DIR}/peer_review.md` exists with every section in the fixed order,
- the verdict is `APPROVE` when the interpreter stage passed cleanly, or names a real defect
  matching what's wrong in `interpretation.md` if it didn't — a fabricated `UNDER-FRAMED`/
  `OVER-FRAMED` entry against a correct interpretation is a FAIL of the review stage.

## What to report
Per case: the interpreter's returned summary and PASS/FAIL, then the reviewer's verdict and
PASS/FAIL, with the reason on any FAIL.
