#!/usr/bin/env bash
# Native Debian 12+ install for STRATUM — БЕЗ Docker.
# Запуск: sudo bash deploy/debian/install.sh [/path/to/repo]
set -euo pipefail

REPO_DIR="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
APP_ROOT="/opt/stratum"
WEB_ROOT="/var/www/stratum"
ENV_DIR="/etc/stratum"
# Cohost with Klaris (2fromlarec): HTTP 8080, API 8001 — docs/COHOST_KLARIS.md
HTTP_PORT="${STRATUM_HTTP_PORT:-80}"
API_PORT="${STRATUM_API_PORT:-8000}"
if [[ -f /etc/nginx/sites-enabled/klaris || -d /opt/klaris ]]; then
  # auto-shift off Klaris ports when co-hosting on the same node
  if [[ "${HTTP_PORT}" == "80" && -z "${STRATUM_HTTP_PORT:-}" ]]; then
    HTTP_PORT=8080
  fi
  if [[ "${API_PORT}" == "8000" && -z "${STRATUM_API_PORT:-}" ]]; then
    API_PORT=8001
  fi
  echo "==> обнаружен Klaris — STRATUM на :${HTTP_PORT} / API :${API_PORT}"
fi

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash $0"
  exit 1
fi

if [[ ! -d "${REPO_DIR}/backend" || ! -d "${REPO_DIR}/frontend" ]]; then
  echo "Не найден backend/frontend в ${REPO_DIR}"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
  python3 python3-venv python3-pip \
  nginx curl ca-certificates rsync \
  nodejs npm

NODE_MAJOR="$(node -v 2>/dev/null | sed 's/v//' | cut -d. -f1 || echo 0)"
if [[ "${NODE_MAJOR}" -lt 20 ]]; then
  echo "Node ${NODE_MAJOR} слишком старый — ставим NodeSource 22.x"
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  apt-get install -y -qq nodejs
fi

id -u stratum >/dev/null 2>&1 || useradd --system --home "${APP_ROOT}" --shell /usr/sbin/nologin stratum
mkdir -p "${APP_ROOT}" "${WEB_ROOT}" "${ENV_DIR}"

echo "== sync code → ${APP_ROOT} =="
rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'frontend/node_modules' \
  --exclude 'frontend/dist' \
  --exclude '.env' \
  "${REPO_DIR}/" "${APP_ROOT}/"

echo "== Python venv + deps =="
python3 -m venv "${APP_ROOT}/.venv"
"${APP_ROOT}/.venv/bin/pip" install --upgrade pip
"${APP_ROOT}/.venv/bin/pip" install -r "${APP_ROOT}/backend/requirements.txt"

echo "== frontend build =="
cd "${APP_ROOT}/frontend"
npm ci
npm run build
rsync -a --delete "${APP_ROOT}/frontend/dist/" "${WEB_ROOT}/"
chown -R www-data:www-data "${WEB_ROOT}"

if [[ ! -f "${ENV_DIR}/stratum.env" ]]; then
  install -m 640 "${APP_ROOT}/deploy/debian/stratum.env.example" "${ENV_DIR}/stratum.env"
fi
# запоминаем git-клон для автообновления
if [[ -d "${REPO_DIR}/.git" ]]; then
  if ! grep -q '^STRATUM_GIT_DIR=' "${ENV_DIR}/stratum.env"; then
    echo "STRATUM_GIT_DIR=${REPO_DIR}" >>"${ENV_DIR}/stratum.env"
  else
    sed -i "s|^STRATUM_GIT_DIR=.*|STRATUM_GIT_DIR=${REPO_DIR}|" "${ENV_DIR}/stratum.env"
  fi
  grep -q '^STRATUM_GIT_BRANCH=' "${ENV_DIR}/stratum.env" || echo "STRATUM_GIT_BRANCH=main" >>"${ENV_DIR}/stratum.env"
  grep -q '^STRATUM_GIT_REMOTE=' "${ENV_DIR}/stratum.env" || echo "STRATUM_GIT_REMOTE=origin" >>"${ENV_DIR}/stratum.env"
