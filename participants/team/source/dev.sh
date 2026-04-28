#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if [[ ! -d "$BACKEND_DIR" ]]; then
  echo "Backend folder not found: $BACKEND_DIR" >&2
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR" ]]; then
  echo "Frontend folder not found: $FRONTEND_DIR" >&2
  exit 1
fi

PYTHON_BIN=""
for candidate in \
  "$ROOT_DIR/.venv/bin/python" \
  "$BACKEND_DIR/.venv/bin/python" \
  "$ROOT_DIR/.venv/Scripts/python.exe" \
  "$BACKEND_DIR/.venv/Scripts/python.exe"
do
  if [[ -n "$candidate" && -x "$candidate" ]]; then
    PYTHON_BIN="$candidate"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -f "$BACKEND_DIR/.venv/Scripts/python.exe" || -f "$ROOT_DIR/.venv/Scripts/python.exe" ]]; then
    echo "Windows virtualenv detected. Recreate the project venv on Linux:" >&2
    echo "  ./prepare.sh --force-venv" >&2
  else
    echo "Python virtualenv not found. Prepare the project on Linux first." >&2
    echo "  ./prepare.sh" >&2
  fi
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node.js before running this script." >&2
  exit 1
fi

echo "Applying database migrations..."
(
  cd "$BACKEND_DIR"
  "$PYTHON_BIN" -m flask --app wsgi db upgrade
)

echo "Starting backend and frontend..."

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM
  kill "$backend_pid" "$frontend_pid" 2>/dev/null || true
  wait "$backend_pid" "$frontend_pid" 2>/dev/null || true
  exit "$exit_code"
}

trap cleanup EXIT INT TERM

(
  cd "$BACKEND_DIR"
  exec "$PYTHON_BIN" -m flask --app wsgi run --debug
) &
backend_pid=$!

(
  cd "$FRONTEND_DIR"
  exec npm run dev
) &
frontend_pid=$!

wait -n "$backend_pid" "$frontend_pid"
exit_code=$?
echo "One of the services stopped. Shutting down the other process..."
kill "$backend_pid" "$frontend_pid" 2>/dev/null || true
wait "$backend_pid" "$frontend_pid" 2>/dev/null || true
exit "$exit_code"
