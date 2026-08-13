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
VERDICT_RE = re.compile(r"VERDICT:\s*(APPROVE|REVISE-DESIGN|REVISE-ANALYSIS|ACCEPT)", re.I)
MODE_RE = re.compile(r"MODE:\s*(DESIGN-REVIEW|RESULTS-REVIEW)", re.I)
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


def _debug_payload(data: dict) -> None:
    """ponytail: temporary — diagnosing why nested dispatches lose their verdict.
    Remove once tool_response's shape for sidechain Agent calls is known."""
    try:
        HOOK_STATE_DIR.mkdir(parents=True, exist_ok=True)
        r = data.get("tool_response")
        with open(HOOK_STATE_DIR / "debug_payload.jsonl", "a") as f:
            f.write(json.dumps({
                "ts": _now(),
                "tool": data.get("tool_name"),
                "desc": data.get("tool_input", {}).get("description"),
                "keys": sorted(data.keys()),
                "resp_type": type(r).__name__,
                "resp_keys": sorted(r.keys()) if isinstance(r, dict) else None,
                "resp_head": repr(r)[:400],
            }) + "\n")
    except Exception:
        pass


def result_text(data: dict) -> str | None:
    """What the subagent actually returned. PostToolUse hands this over directly
    as `tool_response`, which is both cheaper and correct for *nested* dispatches
    — the transcript scan below can only see top-level calls, so a dispatch made
    inside a subagent's sidechain used to log the enclosing call's result instead.
    Transcript scan kept as a fallback in case the field shape changes."""
    _debug_payload(data)
    r = data.get("tool_response")
    if isinstance(r, dict):
        # SendMessage puts its text under "message", Agent under "content"/"text"
        r = r.get("content") or r.get("text") or r.get("message")
    if isinstance(r, list):
        r = " ".join(b.get("text", "") for b in r if isinstance(b, dict))
    if isinstance(r, str) and r.strip():
        return r
    return last_agent_result_text(_entries(data.get("transcript_path", "")))


def last_agent_result_text(entries: list) -> str | None:
    """Text of the tool_result for the most recent top-level Agent tool_use.
    ponytail: only a fallback for result_text() — misses sidechain calls, and
    races the transcript write on the call that triggered this very hook."""
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
    elif "Async agent launched" in result_text or "in the background" in result_text:
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


def _first_line(text: str) -> str:
    stripped = text.strip()
    return stripped.splitlines()[0] if stripped else ""


def _last_logged_prompt(task: str) -> str | None:
    try:
        text = (PROJECT_DIR / "temp" / task / "log.md").read_text()
    except OSError:
        return None
    quoted = re.findall(r"^> (.*)$", text, re.M)
    return quoted[-1] if quoted else None


def flush_prompts(task: str, records: list) -> None:
    """Slash commands (/clear and friends) fire UserPromptSubmit twice for one
    human message — once for the command echo, once for the real prompt — so
    drop a prompt identical to the one logged just before it."""
    prev = _last_logged_prompt(task)
    for record in records:
        current = _first_line(record.get("prompt", ""))
        if current and current == prev:
            continue
        append_log(task, build_user_entry(record))
        prev = current


# --- event handlers ---

SYSTEM_PROMPT_MARKERS = ("<task-notification>", "[SYSTEM NOTIFICATION - NOT USER INPUT]")


def is_system_prompt(prompt: str) -> bool:
    """Background-task notifications arrive through UserPromptSubmit like a human
    message would. They are machine events — logging them as 'user turn' both
    buries log.md under the blob and misrepresents who said what."""
    return any(marker in prompt for marker in SYSTEM_PROMPT_MARKERS)


def handle_user_prompt_submit(data: dict) -> None:
    session_id = data.get("session_id", "")
    prompt = data.get("prompt", "")
    if session_id and prompt and not is_system_prompt(prompt):
        append_user_prompt(session_id, prompt)


def handle_post_tool_use_agent(data: dict) -> None:
    tool_input = data.get("tool_input", {})
    if data.get("tool_name") == "SendMessage":
        # Resuming a parked agent is a dispatch too — same shape, different keys.
        tool_input = {"subagent_type": tool_input.get("to", "?"),
                      "description": tool_input.get("summary", "resume"),
                      "prompt": tool_input.get("message", "")}
    prompt = tool_input.get("prompt", "")
    task = task_dir_from_prompt(prompt)
    session_id = data.get("session_id", "")
    if task is None:
        return  # can't resolve a log.md location yet — nothing to flush to

    remember_task(session_id, task)
    flush_prompts(task, pop_buffered_prompts(session_id))
    append_log(task, build_dispatch_entry(tool_input, result_text(data)))


def handle_post_tool_use_path(data: dict) -> None:
    """Bash commands (render_review_artifact.py / serve_dashboard.sh) and
    Write/Edit file paths also reveal which task is active, even when no Agent
    call follows — this is what lets Stop flush buffered turns when the
    orchestrator's only actions are Bash/Write/Edit, or when its first dispatch
    of the task is rejected and PostToolUse(Agent) never fires at all."""
    tool_input = data.get("tool_input", {})
    # ponytail: command + file_path only, not the whole tool_input — Write's
    # `content` can mention some *other* task's path and steal the pointer.
    for key in ("command", "file_path"):
        task = task_dir_from_prompt(tool_input.get(key, ""))
        if task and data.get("session_id"):
            remember_task(data["session_id"], task)
            return


