#!/usr/bin/env bash
# Native Debian 12+ install for STRATUM — БЕЗ Docker.
# Запуск: sudo bash deploy/debian/install.sh [/path/to/repo]
set -euo pipefail

REPO_DIR="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
APP_ROOT="/opt/stratum"
WEB_ROOT="/var/www/stratum"
ENV_DIR="/etc/stratum"
ENV_FILE="${ENV_DIR}/stratum.env"
# Разделение с Klaris — по домену (оба на :80). API localhost: 8001 рядом с Klaris.
# docs/INSTALL.md · docs/COHOST_KLARIS.md
#
# CLI / текущий shell перекрывает значения из /etc/stratum/stratum.env
REQUESTED_HTTP_PORT="${STRATUM_HTTP_PORT:-}"
REQUESTED_API_PORT="${STRATUM_API_PORT:-}"
REQUESTED_SERVER_NAME="${STRATUM_SERVER_NAME:-}"
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  set -a && source "${ENV_FILE}" && set +a || true
fi
HTTP_PORT="${REQUESTED_HTTP_PORT:-${STRATUM_HTTP_PORT:-80}}"
API_PORT="${REQUESTED_API_PORT:-${STRATUM_API_PORT:-8000}}"
SERVER_NAME="${REQUESTED_SERVER_NAME:-${STRATUM_SERVER_NAME:-_}}"
DEFAULT_SERVER=" default_server"
COHOST=0
if [[ -f /etc/nginx/sites-enabled/klaris || -d /opt/klaris ]]; then
  COHOST=1
fi
if [[ "${COHOST}" -eq 1 ]]; then
  if [[ -z "${REQUESTED_API_PORT}" && -z "${STRATUM_API_PORT:-}" ]]; then
    API_PORT=8001
  elif [[ -n "${REQUESTED_API_PORT}" ]]; then
    API_PORT="${REQUESTED_API_PORT}"
  else
    API_PORT="${STRATUM_API_PORT:-8001}"
  fi
  if [[ "${SERVER_NAME}" == "_" || -z "${SERVER_NAME}" ]]; then
    echo "ERROR: рядом с Klaris нужен домен STRATUM_SERVER_NAME" >&2
    echo "  В команде:  sudo STRATUM_SERVER_NAME=stratum.example.com bash deploy/debian/install.sh ${REPO_DIR}" >&2
    echo "  Или в файле ${ENV_FILE}:" >&2
    echo "    STRATUM_SERVER_NAME=stratum.example.com" >&2
    exit 1
  fi
  # оба vhost на :80 — без default_server у STRATUM
  DEFAULT_SERVER=""
  HTTP_PORT="${REQUESTED_HTTP_PORT:-${STRATUM_HTTP_PORT:-80}}"
  echo "==> cohost по домену: server_name=${SERVER_NAME} http=:${HTTP_PORT} api=:${API_PORT}"
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
# порты / домен в env
set_env() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "${ENV_DIR}/stratum.env"; then
    sed -i "s|^${key}=.*|${key}=${val}|" "${ENV_DIR}/stratum.env"
  else
    echo "${key}=${val}" >>"${ENV_DIR}/stratum.env"
  fi
}
set_env STRATUM_HTTP_PORT "${HTTP_PORT}"
set_env STRATUM_API_PORT "${API_PORT}"
set_env STRATUM_SERVER_NAME "${SERVER_NAME}"
chown root:stratum "${ENV_DIR}/stratum.env"

chmod +x "${APP_ROOT}/deploy/debian/"*.sh

# nginx site from template placeholders
NGINX_CONF="${APP_ROOT}/deploy/debian/nginx-stratum.conf"
# DEFAULT_SERVER may contain a leading space — escape for sed carefully via envsubst-like replace
python3 - <<PY
from pathlib import Path
src = Path("${NGINX_CONF}").read_text()
src = src.replace("__STRATUM_HTTP_PORT__", "${HTTP_PORT}")
src = src.replace("__STRATUM_API_PORT__", "${API_PORT}")
src = src.replace("__STRATUM_SERVER_NAME__", "${SERVER_NAME}")
src = src.replace("__STRATUM_DEFAULT_SERVER__", """${DEFAULT_SERVER}""")
Path("/tmp/stratum-nginx.conf").write_text(src)
PY
install -m 644 /tmp/stratum-nginx.conf /etc/nginx/sites-available/stratum
ln -sfn /etc/nginx/sites-available/stratum /etc/nginx/sites-enabled/stratum
# не трогаем sites-enabled/klaris
rm -f /etc/nginx/sites-enabled/default


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
HOST_URL="http://${SERVER_NAME}"
if [[ "${SERVER_NAME}" == "_" ]]; then
  HOST_URL="http://${IP:-127.0.0.1}"
  if [[ "${HTTP_PORT}" != "80" ]]; then
    HOST_URL="${HOST_URL}:${HTTP_PORT}"
  fi
fi
echo
echo "STRATUM (native, без Docker) установлен."
echo "  UI:     ${HOST_URL}/"
echo "  health: ${HOST_URL}/api/health"
echo "  server_name: ${SERVER_NAME}"
echo "  api localhost: ${API_PORT}"
echo "  Код: ${APP_ROOT}"
echo "  Env: ${ENV_DIR}/stratum.env"
if [[ "${COHOST}" -eq 1 ]]; then
  echo "  DNS: A/AAAA ${SERVER_NAME} → ${IP:-VPS_IP}"
fi
if [[ "${HAS_SYSTEMD}" -eq 1 ]]; then
  echo "  status: systemctl status stratum-api nginx"
  echo "  auto:   sudo bash ${APP_ROOT}/deploy/debian/enable-auto-update.sh"
  echo "          sudo bash ${APP_ROOT}/deploy/debian/enable-auto-update.sh --webhook"
else
  echo "  start:  sudo bash ${APP_ROOT}/deploy/debian/run-native.sh"
fi


