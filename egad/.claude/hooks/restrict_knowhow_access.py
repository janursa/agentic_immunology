#!/usr/bin/env python3
"""PreToolUse hook for study_designer_agent, peer_reviewer_agent, and
data_analyst_agent: confines Read/Grep/Glob to an explicit allowlist —
datalake_docs/, docs/, scAnnotAgent/, singularity_docs/ (all under
PROJECT_DIR, i.e. egad/ itself, the directory `claude` is launched
from) and ${CIIM_TEMP_DIR} (their own workspace: task.md, design.md,
raw_data/, processed_data/, prior phase results) — plus the documented
external data-lake roots (datalake/eqtl files etc. live under
$CIIM_DATALAKE_DIR, images under $CIIM_SINGULARITY_DIR — both outside
PROJECT_DIR entirely). Everything else — knowhow/ (inside PROJECT_DIR), and
memory_bank/, application/, agents/, .claude/, draw/, root-level files (inside
$CIIM_MAIN_DIR, the host project root one level up) — is blocked by default.

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

Run from egad/:
    python3 .claude/hooks/restrict_knowhow_access.py --self-test
"""
import json
import os
import pathlib
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
# Host project root, one level up from egad/ — where memory_bank/, application/
# etc. actually live. Falls back to PROJECT_DIR's parent, which is correct by
# construction (egad/ is always installed one level under the host root).
MAIN_DIR = pathlib.Path(os.environ.get("CIIM_MAIN_DIR", str(PROJECT_DIR.parent))).resolve()

RESTRICTED_AGENTS = {"study_designer_agent", "peer_reviewer_agent", "data_analyst_agent"}

# Their own workspace (task.md, design.md, raw_data/, processed_data/,
# prior-phase results/reviews). May be inside PROJECT_DIR (default: "temp")
# or an external absolute path — checked separately from ALLOWED_DIRS below
# since it isn't necessarily under PROJECT_DIR.
_temp_env = os.environ.get("CIIM_TEMP_DIR", "temp")
TEMP_DIR = (pathlib.Path(_temp_env) if pathlib.Path(_temp_env).is_absolute() else PROJECT_DIR / _temp_env).resolve()

# Answer-key dirs, named by name because they're that, not just out-of-scope
# folders. knowhow/ lives inside PROJECT_DIR (egad/ itself); memory_bank/
# and application/ live at the host root (MAIN_DIR), one level up.
PROJECT_ANSWER_KEY_DIRS = ("knowhow/",)
MAIN_ANSWER_KEY_DIRS = ("memory_bank/", "application/")

# Everything else these agents may read inside PROJECT_DIR (egad/).
ALLOWED_DIRS = ("datalake_docs/", "docs/", "scAnnotAgent/", "singularity_docs/")

# External roots datalake_docs/ actually references — everything else outside the repo is out of scope.
ALLOWED_EXTERNAL_ROOTS = (
    pathlib.Path("/vol/projects/CIIM"),
    pathlib.Path("/vol/projects/BIIM"),
    pathlib.Path("/vol/projects/jnourisa"),
    pathlib.Path("/tmp"),
)

