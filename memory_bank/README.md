# memory_bank

Raw feedback-interaction log. Host infra, not part of `ciim_agentic` — collects
what users actually said, no LLM summarization involved.

## Flow
`ciim_agentic/.claude/hooks/capture_feedback.py` fires automatically on the
user's next message after a design/results review is presented (marked by
`mark_awaiting_feedback.py`), and POSTs the raw text to this server, along
with the `design.md`/`findings.md` content that was actually shown
(`presented` field — read verbatim off disk, not summarized) so a record has
both sides of the exchange. No curation yet — `POST /interactions` just
appends one JSON line to `memory_bank/interactions.jsonl`. Turning that into
`memory_bank/memory_blob.jsonl` lessons is a separate, not-yet-built step.

## Run it
1. Server side, host root `.env` (see `.env.example`):
   - `MEMORY_BANK_TOKENS=user1:tok1,user2:tok2` — token->user map, one entry
     per person allowed to write
   - `MEMORY_BANK_PORT` — default `5055`
2. Client side, `ciim_agentic/.env` (see `ciim_agentic/.env.example`) — each
   person using ciim_agentic sets their own:
   - `MEMORY_BANK_URL` — where the server is (`http://localhost:5055`, or a
     tunnel URL)
   - `MEMORY_BANK_TOKEN` — their own token, must match one value in
     `MEMORY_BANK_TOKENS` above. Tokens are issued by whoever runs the
     server — request one from jalil.nourisa@gmail.com.
3. Start the server: `bash memory_bank/start_server.sh` (backgrounds it with
   `nohup`, writes a PID file, survives logout; `bash memory_bank/start_server.sh stop`
   to stop it, `status` to check).
4. Network-reachable from other machines: `bash memory_bank/start_ngrok.sh`
   (reuses `server/ngrok` + `NGROK_AUTHTOKEN`; writes the public URL to
   `MEMORY_BANK_URL` in `ciim_agentic/.env`). Skip this for localhost-only use.

Not wired into `ciim_agentic/setup/install.sh` — start it separately. The
capturing hook fails open (logs to stderr, never blocks) if the server isn't
configured or reachable.
