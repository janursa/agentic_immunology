#!/usr/bin/env python3
"""PreToolUse hook (matcher: Bash): data_analyst_agent may only run python/R
inside a singularity container (docs/images.md HARD RULE — "the ONLY permitted
environment", no conda/venv). Blocks a direct `python3 script.py` / `Rscript
script.R` in the Bash command unless "singularity" also appears in it.

`sbatch <script>` is allowed at the Bash-command level (submission itself isn't
compute) but the submitted script file is read and must itself invoke
singularity — otherwise the job body would run python/R bare on the compute
node, same violation one layer removed.

# ponytail: token-level regex, not a shell parser — a determined `bash -c`/eval
# obfuscation could slip through. Same limitation restrict_knowhow_access.py
# already documents for Bash. Tighten if that's ever actually exploited.

Run from the repo root:
    python3 .claude/hooks/require_singularity_bash.py --self-test
"""
import json
import os
import pathlib
import re
import sys

PROJECT_DIR = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()

RESTRICTED_AGENTS = {"data_analyst_agent"}
COMPUTE_BINARIES = {"python", "python3", "python2", "Rscript", "R"}
SPLIT_RE = re.compile(r"&&|\|\||[;|\n]")
ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$")
SBATCH_RE = re.compile(r"(?:^|\s)sbatch\s+(\S+)")


def _first_binary(subcmd: str) -> str | None:
    tokens = subcmd.strip().split()
    for tok in tokens:
        if ENV_ASSIGN_RE.match(tok) or tok == "env" or tok.startswith("-"):
            continue
        return pathlib.Path(tok).name
    return None


def _sbatch_script_gap(command: str) -> str | None:
    m = SBATCH_RE.search(command)
    if not m:
        return None
    script_path = pathlib.Path(m.group(1).strip("'\""))
    if not script_path.is_absolute():
        script_path = PROJECT_DIR / script_path
    try:
        text = script_path.read_text()
    except OSError:
        return None  # ponytail: fail-open, script not written yet or path unresolved
    if "singularity" not in text:
        return (
            f"sbatch script '{script_path}' does not invoke singularity — the job body must "
            "run python/R through singularity exec, same as an interactive command would "
            "(docs/images.md HARD RULE)."
        )
    return None


def block_reason(agent_type: str, tool_name: str, command: str) -> str | None:
    if agent_type not in RESTRICTED_AGENTS or tool_name != "Bash" or not command:
        return None
    for subcmd in SPLIT_RE.split(command):
        binary = _first_binary(subcmd)
        if binary in COMPUTE_BINARIES and "singularity" not in subcmd:
            return (
                f"data_analyst_agent ran '{binary}' directly in Bash — python/R must run inside "
                "the required singularity image (docs/images.md HARD RULE, e.g. `singularity exec "
                "... {image}.sif python3 script.py`). No conda/venv/bare interpreter is permitted."
            )
    return _sbatch_script_gap(command)


def main() -> None:
    data = json.load(sys.stdin)
    reason = block_reason(
        data.get("agent_type", ""), data.get("tool_name", ""), data.get("tool_input", {}).get("command", "")
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
    ok = ("env -u SSL_CERT_FILE -u SSL_CERT_DIR singularity exec --bind /vol/projects:/vol/projects "
          "agentic_immunology/singularity/ciim.sif python3 temp/x/code/script.py")
    assert block_reason("data_analyst_agent", "Bash", ok) is None
    assert block_reason("data_analyst_agent", "Bash", "python3 temp/x/code/script.py") is not None
    assert block_reason("data_analyst_agent", "Bash", "Rscript temp/x/code/script.R") is not None
    assert block_reason("data_analyst_agent", "Bash", "ls temp/x/results") is None
    assert block_reason("data_analyst_agent", "Bash", "mkdir -p temp/x/code && python3 y.py") is not None
    assert block_reason("data_analyst_agent", "Bash", f"mkdir -p temp/x/code && {ok}") is None
    assert block_reason("study_designer_agent", "Bash", "python3 y.py") is None  # not restricted
    assert block_reason("data_analyst_agent", "Read", "python3 y.py") is None  # wrong tool
    assert block_reason("data_analyst_agent", "Bash", "") is None

    import tempfile
    global PROJECT_DIR
    real_project_dir = PROJECT_DIR
    with tempfile.TemporaryDirectory() as tmp:
        PROJECT_DIR = pathlib.Path(tmp)
        script = PROJECT_DIR / "job.sh"
        script.write_text("#!/bin/bash\npython3 script.py\n")
        assert block_reason("data_analyst_agent", "Bash", f"sbatch {script}") is not None
        script.write_text(f"#!/bin/bash\n{ok}\n")
        assert block_reason("data_analyst_agent", "Bash", f"sbatch {script}") is None
        assert block_reason("data_analyst_agent", "Bash", "sbatch not_written_yet.sh") is None  # fail-open
    PROJECT_DIR = real_project_dir
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _demo()
    else:
        main()
