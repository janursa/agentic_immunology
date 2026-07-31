#!/usr/bin/env python3
"""Writes temp/{task}/log.md automatically — the orchestrator never writes it
itself, so it can't be forgotten or self-report something that didn't happen.
Two hook events:

1. UserPromptSubmit: every real human message is buffered to
   temp/.hook_state/{session_id}.jsonl — the task dir isn't known yet at this
   point (this fires before any Agent call resolves it, including the very
   first prompt of a task).
2. PostToolUse (Agent): once a call's prompt resolves a `temp/<task>/` dir,
   any buffered prompts are flushed into that task's log.md as user-turn
   entries, followed by a structured dispatch entry for this call — subagent,
   TASK-LEVEL, STAGE, and (parsed from the subagent's actual returned
   text, re-derived from the transcript, not self-reported) MODE/PHASE/
   VERDICT/FINAL_PHASE when present.

Replaces check_log_updated.py: there is nothing left for the orchestrator to
forget, since it never writes log.md itself.

Same transcript-scanning approach as check_log_updated.py — session .jsonl
format is internal to Claude Code and can change between versions, so this
fails open (writes nothing) on read/parse errors rather than block anything.

Run from the repo root:
    python3 .claude/hooks/write_log.py --self-test
"""
import json
import os
import pathlib
import re
import sys
from datetime import datetime, timezone

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
HOOK_STATE_DIR = PROJECT_DIR / "temp" / ".hook_state"

