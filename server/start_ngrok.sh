#!/bin/bash
# Start ngrok tunnel → expose Gemma server publicly
# Updates GEMMA_URL in .env automatically
#
# Usage:
#   bash start_ngrok.sh              # tunnel to bioinf034:8080 (auto-detected)
#   bash start_ngrok.sh bioinf034    # specify node explicitly
#
# Optional: set NGROK_AUTHTOKEN in .env to avoid 2-hour session limit

MAIN_DIR=/vol/projects/CIIM/agentic_central
ENV_FILE="$MAIN_DIR/.env"
NGROK="$MAIN_DIR/server/ngrok"

# ── resolve target node ────────────────────────────────────────────────────────
TARGET_NODE="${1:-}"
if [ -z "$TARGET_NODE" ]; then
    TARGET_NODE=$(squeue -u "$USER" --name=gemma4-server -h -o '%N' 2>/dev/null | cut -d, -f1)
fi
if [ -z "$TARGET_NODE" ] || [ "$TARGET_NODE" = "(null)" ]; then
    echo "ERROR: gemma4-server SLURM job not found. Start it first:"
    echo "  cd $MAIN_DIR/server && sbatch server_gemma4.sh"
    exit 1
fi
TARGET="$TARGET_NODE:8080"
echo "Tunnelling to $TARGET ..."

# ── load ngrok auth token if set ───────────────────────────────────────────────
NGROK_TOKEN=$(grep '^NGROK_AUTHTOKEN=' "$ENV_FILE" | cut -d'=' -f2-)
if [ -n "$NGROK_TOKEN" ]; then
    "$NGROK" config add-authtoken "$NGROK_TOKEN" --config /tmp/ngrok_ciim.yml 2>/dev/null
    NGROK_CFG="--config /tmp/ngrok_ciim.yml"
else
    NGROK_CFG=""
    echo "[warn] No NGROK_AUTHTOKEN set — session limited to 2 hours."
    echo "       Get a free token at https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "       Then set NGROK_AUTHTOKEN=hf_... in $ENV_FILE"
fi

# ── start ngrok in background (nohup so it survives shell exit) ───────────────
nohup "$NGROK" http "$TARGET" $NGROK_CFG \
    --log=stdout --log-format=json \
    > /tmp/ngrok_ciim.log 2>&1 &
NGROK_PID=$!
echo "ngrok PID: $NGROK_PID"

# ── wait for tunnel URL ────────────────────────────────────────────────────────
echo -n "Waiting for tunnel URL"
PUBLIC_URL=""
for i in {1..20}; do
    sleep 1
    echo -n "."
    PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null \
        | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for t in d.get('tunnels', []):
        if t.get('proto') == 'https':
            print(t['public_url'])
            break
except: pass
" 2>/dev/null)
    if [ -n "$PUBLIC_URL" ]; then
        break
    fi
done
echo ""

if [ -z "$PUBLIC_URL" ]; then
    echo "ERROR: Could not get tunnel URL. Check /tmp/ngrok_ciim.log"
    kill "$NGROK_PID" 2>/dev/null
    exit 1
fi

# ── update .env ───────────────────────────────────────────────────────────────
FULL_URL="${PUBLIC_URL}/v1"
sed -i "s|^GEMMA_URL=.*|GEMMA_URL=${FULL_URL}|" "$ENV_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Tunnel active!"
echo "  Public URL : $PUBLIC_URL"
echo "  API base   : $FULL_URL"
echo "  .env updated automatically"
echo ""
echo "  Share with anyone:"
echo "    base_url = '$FULL_URL'"
echo "    api_key  = $(grep '^GEMMA_API_KEY=' $ENV_FILE | cut -d'=' -f2-)"
echo ""
echo "  Stop tunnel: kill $NGROK_PID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Tunnel running. Press Ctrl+C to stop."
wait "$NGROK_PID"