def handle_stop(data: dict) -> None:
    session_id = data.get("session_id", "")
    if not session_id:
        return
    task = recall_task(session_id)
    if task is None:
        return  # no task resolved yet this session — leave buffer for later
    flush_prompts(task, pop_buffered_prompts(session_id))
    drop_stale_buffers()


STALE_BUFFER_DAYS = 7


def drop_stale_buffers() -> None:
    """Sessions that end without ever resolving a task dir leave their buffer
    behind forever. Harmless (buffers are per-session, they can't leak into
    another task's log) but they accumulate, so age them out."""
    cutoff = datetime.now(timezone.utc).timestamp() - STALE_BUFFER_DAYS * 86400
    try:
        stale = [p for p in HOOK_STATE_DIR.glob("*.jsonl") if p.stat().st_mtime < cutoff]
    except OSError:
        return
    for path in stale:
        path.unlink(missing_ok=True)


def main() -> None:
    data = json.load(sys.stdin)
    event = data.get("hook_event_name")
    if event == "UserPromptSubmit":
        handle_user_prompt_submit(data)
    elif event == "PostToolUse" and data.get("tool_name") in ("Agent", "SendMessage"):
        handle_post_tool_use_agent(data)
    elif event == "PostToolUse":
        handle_post_tool_use_path(data)
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

    entry_revise = build_dispatch_entry(
        {"subagent_type": "peer_reviewer_agent", "description": "results review",
         "prompt": "TASK-LEVEL: L2\nSTAGE: PEER_REVIEW\ntemp/x/results_review/"},
        "MODE: RESULTS-REVIEW\nVERDICT: REVISE-ANALYSIS\n",
    )
    assert "VERDICT=REVISE-ANALYSIS" in entry_revise

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

    # background-task notifications are machine events, not user turns
    assert is_system_prompt("<task-notification>\n<task-id>abc</task-id>")
    assert is_system_prompt("[SYSTEM NOTIFICATION - NOT USER INPUT]\nagent finished")
    assert not is_system_prompt("rerun this analysis again")

    # tool_response is preferred over the transcript scan, in every shape
    assert result_text({"tool_response": "VERDICT: APPROVE"}) == "VERDICT: APPROVE"
    assert result_text({"tool_response": [{"type": "text", "text": "VERDICT: REVISE"}]}) == "VERDICT: REVISE"
    assert result_text({"tool_response": {"content": "VERDICT: ACCEPT"}}) == "VERDICT: ACCEPT"
    assert "in the background" in result_text(
        {"tool_response": {"success": True, "message": "resumed from transcript in the background"}})
    # ...and falls back to the transcript when it's absent or empty
    assert result_text({"tool_response": "", "transcript_path": "/nonexistent"}) is None

    # a SendMessage resume reads as a background dispatch, not a lost verdict
    entry_resume = build_dispatch_entry(
        {"subagent_type": "a123", "description": "resume", "prompt": "WORK-DIR: temp/x/"},
        'Agent "a123" had no active task; resumed from transcript in the background',
    )
    assert "background" in entry_resume

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

        # a Write reveals the task too — so a task whose first dispatch is
        # rejected still gets a log.md; `content` must not steal the pointer
        handle_post_tool_use_path({"session_id": "sess1",
                                    "tool_input": {"file_path": "temp/othertask/feedback_log/x/feedback.md",
                                                   "content": "mentions temp/decoy/ in the body"}})
        assert recall_task("sess1") == "othertask"

        # a Bash call revealing the task, then Stop -> flush without any Agent call
        handle_post_tool_use_path({"session_id": "sess1",
                                    "tool_input": {"command": "bash scripts/serve_dashboard.sh temp/mytask/design.html"}})
        assert recall_task("sess1") == "mytask"
        handle_stop({"session_id": "sess1"})
        log_text = (PROJECT_DIR / "temp" / "mytask" / "log.md").read_text()
        assert "some question" in log_text
        assert not _buffer_path("sess1").exists()

        # /clear fires UserPromptSubmit twice for one message -> logged once
        flush_prompts("mytask", [{"prompt": "do the thing", "ts": "t1"},
                                  {"prompt": "do the thing", "ts": "t2"}])
        log_text = (PROJECT_DIR / "temp" / "mytask" / "log.md").read_text()
        assert log_text.count("> do the thing") == 1
        # a genuine repeat of an earlier prompt still logs once more
        flush_prompts("mytask", [{"prompt": "other", "ts": "t3"},
                                  {"prompt": "do the thing", "ts": "t4"}])
        log_text = (PROJECT_DIR / "temp" / "mytask" / "log.md").read_text()
        assert log_text.count("> do the thing") == 2

        # stale buffers age out, fresh ones survive
        append_user_prompt("old_sess", "ancient")
        append_user_prompt("new_sess", "recent")
        old = _buffer_path("old_sess")
        os.utime(old, (0, 0))
        drop_stale_buffers()
        assert not old.exists() and _buffer_path("new_sess").exists()
    PROJECT_DIR, HOOK_STATE_DIR = real_project_dir, real_hook_state_dir

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
