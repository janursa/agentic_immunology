#!/usr/bin/env python3
"""
Gemma Agent — conversational immunology agent backed by a local Gemma server.

Usage:
    python agent.py                          # auto-discover server from SLURM
    python agent.py --server bioinf025:8080  # specify server explicitly
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    MAIN_DIR, MODEL_NAME, MAX_TOKENS, TEMPERATURE,
    MAX_TOOL_ROUNDS, SERVER_PORT, GEMMA_URL, GEMMA_API_KEY,
)
import tools as tool_module
from memory import Memory
from context import build_system_prompt

try:
    from openai import OpenAI
except ImportError:
    print("[error] 'openai' package not found.")
    sys.exit(1)


# ─── Server discovery ──────────────────────────────────────────────────────────

def discover_server() -> Optional[str]:
    """Return server URL: prefers GEMMA_URL from .env if it looks like a public URL,
    otherwise falls back to SLURM node discovery."""
    # If .env has a non-localhost URL (e.g. ngrok), use it directly
    if GEMMA_URL and not GEMMA_URL.startswith("http://localhost") and not GEMMA_URL.startswith("http://127"):
        return GEMMA_URL
    # SLURM discovery
    try:
        node = subprocess.check_output(
            "squeue -u $USER --name=gemma4-server -h -o '%N' 2>/dev/null",
            shell=True, text=True,
        ).strip().split(",")[0]
        if node and node != "(null)":
            return f"http://{node}:{SERVER_PORT}/v1"
    except Exception:
        pass
    # Fallback: read latest server log
    for log in sorted(
        glob.glob(os.path.join(MAIN_DIR, "server", "logs", "gemma4_server", "*.log")),
        key=os.path.getmtime, reverse=True,
    )[:3]:
        try:
            for line in open(log):
                m = re.search(r"base_url\s*=\s*'(http://\S+)'", line)
                if m:
                    return m.group(1)
        except Exception:
            pass
    return None


# ─── Core agent ───────────────────────────────────────────────────────────────

class GemmaAgent:
    def __init__(self, base_url: str, memory: Memory, api_key: str = "none"):
        self.client   = OpenAI(base_url=base_url, api_key=api_key)
        self.memory   = memory
        self.messages: list[dict] = []

    def start(self):
        """Initialise conversation with the system prompt."""
        system_prompt = build_system_prompt(
            session_dir   = self.memory.session_dir,
            history_block = self.memory.history_block(),
        )
        self.messages = [{"role": "system", "content": system_prompt}]

    def respond(self, user_input: str) -> str:
        """
        Add a user message, run the tool loop until the model gives a text
        response, then return that response.

        All messages — including intermediate tool calls and results — are
        persisted in self.messages so the model has full context in future turns.
        """
        self.messages.append({"role": "user", "content": user_input})

        for _ in range(MAX_TOOL_ROUNDS):
            response = self.client.chat.completions.create(
                model       = MODEL_NAME,
                messages    = self.messages,
                tools       = tool_module.DEFINITIONS,
                tool_choice = "auto",
                max_tokens  = MAX_TOKENS,
                temperature = TEMPERATURE,
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                # Persist tool-call request
                self.messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id, "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                })
                # Execute each tool and persist result
                for tc in msg.tool_calls:
                    name = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    _print_tool(name, args)
                    result = tool_module.execute(name, args)
                    _print_tool_result(result)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
                continue  # back to model

            # Final text response
            text = (msg.content or "").strip()
            self.messages.append({"role": "assistant", "content": text})
            return text

        return "[agent] Reached max tool rounds without a final response."

    def end_session(self):
        """Ask model to summarise, save to memory, close out."""
        if len(self.messages) <= 1:
            return
        print("\nSaving session…")
        summary = self.respond(
            "Summarise this session in 1–2 sentences for the memory log. "
            "Include: what was asked, what was done, key output file paths if any. "
            "Reply with only the summary text, no preamble."
        )
        self.memory.append_log(f"Session ended.\nSummary: {summary}")
        self.memory.save_session(summary)
        print(f"  Session saved → {self.memory.session_dir}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Gemma immunology agent")
    parser.add_argument("--server", help="Server, e.g. bioinf025:8080")
    args = parser.parse_args()

    # Resolve server URL
    if args.server:
        url = args.server
        if not url.startswith("http"):
            url = f"http://{url}/v1"
        if not url.endswith("/v1"):
            url = url.rstrip("/") + "/v1"
    else:
        print("Discovering Gemma server…", end=" ", flush=True)
        url = discover_server()
        if url:
            print(f"found: {url}")
        else:
            print("not found.")
            raw = input("Enter server (e.g. bioinf025:8080): ").strip()
            url = f"http://{raw}/v1" if not raw.startswith("http") else raw

    # Check connectivity
    try:
        urllib.request.urlopen(url.replace("/v1", "/health"), timeout=5)
    except Exception as e:
        print(f"[warn] Health check failed ({e}). Proceeding anyway…")

    # Start agent
    memory = Memory()
    agent  = GemmaAgent(base_url=url, memory=memory, api_key=GEMMA_API_KEY)
    agent.start()

    past = len(memory.sessions)
    print(f"\n{'═'*62}")
    print("  Gemma Agent — Immunology Research Assistant")
    print(f"  Server  : {url}")
    print(f"  Session : {memory.session_dir}")
    print(f"  History : {past} past session{'s' if past != 1 else ''}")
    print("  Commands: 'history' | 'reset' | 'exit'")
    print(f"{'═'*62}\n")

    # Main loop
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            agent.end_session()
            break

        if not user_input:
            continue

        low = user_input.lower()

        if low in ("exit", "quit"):
            agent.end_session()
            print("Bye.")
            break

        if low == "reset":
            agent.start()
            print("[Conversation reset — memory kept.]\n")
            continue

        if low in ("history", "memory"):
            print(memory.history_block() or "(no past sessions yet)")
            continue

        print()
        response = agent.respond(user_input)
        print(f"\n{response}\n")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _print_tool(name: str, args: dict):
    parts = []
    for k, v in args.items():
        s = str(v)
        parts.append(f"{k}={s[:60]!r}{'…' if len(s) > 60 else ''}")
    print(f"  \033[2m[{name}({', '.join(parts)})]\033[0m", flush=True)


def _print_tool_result(result: str):
    preview = result.strip().replace("\n", " ")[:160]
    print(f"  \033[2m→ {preview}{'…' if len(result.strip()) > 160 else ''}\033[0m", flush=True)


if __name__ == "__main__":
    main()
