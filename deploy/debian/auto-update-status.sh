#!/usr/bin/env bash
# Диагностика auto-update (timer + webhook на push в main).
# sudo bash /opt/stratum/deploy/debian/auto-update-status.sh
set -euo pipefail

ENV_FILE="${ENV_FILE:-/etc/stratum/stratum.env}"
GIT_DIR="${STRATUM_GIT_DIR:-/opt/stratum-src}"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  set -a && source "${ENV_FILE}" && set +a
fi
GIT_DIR="${STRATUM_GIT_DIR:-$GIT_DIR}"
BRANCH="${STRATUM_GIT_BRANCH:-main}"
SERVER_NAME="${STRATUM_SERVER_NAME:-_}"

echo "== env =="
echo "STRATUM_GIT_DIR=${GIT_DIR}"
echo "STRATUM_GIT_BRANCH=${BRANCH}"
echo "STRATUM_SERVER_NAME=${SERVER_NAME}"
echo "STRATUM_AUTO_UPDATE=${STRATUM_AUTO_UPDATE:-unset}"
echo "STRATUM_GITHUB_TOKEN=$([ -n "${STRATUM_GITHUB_TOKEN:-}" ] && echo set || echo missing)"
echo "STRATUM_WEBHOOK_SECRET=$([ -n "${STRATUM_WEBHOOK_SECRET:-}" ] && echo set || echo missing)"

echo
echo "== git =="
if [[ -d "${GIT_DIR}/.git" ]]; then
  git -C "${GIT_DIR}" remote -v | head -4
  echo "HEAD: $(git -C "${GIT_DIR}" rev-parse --short HEAD 2>/dev/null || echo '?') ($(git -C "${GIT_DIR}" branch --show-current 2>/dev/null || true))"
  git -C "${GIT_DIR}" rev-parse "origin/${BRANCH}" >/dev/null 2>&1 \
    && echo "origin/${BRANCH}: $(git -C "${GIT_DIR}" rev-parse --short "origin/${BRANCH}")" \
    || echo "origin/${BRANCH}: (нет локальной ссылки — сделайте fetch)"
else
  echo "нет клона ${GIT_DIR}"
fi

echo
echo "== systemd =="
systemctl is-enabled stratum-auto-update.timer 2>/dev/null || echo "timer: not enabled"
systemctl list-timers stratum-auto-update.timer --no-pager 2>/dev/null || true
systemctl is-active stratum-webhook 2>/dev/null || echo "webhook: inactive"
systemctl is-enabled stratum-webhook 2>/dev/null || echo "webhook: not enabled"

echo
echo "== ports / health =="
ss -lntp 2>/dev/null | grep -E ':9000|:8000|:8001 ' || true
curl -fsS http://127.0.0.1:9000/health 2>/dev/null && echo || echo "webhook :9000 FAIL (502 снаружи = сервис не запущен)"
if [[ -n "${SERVER_NAME}" && "${SERVER_NAME}" != "_" ]]; then
  curl -fsS -H "Host: ${SERVER_NAME}" http://127.0.0.1/hooks/github/health 2>/dev/null && echo \
    || echo "nginx→webhook HTTP FAIL"
  curl -fsSk "https://${SERVER_NAME}/hooks/github/health" 2>/dev/null && echo \
    || echo "nginx→webhook HTTPS FAIL (нужен cert + location /hooks/github)"
fi

echo
echo "== last logs =="
journalctl -u stratum-auto-update -n 8 --no-pager 2>/dev/null || true
journalctl -u stratum-webhook -n 8 --no-pager 2>/dev/null || true

echo
echo "Включить всё: sudo bash /opt/stratum/deploy/debian/enable-auto-update.sh"
echo "GitHub webhook URL: https://${SERVER_NAME}/hooks/github  (Events: push, branch ${BRANCH})"
