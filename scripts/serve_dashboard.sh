# Serves ONE task's temp/{task}/ dir (design.md/report.md rendered to HTML) over the
# internet, alongside remote_access.sh's ttyd terminal tunnel — same serveo mechanism,
# separate port/tunnel. Only the named task is exposed, never the whole temp/ tree.
# Idempotent: safe to call every time the orchestrator needs to show something; the
# http server is restarted only when the task changes, the ssh tunnel never is (it is
# bound to the port, not the directory, so the base URL stays stable).
# Persists for the session (24h auto-kill, like remote_access.sh).
#
# Usage: bash scripts/serve_dashboard.sh <path>   -> prints the full ready-to-use URL
#          <path> may be given either relative to temp/ (x/design.html) or as the
#          repo-relative path (temp/x/design.html) - a leading "temp/" is stripped
#          either way, so passing the same path used for render_review_artifact.py works.
#          The path argument is required: it names the task whose dir gets served.
#          The resulting URL is verified locally (file exists, HTTP 200) and the tunnel
#          URL is verified non-empty before being printed.

cd "$(dirname "$0")/.." || exit 1
PORT=8766

if [ -z "$1" ]; then
  echo "ERROR: a path is required, e.g. bash scripts/serve_dashboard.sh temp/mytask/design.html" >&2
  exit 1
fi

rel="${1#./}"
rel="${rel#temp/}"
task="${rel%%/*}"
page="${rel#*/}"

if [ "$task" = "$rel" ] || [ -z "$page" ]; then
  echo "ERROR: '$1' has no task segment - expected temp/{task}/{page}.html" >&2
  exit 1
fi

if [ ! -f "temp/$rel" ]; then
  echo "ERROR: temp/$rel does not exist (from argument '$1')" >&2
  exit 1
fi

# Serve only this task. Restart the server if it is down or rooted at another task.
running_dir=$(pgrep -af "[p]ython3 -m http.server $PORT" | sed -n 's/.*--directory \([^ ]*\).*/\1/p' | head -1)
if [ "$running_dir" != "temp/$task" ]; then
  pkill -f "[p]ython3 -m http.server $PORT"
  setsid nohup python3 -m http.server "$PORT" --directory "temp/$task" \
    >/tmp/dashboard_http.log 2>&1 < /dev/null &
  disown
  sleep 1
fi

if ! pgrep -f "[R] 80:localhost:$PORT serveo.net" >/dev/null; then
  setsid nohup ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
    -R 80:localhost:$PORT serveo.net \
    >/tmp/dashboard_serveo.log 2>&1 < /dev/null &
  disown
  sleep 6

  setsid nohup bash -c "sleep 86400; pkill -f '[p]ython3 -m http.server $PORT'; pkill -f '[R] 80:localhost:$PORT serveo.net'" \
    >/dev/null 2>&1 < /dev/null &
  disown
fi

base=$(grep -o 'https://[a-zA-Z0-9.-]*\.serveousercontent\.com' /tmp/dashboard_serveo.log | tail -1)

# Without this the script would happily print a bare "/design.html" and exit 0 —
# both checks below pass on localhost even when the tunnel is down.
if [ -z "$base" ]; then
  echo "ERROR: no serveo URL in /tmp/dashboard_serveo.log - the tunnel is not up. Re-run in a few seconds." >&2
  exit 1
fi

# Validate against the local server, not the public tunnel URL: serveo's
# anti-bot layer 403s plain curl requests even for valid pages, so checking
# the tunnel directly produces false warnings. localhost exercises the same
# path-resolution the tunnel will serve, without that noise.
code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$PORT/$page")
if [ "$code" != "200" ]; then
  echo "WARNING: temp/$rel served HTTP $code locally, not 200" >&2
fi

echo "$base/$page"

# Manual teardown any time:
# pkill -f "[p]ython3 -m http.server 8766"; pkill -f "[R] 80:localhost:8766 serveo.net"
