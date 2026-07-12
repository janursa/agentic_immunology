#!/usr/bin/env bash
# Launch the voice server + a public tunnel, then print the one URL to open.
# Run from the project directory you want Claude to work in (cwd is inherited by claude -p).
#
# Tunnel = localhost.run over SSH (no account). cloudflared was tried but this box's
# firewall blocks its edge ports (7844/QUIC); outbound SSH is open, so localhost.run works.
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${VOICE_PORT:-8765}"
PY="${VOICE_PYTHON:-$HOME/miniconda3/envs/py10/bin/python}"

# ponytail: single-user box — clear any prior instance so each launch is a clean, fresh token+URL
pkill -f "voice-conversation/server.py" 2>/dev/null
pkill -f "nokey@localhost.run" 2>/dev/null
sleep 0.5

TOKEN="$("$PY" -c 'import secrets;print(secrets.token_urlsafe(16))')"
export VOICE_TOKEN="$TOKEN" VOICE_PORT="$PORT"

nohup "$PY" "$DIR/server.py" >"$DIR/.server.log" 2>&1 &
nohup ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
      -R "80:localhost:$PORT" nokey@localhost.run >"$DIR/.tunnel.log" 2>&1 &

URL=""
for _ in $(seq 1 40); do
  URL="$(grep -ohE 'https://[a-z0-9]+\.lhr\.life' "$DIR/.tunnel.log" | head -1)"
  [ -n "$URL" ] && break
  sleep 1
done

if [ -z "$URL" ]; then
  echo "ERROR: tunnel did not come up. See $DIR/.tunnel.log"
  exit 1
fi
echo "OPEN_THIS_URL: ${URL}/?k=${TOKEN}"
