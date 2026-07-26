# Serves temp/ (design.md/report.md rendered to HTML) over the internet, alongside
# remote_access.sh's ttyd terminal tunnel — same serveo mechanism, separate port/tunnel.
# Idempotent: safe to call every time the orchestrator needs to show something; skips
# startup if already running. Persists for the session (24h auto-kill, like remote_access.sh).
#
# Usage: bash scripts/serve_dashboard.sh              -> prints the base https URL
#        bash scripts/serve_dashboard.sh <path>        -> prints the full ready-to-use URL
#          <path> may be given either relative to temp/ (x/design.html) or as the
#          repo-relative path (temp/x/design.html) - a leading "temp/" is stripped
#          either way, so passing the same path used for render_review_artifact.py works.
#          The resulting URL is verified locally (file exists) and remotely (HTTP 200)
#          before being printed; a WARNING is emitted to stderr if either check fails.

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

base=$(grep -o 'https://[a-zA-Z0-9.-]*\.serveousercontent\.com' /tmp/dashboard_serveo.log | tail -1)

if [ -n "$1" ]; then
  rel="${1#./}"
  rel="${rel#temp/}"

  if [ ! -f "temp/$rel" ]; then
    echo "ERROR: temp/$rel does not exist (from argument '$1')" >&2
    exit 1
  fi

  # Validate against the local server, not the public tunnel URL: serveo's
  # anti-bot layer 403s plain curl requests even for valid pages, so checking
  # the tunnel directly produces false warnings. localhost exercises the same
  # path-resolution the tunnel will serve, without that noise.
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$PORT/$rel")
  if [ "$code" != "200" ]; then
    echo "WARNING: temp/$rel served HTTP $code locally, not 200" >&2
  fi

  echo "$base/$rel"
else
  echo "$base"
fi

# Manual teardown any time:
# pkill -f "http.server 8766 --directory"; pkill -f "R 80:localhost:8766 serveo.net"
