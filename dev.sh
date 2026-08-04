#!/usr/bin/env bash
# Starts the backend API and frontend dev server together, for local development.
# Ctrl+C stops both.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=5173

if [ ! -f "$ROOT_DIR/backend/.env" ]; then
  echo "backend/.env not found. Run: cp backend/.env.example backend/.env" >&2
  exit 1
fi

if [ ! -d "$ROOT_DIR/backend/.venv" ]; then
  echo "backend/.venv not found. See README.md Setup section." >&2
  exit 1
fi

if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  echo "frontend/node_modules not found. Run: (cd frontend && npm install)" >&2
  exit 1
fi

kill_port() {
  # -9: a suspended (Ctrl+Z'd) process ignores SIGTERM until resumed, so a plain
  # kill can leave the port held. This is cleanup of orphans, not a graceful stop.
  # The `|| true` matters: under `set -e -o pipefail`, lsof's "no match" exit (1)
  # would otherwise take the whole script down on the (common) empty-port case.
  lsof -ti:"$1" -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 || true
}

# Clear any orphaned processes from a previous run that Ctrl+C didn't fully stop
# (npm doesn't reliably forward SIGTERM to the Vite process it spawns).
kill_port "$BACKEND_PORT"
kill_port "$FRONTEND_PORT"

cleanup() {
  echo
  echo "Stopping..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  # Belt and braces: npm/vite's child process can survive the signal above.
  kill_port "$BACKEND_PORT"
  kill_port "$FRONTEND_PORT"
}
trap cleanup EXIT INT TERM

(cd "$ROOT_DIR/backend" && .venv/bin/uvicorn app.main:app --reload --port "$BACKEND_PORT") &
BACKEND_PID=$!

(cd "$ROOT_DIR/frontend" && npm run dev -- --port "$FRONTEND_PORT" --strictPort) &
FRONTEND_PID=$!

echo "Backend:  http://localhost:$BACKEND_PORT"
echo "Frontend: http://localhost:$FRONTEND_PORT"
wait
