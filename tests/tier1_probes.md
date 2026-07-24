# Tier 1 probes — cheap live checks of orchestrator delegation behavior

Companion to Tier 0 (`test_memory_blob.py`, `check_report_completeness.py`)
and the always-on hook (`.claude/hooks/check_guardrail_flag.py`, which now
enforces output_conventions.md + past-lessons only). These are
manual, single-turn checks — no pytest, since they exercise the real
orchestrator's behavior, not pure code. The hook already blocks a
non-compliant delegation automatically; these probes confirm the
orchestrator produces a *compliant* one in the first place.

## Injection probe

Confirms the orchestrator retrieves memory_blob lessons and appends
output_conventions.md before delegating — using `echo_stub_agent` as the
subagent so the check costs one cheap turn instead of a real analysis.

1. Seed a canary lesson:
   `python memory/memory_blob.py add --issue-tag <tag> --agents echo_stub_agent --task probe --lesson "Situation: probe. Lesson: canary-lesson-xyz."`
2. Ask the `ciim_agentic` orchestrator to delegate a trivial task to
   `echo_stub_agent` instead of the real specialist it would normally pick.
3. Check the echoed `<RECEIVED>` block contains `canary-lesson-xyz` and
   `Past lessons for you:`.
4. `memory_blob.jsonl` is append-only (no `remove` command) — delete the
   canary line from the file by hand afterward.

## Report probe

Confirms the reporting step covers every generated file.

1. Build a fixture task dir with a few dummy files (no real analysis needed).
2. Run just the reporting step (`knowhow/reporting.md`) against it.
3. `python tests/check_report_completeness.py <task_dir>`.

## What NOT to probe this way

Full open-ended analysis correctness is Tier 2: a bounded, known-answer
canary task, run periodically (not per-change) — see the earlier benchmark
design discussion.
