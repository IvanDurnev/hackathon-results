#!/bin/sh
set -eu

if [ "${APP_ENV:-production}" = "production" ] && [ -z "${SECRET_KEY:-}" ]; then
  echo "SECRET_KEY is required when APP_ENV=production." >&2
  echo "Create it in Amvera as a secret or environment variable." >&2
  exit 1
fi

mkdir -p "${DATA_DIR:-/data}/uploads"

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
