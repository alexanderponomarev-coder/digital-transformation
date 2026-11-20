#!/usr/bin/env bash
# Обновление native-установки без пересоздания пользователя/nginx site.
# sudo bash deploy/debian/update.sh [/path/to/new/repo]
set -euo pipefail

REPO_DIR="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
APP_ROOT="/opt/stratum"
WEB_ROOT="/var/www/stratum"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash $0"
  exit 1
fi

rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'frontend/node_modules' \
  --exclude 'frontend/dist' \
  --exclude '.env' \
  "${REPO_DIR}/" "${APP_ROOT}/"

"${APP_ROOT}/.venv/bin/pip" install -r "${APP_ROOT}/backend/requirements.txt"

cd "${APP_ROOT}/frontend"
npm ci
npm run build
rsync -a --delete "${APP_ROOT}/frontend/dist/" "${WEB_ROOT}/"
chown -R www-data:www-data "${WEB_ROOT}"
chown -R stratum:stratum "${APP_ROOT}"

ENV_FILE="/etc/stratum/stratum.env"
# shellcheck disable=SC1090
[[ -f "${ENV_FILE}" ]] && set -a && source "${ENV_FILE}" && set +a || true
HTTP_PORT="${STRATUM_HTTP_PORT:-80}"
API_PORT="${STRATUM_API_PORT:-8000}"
SERVER_NAME="${STRATUM_SERVER_NAME:-_}"
DEFAULT_SERVER=" default_server"
if [[ -f /etc/nginx/sites-enabled/klaris || -d /opt/klaris ]]; then
  DEFAULT_SERVER=""
  API_PORT="${STRATUM_API_PORT:-8001}"
fi

if [[ -f "${APP_ROOT}/deploy/debian/nginx-stratum.conf" ]]; then
  python3 - <<PY
from pathlib import Path
src = Path("${APP_ROOT}/deploy/debian/nginx-stratum.conf").read_text()
src = src.replace("__STRATUM_HTTP_PORT__", "${HTTP_PORT}")
src = src.replace("__STRATUM_API_PORT__", "${API_PORT}")
src = src.replace("__STRATUM_SERVER_NAME__", "${SERVER_NAME}")
src = src.replace("__STRATUM_DEFAULT_SERVER__", """${DEFAULT_SERVER}""")
Path("/etc/nginx/sites-available/stratum").write_text(src)
PY
  ln -sfn /etc/nginx/sites-available/stratum /etc/nginx/sites-enabled/stratum
fi

if command -v systemctl >/dev/null 2>&1 && systemctl list-units >/dev/null 2>&1; then
  systemctl restart stratum-api
  nginx -t && systemctl reload nginx
fi

echo "Обновление завершено."
HOST_HDR=()
if [[ -n "${SERVER_NAME}" && "${SERVER_NAME}" != "_" ]]; then
  HOST_HDR=(-H "Host: ${SERVER_NAME}")
fi
curl -fsS "${HOST_HDR[@]}" "http://127.0.0.1:${HTTP_PORT}/api/health" \
  || curl -fsS "http://127.0.0.1:${API_PORT}/api/health" || true
echo
