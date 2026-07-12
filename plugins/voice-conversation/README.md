# voice-conversation

Talk to Claude Code by voice through a web page. You speak in your browser, a cheap
OpenAI model mediates, Claude Code does the real work in your project, and the reply is
spoken back. Built to work from a **remote/headless box** (the browser on your laptop owns
the mic/speakers; the server here is reached over a public HTTPS tunnel).

## Pieces

| File | Role |
|------|------|
| `server.py` | stdlib HTTP server. `GET /` serves the voice page; `POST /talk` runs one turn: OpenAI composes a prompt → `claude -p --resume` (one dedicated session in the launch cwd) → OpenAI narrates the reply. `/talk` requires a per-launch token. |
| `start.sh` | Launcher. Mints a random token, starts `server.py` (on `127.0.0.1:8765`) + an SSH reverse tunnel to `localhost.run`, waits for the public URL, prints `OPEN_THIS_URL: https://….lhr.life/?k=<token>`. Kills any prior instance first. |
| `conversation.md` | The `/conversation` slash command — tells Claude to run `start.sh` in the current project dir and hand you the URL. |

## How it works

```
browser (laptop): mic -> Web Speech STT -> /talk -> TTS speaks reply
        |  (public HTTPS)
   localhost.run (SSH reverse tunnel)  ->  server.py (this box, 127.0.0.1:8765)
        |
   OpenAI gpt-4o-mini (compose prompt) -> claude -p --resume -> OpenAI (narrate)
```

- **Browser handles speech** via the Web Speech API → **Chrome only**, and needs a secure
  context (HTTPS), which the localhost.run tunnel provides.
- **Token guard**: the tunnel URL is public, and `/talk` can drive Claude Code (run commands,
  edit files), so every `/talk` request must carry the `?k=` token. No token → HTTP 403.
- **Session continuity**: first turn starts a Claude session; later turns use `--resume <id>`,
  so Claude remembers the conversation. Separate from the TUI session you launched it from.

## Use

Type `/conversation` in any Claude Code session, open the printed URL in Chrome, click
**Start talking**. Or manually:

```bash
cd /your/project && bash plugins/voice-conversation/start.sh
```

## Dependencies

- `ssh` (for the `localhost.run` reverse tunnel — no account needed).
- `openai` python pkg + `OPENAI_API_KEY` in the environment.
- `claude` CLI on PATH.
- py10 conda python (override with `VOICE_PYTHON`).

> Why localhost.run and not cloudflared/ngrok: this box's firewall blocks cloudflared's
> edge ports (7844/QUIC + HTTP/2), so cloudflared quick tunnels fail here. Outbound SSH is
> open, so localhost.run works with zero setup. ngrok (`:443`) is also reachable but needs
> an account — swap the tunnel line in `start.sh` if you ever want a stable subdomain.

## Config (env vars)

- `VOICE_MODEL` (default `gpt-4o-mini`), `VOICE_PORT` (default `8765`),
  `VOICE_CLAUDE_TIMEOUT` (default `600`s), `VOICE_PYTHON`.

## Install / wiring

The plugin lives here in the repo; the `/conversation` command is wired into Claude Code by
symlinking the command file into the user commands dir:

```bash
ln -s "$PWD/plugins/voice-conversation/conversation.md" ~/.claude/commands/conversation.md
```

Edit files here in the repo; the symlink means changes are live.

## Known ceilings (`ponytail:`)

- Single user / single Claude session per box (global state). Add a session map for concurrency.
- Browser STT/TTS (free, Chrome-only). Swap to OpenAI Whisper/TTS if quality matters.
- Auto re-listen waits for TTS to finish to avoid echo; not full barge-in.
