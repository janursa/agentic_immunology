#!/usr/bin/env python3
"""PreToolUse hook for study_designer_agent, peer_reviewer_agent, and
data_analyst_agent: confines Read/Grep/Glob to an explicit allowlist —
datalake/, datalake_docs/, docs/, scAnnotAgent/, singularity/, singularity_docs/,
temp/ (their own workspace: task.md, design.md, raw_data/, processed_data/, prior
phase results) — plus the documented external data-lake roots. Everything else in
the repo (knowhow/, memory/, application/, agents/, .claude/, draw/, root-level
files, ...) is blocked by default.

Why an allowlist, not a blocklist: knowhow/'s methodology docs are evaluate.md's
independent "answer key", and application/{author-year}-q*.md (curate_paper's
output) is rubric_agent's CASE-CARD — the source paper's own findings used to
score a run. If the planner, reviewer, or executor can read either, the
evaluation stops being independent. (Caught in practice: study_designer_agent
pulled application/terekhova_2023/'s curated findings into design.md as
"positive controls" for the abf300_aging task, without disclosing they came from
the paper being reproduced rather than being independently derived.) A blocklist
only stops leaks you already thought of; these agents were also observed
wandering into unrelated sibling folders (other projects under ~/projs/ongoing,
etc), so the allowlist closes both at once.

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

# Called out by name because they're answer keys, not just out-of-scope folders.
ANSWER_KEY_DIRS = ("knowhow/", "memory/", "application/")

# Everything these agents may read inside the repo. temp/ is their own workspace
# (task.md, design.md, raw_data/, processed_data/, prior-phase results/reviews).
ALLOWED_DIRS = (
    "datalake/", "datalake_docs/", "docs/", "scAnnotAgent/",
    "singularity/", "singularity_docs/", "temp/",
)

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


def _in_dirs(rel: str, dirs: tuple[str, ...]) -> bool:
    return any(rel == d.rstrip("/") or rel.startswith(d) for d in dirs)


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
        rel = "" if resolved == PROJECT_DIR else str(resolved.relative_to(PROJECT_DIR)).replace(os.sep, "/")
        if _in_dirs(rel, ANSWER_KEY_DIRS):
            return (
                f"{agent_type} may not read knowhow/, memory/, or application/ content "
                f"directly (blocked path: {rel}) — these are evaluate's/rubric_agent's "
                "independent grading reference; planner/reviewer/executor access would "
                "leak the answer key."
            )
        if _in_dirs(rel, ALLOWED_DIRS):
            return None
        return (
            f"{agent_type} may only read datalake/, datalake_docs/, docs/, scAnnotAgent/, "
            f"singularity/, singularity_docs/, or temp/ inside the repo — blocked path: {rel or '.'}"
        )

    if any(_under(resolved, root) for root in ALLOWED_EXTERNAL_ROOTS):
        return None

    allowed = ", ".join(str(r) for r in ALLOWED_EXTERNAL_ROOTS)
    return (
        f"{agent_type} is confined to the agentic_immunology repo's allowlisted folders and "
        f"the documented data-lake roots ({allowed}) — blocked path: {resolved}"
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
    # answer-key dirs: blocked with the specific message
    assert block_reason("study_designer_agent", "Read", {"file_path": "knowhow/aging_clocks.md"}) is not None
    assert block_reason("peer_reviewer_agent", "Read", {"file_path": "memory/guardrail.md"}) is not None
    assert block_reason("data_analyst_agent", "Grep", {"path": "memory/guardrail.md", "pattern": "x"}) is not None
    assert block_reason("study_designer_agent", "Read", {"file_path": "application/terekhova_2023/terekhova_2023-q1.md"}) is not None
    # allowlisted dirs: reachable by every restricted agent
    assert block_reason("data_analyst_agent", "Read", {"file_path": "docs/computing_sbatch.md"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "docs/plotting.md"}) is None
    assert block_reason("study_designer_agent", "Read", {"file_path": "docs/design_graphs.md"}) is None
    assert block_reason("peer_reviewer_agent", "Read", {"file_path": "docs/design_graphs.md"}) is None
    assert block_reason("peer_reviewer_agent", "Read", {"file_path": "docs/reporting.md"}) is None
    assert block_reason("study_designer_agent", "Read", {"file_path": "docs/datalake.md"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "datalake/ciim/x.h5ad"}) is None
    assert block_reason("study_designer_agent", "Read", {"file_path": "datalake_docs/omics/hira/list.md"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "scAnnotAgent/README.md"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "singularity/images.sif"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "singularity_docs/list.md"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "temp/abf300_aging/design.md"}) is None
    assert block_reason("data_analyst_agent", "Read", {"file_path": "temp/abf300_aging/raw_data/x.h5ad"}) is None
    # everything else in the repo: blocked, not just the previously-known offenders
    assert block_reason("study_designer_agent", "Read", {"file_path": "agents/data_analyst_agent.md"}) is not None
    assert block_reason("data_analyst_agent", "Read", {"file_path": ".claude/settings.json"}) is not None
    assert block_reason("peer_reviewer_agent", "Read", {"file_path": "draw/overview.drawio"}) is not None
    assert block_reason("study_designer_agent", "Read", {"file_path": "ciim_agentic.md"}) is not None
    assert block_reason("evaluate", "Read", {"file_path": "knowhow/aging_clocks.md"}) is None
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
