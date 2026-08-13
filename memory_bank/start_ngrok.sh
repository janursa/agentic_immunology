#!/bin/bash
# Start ngrok tunnel → expose memory_bank/server.py publicly.
# Updates MEMORY_BANK_URL in ciim_agentic/.env automatically (the client-side
# config every ciim_agentic user reads). Same pattern as server/start_ngrok.sh,
# targeting a local port instead of a SLURM node.
#
# Usage:
#   python3 memory_bank/server.py &   # start the server first
#   bash memory_bank/start_ngrok.sh
#
# Optional: set NGROK_AUTHTOKEN in .env to avoid the 2-hour session limit.

MAIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$MAIN_DIR/.env"
CLIENT_ENV_FILE="$MAIN_DIR/ciim_agentic/.env"
NGROK="$MAIN_DIR/server/ngrok"

PORT=$(grep '^MEMORY_BANK_PORT=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
PORT="${PORT:-5055}"
WEB_ADDR="127.0.0.1:4041"  # distinct from server/start_ngrok.sh's default 4040, so both can run at once

NGROK_TOKEN=$(grep '^NGROK_AUTHTOKEN=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
if [ -n "$NGROK_TOKEN" ]; then
    "$NGROK" config add-authtoken "$NGROK_TOKEN" --config /tmp/ngrok_memory_bank.yml 2>/dev/null
    NGROK_CFG="--config /tmp/ngrok_memory_bank.yml"
else
    NGROK_CFG=""
    echo "[warn] No NGROK_AUTHTOKEN set — session limited to 2 hours."
fi

echo "Tunnelling to localhost:$PORT ..."
nohup "$NGROK" http "$PORT" $NGROK_CFG --web-addr="$WEB_ADDR" \
    --log=stdout --log-format=json \
    > /tmp/ngrok_memory_bank.log 2>&1 &
NGROK_PID=$!
echo "ngrok PID: $NGROK_PID"

echo -n "Waiting for tunnel URL"
PUBLIC_URL=""
for i in {1..20}; do
    sleep 1
    echo -n "."
    PUBLIC_URL=$(curl -s "http://$WEB_ADDR/api/tunnels" 2>/dev/null \
        | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for t in d.get('tunnels', []):
        if t.get('proto') == 'https':
            print(t['public_url'])
            break
except Exception:
    pass
" 2>/dev/null)
    [ -n "$PUBLIC_URL" ] && break
done
echo ""

if [ -z "$PUBLIC_URL" ]; then
    echo "ERROR: Could not get tunnel URL. Check /tmp/ngrok_memory_bank.log"
    kill "$NGROK_PID" 2>/dev/null
    exit 1
fi

if grep -q '^MEMORY_BANK_URL=' "$CLIENT_ENV_FILE" 2>/dev/null; then
    sed -i "s|^MEMORY_BANK_URL=.*|MEMORY_BANK_URL=${PUBLIC_URL}|" "$CLIENT_ENV_FILE"
else
    echo "MEMORY_BANK_URL=${PUBLIC_URL}" >> "$CLIENT_ENV_FILE"
fi

echo ""
echo "Tunnel active: $PUBLIC_URL  (ciim_agentic/.env updated)"
echo "Stop: kill $NGROK_PID"
wait "$NGROK_PID"
