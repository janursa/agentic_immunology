#!/usr/bin/env python3
"""PreToolUse hook: block study_designer_agent, peer_reviewer_agent, and
data_analyst_agent from reading knowhow/ or memory/ content directly.

Why: those docs (aging_clocks.md, single_cell_rna_analysis.md, drug_repurposing.md,
safety_druggability.md, guardrail.md) are used by evaluate.md as an independent
"answer key" to grade plans/results against. If the planner, reviewer, or executor
can read them too, the evaluation stops being independent.

Only Read/Grep/Glob calls with an explicit path/file_path targeting knowhow/ or
memory/ are blocked. A Grep call with no path (repo-wide search) is not caught —
# ponytail: static path check only, can't know what a pathless repo-wide grep
# will match; add a content-based scan if that proves to be an actual leak vector.

Run from the repo root:
    python3 .claude/hooks/restrict_knowhow_access.py --self-test
"""
import json
import os
import pathlib
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

RESTRICTED_AGENTS = {"study_designer_agent", "peer_reviewer_agent", "data_analyst_agent"}
RESTRICTED_DIRS = ("knowhow/", "memory/")

# Paths each restricted agent still legitimately needs (operational, not methodology/evaluation content).
CARVE_OUTS = {
    "data_analyst_agent": {"knowhow/computing_sbatch.md"},
}


def _rel_path(path_str: str) -> str:
    p = pathlib.Path(path_str)
    try:
        p = p.resolve().relative_to(PROJECT_DIR)
    except ValueError:
        pass
    return str(p).replace(os.sep, "/")


def block_reason(agent_type: str, tool_name: str, tool_input: dict) -> str | None:
    if agent_type not in RESTRICTED_AGENTS:
        return None
    if tool_name == "Read":
        path = tool_input.get("file_path")
    elif tool_name in ("Grep", "Glob"):
        path = tool_input.get("path")
    else:
        return None
    if not path:
        return None
    rel = _rel_path(path)
    if rel in CARVE_OUTS.get(agent_type, set()):
        return None
    if not rel.startswith(RESTRICTED_DIRS):
        return None
    return (
        f"{agent_type} may not read knowhow/ or memory/ content directly "
        f"(blocked path: {rel}) — these are evaluate's independent grading "
        "reference; planner/reviewer/executor access would leak the answer key."
    )


def main() -> None:
    data = json.load(sys.stdin)
    reason = block_reason(
        data.get("agent_type", ""), data.get("tool_name", ""), data.get("tool_input", {})
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
    assert block_reason("study_designer_agent", "Read", {"file_path": "knowhow/aging_clocks.md"}) is not None
    assert block_reason("peer_reviewer_agent", "Read", {"file_path": "memory/guardrail.md"}) is not None
    assert block_reason("data_analyst_agent", "Grep", {"path": "memory/guardrail.md", "pattern": "x"}) is not None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "knowhow/computing_sbatch.md"}) is None
    assert block_reason("evaluate", "Read", {"file_path": "knowhow/aging_clocks.md"}) is None
    assert block_reason("study_designer_agent", "Read", {"file_path": "docs/datalake.md"}) is None
    assert block_reason("study_designer_agent", "Grep", {"pattern": "x"}) is None  # no path: known gap
    assert block_reason("", "Read", {"file_path": "knowhow/aging_clocks.md"}) is None  # main session, unrestricted
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
