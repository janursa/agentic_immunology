"""
Wait for the Gemma 4 server job to start, then run the conversation test.

Usage:
    python3 wait_and_test.py --job 10209856
    python3 wait_and_test.py --job 10209856 --interactive
"""

import argparse
import subprocess
import sys
import time
import re
import os

LOG_DIR = "/vol/projects/CIIM/agentic_central/server/gemma4/logs"


def get_job_state(job_id: str) -> str:
    r = subprocess.run(
        ["squeue", "-j", job_id, "-o", "%T", "--noheader"],
        capture_output=True, text=True
    )
    state = r.stdout.strip()
    if not state:
        r2 = subprocess.run(
            ["sacct", "-j", job_id, "-o", "State", "--noheader", "-X"],
            capture_output=True, text=True
        )
        state = r2.stdout.strip().split()[0] if r2.stdout.strip() else ""
    return state


def get_node_from_log(job_id: str) -> str | None:
    log = os.path.join(LOG_DIR, f"server_{job_id}.log")
    if not os.path.exists(log):
        return None
    with open(log) as f:
        for line in f:
            m = re.search(r"Node\s*:\s*(\S+)", line)
            if m:
                return m.group(1)
    return None


def server_ready(host: str, port: int) -> bool:
    try:
        from openai import OpenAI
        client = OpenAI(base_url=f"http://{host}:{port}/v1", api_key="none")
        client.models.list()
        return True
    except Exception:
        return False


def wait_for_server(job_id: str, port: int = 8080, timeout: int = 3600) -> tuple[str, int]:
    print(f"Job {job_id}: waiting to start...", flush=True)
    deadline = time.time() + timeout

    while time.time() < deadline:
        state = get_job_state(job_id)

        if state == "RUNNING":
            # Wait for log to appear with hostname
            node = None
            for _ in range(12):
                node = get_node_from_log(job_id)
                if node:
                    break
                print("  RUNNING but log not ready yet, waiting 5s...", flush=True)
                time.sleep(5)

            if not node:
                print("  Could not read node from log, retrying loop...", flush=True)
                time.sleep(10)
                continue

            print(f"Job RUNNING on {node} — waiting for llama-server to come online...", flush=True)
            while time.time() < deadline:
                if server_ready(node, port):
                    return node, port
                print("  server not ready yet, retrying in 10s...", flush=True)
                time.sleep(10)

        elif state in ("FAILED", "CANCELLED", "TIMEOUT"):
            log = os.path.join(LOG_DIR, f"server_{job_id}.log")
            print(f"Job ended with state: '{state}'. See log: {log}")
            sys.exit(1)

        else:
            print(f"  state={state or 'PENDING'} — sleeping 30s...", flush=True)
            time.sleep(30)

    print("Timed out waiting for server.")
    sys.exit(1)


def chat(client, conversation: list, user_message: str) -> str:
    conversation.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="gemma-4",
        messages=conversation,
        max_tokens=512,
        temperature=0.7,
    )
    reply = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": reply})
    return reply


def run_scripted_test(client):
    print("\n" + "=" * 60)
    print("Gemma 4 — Scripted multi-turn conversation test")
    print("=" * 60)
    conversation = []
    turns = [
        "What are the main immune cell types found in human peripheral blood?",
        "Which of those are most affected by IL-10?",
        "What transcription factors are key mediators of IL-10 signaling in those cells?",
    ]
    for i, q in enumerate(turns, 1):
        print(f"\n[Turn {i}] YOU: {q}")
        reply = chat(client, conversation, q)
        print(f"[Turn {i}] GEMMA4: {reply}")
    print("\n✅ Test passed — multi-turn conversation works correctly.")


def run_interactive(client):
    print("\n" + "=" * 60)
    print("Gemma 4 — Interactive (type 'quit' to exit, 'reset' for new topic)")
    print("=" * 60)
    conversation = []
    while True:
        try:
            user_input = input("\nYOU: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if user_input.lower() in ("quit", "exit"):
            break
        if user_input.lower() == "reset":
            conversation = []
            print("[Conversation reset]")
            continue
        if not user_input:
            continue
        reply = chat(client, conversation, user_input)
        print(f"GEMMA4: {reply}")
        print(f"  [{len(conversation)//2} turns in history]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", default="10219185", help="SLURM job ID")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--timeout", type=int, default=3600, help="Seconds to wait for server (default: 3600)")
    args = parser.parse_args()

    node, port = wait_for_server(args.job, args.port, timeout=args.timeout)

    from openai import OpenAI
    client = OpenAI(base_url=f"http://{node}:{port}/v1", api_key="none")
    print(f"\n✅ Server online at http://{node}:{port}/v1\n")

    if args.interactive:
        run_interactive(client)
    else:
        run_scripted_test(client)
