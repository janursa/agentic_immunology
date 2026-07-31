#!/usr/bin/env python3
"""PreToolUse hook: every `Agent` call must open its prompt with
`TASK-LEVEL: L0|L1|L2|L3` and `STAGE: <value>` lines, both drawn from
docs/state_tags.json (ciim_agentic.md HARD RULE). This turns open-ended
prose-guessing of "what stage is this call" into a validated, fixed
vocabulary that write_log.py's PostToolUse hook can tag log.md entries with.

Also blocks:
- TASK-LEVEL silently flipping mid-task once log.md recorded a different value;
- L0 dispatching the planning loop. L0 means the orchestrator does it itself, so
  study_designer_agent/peer_reviewer_agent at L0 is a definitional contradiction.
  Utility agents (data_download_agent, curate_paper) stay allowed.

Whether the checkpoint is *really* a rubric is semantic — that's DESIGN-REVIEW's
job, deliberately not checked here.

Run from the repo root:
    python3 .claude/hooks/check_stage_tags.py --self-test
"""
import json
import os
import pathlib
import re
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
TAGS_FILE = PROJECT_DIR / "docs" / "state_tags.json"
TASK_DIR_RE = re.compile(r"temp/([A-Za-z0-9_\-]+)/")
PLANNING_AGENTS = {"study_designer_agent", "peer_reviewer_agent"}


def _load_tags() -> dict:
    try:
        return json.loads(TAGS_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _extract(prompt: str, tag: str) -> str | None:
    m = re.search(rf"{tag}:\s*([A-Z0-9_]+)", prompt)
    return m.group(1) if m else None


def block_reason_tags(prompt: str, tags: dict) -> str | None:
    if not tags:
        return None  # ponytail: fail-open if docs/state_tags.json is missing/unreadable
    level = _extract(prompt, "TASK-LEVEL")
    stage = _extract(prompt, "STAGE")
    valid_level = set(tags.get("TASK_LEVEL", {}))
    valid_stage = set(tags.get("STAGE", {}))

    if level is None or stage is None:
        return (
            "Agent call must open its prompt with 'TASK-LEVEL: L0|L1|L2|L3' "
            "and 'STAGE: <value>' lines (ciim_agentic.md HARD RULE, docs/state_tags.json)."
        )
    if level not in valid_level:
        return f"TASK-LEVEL '{level}' is not one of {sorted(valid_level)} (docs/state_tags.json)."
    if stage not in valid_stage:
        return f"STAGE '{stage}' is not one of {sorted(valid_stage)} (docs/state_tags.json)."
    return None


def _existing_level(task: str) -> str | None:
    log_path = PROJECT_DIR / "temp" / task / "log.md"
    try:
        text = log_path.read_text()
    except OSError:
        return None
    matches = re.findall(r"TASK-LEVEL:\s*(L[0-9])", text)
    return matches[0] if matches else None


def block_reason_consistency(prompt: str) -> str | None:
    task = TASK_DIR_RE.search(prompt)
    level = _extract(prompt, "TASK-LEVEL")
    if not task or not level:
        return None
    prior = _existing_level(task.group(1))
    if prior and prior != level:
        return (
            f"TASK-LEVEL changed from {prior} to {level} for the same task "
            f"(temp/{task.group(1)}/log.md) — a task's level shouldn't flip mid-run. "
            "If this is a LEVEL-MISMATCH reclassification from study_designer_agent, "
            "note that in log.md first."
        )
    return None


def block_reason_l0(prompt: str, subagent_type: str) -> str | None:
    if _extract(prompt, "TASK-LEVEL") != "L0" or subagent_type not in PLANNING_AGENTS:
        return None
    return (
        f"TASK-LEVEL L0 must not dispatch {subagent_type} — L0 means the orchestrator "
        "does the analysis itself (ciim_agentic.md). Either do it directly, or "
        "reclassify the task to L1+ if it genuinely needs a plan."
    )


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    tool_input = data.get("tool_input", {})
    prompt = tool_input.get("prompt", "")
    reason = (
        block_reason_tags(prompt, _load_tags())
        or block_reason_consistency(prompt)
        or block_reason_l0(prompt, tool_input.get("subagent_type", ""))
    )
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))


def _demo() -> None:
    tags = {"TASK_LEVEL": {"L0": "", "L1": "", "L2": "", "L3": ""},
            "STAGE": {"PLANNING": "", "EXECUTION": ""}}
    assert block_reason_tags("no tags here", tags) is not None
    assert block_reason_tags("TASK-LEVEL: L2\nSTAGE: PLANNING\n...", tags) is None
    assert block_reason_tags("TASK-LEVEL: L9\nSTAGE: PLANNING", tags) is not None
    assert block_reason_tags("TASK-LEVEL: COMPLEX\nSTAGE: PLANNING", tags) is not None
    assert block_reason_tags("TASK-LEVEL: L2\nSTAGE: NOPE", tags) is not None
    assert block_reason_tags("...", {}) is None  # fail-open, no tags file

    assert block_reason_l0("TASK-LEVEL: L0\nSTAGE: PLANNING", "study_designer_agent") is not None
    assert block_reason_l0("TASK-LEVEL: L0\nSTAGE: PEER_REVIEW", "peer_reviewer_agent") is not None
    assert block_reason_l0("TASK-LEVEL: L0\nSTAGE: EXECUTION", "data_download_agent") is None
    assert block_reason_l0("TASK-LEVEL: L1\nSTAGE: PLANNING", "study_designer_agent") is None

    # consistency check against a real log.md
    import tempfile
    global PROJECT_DIR
    real_project_dir = PROJECT_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        log = PROJECT_DIR / "temp" / "demo_task" / "log.md"
        log.parent.mkdir(parents=True)
        log.write_text("TASK-LEVEL: L1\n")
        assert block_reason_consistency("TASK-LEVEL: L1\nSTAGE: PLANNING\ntemp/demo_task/design.md") is None
        assert block_reason_consistency("TASK-LEVEL: L2\nSTAGE: PLANNING\ntemp/demo_task/design.md") is not None
        assert block_reason_consistency("TASK-LEVEL: L2\nSTAGE: PLANNING\ntemp/other_task/design.md") is None
    PROJECT_DIR = real_project_dir

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
