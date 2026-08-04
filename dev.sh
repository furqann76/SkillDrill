#!/usr/bin/env bash
# Starts the backend API and frontend dev server together, for local development.
# Ctrl+C stops both.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

cleanup() {
  echo
  echo "Stopping..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(cd "$ROOT_DIR/backend" && .venv/bin/uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!

(cd "$ROOT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
wait
