#!/usr/bin/env python3
"""PreToolUse hook: every `Agent` call must open its prompt with
`TASK-LEVEL: L0|L1|L2|L3`, `WORK-DIR: <path>` and `STAGE: <value>` lines, the
tags drawn from docs/state_tags.json (egad.md HARD RULE). This turns
open-ended prose-guessing of "what stage is this call" into a validated, fixed
vocabulary that write_log.py's PostToolUse hook can tag log.md entries with.

Also blocks:
- a missing WORK-DIR, or one outside temp/. Which exact folder is the
  orchestrator's call (see egad.md's table) — only "it exists and it's
  in the output tree" is checked, so the table can move without breaking this;
- TASK-LEVEL silently flipping mid-task once log.md recorded a different value;
- L0 dispatching the planning loop. L0 means the orchestrator does it itself, so
  study_designer_agent/peer_reviewer_agent at L0 is a definitional contradiction.
  Utility agents (curate_paper, knowhow_audit) stay allowed;
- data_analyst_agent dispatched without a 'TASK-FILE: <abs path>' line pointing
  at an existing, non-empty file — egad.md has the orchestrator write
  {WORK-DIR}/task.md (scripts/extract_phase_task.py, phase n's design.md section
  verbatim) before dispatching, instead of retyping the task into the prompt.
- peer_reviewer_agent dispatched in RESULTS-REVIEW mode (a 'MODE: RESULTS-REVIEW'
  line) without 'CYCLE:', 'RESULTS-DIR: <abs path>' (existing dir), and
  'DESIGN-FILE: <abs path>' (existing file) lines — agents/peer_reviewer_agent.md
  'What you receive' needs the cycle number and both paths to fact-check results
  against actual output files; egad.md step 1.5 names them explicitly.

Whether a checkpoint is well-formed is semantic — that's DESIGN-REVIEW's job,
deliberately not checked here.

Run from the repo root:
    python3 .claude/hooks/check_stage_tags.py --self-test
"""
import json
import os
import pathlib
import re
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
TAGS_FILE = PROJECT_DIR / "egad" / "docs" / "state_tags.json"
TASK_DIR_RE = re.compile(r"temp/([A-Za-z0-9_\-]+)/")
WORKDIR_RE = re.compile(r"WORK-DIR:\s*(\S+)")
TASKFILE_RE = re.compile(r"TASK-FILE:\s*(\S+)")
MODE_RE = re.compile(r"MODE:\s*(\S+)")
CYCLE_RE = re.compile(r"CYCLE:\s*(\d+)")
RESULTSDIR_RE = re.compile(r"RESULTS-DIR:\s*(\S+)")
DESIGNFILE_RE = re.compile(r"DESIGN-FILE:\s*(\S+)")
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
            "and 'STAGE: <value>' lines (egad.md HARD RULE, docs/state_tags.json)."
        )
    if level not in valid_level:
        return f"TASK-LEVEL '{level}' is not one of {sorted(valid_level)} (docs/state_tags.json)."
    if stage not in valid_stage:
        return f"STAGE '{stage}' is not one of {sorted(valid_stage)} (docs/state_tags.json)."
    return None


def block_reason_workdir(prompt: str) -> str | None:
    m = WORKDIR_RE.search(prompt)
    if not m:
        return (
            "Agent call must open its prompt with a 'WORK-DIR: <path>' line — the exact "
            "folder the agent writes into (egad.md HARD RULE)."
        )
    workdir = m.group(1).strip("`'\"")
    rel = workdir[len(str(PROJECT_DIR)) + 1:] if workdir.startswith(str(PROJECT_DIR) + "/") else workdir
    if not rel.startswith("temp/"):
        return (
            f"WORK-DIR '{workdir}' is outside the output tree — it must be under "
            "temp/{task}/ (egad.md HARD RULE)."
        )
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
            "If this is an L3 task past the objective gate, keep TASK-LEVEL: L3 — "
            "'then as L2' is the procedure it follows, not a new tag."
        )
    return None


def block_reason_l0(prompt: str, subagent_type: str) -> str | None:
    if _extract(prompt, "TASK-LEVEL") != "L0" or subagent_type not in PLANNING_AGENTS:
        return None
    return (
        f"TASK-LEVEL L0 must not dispatch {subagent_type} — L0 means the orchestrator "
        "does the analysis itself (egad.md). Either do it directly, or "
        "reclassify the task to L1+ if it genuinely needs a plan."
    )


