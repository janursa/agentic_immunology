# Serves temp/ (design.md/report.md rendered to HTML) over the internet, alongside
# remote_access.sh's ttyd terminal tunnel — same serveo mechanism, separate port/tunnel.
# Idempotent: safe to call every time the orchestrator needs to show something; skips
# startup if already running. Persists for the session (24h auto-kill, like remote_access.sh).
#
# Usage: bash scripts/serve_dashboard.sh   -> prints the base https URL
#        Full link to a rendered page = "<base URL>/<path under temp/>"

cd "$(dirname "$0")/.." || exit 1
PORT=8766

if ! pgrep -f "http.server $PORT --directory" >/dev/null; then
  setsid nohup python3 -m http.server "$PORT" --directory temp/ \
    >/tmp/dashboard_http.log 2>&1 < /dev/null &
  disown
fi

if ! pgrep -f "R 80:localhost:$PORT serveo.net" >/dev/null; then
  setsid nohup ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
    -R 80:localhost:$PORT serveo.net \
    >/tmp/dashboard_serveo.log 2>&1 < /dev/null &
  disown
  sleep 6

  setsid nohup bash -c "sleep 86400; pkill -f 'http.server $PORT --directory'; pkill -f 'R 80:localhost:$PORT serveo.net'" \
    >/dev/null 2>&1 < /dev/null &
  disown
fi

grep -o 'https://[a-zA-Z0-9.-]*\.serveousercontent\.com' /tmp/dashboard_serveo.log | tail -1

# Manual teardown any time:
# pkill -f "http.server 8766 --directory"; pkill -f "R 80:localhost:8766 serveo.net"
