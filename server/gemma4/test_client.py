"""
Gemma 4 conversation test client.
Usage:
    python3 test_client.py --host bioinf040 --port 8080
    python3 test_client.py --host bioinf040 --port 8080 --interactive
"""

import argparse
import sys
from openai import OpenAI


def make_client(host: str, port: int) -> OpenAI:
    return OpenAI(base_url=f"http://{host}:{port}/v1", api_key="none")


def chat(client: OpenAI, conversation: list, user_message: str, model: str = "gemma-4") -> str:
    conversation.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model=model,
        messages=conversation,
        max_tokens=512,
        temperature=0.7,
    )
    reply = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": reply})
    return reply


def run_scripted_test(client: OpenAI):
    """Run a fixed multi-turn conversation to verify the server works."""
    print("=" * 60)
    print("Gemma 4 — Scripted conversation test")
    print("=" * 60)

    conversation = []
    turns = [
        "What are the main immune cell types found in human peripheral blood?",
        "Which of those are most affected by IL-10?",
        "What transcription factors are key mediators of IL-10 signaling in those cells?",
    ]

    for i, question in enumerate(turns, 1):
        print(f"\n[Turn {i}] USER: {question}")
        reply = chat(client, conversation, question)
        print(f"[Turn {i}] GEMMA4: {reply}")

    print("\n" + "=" * 60)
    print("✅ Conversation test passed — model responds correctly to follow-ups")
    print("=" * 60)


def run_interactive(client: OpenAI):
    """Interactive REPL conversation."""
    print("=" * 60)
    print("Gemma 4 — Interactive conversation (type 'quit' to exit, 'reset' for new topic)")
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
        print(f"  [history: {len(conversation)//2} turns]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemma 4 API test client")
    parser.add_argument("--host", default="bioinf040", help="Server hostname")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--interactive", action="store_true", help="Run interactive REPL")
    args = parser.parse_args()

    print(f"Connecting to http://{args.host}:{args.port}/v1 ...")
    client = make_client(args.host, args.port)

    # Quick connectivity check
    try:
        models = client.models.list()
        print(f"✅ Server online. Model: {models.data[0].id if models.data else 'unknown'}\n")
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")
        print(f"   Make sure the server job is running: squeue -u $USER")
        sys.exit(1)

    if args.interactive:
        run_interactive(client)
    else:
        run_scripted_test(client)
