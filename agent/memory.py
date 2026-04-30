"""Per-session workspace."""

import os
from datetime import datetime
from config import TEMP_DIR


class Memory:
    def __init__(self):
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.session_dir = os.path.join(TEMP_DIR, f"session_{stamp}")
        os.makedirs(self.session_dir, exist_ok=True)
        self.log_path = os.path.join(self.session_dir, "LOG.md")
        self._init_log(stamp)

    def append_log(self, entry: str):
        """Append a timestamped entry to this session's LOG.md."""
        ts = datetime.now().strftime("%H:%M:%S")
        with open(self.log_path, "a") as f:
            f.write(f"\n## {ts}\n{entry.strip()}\n")

    def _init_log(self, stamp: str):
        with open(self.log_path, "w") as f:
            f.write(f"# Agent Session Log — {stamp}\n\n")
            f.write(f"Workspace: {self.session_dir}\n")
