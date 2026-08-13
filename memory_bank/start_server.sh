#!/bin/bash
# Keep memory_bank/server.py running persistently via nohup + a PID file.
# This login node has no systemd --user session, so nohup (with logout's
# KillUserProcesses left at its default "no") is the lightweight fit —
# sbatch would impose a --time limit, wrong for an always-on service.
#
# Usage:
#   bash memory_bank/start_server.sh          # start (no-op if already running)
#   bash memory_bank/start_server.sh stop
#   bash memory_bank/start_server.sh status

MAIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$MAIN_DIR/memory_bank/.server.pid"
LOG_FILE="$MAIN_DIR/memory_bank/server.log"

is_running() {
    [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

case "$1" in
    stop)
        if is_running; then
            kill "$(cat "$PID_FILE")" && echo "stopped ($(cat "$PID_FILE"))"
            rm -f "$PID_FILE"
        else
            echo "not running"
        fi
        ;;
    status)
        if is_running; then
            echo "running (PID $(cat "$PID_FILE"))"
        else
            echo "not running"
        fi
        ;;
    *)
        if is_running; then
            echo "already running (PID $(cat "$PID_FILE"))"
            exit 0
        fi
        cd "$MAIN_DIR" || exit 1
        nohup python3 memory_bank/server.py > "$LOG_FILE" 2>&1 &
        disown
        echo $! > "$PID_FILE"
        sleep 1
        if is_running; then
            echo "started (PID $(cat "$PID_FILE")), log: $LOG_FILE"
        else
            echo "failed to start, check $LOG_FILE"
            exit 1
        fi
        ;;
esac
