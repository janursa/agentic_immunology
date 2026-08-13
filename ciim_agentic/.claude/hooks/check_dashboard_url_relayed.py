#!/usr/bin/env python3
"""Stop hook: if scripts/serve_dashboard.sh printed a dashboard URL this turn,
that URL must appear verbatim in the final reply text — tool results aren't
shown to the user, only text output is, so a run with no URL in the text
leaves the user with nothing to click (ciim_agentic.md 'Interact with user',
which also forbids hand-building the URL instead of relaying the printed one).

Run from the repo root:
    python3 .claude/hooks/check_dashboard_url_relayed.py --self-test
"""
import json
import re
import sys

# \S* not \S+ — the no-arg form of serve_dashboard.sh prints the bare base URL
URL_RE = re.compile(r"https://[a-zA-Z0-9.-]+\.serveousercontent\.com\S*")


def is_real_user_text(entry: dict) -> bool:
    if entry.get("type") != "user" or entry.get("isSidechain"):
        return False
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list) and content:
        return all(b.get("type") == "text" for b in content)
    return False


def _result_text(entry: dict) -> str:
    """Text of a tool result — Bash puts it in toolUseResult.stdout/stderr."""
    result = entry.get("toolUseResult")
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return (result.get("stdout") or "") + "\n" + (result.get("stderr") or "")
    return ""


def dashboard_urls_this_turn(transcript_path: str) -> list:
    try:
        with open(transcript_path) as f:
            lines = f.readlines()
    except OSError:
        return []
    entries = []
    for line in lines:
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    start = 0
    for i in range(len(entries) - 1, -1, -1):
        if is_real_user_text(entries[i]):
            start = i + 1
            break

    urls = []
    for entry in entries[start:]:
        # tool results only — scanning assistant text would defeat the check
        if entry.get("isSidechain") or entry.get("type") != "user":
            continue
        urls += URL_RE.findall(_result_text(entry))
    return urls


def block_reason(transcript_path: str, last_assistant_message: str) -> str | None:
    urls = dashboard_urls_this_turn(transcript_path)
    if not urls:
        return None
    missing = [u for u in urls if u not in (last_assistant_message or "")]
    if not missing:
        return None
    return (
        "serve_dashboard.sh printed a dashboard URL this turn but it doesn't "
        "appear verbatim in your reply text — tool results aren't shown to the "
        "user, so they have no link to open. Relay it exactly as printed (never "
        "hand-built): " + ", ".join(missing)
    )


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return
    reason = block_reason(data.get("transcript_path", ""), data.get("last_assistant_message", ""))
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))


def _self_test() -> None:
    import os
    import tempfile

    URL = "https://abc123.serveousercontent.com/mytask/design.html"

    user_prompt = {"type": "user", "isSidechain": False,
                   "message": {"role": "user", "content": "show me the design"}}
    bash_call = {"type": "assistant", "isSidechain": False,
                 "message": {"role": "assistant", "content": [
                     {"type": "tool_use", "id": "toolu_1", "name": "Bash",
                      "input": {"command": "bash scripts/serve_dashboard.sh temp/mytask/design.html"}}]}}
    bash_result = {"type": "user", "isSidechain": False,
                   "message": {"role": "user", "content": [
                       {"type": "tool_result", "tool_use_id": "toolu_1", "content": URL}]},
                   "toolUseResult": {"stdout": URL + "\n", "stderr": ""}}

    def write_transcript(entries):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        for e in entries:
            f.write(json.dumps(e) + "\n")
        f.close()
        return f.name

    # 1. URL missing from the reply -> block
    path = write_transcript([user_prompt, bash_call, bash_result])
    reason = block_reason(path, "the dashboard is up, have a look")
    assert reason is not None and URL in reason
    os.unlink(path)

    # 2. URL present verbatim -> allow
    path = write_transcript([user_prompt, bash_call, bash_result])
    assert block_reason(path, f"Design ready for review: {URL}") is None
    os.unlink(path)

    # 3. a hand-built variant is not the printed URL -> still blocks
    path = write_transcript([user_prompt, bash_call, bash_result])
    assert block_reason(path, "https://abc123.serveousercontent.com/temp/mytask/design.html") is not None
    os.unlink(path)

    # 4. no serve_dashboard run this turn -> allow
    path = write_transcript([user_prompt])
    assert block_reason(path, "no dashboard involved") is None
    os.unlink(path)

    # 5. served in a PRIOR turn only -> current turn shouldn't re-trigger
    new_prompt = {"type": "user", "isSidechain": False,
                  "message": {"role": "user", "content": "next question"}}
    reply = {"type": "assistant", "isSidechain": False,
             "message": {"role": "assistant", "content": [{"type": "text", "text": "sure"}]}}
    path = write_transcript([user_prompt, bash_call, bash_result, new_prompt, reply])
    assert block_reason(path, "sure, here's the answer") is None
    os.unlink(path)

    # 6. the base-URL form (no path) is also a URL the user needs
    base_result = dict(bash_result, toolUseResult={"stdout": "https://abc123.serveousercontent.com\n", "stderr": ""})
    path = write_transcript([user_prompt, bash_call, base_result])
    assert block_reason(path, "up and running") is not None
    os.unlink(path)

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _self_test()
    else:
        main()
