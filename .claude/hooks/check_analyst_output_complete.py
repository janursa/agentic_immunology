#!/usr/bin/env python3
"""PostToolUse hook (matcher: Agent): after data_analyst_agent returns, verify its
WORK-DIR actually contains results.md and README.md (agents/data_analyst_agent.md
'Output dir structure'). report_format_check.py's PreToolUse hook validates
results.md's structure *when written* but can't catch a run that finishes without
ever writing one — this closes that gap after the fact and blocks the orchestrator
from moving on to RESULTS-REVIEW with an incomplete handoff.

Run from the repo root:
    python3 .claude/hooks/check_analyst_output_complete.py --self-test
"""
import json
import os
import pathlib
import re
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
WORKDIR_RE = re.compile(r"WORK-DIR:\s*(\S+)")
REQUIRED_FILES = ("results.md", "README.md")


def block_reason(subagent_type: str, prompt: str) -> str | None:
    if subagent_type != "data_analyst_agent":
        return None
    m = WORKDIR_RE.search(prompt)
    if not m:
        return None  # check_stage_tags.py already blocks a missing WORK-DIR at dispatch time
    workdir = pathlib.Path(m.group(1).strip("`'\""))
    if not workdir.is_absolute():
        workdir = PROJECT_DIR / workdir
    missing = [f for f in REQUIRED_FILES if not (workdir / f).exists()]
    if missing:
        return (
            f"data_analyst_agent returned but {workdir} is missing {missing} "
            "(agents/data_analyst_agent.md 'Output dir structure' requires both). "
            "Send it back to finish the report/readme before dispatching RESULTS-REVIEW."
        )
    return None


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Agent":
        return
    tool_input = data.get("tool_input", {})
    reason = block_reason(tool_input.get("subagent_type", ""), tool_input.get("prompt", ""))
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))


def _demo() -> None:
    import tempfile
    global PROJECT_DIR
    real_project_dir = PROJECT_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        workdir = PROJECT_DIR / "temp" / "x" / "phase_0" / "data_analyst"
        workdir.mkdir(parents=True)
        prompt = "TASK-LEVEL: L2\nWORK-DIR: temp/x/phase_0/data_analyst/\n"

        assert block_reason("data_analyst_agent", prompt) is not None  # both missing
        (workdir / "results.md").write_text("x")
        assert block_reason("data_analyst_agent", prompt) is not None  # README still missing
        (workdir / "README.md").write_text("x")
        assert block_reason("data_analyst_agent", prompt) is None

        assert block_reason("study_designer_agent", prompt) is None  # not scoped
        assert block_reason("data_analyst_agent", "no workdir here") is None  # fail-open
    PROJECT_DIR = real_project_dir
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
