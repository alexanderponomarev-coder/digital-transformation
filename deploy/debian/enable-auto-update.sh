#!/usr/bin/env bash
# Включает автообновление с GitHub: timer и/или webhook.
# sudo bash deploy/debian/enable-auto-update.sh [--webhook]
set -euo pipefail

WITH_WEBHOOK=0
[[ "${1:-}" == "--webhook" ]] && WITH_WEBHOOK=1

APP_ROOT="${APP_ROOT:-/opt/stratum}"
ENV_DIR="/etc/stratum"
ENV_FILE="${ENV_DIR}/stratum.env"
GIT_DIR="${STRATUM_GIT_DIR:-/opt/stratum-src}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash $0 [--webhook]"
  exit 1
fi

if [[ ! -d "${GIT_DIR}/.git" ]]; then
  echo "Нет ${GIT_DIR}/.git"
  echo "Склонируйте репозиторий:"
  echo "  git clone <url> ${GIT_DIR}"
  echo "и пропишите STRATUM_GIT_DIR в ${ENV_FILE}"
  exit 1
fi

mkdir -p "${ENV_DIR}"
if [[ ! -f "${ENV_FILE}" ]]; then
  install -m 640 "${APP_ROOT}/deploy/debian/stratum.env.example" "${ENV_FILE}"
fi

# гарантируем ключи в env
grep -q '^STRATUM_GIT_DIR=' "${ENV_FILE}" || echo "STRATUM_GIT_DIR=${GIT_DIR}" >>"${ENV_FILE}"
grep -q '^STRATUM_GIT_BRANCH=' "${ENV_FILE}" || echo "STRATUM_GIT_BRANCH=main" >>"${ENV_FILE}"
grep -q '^STRATUM_GIT_REMOTE=' "${ENV_FILE}" || echo "STRATUM_GIT_REMOTE=origin" >>"${ENV_FILE}"
grep -q '^STRATUM_AUTO_UPDATE=' "${ENV_FILE}" || echo "STRATUM_AUTO_UPDATE=1" >>"${ENV_FILE}"

# Private GitHub: токен в env (не в remote URL)
HAS_TOKEN=0
if grep -qE '^(STRATUM_GITHUB_TOKEN|GITHUB_TOKEN)=.+' "${ENV_FILE}" 2>/dev/null; then
  HAS_TOKEN=1
fi
REMOTE_URL="$(git -C "${GIT_DIR}" remote get-url origin 2>/dev/null || true)"
if [[ "${HAS_TOKEN}" -eq 0 && "${REMOTE_URL}" == https://github.com/* ]]; then
  echo "WARNING: нет STRATUM_GITHUB_TOKEN в ${ENV_FILE}"
  echo "  Для private repo auto-update упадёт на git fetch."
  echo "  Добавьте:  STRATUM_GITHUB_TOKEN=ghp_xxx   (Contents: Read)"
  echo "  Документация: docs/INSTALL.md §3"
fi

# синхронизируем скрипты в APP_ROOT на случай, если enable вызвали из src
if [[ -d "${GIT_DIR}/deploy/debian" ]]; then
  rsync -a "${GIT_DIR}/deploy/debian/" "${APP_ROOT}/deploy/debian/"
fi
chmod +x "${APP_ROOT}/deploy/debian/"*.sh
chmod +x "${APP_ROOT}/deploy/debian/webhook-server.py"

install -m 644 "${APP_ROOT}/deploy/debian/stratum-auto-update.service" /etc/systemd/system/
install -m 644 "${APP_ROOT}/deploy/debian/stratum-auto-update.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now stratum-auto-update.timer

echo "Timer включён:"
systemctl list-timers stratum-auto-update.timer --no-pager || true

if [[ "${WITH_WEBHOOK}" -eq 1 ]]; then
  if ! grep -q '^STRATUM_WEBHOOK_SECRET=' "${ENV_FILE}"; then
    SECRET="$(openssl rand -hex 24)"
    echo "STRATUM_WEBHOOK_SECRET=${SECRET}" >>"${ENV_FILE}"
    echo "Сгенерирован STRATUM_WEBHOOK_SECRET (сохранён в ${ENV_FILE})"
  else
    # shellcheck disable=SC1090
    source "${ENV_FILE}"
    SECRET="${STRATUM_WEBHOOK_SECRET}"
  fi

  install -m 644 "${APP_ROOT}/deploy/debian/stratum-webhook.service" /etc/systemd/system/
  # nginx snippet for webhook
  if [[ -f /etc/nginx/sites-available/stratum ]]; then
    if ! grep -q 'location /hooks/github' /etc/nginx/sites-available/stratum; then
      python3 - <<'PY'
from pathlib import Path
path = Path("/etc/nginx/sites-available/stratum")
text = path.read_text()
snippet = """
    location /hooks/github {
        proxy_pass http://127.0.0.1:9000/hooks/github;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Hub-Signature-256 $http_x_hub_signature_256;
        proxy_set_header X-GitHub-Event $http_x_github_event;
        proxy_read_timeout 10s;
    }
"""
    if "location /api/" in text and snippet.strip() not in text:
        text = text.replace("location /api/", snippet + "\n    location /api/", 1)
        path.write_text(text)
PY
      nginx -t && systemctl reload nginx
    fi
  fi

  systemctl daemon-reload
  systemctl enable --now stratum-webhook
  IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
  echo
  echo "Webhook включён."
  echo "  URL:    http://${IP:-YOUR_VPS}/hooks/github"
  echo "  Secret: см. STRATUM_WEBHOOK_SECRET в ${ENV_FILE}"
  echo "В GitHub → Settings → Webhooks:"
  echo "  Content type: application/json"
  echo "  Secret: <из stratum.env>"
  echo "  Events: Just the push event"
fi

echo
echo "Ручной прогон: sudo bash ${APP_ROOT}/deploy/debian/auto-update.sh --force"
echo "Логи timer:    journalctl -u stratum-auto-update -f"
echo "Private repo:  STRATUM_GITHUB_TOKEN в ${ENV_FILE} (см. docs/INSTALL.md §3)"