fi
# порты в env
grep -q '^STRATUM_HTTP_PORT=' "${ENV_DIR}/stratum.env" \
  && sed -i "s|^STRATUM_HTTP_PORT=.*|STRATUM_HTTP_PORT=${HTTP_PORT}|" "${ENV_DIR}/stratum.env" \
  || echo "STRATUM_HTTP_PORT=${HTTP_PORT}" >>"${ENV_DIR}/stratum.env"
grep -q '^STRATUM_API_PORT=' "${ENV_DIR}/stratum.env" \
  && sed -i "s|^STRATUM_API_PORT=.*|STRATUM_API_PORT=${API_PORT}|" "${ENV_DIR}/stratum.env" \
  || echo "STRATUM_API_PORT=${API_PORT}" >>"${ENV_DIR}/stratum.env"
chown root:stratum "${ENV_DIR}/stratum.env"

chmod +x "${APP_ROOT}/deploy/debian/"*.sh

# nginx site from template placeholders
NGINX_CONF="${APP_ROOT}/deploy/debian/nginx-stratum.conf"
sed \
  -e "s/__STRATUM_HTTP_PORT__/${HTTP_PORT}/g" \
  -e "s/__STRATUM_API_PORT__/${API_PORT}/g" \
  "${NGINX_CONF}" > /tmp/stratum-nginx.conf
# если Klaris уже default на :80 — убрать default_server у STRATUM на 8080 не обязательно
install -m 644 /tmp/stratum-nginx.conf /etc/nginx/sites-available/stratum
ln -sfn /etc/nginx/sites-available/stratum /etc/nginx/sites-enabled/stratum
# не трогаем sites-enabled/klaris; default убираем только если нет klaris
if [[ ! -e /etc/nginx/sites-enabled/klaris ]]; then
  rm -f /etc/nginx/sites-enabled/default
fi

chown -R stratum:stratum "${APP_ROOT}"

HAS_SYSTEMD=0
if command -v systemctl >/dev/null 2>&1 && systemctl list-units >/dev/null 2>&1; then
  HAS_SYSTEMD=1
fi

if [[ "${HAS_SYSTEMD}" -eq 1 ]]; then
  echo "== systemd + nginx =="
  install -m 644 "${APP_ROOT}/deploy/debian/stratum-api.service" /etc/systemd/system/stratum-api.service
  systemctl daemon-reload
  systemctl enable --now stratum-api
  nginx -t
  systemctl enable nginx
  systemctl reload nginx || systemctl restart nginx

  if [[ "${STRATUM_AUTO_UPDATE:-0}" == "1" && -d "${REPO_DIR}/.git" ]]; then
    echo "== автообновление с GitHub =="
    bash "${APP_ROOT}/deploy/debian/enable-auto-update.sh" || true
  fi
else
  echo "== systemd недоступен: API поднимается через helper (foreground/tmux) =="
  echo "   Используйте: sudo bash ${APP_ROOT}/deploy/debian/run-native.sh"
fi

IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo
echo "STRATUM (native, без Docker) установлен."
echo "  UI:  http://${IP:-127.0.0.1}:${HTTP_PORT}/"
echo "  API: http://${IP:-127.0.0.1}:${HTTP_PORT}/api/health"
echo "  Код: ${APP_ROOT}"
echo "  Env: ${ENV_DIR}/stratum.env"
if [[ "${HAS_SYSTEMD}" -eq 1 ]]; then
  echo "  status: systemctl status stratum-api nginx"
  echo "  auto:   sudo bash ${APP_ROOT}/deploy/debian/enable-auto-update.sh"
  echo "          sudo bash ${APP_ROOT}/deploy/debian/enable-auto-update.sh --webhook"
else
  echo "  start:  sudo bash ${APP_ROOT}/deploy/debian/run-native.sh"
fi

