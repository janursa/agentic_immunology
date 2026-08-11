#!/usr/bin/env python3
"""PreToolUse hook (matcher: Write, Edit): validate a DESIGN-REVIEW review file
against docs/design_review_checks.json before it lands.

Deterministic checks only — whether a check was reviewed *well* is not decidable
here. What is decidable:
- coverage: one CHECKS line per id in the canonical list, in order, nothing added;
- honest N/A: only with an `exempt_when` condition of that check quoted verbatim;
- verdict consistency: a FAIL on a blocking check must produce VERDICT: REVISE-DESIGN
  and an ISSUES entry tagged [id]. This is the one that catches the real failure —
  "listed three blocking problems, returned APPROVE".

Gated on content, not filename: fires on any write under temp/ whose resulting text
carries a `MODE: DESIGN-REVIEW` line and a CHECKS block. Fails open otherwise (no
canonical list, no mode line, no CHECKS block — so RESULTS-REVIEW files pass straight
through), which also keeps the reviewer able to fix a denied write inside its own
call rather than needing a re-dispatch.

Run from the repo root:
    python3 .claude/hooks/check_design_review_format.py --self-test
"""
import json
import os
import pathlib
import re
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
CHECKS_FILE = PROJECT_DIR / "docs" / "design_review_checks.json"
MODE_RE = re.compile(r"^\s*MODE:\s*DESIGN-REVIEW\s*$", re.MULTILINE)
CHECK_LINE_RE = re.compile(
    r"^\s*(\d+)\s+([A-Z_]+)\s*:\s*(PASS|FAIL|N/?A)[^\S\n]*[—–-]?[^\S\n]*(.*)$", re.MULTILINE
)
VERDICT_RE = re.compile(r"^\s*VERDICT:\s*(APPROVE|REVISE-DESIGN)\s*$", re.MULTILINE)
TAG_RE = re.compile(r"\[(\d+)\]")
MIN_EVIDENCE = 20


def _load_checks() -> list:
    try:
        return json.loads(CHECKS_FILE.read_text())["CHECKS"]
    except (OSError, KeyError, json.JSONDecodeError):
        return []  # ponytail: fail-open if the canonical list is missing/unreadable


def _tagged_ids(content: str, header: str, until: tuple) -> set:
    m = re.search(rf"^\s*{header}\b.*$", content, re.MULTILINE)
    if not m:
        return set()
    rest = content[m.end():]
    nxt = re.search(rf"^\s*(?:{'|'.join(until)})\b", rest, re.MULTILINE)
    return {int(i) for i in TAG_RE.findall(rest[: nxt.start()] if nxt else rest)}


def block_reason(content: str, checks: list) -> str | None:
    if not checks:
        return None
    if not MODE_RE.search(content):
        return None  # ponytail: content gate — not a DESIGN-REVIEW, whatever it's named
    found = CHECK_LINE_RE.findall(content)
    if not found:
        return None  # ponytail: no CHECKS block at all -> not a design review, let it through

    expected = [(c["id"], c["label"]) for c in checks]
    got = [(int(i), label) for i, label, _, _ in found]
    if got != expected:
        return (
            f"CHECKS block is {got}, expected exactly {expected} in this order "
            "(docs/design_review_checks.json). One line per check id, none omitted, "
            "none added, order preserved."
        )

    verdict_m = VERDICT_RE.search(content)
    if not verdict_m:
        return "No 'VERDICT: APPROVE | REVISE-DESIGN' line found."
    verdict = verdict_m.group(1)

    issue_ids = _tagged_ids(content, "ISSUES", ("NOTES",))
    by_id = {c["id"]: c for c in checks}
    failed_blocking = []

    for raw_id, label, raw_verdict, evidence in found:
        cid, evidence = int(raw_id), evidence.strip()
        check, status = by_id[cid], raw_verdict.replace("/", "")

        if status == "NA":
            exempt = check.get("exempt_when") or []
            if not exempt:
                return (
                    f"Check {cid} {label} is marked N/A but has no exempt_when condition "
                    "in docs/design_review_checks.json — it must be reviewed."
                )
            if not any(cond.lower() in evidence.lower() for cond in exempt):
                return (
                    f"Check {cid} {label} is N/A without a valid exemption. Quote one of "
                    f"{exempt} verbatim in the evidence (e.g. 'N/A — {exempt[0]}')."
                )
            continue

        if len(evidence) < MIN_EVIDENCE:
            return (
                f"Check {cid} {label}: {status} has no evidence. State what you read in "
                "design.md — section name, phase, or a quoted line. Restating the check "
                "back is not evidence."
            )
        if status == "FAIL":
            if check.get("severity") == "blocking":
                failed_blocking.append(cid)
                if cid not in issue_ids:
                    return (
                        f"Check {cid} {label} FAILed (blocking) but no ISSUES entry is tagged "
                        f"'[{cid}]'. Every blocking FAIL needs a specific, actionable issue."
                    )
            elif cid not in _tagged_ids(content, "NOTES", ("---", "MODE:")):
                return (
                    f"Check {cid} {label} FAILed (severity: note) but no NOTES entry is "
                    f"tagged '[{cid}]'."
                )

    if failed_blocking and verdict != "REVISE-DESIGN":
        return (
            f"VERDICT is {verdict} but blocking checks {failed_blocking} FAILed — that is a "
            "malformed review. Any blocking FAIL means VERDICT: REVISE-DESIGN."
        )
    return None