def block_reason_rerun_slot(prompt: str, subagent_type: str) -> str | None:
    """A second review dispatched into the folder that already holds the first
    one overwrites or clutters it — egad.md says re-runs get a suffixed
    folder. Only peer_reviewer_agent: study_designer_agent legitimately re-enters
    temp/{task}/ to append to design.md."""
    if subagent_type != "peer_reviewer_agent":
        return None
    m = WORKDIR_RE.search(prompt)
    if not m:
        return None
    raw = m.group(1).strip("`'\"")
    workdir = pathlib.Path(raw)
    if not workdir.is_absolute():
        workdir = PROJECT_DIR / workdir
    if any(workdir.glob("peer_review*.md")):
        return (
            f"WORK-DIR '{raw}' already holds a peer review — a re-run for the same slot "
            "must go to a suffixed folder (e.g. design_review_2/), not back into the "
            "same one (egad.md HARD RULE)."
        )
    return None


def block_reason_task_file(prompt: str, subagent_type: str) -> str | None:
    if subagent_type != "data_analyst_agent":
        return None
    m = TASKFILE_RE.search(prompt)
    if not m:
        return (
            "data_analyst_agent dispatch must include a 'TASK-FILE: <abs path>' line "
            "pointing at the {WORK-DIR}/task.md written for this phase "
            "(egad.md HARD RULE, scripts/extract_phase_task.py)."
        )
    path = pathlib.Path(m.group(1).strip("`'\""))
    if not path.is_absolute():
        return f"TASK-FILE '{path}' must be an absolute path (egad.md HARD RULE)."
    try:
        empty = path.stat().st_size == 0
    except OSError:
        return f"TASK-FILE '{path}' does not exist — write it before dispatching."
    if empty:
        return f"TASK-FILE '{path}' exists but is empty."
    return None


def _abs_existing(m: re.Match | None, tag: str, must_be_dir: bool) -> str | None:
    if not m:
        return f"'{tag}: <abs path>' line"
    path = pathlib.Path(m.group(1).strip("`'\""))
    if not path.is_absolute():
        return f"{tag} '{path}' must be an absolute path"
    ok = path.is_dir() if must_be_dir else path.is_file()
    if not ok:
        return f"{tag} '{path}' does not exist"
    return None


