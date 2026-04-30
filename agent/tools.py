"""Tool registry: definitions (OpenAI format) + execution."""

import os
import glob
import subprocess
from config import ALLOWED_WRITE_PREFIXES, BLOCKED_COMMANDS, MAIN_DIR, TOOL_TIMEOUT

# ─── Definitions (passed to the model) ────────────────────────────────────────

DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the full text of a file. "
                "Use this to inspect overview .md files, Python modules, data lists, etc. "
                "Long files are automatically truncated to 8 000 characters."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute file path"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": (
                "List the contents of a directory. "
                "Set recursive=true to walk up to 2 levels deep."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path":      {"type": "string",  "description": "Absolute directory path"},
                    "recursive": {"type": "boolean", "description": "Walk 2 levels deep (default false)"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a bash command (max 60 s). "
                "Good for: head/tail/grep on data files, squeue, scancel, "
                "submitting sbatch scripts, checking disk usage, running Python scripts. "
                "stdout+stderr returned (truncated at 6 000 chars)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command":     {"type": "string", "description": "Bash command to run"},
                    "working_dir": {"type": "string", "description": "Working directory (optional; defaults to MAIN_DIR)"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write (create or overwrite) a file. "
                "ONLY allowed under temp/ or agent/ subdirectories of the main dir."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path":    {"type": "string", "description": "Absolute path to write"},
                    "content": {"type": "string", "description": "File content"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Find files matching a glob pattern inside a directory (recursive).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Root directory to search"},
                    "pattern":   {"type": "string", "description": "Glob pattern, e.g. '*.h5ad', '*scRNA*'"},
                },
                "required": ["directory", "pattern"],
            },
        },
    },
]


# ─── Execution ─────────────────────────────────────────────────────────────────

def execute(name: str, args: dict) -> str:
    """Dispatch a tool call and return the result as a string."""
    try:
        if name == "read_file":
            return _read_file(args["path"])

        elif name == "list_directory":
            return _list_directory(args["path"], args.get("recursive", False))

        elif name == "run_command":
            return _run_command(args["command"], args.get("working_dir", MAIN_DIR))

        elif name == "write_file":
            return _write_file(args["path"], args["content"])

        elif name == "search_files":
            return _search_files(args["directory"], args["pattern"])

        else:
            return f"[tool error] Unknown tool: {name}"

    except KeyError as e:
        return f"[tool error] Missing argument: {e}"
    except Exception as e:
        return f"[tool error] {type(e).__name__}: {e}"


# ─── Implementations ───────────────────────────────────────────────────────────

def _read_file(path: str) -> str:
    if not os.path.isfile(path):
        return f"[error] File not found: {path}"
    with open(path, errors="replace") as f:
        content = f.read()
    if len(content) > 8000:
        content = content[:8000] + f"\n\n[... truncated — {len(content):,} chars total ...]"
    return content


def _list_directory(path: str, recursive: bool) -> str:
    if not os.path.isdir(path):
        return f"[error] Directory not found: {path}"
    if recursive:
        lines = []
        for root, dirs, files in os.walk(path):
            depth = root.replace(path, "").count(os.sep)
            if depth >= 2:
                dirs.clear()
                continue
            indent = "  " * depth
            lines.append(f"{indent}{os.path.basename(root) or path}/")
            for fname in sorted(files):
                size = os.path.getsize(os.path.join(root, fname))
                lines.append(f"{indent}  {fname}  ({size:,} B)")
        return "\n".join(lines) or "(empty)"
    else:
        lines = []
        for item in sorted(os.listdir(path)):
            full = os.path.join(path, item)
            if os.path.isdir(full):
                lines.append(f"{item}/")
            else:
                lines.append(f"{item}  ({os.path.getsize(full):,} B)")
        return "\n".join(lines) or "(empty)"


def _run_command(command: str, working_dir: str) -> str:
    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            return f"[blocked] Dangerous command pattern: '{blocked}'"
    if not os.path.isdir(working_dir):
        working_dir = MAIN_DIR
    env = os.environ.copy()
    env["PATH"] = "/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin:" + env.get("PATH", "")
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True,
        cwd=working_dir, timeout=TOOL_TIMEOUT, env=env,
    )
    out = (result.stdout + result.stderr).strip()
    if len(out) > 6000:
        out = out[:6000] + "\n[... truncated ...]"
    return out or "(no output)"


def _write_file(path: str, content: str) -> str:
    if not any(path.startswith(p) for p in ALLOWED_WRITE_PREFIXES):
        return (
            f"[blocked] Can only write inside temp/ or agent/ directories.\n"
            f"Attempted path: {path}"
        )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"[ok] Written: {path}  ({len(content):,} chars)"


def _search_files(directory: str, pattern: str) -> str:
    matches = sorted(glob.glob(os.path.join(directory, "**", pattern), recursive=True))
    if not matches:
        return f"No files found for pattern '{pattern}' in {directory}"
    lines = matches[:60]
    suffix = f"\n... ({len(matches) - 60} more)" if len(matches) > 60 else ""
    return "\n".join(lines) + suffix