def _resulting_content(data: dict) -> str | None:
    tool_name = data.get("tool_name")
    if tool_name not in ("Write", "Edit"):
        return None
    tool_input = data.get("tool_input", {})
    path = pathlib.Path(tool_input.get("file_path", ""))
    try:
        # ponytail: output tree only, so editing the review template in agents/ or docs/
        # (which quotes MODE: DESIGN-REVIEW) can't deny itself. Not a filename check.
        path.resolve().relative_to((PROJECT_DIR / "temp").resolve())
    except ValueError:
        return None
    if tool_name == "Write":
        return tool_input.get("content", "")
    try:
        current = path.read_text()
    except (OSError, UnicodeDecodeError):
        return None  # ponytail: fail-open, e.g. Edit on a not-yet-existing or binary file
    count = -1 if tool_input.get("replace_all") else 1
    return current.replace(tool_input.get("old_string", ""), tool_input.get("new_string", ""), count)


def main() -> None:
    data = json.load(sys.stdin)
    content = _resulting_content(data)
    if content is None:
        return
    reason = block_reason(content, _load_checks())
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))


def _demo() -> None:
    checks = [
        {"id": 1, "label": "SUFFICIENCY", "severity": "blocking", "exempt_when": []},
        {"id": 2, "label": "TRAJECTORY", "severity": "blocking", "exempt_when": ["PHASE: 0"]},
        {"id": 3, "label": "LIMITATIONS", "severity": "note", "exempt_when": []},
    ]
    ev = "design.md 'Plan phase 0' covers both axes of the question"
    good = (
        "# Peer Review — DESIGN-REVIEW\n## Output\nMODE: DESIGN-REVIEW\nPHASE: 0\nCHECKS:\n"
        f"1 SUFFICIENCY: PASS — {ev}\n"
        "2 TRAJECTORY: N/A — PHASE: 0\n"
        f"3 LIMITATIONS: PASS — {ev}\n"
        "VERDICT: APPROVE\n"
    )
    assert block_reason(good, checks) is None
    assert block_reason(good, []) is None  # fail-open without the canonical list
    assert block_reason("no checks block here", checks) is None  # not a design review
    assert block_reason(good.replace("MODE: DESIGN-REVIEW", "MODE: RESULTS-REVIEW"), checks) is None

    assert block_reason(good.replace(f"3 LIMITATIONS: PASS — {ev}\n", ""), checks)  # missing id
    assert block_reason(good.replace("2 TRAJECTORY", "9 TRAJECTORY"), checks)  # wrong id
    assert block_reason(good.replace("VERDICT: APPROVE\n", ""), checks)  # no verdict
    assert block_reason(good.replace("N/A — PHASE: 0", "N/A — seemed fine"), checks)  # bogus N/A
    assert block_reason(good.replace(f"1 SUFFICIENCY: PASS — {ev}", "1 SUFFICIENCY: PASS — ok"), checks)  # thin evidence

    # blocking FAIL: needs both a tagged issue and REVISE-DESIGN
    failed = good.replace(f"1 SUFFICIENCY: PASS — {ev}", f"1 SUFFICIENCY: FAIL — {ev}")
    assert block_reason(failed, checks)  # no ISSUES entry
    with_issue = failed.replace("VERDICT: APPROVE\n", "VERDICT: APPROVE\nISSUES:\n- [1] no validation cohort\n")
    assert "malformed review" in block_reason(with_issue, checks)  # FAIL + APPROVE
    fixed = with_issue.replace("VERDICT: APPROVE", "VERDICT: REVISE-DESIGN")
    assert block_reason(fixed, checks) is None

    # note-severity FAIL needs a NOTES entry, not an issue, and doesn't force REVISE-DESIGN
    note_fail = good.replace(f"3 LIMITATIONS: PASS — {ev}", f"3 LIMITATIONS: FAIL — {ev}")
    assert block_reason(note_fail, checks)
    assert block_reason(
        note_fail.replace("VERDICT: APPROVE\n", "VERDICT: APPROVE\nNOTES:\n- [3] batch effect is fixable\n"),
        checks,
    ) is None

    # content-gated: any name under temp/ is inspected, anything outside it is not
    for name in ("temp/x/phase_0/design_review/peer_review.md", "temp/x/anything.md"):
        assert _resulting_content({"tool_name": "Write", "tool_input": {"file_path": name, "content": good}}) == good
    assert _resulting_content({"tool_name": "Write", "tool_input": {"file_path": "agents/peer_reviewer_agent.md", "content": good}}) is None

    # the real canonical list must parse and be self-consistent
    real = _load_checks()
    if real:
        assert [c["id"] for c in real] == list(range(1, len(real) + 1))
        assert all(c["severity"] in ("blocking", "note") for c in real)

    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
