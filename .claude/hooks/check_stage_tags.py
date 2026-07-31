#!/usr/bin/env python3
"""PreToolUse hook: every `Agent` call must open its prompt with
`TASK-COMPLEXITY: SIMPLE|COMPLEX` and `STAGE: <value>` lines, both drawn from
docs/state_tags.json (ciim_agentic.md HARD RULE). This turns open-ended
prose-guessing of "what stage is this call" into a validated, fixed
vocabulary that write_log.py's PostToolUse hook can tag log.md entries with.

Also blocks TASK-COMPLEXITY silently flipping mid-task: a task's complexity
classification (SIMPLE vs COMPLEX) shouldn't change once log.md already
recorded a different value for it.

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


def _load_tags() -> dict:
    try:
        return json.loads(TAGS_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _extract(prompt: str, tag: str) -> str | None:
    m = re.search(rf"{tag}:\s*([A-Z_]+)", prompt)
    return m.group(1) if m else None


def block_reason_tags(prompt: str, tags: dict) -> str | None:
    if not tags:
        return None  # ponytail: fail-open if docs/state_tags.json is missing/unreadable
    complexity = _extract(prompt, "TASK-COMPLEXITY")
    stage = _extract(prompt, "STAGE")
    valid_complexity = set(tags.get("TASK_COMPLEXITY", {}))
    valid_stage = set(tags.get("STAGE", {}))

    if complexity is None or stage is None:
        return (
            "Agent call must open its prompt with 'TASK-COMPLEXITY: SIMPLE|COMPLEX' "
            "and 'STAGE: <value>' lines (ciim_agentic.md HARD RULE, docs/state_tags.json)."
        )
    if complexity not in valid_complexity:
        return f"TASK-COMPLEXITY '{complexity}' is not one of {sorted(valid_complexity)} (docs/state_tags.json)."
    if stage not in valid_stage:
        return f"STAGE '{stage}' is not one of {sorted(valid_stage)} (docs/state_tags.json)."
    return None


def _existing_complexity(task: str) -> str | None:
    log_path = PROJECT_DIR / "temp" / task / "log.md"
    try:
        text = log_path.read_text()
    except OSError:
        return None
    matches = re.findall(r"TASK-COMPLEXITY:\s*([A-Z]+)", text)
    return matches[0] if matches else None


def block_reason_consistency(prompt: str) -> str | None:
    task = TASK_DIR_RE.search(prompt)
    complexity = _extract(prompt, "TASK-COMPLEXITY")
    if not task or not complexity:
        return None
    prior = _existing_complexity(task.group(1))
    if prior and prior != complexity:
        return (
            f"TASK-COMPLEXITY changed from {prior} to {complexity} for the same task "
            f"(temp/{task.group(1)}/log.md) — a task's complexity classification shouldn't "
            "flip mid-run; if this is deliberate, note why in log.md first."
        )
    return None


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    prompt = data.get("tool_input", {}).get("prompt", "")
    reason = block_reason_tags(prompt, _load_tags()) or block_reason_consistency(prompt)
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))


def _demo() -> None:
    tags = {"TASK_COMPLEXITY": {"SIMPLE": "", "COMPLEX": ""}, "STAGE": {"PLANNING": "", "EXECUTION": ""}}
    assert block_reason_tags("no tags here", tags) is not None
    assert block_reason_tags("TASK-COMPLEXITY: COMPLEX\nSTAGE: PLANNING\n...", tags) is None
    assert block_reason_tags("TASK-COMPLEXITY: WEIRD\nSTAGE: PLANNING", tags) is not None
    assert block_reason_tags("TASK-COMPLEXITY: COMPLEX\nSTAGE: NOPE", tags) is not None
    assert block_reason_tags("...", {}) is None  # fail-open, no tags file

    # consistency check against a real log.md
    import tempfile
    global PROJECT_DIR
    real_project_dir = PROJECT_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        log = PROJECT_DIR / "temp" / "demo_task" / "log.md"
        log.parent.mkdir(parents=True)
        log.write_text("TASK-COMPLEXITY: SIMPLE\n")
        assert block_reason_consistency("TASK-COMPLEXITY: SIMPLE\nSTAGE: PLANNING\ntemp/demo_task/design.md") is None
        assert block_reason_consistency("TASK-COMPLEXITY: COMPLEX\nSTAGE: PLANNING\ntemp/demo_task/design.md") is not None
        assert block_reason_consistency("TASK-COMPLEXITY: COMPLEX\nSTAGE: PLANNING\ntemp/other_task/design.md") is None
    PROJECT_DIR = real_project_dir

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
