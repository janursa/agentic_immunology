#!/usr/bin/env python3
"""PreToolUse hook (matcher: Write, Edit): validate findings.md/results.md against its
fixed structure before the write/edit lands. Two different schemas, two different
filenames (both avoid Claude Code's built-in block on subagent writes to
report*.md — github.com/anthropics/claude-code/issues/44657): the orchestrator's
compiled temp/{task}/findings.md (docs/reporting.md, agent_type "" — main session) and
data_analyst_agent's own per-phase results.md (agents/data_analyst_agent.md 'Report
file', agent_type "data_analyst_agent"). Dispatches on `agent_type` from the hook
payload to pick the right schema — without this, an analyst report gets checked
against the compiled schema and always fails, since the headers never match.

Catches the class of bug where figures get listed as plain backtick paths
instead of `![alt](path)` markdown images and silently never render in
findings.html (scripts/render_review_artifact.py only turns actual markdown image
syntax into <img> tags), plus renamed/missing/extra/reordered `## ` sections,
plus listed result files that don't actually exist.

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
# absolute path, >=2 segments; lookbehind keeps URLs (http://host/a) out
ABS_PATH_RE = re.compile(r"(?<![\w:/])(/[\w.\-]+(?:/[\w.\-]+)+)")

# `FINAL_PHASE: true` reaches findings.md inside the RESULTS-REVIEW block the orchestrator pastes
# verbatim into a phase's '#### Checkpoint outcome' — written by the reviewer, so it can't go missing
# in the same lapse that drops the interpretation subsections.
FINAL_PHASE_RE = re.compile(r"^\s*FINAL_PHASE:\s*true\b", re.MULTILINE | re.IGNORECASE)
SUB_HEADER_RE = re.compile(r"^### (.+)$", re.MULTILINE)
FINAL_SUMMARY_SUBSECTIONS = [
    "Principal findings",
    "Concordance with prior expectation",
    "Synthesis",
    "Alternative explanations",
    "Derived hypotheses",
]

EXPECTED_HEADERS = [
    "Task",
    "Summary",
    "Detailed findings",
    "Issues",
    "Code/files generated",
]

# agents/data_analyst_agent.md 'Report file'
ANALYST_HEADERS = [
    "Task",
    "Main findings",
    "Checkpoint outcome",
    "Results files",
    "Folder structure",
    "Singularity images",
    "Issues",
]


def _section(content: str, header: str) -> str:
    m = re.search(rf"^## {re.escape(header)}\s*$", content, re.MULTILINE)
    if not m:
        return ""
    rest = content[m.end():]
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def _checkpoint_gap(content: str) -> str | None:
    """Every '### Phase n' block carries its RESULTS-REVIEW verdict verbatim. Without it the
    FINAL_PHASE signal _summary_gap relies on can go missing, so this is checked first."""
    blocks = re.split(r"^### ", _section(content, "Detailed findings"), flags=re.MULTILINE)[1:]
    bad = [b.splitlines()[0].strip() for b in blocks if "#### Checkpoint outcome" not in b]
    if bad:
        return (
            f"findings.md 'Detailed findings' phase block(s) {bad} have no "
            "'#### Checkpoint outcome' section. Paste peer_reviewer_agent's RESULTS-REVIEW "
            "output block for that phase verbatim (docs/reporting.md)."
        )
    return None


def _principal_findings_gap(content: str) -> str | None:
    """Principal findings must be one bullet per finding (docs/reporting.md), not a table."""
    m = re.search(r"^### Principal findings\s*$", _section(content, "Summary"), re.MULTILINE)
    if not m:
        return None
    rest = m.string[m.end():]
    nxt = re.search(r"^### ", rest, re.MULTILINE)
    body = rest[: nxt.start()] if nxt else rest
    lines = [l for l in body.splitlines() if l.strip()]
    if not lines:
        return None
    if any(l.lstrip().startswith("|") for l in lines):
        return (
            "findings.md 'Summary > Principal findings' uses a table — must be one bullet "
            "('- ...') per finding instead (docs/reporting.md)."
        )
    if not all(l.lstrip().startswith("- ") for l in lines):
        return (
            "findings.md 'Summary > Principal findings' has non-bullet line(s) — every line "
            "must be a '- ' bullet, one per finding (docs/reporting.md)."
        )
    return None


def _summary_gap(content: str) -> str | None:
    """At FINAL_PHASE the Summary must carry all five subsections, each with content.
    Before then only the first two are expected, so nothing is checked."""
    if not FINAL_PHASE_RE.search(content):
        return None

    summary = _section(content, "Summary")
    bodies, current = {}, None
    for line in summary.splitlines():
        m = SUB_HEADER_RE.match(line)
        if m:
            current = m.group(1).strip()
            bodies[current] = ""
        elif current:
            bodies[current] += line.strip()

    missing = [s for s in FINAL_SUMMARY_SUBSECTIONS if s not in bodies]
    empty = [s for s in FINAL_SUMMARY_SUBSECTIONS if s in bodies and not bodies[s]]
    if missing or empty:
        return (
            "findings.md carries a FINAL_PHASE checkpoint, so '## Summary' must have all five "
            f"subsections filled in (docs/reporting.md): missing {missing}, empty {empty}. "
            "Write the final phase's findings and the interpretation subsections in one update."
        )
    return None


def _missing_paths(content: str, report_dir: pathlib.Path) -> str | None:
    """Every artifact the report points at must exist: absolute paths listed under
    'Code/files generated', and image paths (findings.md-relative) anywhere."""
    absolute = {p.rstrip(".,;") for p in ABS_PATH_RE.findall(_section(content, "Code/files generated"))}
    gone = sorted(p for p in absolute if not pathlib.Path(p).exists())
    if gone:
        return (
            f"findings.md 'Code/files generated' lists path(s) that do not exist: {gone}. "
            "Report only artifacts that were actually produced (docs/reporting.md)."
        )

    images = {p for p in MD_IMAGE_RE.findall(content) if not p.startswith(("http://", "https://"))}
    gone = sorted(p for p in images if not (report_dir / p).exists())
    if gone:
        return (
            f"findings.md references image(s) that do not exist relative to {report_dir}: {gone}. "
            "They would render as broken images in findings.html (docs/reporting.md)."
        )
    return None


def block_reason(content: str, report_dir: pathlib.Path | None = None) -> str | None:
    headers = HEADER_RE.findall(content)
    if headers != EXPECTED_HEADERS:
        return (
            f"findings.md top-level '## ' headers are {headers}, expected exactly "
            f"{EXPECTED_HEADERS} in this order (docs/reporting.md)."
        )

    detailed = _section(content, "Detailed findings")
    md_image_paths = set(MD_IMAGE_RE.findall(detailed))
    bare = sorted({
        m.group(0) for m in IMG_EXT_RE.finditer(detailed)
        if not any(m.group(0) in p for p in md_image_paths)
    })
    if bare:
        return (
            "findings.md 'Detailed findings' references image file(s) as plain text "
            f"instead of markdown images: {bare}. Use `![alt](path)` (path relative "
            "to findings.md's own directory) or they silently won't render in "
            "findings.html (docs/reporting.md)."
        )

    for path in md_image_paths:
        if path.startswith("/"):
            return (
                f"findings.md image path '{path}' is absolute — must be relative to "
                "findings.md's own directory (docs/reporting.md), or it won't "
                "resolve in the browser."
            )

    gap = _checkpoint_gap(content) or _principal_findings_gap(content) or _summary_gap(content)
    if gap:
        return gap

    if report_dir is not None:
        return _missing_paths(content, report_dir)
    return None


def block_reason_analyst(content: str) -> str | None:
    headers = HEADER_RE.findall(content)
    if headers != ANALYST_HEADERS:
        return (
            f"results.md top-level '## ' headers are {headers}, expected exactly "
            f"{ANALYST_HEADERS} in this order (agents/data_analyst_agent.md 'Report file')."
        )
    absolute = {p.rstrip(".,;") for p in ABS_PATH_RE.findall(_section(content, "Results files"))}
    gone = sorted(p for p in absolute if not pathlib.Path(p).exists())
    if gone:
        return (
            f"results.md 'Results files' lists path(s) that do not exist: {gone}. "
            "Report only files that were actually produced (agents/data_analyst_agent.md)."
        )
    return None


def _resulting_content(data: dict) -> str | None:
    tool_name = data.get("tool_name")
    if tool_name not in ("Write", "Edit"):
        return None
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if pathlib.Path(file_path).name not in ("findings.md", "results.md"):
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
    if data.get("agent_type", ""):
        reason = block_reason_analyst(content)
    else:
        report_dir = pathlib.Path(data["tool_input"]["file_path"]).resolve().parent
        reason = block_reason(content, report_dir)
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
        "## Summary\n### Principal findings\n- a\n\n"
        "## Detailed findings\n### Phase 0\nSee ![plot](results/images/foo.png)\n\n"
        "#### Checkpoint outcome\nVERDICT: ACCEPT\nFINAL_PHASE: false\n\n"
        "## Issues\nNone\n\n"
        "## Code/files generated\nz\n"
    )
    assert block_reason(good) is None
    assert block_reason(good.replace("#### Checkpoint outcome", "#### Notes")) is not None

    assert block_reason(good.replace("## Issues", "## Notes")) is not None  # renamed header
    assert block_reason(good.replace("## Issues\nNone\n\n", "")) is not None  # missing header
    assert block_reason(good.replace("## Summary\n", "## Summary\n## Extra\n")) is not None  # extra header

    table = good.replace("### Principal findings\n- a\n", "### Principal findings\n| a | b |\n")
    assert block_reason(table) is not None  # table instead of bullets

    # FINAL_PHASE gate: interpretation subsections required only once the report says it's final
    final = good.replace("FINAL_PHASE: false", "FINAL_PHASE: true")
    assert block_reason(final) is not None  # Synthesis etc. missing
    full = final.replace(
        "### Principal findings\n- a\n",
        "### Principal findings\n- a\n\n### Concordance with prior expectation\nb\n\n"
        "### Synthesis\nc\n\n### Alternative explanations\nd\n\n### Derived hypotheses\ne\n",
    )
    assert block_reason(full) is None
    assert block_reason(full.replace("### Derived hypotheses\ne", "### Derived hypotheses\n")) is not None  # stub

    bare = good.replace("See ![plot](results/images/foo.png)", "See `results/images/foo.png`")
    assert block_reason(bare) is not None  # image not markdown-wrapped

    absolute = good.replace("results/images/foo.png)", "/home/x/results/images/foo.png)")
    assert block_reason(absolute) is not None  # absolute image path

    # _resulting_content: Write vs Edit vs non-findings.md path
    assert _resulting_content({"tool_name": "Write", "tool_input": {"file_path": "temp/x/design.md", "content": "no"}}) is None
    assert _resulting_content({"tool_name": "Write", "tool_input": {"file_path": "temp/x/findings.md", "content": good}}) == good

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        rp = tmpdir / "findings.md"
        rp.write_text(good)

        # path existence: only checked when report_dir is given
        assert block_reason(good, tmpdir) is not None  # results/images/foo.png missing
        (tmpdir / "results/images").mkdir(parents=True)
        (tmpdir / "results/images/foo.png").touch()
        assert block_reason(good, tmpdir) is None

        listed = good.replace("## Code/files generated\nz", f"## Code/files generated\n- `{rp}`")
        assert block_reason(listed, tmpdir) is None
        assert block_reason(listed.replace(str(rp), f"{tmpdir}/nope.py"), tmpdir) is not None
        # URLs are not paths
        assert block_reason(listed.replace(str(rp), "https://host/a/b"), tmpdir) is None

        edited = _resulting_content({
            "tool_name": "Edit",
            "tool_input": {"file_path": str(rp), "old_string": "## Issues\nNone\n", "new_string": "## Notes\nNone\n"},
        })
        assert edited is not None and block_reason(edited) is not None

    # analyst schema: same filename, different structure, dispatched on agent_type
    analyst_good = (
        "## Task\nx\n\n## Main findings\n- a\n\n## Checkpoint outcome\n- b: c - MET\n\n"
        "## Results files\nz\n\n## Folder structure\nsee readme\n\n"
        "## Singularity images\nNone\n\n## Issues\nNone\n"
    )
    assert block_reason_analyst(analyst_good) is None
    assert block_reason(analyst_good) is not None  # wrong schema for compiled report
    assert block_reason_analyst(good) is not None  # and vice versa

    assert _resulting_content({"tool_name": "Write", "tool_input": {"file_path": "temp/x/results.md", "content": analyst_good}}) == analyst_good

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        existing = tmpdir / "results.csv"
        existing.touch()
        listed = analyst_good.replace("## Results files\nz", f"## Results files\n- `{existing}`")
        assert block_reason_analyst(listed) is None
        assert block_reason_analyst(listed.replace(str(existing), f"{tmpdir}/nope.csv")) is not None

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
