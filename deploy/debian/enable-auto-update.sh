#!/usr/bin/env bash
# Автообновление с GitHub: polling ветки main раз в ~2 минуты (systemd timer).
# Webhook опционален: --webhook
#
# sudo bash deploy/debian/enable-auto-update.sh
# sudo bash deploy/debian/enable-auto-update.sh --webhook
set -euo pipefail

WITH_TIMER=1
WITH_WEBHOOK=0
for arg in "$@"; do
  case "${arg}" in
    --timer-only) WITH_WEBHOOK=0; WITH_TIMER=1 ;;
    --webhook-only) WITH_WEBHOOK=1; WITH_TIMER=0 ;;
    --webhook) WITH_WEBHOOK=1 ;;
    --no-webhook) WITH_WEBHOOK=0 ;;
    -h|--help)
      echo "Usage: $0 [--webhook|--webhook-only|--timer-only]"
      exit 0
      ;;
  esac
done

APP_ROOT="${APP_ROOT:-/opt/stratum}"
ENV_DIR="/etc/stratum"
ENV_FILE="${ENV_DIR}/stratum.env"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash $0"
  exit 1
fi

mkdir -p "${ENV_DIR}"
if [[ ! -f "${ENV_FILE}" ]]; then
  if [[ -f "${APP_ROOT}/deploy/debian/stratum.env.example" ]]; then
    install -m 640 "${APP_ROOT}/deploy/debian/stratum.env.example" "${ENV_FILE}"
  elif [[ -f "${SCRIPT_DIR}/stratum.env.example" ]]; then
    install -m 640 "${SCRIPT_DIR}/stratum.env.example" "${ENV_FILE}"
  else
    touch "${ENV_FILE}"
    chmod 640 "${ENV_FILE}"
  fi
fi

# shellcheck source=git-auth.sh
source "${SCRIPT_DIR}/git-auth.sh"
stratum_load_git_env "${ENV_FILE}"

GIT_DIR="${STRATUM_GIT_DIR:-/opt/stratum-src}"
BRANCH="${STRATUM_GIT_BRANCH:-main}"
REPO_URL="${STRATUM_REPO_URL:-${STRATUM_DEFAULT_REPO_URL}}"
SERVER_NAME="${STRATUM_SERVER_NAME:-_}"

grep -q '^STRATUM_GIT_DIR=' "${ENV_FILE}" || echo "STRATUM_GIT_DIR=${GIT_DIR}" >>"${ENV_FILE}"
grep -q '^STRATUM_GIT_BRANCH=' "${ENV_FILE}" || echo "STRATUM_GIT_BRANCH=${BRANCH}" >>"${ENV_FILE}"
grep -q '^STRATUM_GIT_REMOTE=' "${ENV_FILE}" || echo "STRATUM_GIT_REMOTE=origin" >>"${ENV_FILE}"
grep -q '^STRATUM_AUTO_UPDATE=' "${ENV_FILE}" || echo "STRATUM_AUTO_UPDATE=1" >>"${ENV_FILE}"
if ! grep -q '^STRATUM_REPO_URL=' "${ENV_FILE}"; then
  echo "STRATUM_REPO_URL=${REPO_URL}" >>"${ENV_FILE}"
fi
# pin tracked branch to main unless already set differently
if ! grep -q '^STRATUM_GIT_BRANCH=' "${ENV_FILE}"; then
  echo "STRATUM_GIT_BRANCH=main" >>"${ENV_FILE}"
fi

if ! stratum_ensure_git_clone "${GIT_DIR}" "${BRANCH}" "${REPO_URL}" echo; then
  echo
  echo "Сначала положите токен в ${ENV_FILE}:"
  echo "  STRATUM_GITHUB_TOKEN=ghp_xxx"
  echo "  STRATUM_REPO_URL=${REPO_URL}"
  echo "Затем снова: sudo bash $0"
  exit 1
fi

HAS_TOKEN=0
if grep -qE '^(STRATUM_GITHUB_TOKEN|GITHUB_TOKEN)=.+' "${ENV_FILE}" 2>/dev/null; then
  HAS_TOKEN=1