TASK_DIR_RE = re.compile(r"temp/([A-Za-z0-9_\-]+)/")
TAG_RE = lambda tag: re.compile(rf"{tag}:\s*([A-Z0-9_]+)")  # noqa: E731
VERDICT_RE = re.compile(r"VERDICT:\s*(APPROVE|REVISE-DESIGN|ACCEPT|REVISE|CANNOT-MEET)", re.I)
MODE_RE = re.compile(r"MODE:\s*(DESIGN-REVIEW|RESULTS-REVIEW|METHOD-REVIEW)", re.I)
PHASE_RE = re.compile(r"PHASE:\s*(\d+)", re.I)
FINAL_PHASE_RE = re.compile(r"FINAL_PHASE:\s*(true|false)", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def task_dir_from_prompt(prompt: str) -> str | None:
    m = TASK_DIR_RE.search(prompt)
    return m.group(1) if m else None


def _tag_value(prompt: str, tag: str) -> str | None:
    m = TAG_RE(tag).search(prompt)
    return m.group(1) if m else None


# --- pending user-turn buffer (task dir unknown until the next Agent call) ---

def _buffer_path(session_id: str) -> pathlib.Path:
    return HOOK_STATE_DIR / f"{session_id}.jsonl"


def append_user_prompt(session_id: str, prompt: str) -> None:
    HOOK_STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(_buffer_path(session_id), "a") as f:
        f.write(json.dumps({"prompt": prompt, "ts": _now()}) + "\n")


def pop_buffered_prompts(session_id: str) -> list:
    path = _buffer_path(session_id)
    if not path.exists():
        return []
    try:
        entries = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    except (OSError, json.JSONDecodeError):
        return []
    path.unlink(missing_ok=True)
    return entries


# --- last-known-task pointer (Stop can flush even with no Agent call this turn) ---

def _last_task_path(session_id: str) -> pathlib.Path:
    return HOOK_STATE_DIR / f"{session_id}_last_task.txt"


def remember_task(session_id: str, task: str) -> None:
    HOOK_STATE_DIR.mkdir(parents=True, exist_ok=True)
    _last_task_path(session_id).write_text(task)


def recall_task(session_id: str) -> str | None:
    try:
        text = _last_task_path(session_id).read_text().strip()
    except OSError:
        return None
    return text or None


# --- transcript re-derivation (ground truth, not self-reported) ---

def _entries(transcript_path: str) -> list:
    try:
        with open(transcript_path) as f:
            lines = f.readlines()
    except OSError:
        return []
    out = []
    for line in lines:
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def last_agent_result_text(entries: list) -> str | None:
    """Text of the tool_result for the most recent top-level Agent tool_use —
    i.e. the call that just completed and triggered this PostToolUse."""
    last_id = None
    for entry in entries:
        if entry.get("isSidechain") or entry.get("type") != "assistant":
            continue
        for block in (entry.get("message", {}) or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Agent":
                last_id = block.get("id")
    if last_id is None:
        return None
    for entry in entries:
        if entry.get("type") != "user":
            continue
        content = entry.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("tool_use_id") == last_id:
                c = block.get("content")
                if isinstance(c, str):
                    return c
                if isinstance(c, list):
                    return " ".join(b.get("text", "") for b in c if isinstance(b, dict))
    return None


# --- entry formatting ---

def build_dispatch_entry(tool_input: dict, result_text: str | None) -> str:
    subagent = tool_input.get("subagent_type", "?")
    description = tool_input.get("description", "")
    prompt = tool_input.get("prompt", "")
    level = _tag_value(prompt, "TASK-LEVEL")
    stage = _tag_value(prompt, "STAGE")

    lines = [f"### [{_now()}] dispatch -> `{subagent}` ({description})"]
    lines.append(f"- TASK-LEVEL: {level or '-'} | STAGE: {stage or '-'}")

    if result_text is None:
        lines.append("- result: (not found in transcript)")
    elif "Async agent launched" in result_text:
        lines.append("- result: dispatched in background — verdict not available at dispatch time")
    else:
        bits = []
        mode = MODE_RE.search(result_text)
        phase = PHASE_RE.search(result_text)
        verdict = VERDICT_RE.search(result_text)
        final_phase = FINAL_PHASE_RE.search(result_text)
        if mode:
            bits.append(f"MODE={mode.group(1).upper()}")
        if phase:
            bits.append(f"PHASE={phase.group(1)}")
        if verdict:
            bits.append(f"VERDICT={verdict.group(1).upper()}")
        if final_phase:
            bits.append(f"FINAL_PHASE={final_phase.group(1).lower()}")
        lines.append("- result: " + (", ".join(bits) if bits else "(no structured verdict found)"))
    return "\n".join(lines) + "\n"


def build_user_entry(prompt_record: dict) -> str:
    return f"### [{prompt_record.get('ts', '?')}] user turn\n> {prompt_record.get('prompt', '').strip()}\n"


def append_log(task: str, text: str) -> None:
    log_path = PROJECT_DIR / "temp" / task / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(text + "\n")


# --- event handlers ---

def handle_user_prompt_submit(data: dict) -> None:
    session_id = data.get("session_id", "")
    prompt = data.get("prompt", "")
    if session_id and prompt:
        append_user_prompt(session_id, prompt)


def handle_post_tool_use_agent(data: dict) -> None:
    tool_input = data.get("tool_input", {})
    prompt = tool_input.get("prompt", "")
    task = task_dir_from_prompt(prompt)
    session_id = data.get("session_id", "")
    if task is None:
        return  # can't resolve a log.md location yet — nothing to flush to

    remember_task(session_id, task)
    result_text = last_agent_result_text(_entries(data.get("transcript_path", "")))

    for record in pop_buffered_prompts(session_id):
        append_log(task, build_user_entry(record))

    append_log(task, build_dispatch_entry(tool_input, result_text))


def handle_post_tool_use_bash(data: dict) -> None:
    """Bash calls (e.g. render_review_artifact.py / serve_dashboard.sh) also
    reveal which task is active, even when no Agent call follows — this is
    what lets Stop flush buffered turns during a user-feedback wait, when the
    orchestrator's only actions are Bash/Read/Write, not another Agent call."""
    command = data.get("tool_input", {}).get("command", "")
    task = task_dir_from_prompt(command)
    session_id = data.get("session_id", "")
    if task and session_id:
        remember_task(session_id, task)


def handle_stop(data: dict) -> None:
    session_id = data.get("session_id", "")
    if not session_id:
        return
    task = recall_task(session_id)
    if task is None:
        return  # no task resolved yet this session — leave buffer for later
    for record in pop_buffered_prompts(session_id):
        append_log(task, build_user_entry(record))


def main() -> None:
    data = json.load(sys.stdin)
    event = data.get("hook_event_name")
    if event == "UserPromptSubmit":
        handle_user_prompt_submit(data)
    elif event == "PostToolUse" and data.get("tool_name") == "Agent":
        handle_post_tool_use_agent(data)
    elif event == "PostToolUse" and data.get("tool_name") == "Bash":
        handle_post_tool_use_bash(data)
    elif event == "Stop":
        handle_stop(data)


def _demo() -> None:
    assert task_dir_from_prompt("write to temp/abf300_tcell_aging/design.md") == "abf300_tcell_aging"
    assert task_dir_from_prompt("no path here") is None

    entry = build_dispatch_entry(
        {"subagent_type": "peer_reviewer_agent", "description": "review phase 0",
         "prompt": "TASK-LEVEL: L2\nSTAGE: PEER_REVIEW\ntemp/x/design.md ..."},
        "MODE: DESIGN-REVIEW\nPHASE: 0\nVERDICT: APPROVE\n",
    )
    assert "VERDICT=APPROVE" in entry and "MODE=DESIGN-REVIEW" in entry and "PHASE=0" in entry
    assert "TASK-LEVEL: L2" in entry and "STAGE: PEER_REVIEW" in entry

    entry_bg = build_dispatch_entry(
        {"subagent_type": "data_analyst_agent", "description": "x",
         "prompt": "TASK-LEVEL: L2\nSTAGE: EXECUTION"},
        "Async agent launched successfully. agentId: abc123",
    )
    assert "background" in entry_bg

    entry_missing = build_dispatch_entry(
        {"subagent_type": "study_designer_agent", "description": "x", "prompt": "no tags"}, None,
    )
    assert "TASK-LEVEL: -" in entry_missing and "(not found in transcript)" in entry_missing

    # transcript re-derivation: last Agent tool_use's matching tool_result
    entries = [
        {"type": "assistant", "isSidechain": False,
         "message": {"content": [{"type": "tool_use", "id": "t1", "name": "Agent"}]}},
        {"type": "user", "isSidechain": False,
         "message": {"content": [{"type": "tool_result", "tool_use_id": "t1",
                                   "content": [{"type": "text", "text": "VERDICT: ACCEPT"}]}]}},
    ]
    assert last_agent_result_text(entries) == "VERDICT: ACCEPT"
    assert last_agent_result_text([]) is None

    # Stop-hook flush: a buffered turn with no following Agent call still
    # reaches log.md, as long as a prior Agent or Bash call revealed the task.
    import tempfile
    global PROJECT_DIR, HOOK_STATE_DIR
    real_project_dir, real_hook_state_dir = PROJECT_DIR, HOOK_STATE_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        HOOK_STATE_DIR = PROJECT_DIR / "temp" / ".hook_state"

        # no task known yet -> Stop must not lose the buffered prompt
        append_user_prompt("sess1", "some question")
        handle_stop({"session_id": "sess1"})
        buffered_still_there = json.loads(_buffer_path("sess1").read_text().splitlines()[0])
        assert buffered_still_there["prompt"] == "some question"

        # a Bash call revealing the task, then Stop -> flush without any Agent call
        handle_post_tool_use_bash({"session_id": "sess1",
                                    "tool_input": {"command": "bash scripts/serve_dashboard.sh temp/mytask/design.html"}})
        assert recall_task("sess1") == "mytask"
        handle_stop({"session_id": "sess1"})
        log_text = (PROJECT_DIR / "temp" / "mytask" / "log.md").read_text()
        assert "some question" in log_text
        assert not _buffer_path("sess1").exists()
    PROJECT_DIR, HOOK_STATE_DIR = real_project_dir, real_hook_state_dir

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
