#!/usr/bin/env bash
# Запуск native-стека без systemd (VPS/контейнер без init, локальный smoke).
# Предполагается: sudo bash deploy/debian/install.sh уже выполнен.
# sudo bash deploy/debian/run-native.sh [http_port]
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/stratum}"
WEB_ROOT="${WEB_ROOT:-/var/www/stratum}"
HTTP_PORT="${1:-${STRATUM_HTTP_PORT:-8080}}"
API_PORT=8000
ENV_FILE="${ENV_FILE:-/etc/stratum/stratum.env}"
API_LOG="/var/log/stratum-api.log"
API_PID_FILE="/var/run/stratum-api.pid"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash $0"
  exit 1
fi

if [[ ! -x "${APP_ROOT}/.venv/bin/uvicorn" ]]; then
  echo "Нет ${APP_ROOT}/.venv — сначала: sudo bash deploy/debian/install.sh"
  exit 1
fi
if [[ ! -f "${WEB_ROOT}/index.html" ]]; then
  echo "Нет сборки в ${WEB_ROOT} — сначала: sudo bash deploy/debian/install.sh"
  exit 1
fi

# shellcheck disable=SC1090
[[ -f "${ENV_FILE}" ]] && set -a && source "${ENV_FILE}" && set +a

stop_api() {
  if [[ -f "${API_PID_FILE}" ]]; then
    kill "$(cat "${API_PID_FILE}")" 2>/dev/null || true
    rm -f "${API_PID_FILE}"
  fi
  pkill -f "${APP_ROOT}/.venv/bin/uvicorn app.main:app" 2>/dev/null || true
}

port_busy() {
  local port="$1"
  ss -ltn "sport = :${port}" 2>/dev/null | grep -q LISTEN
}

stop_api
if port_busy "${API_PORT}"; then
  echo "Порт ${API_PORT} занят — освободите его (docker/старый uvicorn) и повторите."
  ss -ltnp | grep ":${API_PORT}" || true
  exit 1
fi

echo "API → 127.0.0.1:${API_PORT}"
cd "${APP_ROOT}/backend"
nohup "${APP_ROOT}/.venv/bin/uvicorn" app.main:app \
  --host 127.0.0.1 --port "${API_PORT}" --workers 2 \
  >"${API_LOG}" 2>&1 &
echo $! >"${API_PID_FILE}"

for i in $(seq 1 40); do
  if curl -fsS "http://127.0.0.1:${API_PORT}/api/health" >/dev/null 2>&1; then
    echo "API healthy"
    break
  fi
  if [[ "${i}" -eq 40 ]]; then
    echo "API не поднялся. Лог:"
    tail -50 "${API_LOG}" || true
    exit 1
  fi
  sleep 0.25
done

# nginx site на нужный порт
TMP_CONF="/etc/nginx/sites-available/stratum"
sed "s/listen 80 default_server/listen ${HTTP_PORT} default_server/g; s/listen \[::\]:80 default_server/listen [::]:${HTTP_PORT} default_server/g" \
  "${APP_ROOT}/deploy/debian/nginx-stratum.conf" > "${TMP_CONF}"
ln -sfn "${TMP_CONF}" /etc/nginx/sites-enabled/stratum
rm -f /etc/nginx/sites-enabled/default

nginx -t

if pgrep -x nginx >/dev/null 2>&1; then
  # если nginx запущен нештатно (пустой pid) — полный рестарт
  if [[ ! -s /run/nginx.pid ]]; then
    pkill -x nginx 2>/dev/null || true
    sleep 0.5
    nginx
  else
    nginx -s reload
  fi
else
  nginx
fi

if port_busy "${HTTP_PORT}"; then
  :
else
  echo "nginx не слушает :${HTTP_PORT}"
  exit 1
fi

echo "Прокси: http://127.0.0.1:${HTTP_PORT}/"
curl -fsS "http://127.0.0.1:${HTTP_PORT}/api/health"
echo
curl -fsS -o /dev/null -w "ui:%{http_code}\n" "http://127.0.0.1:${HTTP_PORT}/"
echo "OK. Логи API: ${API_LOG}"
echo "Стоп API: kill \$(cat ${API_PID_FILE})"