fi
REMOTE_URL="$(git -C "${GIT_DIR}" remote get-url origin 2>/dev/null || true)"
if [[ "${HAS_TOKEN}" -eq 0 && "${REMOTE_URL}" == https://github.com/* ]]; then
  echo "WARNING: нет STRATUM_GITHUB_TOKEN в ${ENV_FILE}"
  echo "  Для private repo auto-update упадёт на git fetch."
fi

if [[ -d "${GIT_DIR}/deploy/debian" ]]; then
  rsync -a "${GIT_DIR}/deploy/debian/" "${APP_ROOT}/deploy/debian/"
fi
chmod +x "${APP_ROOT}/deploy/debian/"*.sh "${APP_ROOT}/deploy/debian/"*.py 2>/dev/null || true

if [[ "${WITH_TIMER}" -eq 1 ]]; then
  install -m 644 "${APP_ROOT}/deploy/debian/stratum-auto-update.service" /etc/systemd/system/
  install -m 644 "${APP_ROOT}/deploy/debian/stratum-auto-update.timer" /etc/systemd/system/
  systemctl daemon-reload
  systemctl enable --now stratum-auto-update.timer
  echo "Timer включён (polling origin/${BRANCH}):"
  systemctl list-timers stratum-auto-update.timer --no-pager || true
fi

if [[ "${WITH_WEBHOOK}" -eq 1 ]]; then
  if ! grep -q '^STRATUM_WEBHOOK_SECRET=' "${ENV_FILE}"; then
    SECRET="$(openssl rand -hex 24)"
    echo "STRATUM_WEBHOOK_SECRET=${SECRET}" >>"${ENV_FILE}"
    echo "Сгенерирован STRATUM_WEBHOOK_SECRET → ${ENV_FILE}"
  else
    # shellcheck disable=SC1090
    set -a && source "${ENV_FILE}" && set +a
    SECRET="${STRATUM_WEBHOOK_SECRET}"
  fi

  # nginx: HTTP + SSL (после certbot) — location /hooks/github
  if [[ -f /etc/nginx/sites-available/stratum ]]; then
    python3 "${APP_ROOT}/deploy/debian/patch-webhook-nginx.py" /etc/nginx/sites-available/stratum
    nginx -t && systemctl reload nginx
  fi

  install -m 644 "${APP_ROOT}/deploy/debian/stratum-webhook.service" /etc/systemd/system/
  systemctl daemon-reload
  systemctl enable --now stratum-webhook
  systemctl restart stratum-webhook

  sleep 1
  if curl -fsS http://127.0.0.1:9000/health >/dev/null; then
    echo "Webhook service OK (:9000)"
  else
    echo "ERROR: stratum-webhook не отвечает на :9000" >&2
    systemctl status stratum-webhook --no-pager || true
    exit 1
  fi

  HOOK_URL="http://YOUR_VPS/hooks/github"
  if [[ -n "${SERVER_NAME}" && "${SERVER_NAME}" != "_" ]]; then
    HOOK_URL="https://${SERVER_NAME}/hooks/github"
  fi

  echo
  echo "Webhook включён (push → refs/heads/${BRANCH})."
  echo "  GitHub → Settings → Webhooks → Add webhook"
  echo "  Payload URL:  ${HOOK_URL}"
  echo "  Content type: application/json"
  echo "  Secret:       STRATUM_WEBHOOK_SECRET в ${ENV_FILE}"
  echo "  Events:       Just the push event"
  echo
  echo "Проверка:"
  echo "  curl -fsS http://127.0.0.1:9000/health"
  if [[ -n "${SERVER_NAME}" && "${SERVER_NAME}" != "_" ]]; then
    echo "  curl -fsS https://${SERVER_NAME}/hooks/github/health"
  fi
fi

echo
echo "Клон:          ${GIT_DIR} @ ${BRANCH}"
echo "Статус:        sudo bash ${APP_ROOT}/deploy/debian/auto-update-status.sh"
echo "Ручной прогон: sudo bash ${APP_ROOT}/deploy/debian/auto-update.sh --force"
echo "Логи:          journalctl -u stratum-auto-update -u stratum-webhook -f"
