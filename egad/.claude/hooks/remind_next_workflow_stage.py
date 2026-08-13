#!/usr/bin/env python3
"""PreToolUse hook (matcher: Agent): before each dispatch, look up the last
recorded dispatch for this task in log.md (written by write_log.py — STAGE,
MODE, VERDICT, FINAL_PHASE, PHASE) and remind the orchestrator what the
L1+ phase loop in egad.md says should come next. Purely
informational (additionalContext) — never denies the call, since the
orchestrator may have a good reason to deviate (e.g. "small change, do it
yourself" for a minor REVISE).

Run from the repo root:
    python3 .claude/hooks/remind_next_workflow_stage.py --self-test
"""
import json
import os
import pathlib
import re
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
TASK_DIR_RE = re.compile(r"temp/([A-Za-z0-9_\-]+)/")
STAGE_RE = re.compile(r"STAGE:\s*([A-Z_]+)")
MODE_RE = re.compile(r"MODE=([A-Z\-]+)")
VERDICT_RE = re.compile(r"VERDICT=([A-Z\-]+)")
FINAL_PHASE_RE = re.compile(r"FINAL_PHASE=(true|false)")


def last_dispatch_block(log_text: str) -> str | None:
    # log.md interleaves dispatch blocks (have a STAGE: line) with user-turn blocks
    # (don't). Only dispatches carry workflow state — the last block is almost always
    # a user turn, so take the last one that actually has a STAGE:.
    for block in reversed(log_text.split("### [")[1:]):
        if STAGE_RE.search(block):
            return "### [" + block
    return None


def next_stage(stage: str | None, mode: str | None, verdict: str | None, final_phase: str | None) -> str:
    if stage is None:
        return "INTERPRETATION (clarify the prompt) or PLANNING phase 0 if it's already clear."
    if stage == "INTERPRETATION":
        return "PLANNING — dispatch study_designer_agent for phase 0."
    if stage == "PLANNING":
        return "PEER_REVIEW — DESIGN-REVIEW of the same phase."
    if stage == "PEER_REVIEW" and mode == "DESIGN-REVIEW":
        if verdict == "REVISE-DESIGN":
            return "PLANNING — send issues back to study_designer_agent, same phase (capped at 1 revision)."
        if verdict == "APPROVE":
            return "USER_FEEDBACK — present design.md to the user via the dashboard."
        return "awaiting a DESIGN-REVIEW verdict (APPROVE/REVISE-DESIGN) before proceeding."
    if stage == "USER_FEEDBACK":
        return "EXECUTION — dispatch this phase's tasks to specialist subagents."
    if stage == "EXECUTION":
        return "PEER_REVIEW — RESULTS-REVIEW of the same phase."
    if stage == "PEER_REVIEW" and mode == "RESULTS-REVIEW":
        if verdict == "REVISE-ANALYSIS":
            return "send the GAP back to the specialist agent to fix the analysis (or fix it yourself if small)."
        if verdict == "REVISE-DESIGN":
            return ("PLANNING — send the GAP back to study_designer_agent, same phase (or fix it yourself "
                    "if small). Only study_designer_agent may respond CANNOT-MEET — if it does, STOP and "
                    "return to the user.")
        if verdict == "ACCEPT" and final_phase == "false":
            return "PLANNING — phase += 1."
        if verdict == "ACCEPT" and final_phase == "true":
            return "USER_FEEDBACK (final review) then REPORTING — compile findings.md."
        return "awaiting a RESULTS-REVIEW verdict (ACCEPT/REVISE-ANALYSIS/REVISE-DESIGN) before proceeding."
    if stage == "REPORTING":
        return "done — findings.md compiled and presented."
    return f"unrecognized STAGE '{stage}' — check egad.md's phase loop manually."


