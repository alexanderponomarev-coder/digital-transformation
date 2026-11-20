#!/usr/bin/env bash
# Автообновление STRATUM с GitHub: git fetch/pull → update.sh при новых коммитах.
# sudo bash deploy/debian/auto-update.sh [--force]
set -euo pipefail

FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

ENV_FILE="${ENV_FILE:-/etc/stratum/stratum.env}"
APP_ROOT="${APP_ROOT:-/opt/stratum}"
LOG_TAG="stratum-auto-update"
# /var/lock → /run/lock; на некоторых хостах symlink битый — создаём /run/lock
if [[ -d /run/lock ]] || mkdir -p /run/lock 2>/dev/null; then
  LOCK_DIR="${LOCK_DIR:-/run/lock}"
else
  LOCK_DIR="${LOCK_DIR:-/tmp}"
fi
LOCK_FILE="${LOCK_FILE:-${LOCK_DIR}/stratum-auto-update.lock}"

log() { logger -t "${LOG_TAG}" -- "$*" 2>/dev/null || true; echo "[$(date -Is)] $*"; }

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash $0"
  exit 1
fi

# shellcheck disable=SC1090
[[ -f "${ENV_FILE}" ]] && set -a && source "${ENV_FILE}" && set +a

GIT_DIR="${STRATUM_GIT_DIR:-/opt/stratum-src}"
REMOTE="${STRATUM_GIT_REMOTE:-origin}"
BRANCH="${STRATUM_GIT_BRANCH:-main}"

if [[ ! -d "${GIT_DIR}/.git" ]]; then
  log "ERROR: нет git-репозитория в ${GIT_DIR}. Склонируйте репо и укажите STRATUM_GIT_DIR."
  exit 1
fi

mkdir -p "$(dirname "${LOCK_FILE}")"
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  log "уже выполняется — выход"
  exit 0
fi

cd "${GIT_DIR}"

# безопасный pull: только ff-only
if ! git fetch --prune "${REMOTE}" "${BRANCH}"; then
  log "ERROR: git fetch не удался. Для private repo настройте deploy key или token в remote URL."
  exit 1
fi
LOCAL="$(git rev-parse HEAD)"
if ! REMOTE_SHA="$(git rev-parse "${REMOTE}/${BRANCH}")"; then
  log "ERROR: нет ссылки ${REMOTE}/${BRANCH}"
  exit 1
fi

if [[ "${FORCE}" -eq 0 && "${LOCAL}" == "${REMOTE_SHA}" ]]; then
  log "нет обновлений (${LOCAL:0:8})"
  exit 0
fi

log "обновление ${LOCAL:0:8} → ${REMOTE_SHA:0:8} (${REMOTE}/${BRANCH})"
git checkout "${BRANCH}"
git merge --ff-only "${REMOTE}/${BRANCH}"

# после pull берём свежий update.sh из клона, иначе из APP_ROOT
if [[ -f "${GIT_DIR}/deploy/debian/update.sh" ]]; then
  UPDATE_SCRIPT="${GIT_DIR}/deploy/debian/update.sh"
elif [[ -f "${APP_ROOT}/deploy/debian/update.sh" ]]; then
  UPDATE_SCRIPT="${APP_ROOT}/deploy/debian/update.sh"
else
  log "ERROR: не найден update.sh"
  exit 1
fi

bash "${UPDATE_SCRIPT}" "${GIT_DIR}"
log "готово: $(git rev-parse --short HEAD)"

# health check (не валим timer при кратковременном рестарте)
sleep 2
if curl -fsS http://127.0.0.1/api/health >/dev/null 2>&1 \
  || curl -fsS http://127.0.0.1:8080/api/health >/dev/null 2>&1; then
  log "health ok"
else
  log "WARN: health check не прошёл сразу после обновления"
  exit 1
fi
