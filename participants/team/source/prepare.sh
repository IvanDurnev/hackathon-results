#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 > /dev/null 2>&1; then
    exec python3 "$ROOT/prepare_platform.py" "$@"
fi

exec python "$ROOT/prepare_platform.py" "$@"
