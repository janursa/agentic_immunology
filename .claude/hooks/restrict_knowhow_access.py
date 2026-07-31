#!/usr/bin/env python3
"""PreToolUse hook for study_designer_agent, peer_reviewer_agent, and
data_analyst_agent: (1) blocks reading knowhow/ or memory/ content directly,
(2) confines Read/Grep/Glob to the repo plus the documented data-lake roots.

(1) Why: those docs (aging_clocks.md, single_cell_rna_analysis.md, drug_repurposing.md,
safety_druggability.md, guardrail.md) are used by evaluate.md as an independent
"answer key" to grade plans/results against. If the planner, reviewer, or executor
can read them too, the evaluation stops being independent.

(2) Why: these agents were observed wandering into unrelated sibling folders
(other projects under ~/projs/ongoing, etc). They're confined to this repo plus
the external roots datalake_docs/ actually references (/vol/projects/CIIM,
/vol/projects/BIIM — symlinked per CLAUDE.md — and /vol/projects/jnourisa) and
/tmp (singularity runs, per CLAUDE.md).

Only Read/Grep/Glob calls with an explicit path/file_path are checked. A Grep/Glob
call with no path (repo-wide search, cwd = project root) is not caught —
# ponytail: static path check only, can't know what a pathless repo-wide grep
# will match; add a content-based scan if that proves to be an actual leak vector.
Bash is not covered — arbitrary shell text isn't reliably parseable for paths.

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
    "study_designer_agent": {"knowhow/design_graphs.md", "knowhow/task_levels.md"},
    "peer_reviewer_agent": {"knowhow/design_graphs.md", "knowhow/task_levels.md"},
}

# External roots datalake_docs/ actually references — everything else outside the repo is out of scope.
ALLOWED_EXTERNAL_ROOTS = (
    pathlib.Path("/vol/projects/CIIM"),
    pathlib.Path("/vol/projects/BIIM"),
    pathlib.Path("/vol/projects/jnourisa"),
    pathlib.Path("/tmp"),
)


def _under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


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

    resolved = pathlib.Path(path).resolve()

    if _under(resolved, PROJECT_DIR):
        rel = str(resolved.relative_to(PROJECT_DIR)).replace(os.sep, "/")
        if rel in CARVE_OUTS.get(agent_type, set()):
            return None
        if rel.startswith(RESTRICTED_DIRS):
            return (
                f"{agent_type} may not read knowhow/ or memory/ content directly "
                f"(blocked path: {rel}) — these are evaluate's independent grading "
                "reference; planner/reviewer/executor access would leak the answer key."
            )
        return None

    if any(_under(resolved, root) for root in ALLOWED_EXTERNAL_ROOTS):
        return None

    allowed = ", ".join(str(r) for r in (PROJECT_DIR, *ALLOWED_EXTERNAL_ROOTS))
    return (
        f"{agent_type} is confined to the agentic_immunology repo and the documented "
        f"data-lake roots ({allowed}) — blocked path: {resolved}"
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
    assert block_reason("study_designer_agent", "Read", {"file_path": "knowhow/design_graphs.md"}) is None
    assert block_reason("peer_reviewer_agent", "Read", {"file_path": "knowhow/design_graphs.md"}) is None
    assert block_reason("evaluate", "Read", {"file_path": "knowhow/aging_clocks.md"}) is None
    assert block_reason("study_designer_agent", "Read", {"file_path": "docs/datalake.md"}) is None
    assert block_reason("study_designer_agent", "Grep", {"pattern": "x"}) is None  # no path: known gap
    assert block_reason("", "Read", {"file_path": "knowhow/aging_clocks.md"}) is None  # main session, unrestricted
    # scope: repo and documented data-lake roots allowed
    assert block_reason("data_analyst_agent", "Read", {"file_path": "/vol/projects/CIIM/cohorts/x.h5ad"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "/vol/projects/BIIM/x.csv"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "/vol/projects/jnourisa/hira/x.csv"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "/tmp/scratch.txt"}) is None
    # scope: unrelated folders blocked
    assert block_reason("data_analyst_agent", "Read", {"file_path": "/home/jnourisa/projs/ongoing/application/kumar_2024/x.md"}) is not None
    assert block_reason("study_designer_agent", "Read", {"file_path": "../other_project/notes.md"}) is not None
    assert block_reason("peer_reviewer_agent", "Glob", {"path": "/vol/projects/other_lab", "pattern": "*"}) is not None
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
