#!/usr/bin/env python3
"""Stop hook: if the Artifact tool was called this turn, its returned URL
must appear verbatim in the final reply text — tool call results aren't
shown to the user, only text output is, so a call with no URL in the text
leaves the user with nothing to click. See memory:
feedback_artifact_url_must_be_in_text.

Run from the repo root:
    python3 .claude/hooks/check_artifact_relayed.py --self-test
"""
import json
import sys


def is_real_user_text(entry: dict) -> bool:
    if entry.get("type") != "user" or entry.get("isSidechain"):
        return False
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list) and content:
        return all(b.get("type") == "text" for b in content)
    return False


def artifact_urls_this_turn(transcript_path: str) -> list:
    try:
        with open(transcript_path) as f:
            lines = f.readlines()
    except OSError:
        return []
    entries = [json.loads(l) for l in lines if l.strip()]

    start = 0
    for i in range(len(entries) - 1, -1, -1):
        if is_real_user_text(entries[i]):
            start = i + 1
            break

    artifact_tool_ids = set()
    urls = []
    for entry in entries[start:]:
        if entry.get("isSidechain"):
            continue
        msg = entry.get("message", {})
        if entry.get("type") == "assistant":
            for block in msg.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Artifact":
                    artifact_tool_ids.add(block.get("id"))
        elif entry.get("type") == "user":
            for block in msg.get("content") or []:
                if isinstance(block, dict) and block.get("tool_use_id") in artifact_tool_ids:
                    url = (entry.get("toolUseResult") or {}).get("url")
                    if url:
                        urls.append(url)
    return urls


def block_reason(transcript_path: str, last_assistant_message: str) -> str | None:
    urls = artifact_urls_this_turn(transcript_path)
    if not urls:
        return None
    missing = [u for u in urls if u not in (last_assistant_message or "")]
    if not missing:
        return None
    return (
        "This turn published an Artifact but its URL doesn't appear verbatim "
        "in your reply text — tool results aren't shown to the user, so they "
        "have no link to open. Add the URL(s) to your reply: " + ", ".join(missing)
    )


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return
    reason = block_reason(data.get("transcript_path", ""), data.get("last_assistant_message", ""))
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))


def _self_test() -> None:
    import tempfile
    import os

    def entry(**kw):
        return kw

    user_prompt = entry(type="user", isSidechain=False, message={"role": "user", "content": "do the thing"})
    assistant_artifact_call = entry(
        type="assistant", isSidechain=False,
        message={"role": "assistant", "content": [
            {"type": "tool_use", "id": "toolu_1", "name": "Artifact", "input": {}}
        ]},
    )
    tool_result = entry(
        type="user", isSidechain=False,
        message={"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "..."}]},
        toolUseResult={"url": "https://claude.ai/code/artifact/abc123"},
    )

    def write_transcript(entries):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        for e in entries:
            f.write(json.dumps(e) + "\n")
        f.close()
        return f.name

    # Case 1: URL missing from reply -> block
    path = write_transcript([user_prompt, assistant_artifact_call, tool_result])
    reason = block_reason(path, "here you go, the artifact above has the review")
    assert reason is not None and "abc123" in reason
    os.unlink(path)

    # Case 2: URL present in reply -> allow
    path = write_transcript([user_prompt, assistant_artifact_call, tool_result])
    reason = block_reason(path, "Review it here: https://claude.ai/code/artifact/abc123")
    assert reason is None
    os.unlink(path)

    # Case 3: no Artifact call this turn -> allow regardless of text
    path = write_transcript([user_prompt])
    reason = block_reason(path, "no artifact involved")
    assert reason is None
    os.unlink(path)

    # Case 4: Artifact called in a PRIOR turn only -> current turn shouldn't re-trigger
    prior_turn = [user_prompt, assistant_artifact_call, tool_result]
    new_prompt = entry(type="user", isSidechain=False, message={"role": "user", "content": "next question"})
    assistant_reply = entry(type="assistant", isSidechain=False, message={"role": "assistant", "content": [{"type": "text", "text": "sure"}]})
    path = write_transcript(prior_turn + [new_prompt, assistant_reply])
    reason = block_reason(path, "sure, here's the answer")
    assert reason is None
    os.unlink(path)

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _self_test()
    else:
        main()
