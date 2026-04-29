#!/bin/sh
set -eu

if [ "${APP_ENV:-production}" = "production" ] && [ -z "${SECRET_KEY:-}" ]; then
  echo "SECRET_KEY is required when APP_ENV=production." >&2
  echo "Create it in Amvera as a secret or environment variable." >&2
  exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
  DB_HOST="${POSTGRES_HOST:-${PGHOST:-}}"
  DB_PORT="${POSTGRES_PORT:-${PGPORT:-5432}}"
  DB_NAME="${POSTGRES_DB:-${PGDATABASE:-}}"
  DB_USER="${POSTGRES_USER:-${PGUSER:-}}"
  DB_PASSWORD="${POSTGRES_PASSWORD:-${PGPASSWORD:-}}"
  if [ -n "${DB_HOST}" ] && [ -n "${DB_NAME}" ] && [ -n "${DB_USER}" ] && [ -n "${DB_PASSWORD}" ]; then
    export DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
  fi
fi

if [ "${DISABLE_SQLITE:-0}" = "1" ] && [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is required because SQLite is disabled." >&2
  echo "Set DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname in Amvera." >&2
  exit 1
fi

mkdir -p "${DATA_DIR:-/data}/uploads"

if [ "${AI_MODULE_ENABLED:-0}" = "1" ]; then
  export AI_MODULE_HOST="${AI_MODULE_HOST:-127.0.0.1}"
  export AI_MODULE_PORT="${AI_MODULE_PORT:-8091}"
  export AI_MODULE_URL="${AI_MODULE_URL:-http://127.0.0.1:${AI_MODULE_PORT}/api/ai}"
  export STT_PROVIDER="${STT_PROVIDER:-cloudflare}"
  export STT_MODEL="${STT_MODEL:-@cf/openai/whisper-large-v3-turbo}"
  export STT_LANGUAGE="${STT_LANGUAGE:-ru}"

  echo "Starting AImodule on ${AI_MODULE_HOST}:${AI_MODULE_PORT}..."
  gunicorn --chdir /app/AImodule --bind "${AI_MODULE_HOST}:${AI_MODULE_PORT}" server:app &
  AI_MODULE_PID="$!"
  trap 'kill "${AI_MODULE_PID}" 2>/dev/null || true' INT TERM EXIT
fi

cd /app/backend

flask --app wsgi db upgrade
flask --app wsgi ensure-roles

if [ -n "${ADMIN_EMAIL:-}" ] && [ -n "${ADMIN_PASSWORD:-}" ]; then
  flask --app wsgi ensure-admin \
    --email "${ADMIN_EMAIL}" \
    --username "${ADMIN_USERNAME:-admin}" \
    --password "${ADMIN_PASSWORD}"
fi

exec "$@"