def build_reminder(task: str, block: str) -> str:
    stage = STAGE_RE.search(block)
    mode = MODE_RE.search(block)
    verdict = VERDICT_RE.search(block)
    final_phase = FINAL_PHASE_RE.search(block)
    stage_v = stage.group(1) if stage else None
    nxt = next_stage(stage_v, mode.group(1) if mode else None,
                      verdict.group(1) if verdict else None,
                      final_phase.group(1) if final_phase else None)
    return (
        f"Workflow reminder (egad.md phase loop, temp/{task}/log.md): "
        f"last recorded STAGE was {stage_v or '?'}"
        + (f" ({mode.group(1)} verdict {verdict.group(1)})" if mode and verdict else "")
        + f". Per the workflow, next up: {nxt}"
    )


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    prompt = data.get("tool_input", {}).get("prompt", "")
    task_m = TASK_DIR_RE.search(prompt)
    if not task_m:
        return
    task = task_m.group(1)
    log_path = PROJECT_DIR / "temp" / task / "log.md"
    try:
        log_text = log_path.read_text()
    except OSError:
        return
    block = last_dispatch_block(log_text)
    if block is None:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": build_reminder(task, block),
        }
    }))


def _demo() -> None:
    assert next_stage(None, None, None, None).startswith("INTERPRETATION")
    assert next_stage("INTERPRETATION", None, None, None) == "PLANNING — dispatch study_designer_agent for phase 0."
    assert next_stage("PLANNING", None, None, None).startswith("PEER_REVIEW")
    assert next_stage("PEER_REVIEW", "DESIGN-REVIEW", "APPROVE", None).startswith("USER_FEEDBACK")
    assert next_stage("PEER_REVIEW", "DESIGN-REVIEW", "REVISE-DESIGN", None).startswith("PLANNING")
    assert next_stage("USER_FEEDBACK", None, None, None).startswith("EXECUTION")
    assert next_stage("EXECUTION", None, None, None).startswith("PEER_REVIEW")
    assert "specialist" in next_stage("PEER_REVIEW", "RESULTS-REVIEW", "REVISE-ANALYSIS", None)
    assert next_stage("PEER_REVIEW", "RESULTS-REVIEW", "REVISE-DESIGN", None).startswith("PLANNING")
    assert "CANNOT-MEET" in next_stage("PEER_REVIEW", "RESULTS-REVIEW", "REVISE-DESIGN", None)
    assert next_stage("PEER_REVIEW", "RESULTS-REVIEW", "ACCEPT", "false") == "PLANNING — phase += 1."
    assert next_stage("PEER_REVIEW", "RESULTS-REVIEW", "ACCEPT", "true").startswith("USER_FEEDBACK")
    assert next_stage("REPORTING", None, None, None).startswith("done")
    assert next_stage("BOGUS", None, None, None).startswith("unrecognized")

    block = last_dispatch_block(
        "### [t1] dispatch -> `study_designer_agent` (x)\n- TASK-LEVEL: L2 | STAGE: PLANNING\n- result: (no structured verdict found)\n\n"
        "### [t2] dispatch -> `peer_reviewer_agent` (y)\n- TASK-LEVEL: L2 | STAGE: PEER_REVIEW\n- result: MODE=DESIGN-REVIEW, PHASE=0, VERDICT=APPROVE\n"
    )
    assert "STAGE: PEER_REVIEW" in block and "VERDICT=APPROVE" in block

    # user-turn blocks have no STAGE: — they must not shadow the last real dispatch
    block = last_dispatch_block(
        "### [t1] dispatch -> `peer_reviewer_agent` (y)\n- TASK-LEVEL: L2 | STAGE: PEER_REVIEW\n- result: MODE=DESIGN-REVIEW, PHASE=0, VERDICT=APPROVE\n\n"
        "### [t2] user turn\n> looks good, go ahead\n\n"
        "### [t3] user turn\n> also add a PCA\n"
    )
    assert "STAGE: PEER_REVIEW" in block
    assert "USER_FEEDBACK" in build_reminder("x", block)

    msg = build_reminder("x", block)
    assert "PEER_REVIEW" in msg and "USER_FEEDBACK" in msg

    assert last_dispatch_block("no blocks here") is None

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
