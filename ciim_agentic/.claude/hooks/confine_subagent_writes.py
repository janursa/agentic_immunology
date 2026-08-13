#!/usr/bin/env python3
"""PreToolUse hook (matcher: Write, Edit): study_designer_agent, peer_reviewer_agent,
and data_analyst_agent may only write/edit files under ${CIIM_TEMP_DIR} (default:
temp/) — mirrors restrict_knowhow_access.py's read-side confinement, same
RESTRICTED_AGENTS set, same reasoning (ciim_agentic.md 'only use the host project
root as your workspace' plus the data lake / knowhow being read-only to these
agents).

Run from the repo root:
    python3 .claude/hooks/confine_subagent_writes.py --self-test
"""
import json
import os
import pathlib
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
_temp = os.environ.get("CIIM_TEMP_DIR", "temp")
TEMP_DIR = pathlib.Path(_temp) if pathlib.Path(_temp).is_absolute() else PROJECT_DIR / _temp
TEMP_DIR = TEMP_DIR.resolve()

RESTRICTED_AGENTS = {"study_designer_agent", "peer_reviewer_agent", "data_analyst_agent"}


def block_reason(agent_type: str, tool_name: str, tool_input: dict) -> str | None:
    if agent_type not in RESTRICTED_AGENTS or tool_name not in ("Write", "Edit"):
        return None
    path = tool_input.get("file_path")
    if not path:
        return None
    resolved = pathlib.Path(path).resolve()
    try:
        resolved.relative_to(TEMP_DIR)
        return None
    except ValueError:
        return (
            f"{agent_type} may only write/edit files under ${{CIIM_TEMP_DIR}} "
            f"(blocked path: {resolved}) — ciim_agentic.md HARD RULE."
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
    assert block_reason("data_analyst_agent", "Write", {"file_path": "temp/x/results.md"}) is None
    assert block_reason("data_analyst_agent", "Edit", {"file_path": "temp/x/phase_0/y/results.md"}) is None
    assert block_reason("data_analyst_agent", "Write", {"file_path": "docs/datalake.md"}) is not None
    assert block_reason("data_analyst_agent", "Write", {"file_path": "agents/data_analyst_agent.md"}) is not None
    assert block_reason("study_designer_agent", "Write", {"file_path": "../other_project/x.md"}) is not None
    assert block_reason("peer_reviewer_agent", "Write", {"file_path": "temp/x/peer_review.md"}) is None
    assert block_reason("", "Write", {"file_path": "docs/datalake.md"}) is None  # main session, unrestricted
    assert block_reason("data_analyst_agent", "Read", {"file_path": "docs/datalake.md"}) is None  # not covered
    assert block_reason("data_analyst_agent", "Write", {}) is None  # no path: fail-open
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
