#!/usr/bin/env python3
"""PreToolUse hook (matcher: Write, Edit): validate report.md against
knowhow/reporting.md's fixed structure and image-markdown rule before the
write/edit lands. Catches the class of bug where figures get listed as plain
backtick paths instead of `![alt](path)` markdown images and silently never
render in report.html (knowhow/render_review_artifact.py only turns actual
markdown image syntax into <img> tags), plus renamed/missing/extra/reordered
`## ` sections.

Run from the repo root:
    python3 .claude/hooks/report_format_check.py --self-test
"""
import json
import pathlib
import re
import sys

IMG_EXT_RE = re.compile(r"[\w./\-]+\.(?:png|jpe?g|gif|svg)\b")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HEADER_RE = re.compile(r"^## (.+)$", re.MULTILINE)

EXPECTED_HEADERS = [
    "Task",
    "Code/files generated",
    "Summary of findings",
    "Detailed findings",
    "Issues",
]


def _section(content: str, header: str) -> str:
    m = re.search(rf"^## {re.escape(header)}\s*$", content, re.MULTILINE)
    if not m:
        return ""
    rest = content[m.end():]
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def block_reason(content: str) -> str | None:
    headers = HEADER_RE.findall(content)
    if headers != EXPECTED_HEADERS:
        return (
            f"report.md top-level '## ' headers are {headers}, expected exactly "
            f"{EXPECTED_HEADERS} in this order (knowhow/reporting.md)."
        )

    detailed = _section(content, "Detailed findings")
    md_image_paths = set(MD_IMAGE_RE.findall(detailed))
    bare = sorted({
        m.group(0) for m in IMG_EXT_RE.finditer(detailed)
        if not any(m.group(0) in p for p in md_image_paths)
    })
    if bare:
        return (
            "report.md 'Detailed findings' references image file(s) as plain text "
            f"instead of markdown images: {bare}. Use `![alt](path)` (path relative "
            "to report.md's own directory) or they silently won't render in "
            "report.html (knowhow/reporting.md)."
        )

    for path in md_image_paths:
        if path.startswith("/"):
            return (
                f"report.md image path '{path}' is absolute — must be relative to "
                "report.md's own directory (knowhow/reporting.md), or it won't "
                "resolve in the browser."
            )
    return None


def _resulting_content(data: dict) -> str | None:
    tool_name = data.get("tool_name")
    if tool_name not in ("Write", "Edit"):
        return None
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if pathlib.Path(file_path).name != "report.md":
        return None
    if tool_name == "Write":
        return tool_input.get("content", "")
    try:
        current = pathlib.Path(file_path).read_text()
    except OSError:
        return None  # ponytail: fail-open, e.g. Edit on a not-yet-existing file
    old, new = tool_input.get("old_string", ""), tool_input.get("new_string", "")
    count = -1 if tool_input.get("replace_all") else 1
    return current.replace(old, new, count)


def main() -> None:
    data = json.load(sys.stdin)
    content = _resulting_content(data)
    if content is None:
        return
    reason = block_reason(content)
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))


def _demo() -> None:
    good = (
        "## Task\n### Original prompt\nx\n\n### Interpreted prompt\ny\n\n"
        "## Code/files generated\nz\n\n## Summary of findings\na\n\n"
        "## Detailed findings\nSee ![plot](results/images/foo.png)\n\n"
        "## Issues\nNone\n"
    )
    assert block_reason(good) is None

    assert block_reason(good.replace("## Issues", "## Notes")) is not None  # renamed header
    assert block_reason(good.replace("## Issues\nNone\n", "")) is not None  # missing header

    bare = good.replace("See ![plot](results/images/foo.png)", "See `results/images/foo.png`")
    assert block_reason(bare) is not None  # image not markdown-wrapped

    absolute = good.replace("results/images/foo.png)", "/home/x/results/images/foo.png)")
    assert block_reason(absolute) is not None  # absolute image path

    # _resulting_content: Write vs Edit vs non-report.md path
    assert _resulting_content({"tool_name": "Write", "tool_input": {"file_path": "temp/x/design.md", "content": "no"}}) is None
    assert _resulting_content({"tool_name": "Write", "tool_input": {"file_path": "temp/x/report.md", "content": good}}) == good

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        rp = pathlib.Path(tmp) / "report.md"
        rp.write_text(good)
        edited = _resulting_content({
            "tool_name": "Edit",
            "tool_input": {"file_path": str(rp), "old_string": "## Issues\nNone\n", "new_string": "## Notes\nNone\n"},
        })
        assert edited is not None and block_reason(edited) is not None

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