def block_reason_results_review_input(prompt: str, subagent_type: str) -> str | None:
    if subagent_type != "peer_reviewer_agent":
        return None
    mode = MODE_RE.search(prompt)
    if not mode or mode.group(1) != "RESULTS-REVIEW":
        return None
    missing = [m for m in (
        None if CYCLE_RE.search(prompt) else "'CYCLE: <n>' line",
        _abs_existing(RESULTSDIR_RE.search(prompt), "RESULTS-DIR", must_be_dir=True),
        _abs_existing(DESIGNFILE_RE.search(prompt), "DESIGN-FILE", must_be_dir=False),
    ) if m]
    if missing:
        return (
            "peer_reviewer_agent RESULTS-REVIEW dispatch is missing: " + "; ".join(missing) +
            " (egad.md step 1.5, agents/peer_reviewer_agent.md 'What you receive')."
        )
    return None


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    tool_input = data.get("tool_input", {})
    prompt = tool_input.get("prompt", "")
    subagent_type = tool_input.get("subagent_type", "")
    reason = (
        block_reason_tags(prompt, _load_tags())
        or block_reason_workdir(prompt)
        or block_reason_consistency(prompt)
        or block_reason_l0(prompt, subagent_type)
        or block_reason_rerun_slot(prompt, subagent_type)
        or block_reason_task_file(prompt, subagent_type)
        or block_reason_results_review_input(prompt, subagent_type)
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
    global PROJECT_DIR
    tags ={"TASK_LEVEL": {"L0": "", "L1": "", "L2": "", "L3": ""},
            "STAGE": {"PLANNING": "", "EXECUTION": ""}}
    assert block_reason_tags("no tags here", tags) is not None
    assert block_reason_tags("TASK-LEVEL: L2\nSTAGE: PLANNING\n...", tags) is None
    assert block_reason_tags("TASK-LEVEL: L9\nSTAGE: PLANNING", tags) is not None
    assert block_reason_tags("TASK-LEVEL: COMPLEX\nSTAGE: PLANNING", tags) is not None
    assert block_reason_tags("TASK-LEVEL: L2\nSTAGE: NOPE", tags) is not None
    assert block_reason_tags("...", {}) is None  # fail-open, no tags file

    assert block_reason_workdir("TASK-LEVEL: L2\nWORK-DIR: temp/x/phase_0/design_review/") is None
    assert block_reason_workdir(f"WORK-DIR: {PROJECT_DIR}/temp/x/") is None
    assert block_reason_workdir("TASK-LEVEL: L2\nSTAGE: PLANNING") is not None  # missing
    assert block_reason_workdir("WORK-DIR: output/x/") is not None  # outside temp/

    assert block_reason_l0("TASK-LEVEL: L0\nSTAGE: PLANNING", "study_designer_agent") is not None
    assert block_reason_l0("TASK-LEVEL: L0\nSTAGE: PEER_REVIEW", "peer_reviewer_agent") is not None
    assert block_reason_l0("TASK-LEVEL: L0\nSTAGE: EXECUTION", "curate_paper") is None
    assert block_reason_l0("TASK-LEVEL: L1\nSTAGE: PLANNING", "study_designer_agent") is None

    # consistency check against a real log.md
    import tempfile
    real_project_dir = PROJECT_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        log = PROJECT_DIR / "temp" / "demo_task" / "log.md"
        log.parent.mkdir(parents=True)
        log.write_text("TASK-LEVEL: L1\n")

        # re-running a review into an already-used slot must be blocked
        slot = PROJECT_DIR / "temp" / "demo_task" / "phase_0" / "design_review"
        slot.mkdir(parents=True)
        (slot / "peer_review.md").write_text("VERDICT: REVISE-DESIGN")
        used = "WORK-DIR: temp/demo_task/phase_0/design_review/"
        assert block_reason_rerun_slot(used, "peer_reviewer_agent") is not None
        assert block_reason_rerun_slot(used, "study_designer_agent") is None
        assert block_reason_rerun_slot(
            "WORK-DIR: temp/demo_task/phase_0/design_review_2/", "peer_reviewer_agent") is None

        assert block_reason_consistency("TASK-LEVEL: L1\nSTAGE: PLANNING\ntemp/demo_task/design.md") is None
        assert block_reason_consistency("TASK-LEVEL: L2\nSTAGE: PLANNING\ntemp/demo_task/design.md") is not None
        assert block_reason_consistency("TASK-LEVEL: L2\nSTAGE: PLANNING\ntemp/other_task/design.md") is None

        task_file = PROJECT_DIR / "temp" / "demo_task" / "phase_0" / "analyst" / "task.md"
        task_file.parent.mkdir(parents=True)
        assert block_reason_task_file("STAGE: EXECUTION", "data_analyst_agent") is not None  # missing line
        assert block_reason_task_file(f"TASK-FILE: {task_file}", "data_analyst_agent") is not None  # not written yet
        task_file.write_text("")
        assert block_reason_task_file(f"TASK-FILE: {task_file}", "data_analyst_agent") is not None  # empty
        task_file.write_text("## Plan phase 0\n...")
        assert block_reason_task_file(f"TASK-FILE: {task_file}", "data_analyst_agent") is None
        assert block_reason_task_file("TASK-FILE: relative/task.md", "data_analyst_agent") is not None  # not abs
        assert block_reason_task_file("STAGE: PLANNING", "study_designer_agent") is None  # not scoped

        results_dir = PROJECT_DIR / "temp" / "demo_task" / "phase_0" / "analyst" / "results"
        results_dir.mkdir(parents=True)
        design_file = PROJECT_DIR / "temp" / "demo_task" / "design.md"
        design_file.write_text("## Plan phase 0")
        full = (f"MODE: RESULTS-REVIEW\nCYCLE: 0\nRESULTS-DIR: {results_dir}\nDESIGN-FILE: {design_file}")
        assert block_reason_results_review_input(full, "peer_reviewer_agent") is None
        assert block_reason_results_review_input("MODE: DESIGN-REVIEW", "peer_reviewer_agent") is None  # wrong mode, not scoped
        assert block_reason_results_review_input(full, "study_designer_agent") is None  # not scoped
        assert block_reason_results_review_input("MODE: RESULTS-REVIEW", "peer_reviewer_agent") is not None  # everything missing
        assert block_reason_results_review_input(
            f"MODE: RESULTS-REVIEW\nCYCLE: 0\nRESULTS-DIR: results/relative\nDESIGN-FILE: {design_file}",
            "peer_reviewer_agent") is not None  # RESULTS-DIR not absolute
        assert block_reason_results_review_input(
            f"MODE: RESULTS-REVIEW\nCYCLE: 0\nRESULTS-DIR: {results_dir}/nope\nDESIGN-FILE: {design_file}",
            "peer_reviewer_agent") is not None  # RESULTS-DIR doesn't exist
    PROJECT_DIR = real_project_dir

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
