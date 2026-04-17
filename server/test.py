#!/usr/bin/env python3
"""
Quick smoke-test for the Gemma agent.
Sends two prompts that exercise tool use and routing:
  1. Navigation test — should go to summary_stats, not datalake
  2. Coding test    — should write a script and save it
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))
from agent import GemmaAgent, discover_server
from memory import Memory

# ── discover server ────────────────────────────────────────────────────────────
print("Discovering server…", end=" ", flush=True)
url = discover_server()
if not url:
    url_raw = input("not found.\nEnter server (e.g. bioinf034:8080): ").strip()
    url = f"http://{url_raw}/v1" if not url_raw.startswith("http") else url_raw
else:
    print(f"found: {url}")

# ── run agent ─────────────────────────────────────────────────────────────────
memory = Memory()
agent  = GemmaAgent(base_url=url, memory=memory)
agent.start()

print(f"\n{'='*60}")
print("TEST 1 — Navigation / routing (should use summary_stats)")
print('='*60)
r1 = agent.respond("Can you compare CD8T and CD4T aging signatures?")
print(f"\n{r1}\n")

print(f"\n{'='*60}")
print("TEST 2 — Tool use / planning")
print('='*60)
r2 = agent.respond("List the available cell types in the summary stats.")
print(f"\n{r2}\n")

agent.end_session()
print("\nTest complete.")
