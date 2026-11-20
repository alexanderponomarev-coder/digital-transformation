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

if command -v systemctl >/dev/null 2>&1 && systemctl list-units >/dev/null 2>&1; then
  systemctl restart stratum-api
  nginx -t && systemctl reload nginx
fi

echo "Обновление завершено."
curl -fsS http://127.0.0.1/api/health || curl -fsS http://127.0.0.1:8080/api/health || true
echo