ANSWER_KEY_MSG = (
    "{agent} may not read knowhow/, memory_bank/, or application/ content directly "
    "(blocked path: {rel}) — these are evaluate's/rubric_agent's independent "
    "grading reference; planner/reviewer/executor access would leak the answer key."
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

    if _under(resolved, TEMP_DIR):
        return None

    if _under(resolved, PROJECT_DIR):
        rel = "" if resolved == PROJECT_DIR else str(resolved.relative_to(PROJECT_DIR)).replace(os.sep, "/")
        if _in_dirs(rel, PROJECT_ANSWER_KEY_DIRS):
            return ANSWER_KEY_MSG.format(agent=agent_type, rel=rel)
        if _in_dirs(rel, ALLOWED_DIRS):
            return None
        return (
            f"{agent_type} may only read datalake_docs/, docs/, scAnnotAgent/, "
            f"singularity_docs/, or ${{CIIM_TEMP_DIR}} inside egad/ — "
            f"blocked path: {rel or '.'}"
        )

    if _under(resolved, MAIN_DIR):
        rel_main = str(resolved.relative_to(MAIN_DIR)).replace(os.sep, "/")
        if _in_dirs(rel_main, MAIN_ANSWER_KEY_DIRS):
            return ANSWER_KEY_MSG.format(agent=agent_type, rel=rel_main)
        return (
            f"{agent_type} is confined to egad/'s allowlisted folders and "
            f"the documented data-lake roots — blocked path: {rel_main}"
        )

    if any(_under(resolved, root) for root in ALLOWED_EXTERNAL_ROOTS):
        return None

    allowed = ", ".join(str(r) for r in ALLOWED_EXTERNAL_ROOTS)
    return (
        f"{agent_type} is confined to the repo's allowlisted folders and "
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
    global PROJECT_DIR, MAIN_DIR, TEMP_DIR
    import tempfile
    real_project_dir, real_main_dir, real_temp_dir = PROJECT_DIR, MAIN_DIR, TEMP_DIR
    with tempfile.TemporaryDirectory() as tmp:
        MAIN_DIR = pathlib.Path(tmp).resolve()
        PROJECT_DIR = (MAIN_DIR / "egad").resolve()
        PROJECT_DIR.mkdir()
        TEMP_DIR = (MAIN_DIR / "temp").resolve()

        # project-level answer key: blocked with the specific message
        assert block_reason("study_designer_agent", "Read", {"file_path": str(PROJECT_DIR / "knowhow/aging_clocks.md")}) is not None
        # host-level answer keys: blocked with the specific message
        assert block_reason("peer_reviewer_agent", "Read", {"file_path": str(MAIN_DIR / "memory_bank/guardrail.md")}) is not None
        assert block_reason("data_analyst_agent", "Grep", {"path": str(MAIN_DIR / "memory_bank/guardrail.md"), "pattern": "x"}) is not None
        assert block_reason("study_designer_agent", "Read", {"file_path": str(MAIN_DIR / "application/terekhova_2023/terekhova_2023-q1.md")}) is not None
        # allowlisted dirs (under PROJECT_DIR): reachable by every restricted agent
        assert block_reason("data_analyst_agent", "Read", {"file_path": str(PROJECT_DIR / "docs/computing_sbatch.md")}) is None
        assert block_reason("data_analyst_agent", "Read", {"file_path": str(PROJECT_DIR / "docs/plotting.md")}) is None
        assert block_reason("study_designer_agent", "Read", {"file_path": str(PROJECT_DIR / "docs/design_graphs.md")}) is None
        assert block_reason("peer_reviewer_agent", "Read", {"file_path": str(PROJECT_DIR / "docs/reporting.md")}) is None
        assert block_reason("study_designer_agent", "Read", {"file_path": str(PROJECT_DIR / "docs/datalake.md")}) is None
        assert block_reason("study_designer_agent", "Read", {"file_path": str(PROJECT_DIR / "datalake_docs/omics/hira/list.md")}) is None
        assert block_reason("data_analyst_agent", "Read", {"file_path": str(PROJECT_DIR / "scAnnotAgent/README.md")}) is None
        assert block_reason("data_analyst_agent", "Read", {"file_path": str(PROJECT_DIR / "singularity_docs/list.md")}) is None
        assert block_reason("data_analyst_agent", "Read", {"file_path": str(TEMP_DIR / "abf300_aging/design.md")}) is None
        assert block_reason("data_analyst_agent", "Read", {"file_path": str(TEMP_DIR / "abf300_aging/raw_data/x.h5ad")}) is None
        # $CIIM_DATALAKE_DIR/$CIIM_SINGULARITY_DIR are external absolute paths (e.g.
        # /vol/projects/CIIM/...) — outside MAIN_DIR entirely, allowed via
        # ALLOWED_EXTERNAL_ROOTS, not the repo allowlist.
        assert block_reason("data_analyst_agent", "Read", {"file_path": "/vol/projects/CIIM/agentic/datalake/ciim/x.h5ad"}) is None
        # everything else at the host root: blocked, not just the previously-known offenders
        assert block_reason("study_designer_agent", "Read", {"file_path": str(PROJECT_DIR / "agents/data_analyst_agent.md")}) is not None
        assert block_reason("data_analyst_agent", "Read", {"file_path": str(MAIN_DIR / ".claude/settings.json")}) is not None
        assert block_reason("peer_reviewer_agent", "Read", {"file_path": str(MAIN_DIR / "draw/overview.drawio")}) is not None
        assert block_reason("study_designer_agent", "Read", {"file_path": str(PROJECT_DIR / "egad.md")}) is not None
        assert block_reason("evaluate", "Read", {"file_path": str(PROJECT_DIR / "knowhow/aging_clocks.md")}) is None
        assert block_reason("study_designer_agent", "Grep", {"pattern": "x"}) is None  # no path: known gap
        assert block_reason("", "Read", {"file_path": str(PROJECT_DIR / "knowhow/aging_clocks.md")}) is None  # main session, unrestricted
        # scope: documented data-lake roots allowed
        assert block_reason("data_analyst_agent", "Read", {"file_path": "/vol/projects/CIIM/cohorts/x.h5ad"}) is None
        assert block_reason("data_analyst_agent", "Read", {"file_path": "/vol/projects/BIIM/x.csv"}) is None
        assert block_reason("data_analyst_agent", "Read", {"file_path": "/vol/projects/jnourisa/hira/x.csv"}) is None
        assert block_reason("data_analyst_agent", "Read", {"file_path": "/tmp/scratch.txt"}) is None
        # scope: unrelated folders blocked
        assert block_reason("data_analyst_agent", "Read", {"file_path": "/home/jnourisa/projs/ongoing/application/kumar_2024/x.md"}) is not None
        assert block_reason("study_designer_agent", "Read", {"file_path": str(MAIN_DIR / "../other_project/notes.md")}) is not None
        assert block_reason("peer_reviewer_agent", "Glob", {"path": "/vol/projects/other_lab", "pattern": "*"}) is not None
    PROJECT_DIR, MAIN_DIR, TEMP_DIR = real_project_dir, real_main_dir, real_temp_dir
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
