"""Per-session workspace + cross-session history index."""

import json
import os
from datetime import datetime
from config import TEMP_DIR, SESSIONS_INDEX, AGENT_DIR


class Memory:
    def __init__(self):
        # ── Per-session workspace ───────────────────────────────────────────────
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.session_dir = os.path.join(TEMP_DIR, f"session_{stamp}")
        os.makedirs(self.session_dir, exist_ok=True)
        self.log_path = os.path.join(self.session_dir, "LOG.md")
        self._init_log(stamp)

        # ── Cross-session history ───────────────────────────────────────────────
        os.makedirs(AGENT_DIR, exist_ok=True)
        self.sessions: list[dict] = self._load_json(SESSIONS_INDEX, [])

    # ── Public API ─────────────────────────────────────────────────────────────

    def append_log(self, entry: str):
        """Append a timestamped entry to this session's LOG.md."""
        ts = datetime.now().strftime("%H:%M:%S")
        with open(self.log_path, "a") as f:
            f.write(f"\n## {ts}\n{entry.strip()}\n")

    def save_session(self, summary: str):
        """Record this session in the global sessions index."""
        self.sessions.append({
            "date":        datetime.now().strftime("%Y-%m-%d %H:%M"),
            "session_dir": self.session_dir,
            "summary":     summary,
        })
        self.sessions = self.sessions[-30:]
        with open(SESSIONS_INDEX, "w") as f:
            json.dump(self.sessions, f, indent=2)

    def history_block(self) -> str:
        """Return formatted past session history for the system prompt."""
        if not self.sessions:
            return ""
        lines = ["## Past Sessions (most recent first)"]
        for s in reversed(self.sessions[-6:]):
            lines.append(f"  [{s['date']}] {s['summary']}")
            lines.append(f"    Workspace: {s['session_dir']}")
        return "\n".join(lines)

    # ── Internal ───────────────────────────────────────────────────────────────

    def _init_log(self, stamp: str):
        with open(self.log_path, "w") as f:
            f.write(f"# Agent Session Log — {stamp}\n\n")
            f.write(f"Workspace: {self.session_dir}\n")

    def _load_json(self, path: str, default):
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                pass
        return default
