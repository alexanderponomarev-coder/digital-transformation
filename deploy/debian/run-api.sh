#!/usr/bin/env bash
# Wrapper so systemd/EnvironmentFile can set STRATUM_API_PORT.
set -euo pipefail
APP_ROOT="${APP_ROOT:-/opt/stratum}"
ENV_FILE="${ENV_FILE:-/etc/stratum/stratum.env}"
# shellcheck disable=SC1090
[[ -f "${ENV_FILE}" ]] && set -a && source "${ENV_FILE}" && set +a
API_PORT="${STRATUM_API_PORT:-8000}"
cd "${APP_ROOT}/backend"
exec "${APP_ROOT}/.venv/bin/uvicorn" app.main:app \
  --host 127.0.0.1 --port "${API_PORT}" --workers 2
