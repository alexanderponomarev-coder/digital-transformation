#!/usr/bin/env bash
# Автообновление STRATUM с GitHub: clone (если нет) → fetch/pull → update.sh.
# Private GitHub: STRATUM_GITHUB_TOKEN (или GITHUB_TOKEN) в /etc/stratum/stratum.env
# sudo bash deploy/debian/auto-update.sh [--force]
set -euo pipefail

FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

ENV_FILE="${ENV_FILE:-/etc/stratum/stratum.env}"
APP_ROOT="${APP_ROOT:-/opt/stratum}"
LOG_TAG="stratum-auto-update"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

# shellcheck source=git-auth.sh
source "${SCRIPT_DIR}/git-auth.sh"
stratum_load_git_env "${ENV_FILE}"

GIT_DIR="${STRATUM_GIT_DIR:-/opt/stratum-src}"
REMOTE="${STRATUM_GIT_REMOTE:-origin}"
BRANCH="${STRATUM_GIT_BRANCH:-main}"
REPO_URL="${STRATUM_REPO_URL:-${STRATUM_DEFAULT_REPO_URL}}"
GITHUB_TOKEN="${STRATUM_GITHUB_TOKEN:-${GITHUB_TOKEN:-}}"

mkdir -p "$(dirname "${LOCK_FILE}")"
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  log "уже выполняется — выход"
  exit 0
fi

if ! stratum_ensure_git_clone "${GIT_DIR}" "${BRANCH}" "${REPO_URL}" log; then
  exit 1
fi

cd "${GIT_DIR}"

REPO_URL="$(stratum_public_repo_url "${REPO_URL}")"
if [[ -z "${REPO_URL}" || "${REPO_URL}" == "${STRATUM_DEFAULT_REPO_URL}" ]]; then
  # если в env пусто — взять public URL с origin (уже без токена после ensure)
  ORIGIN_URL="$(git remote get-url "${REMOTE}" 2>/dev/null || true)"
  if [[ -n "${ORIGIN_URL}" ]]; then
    REPO_URL="$(stratum_public_repo_url "${ORIGIN_URL}")"
  fi
fi
git remote set-url "${REMOTE}" "${REPO_URL}" 2>/dev/null || true

export GIT_TERMINAL_PROMPT=0
AUTH_URL="$(stratum_auth_repo_url "${REPO_URL}")"

git_fetch_branch() {
  if [[ -n "${GITHUB_TOKEN}" && "${AUTH_URL}" == https://* ]]; then
    git fetch --prune "${AUTH_URL}" "+refs/heads/${BRANCH}:refs/remotes/${REMOTE}/${BRANCH}"
  else
    git fetch --prune "${REMOTE}" "${BRANCH}"
  fi
}

if ! git_fetch_branch; then
  log "ERROR: git fetch не удался."
  if [[ -z "${GITHUB_TOKEN}" ]]; then
    log "hint: private repo — добавьте в ${ENV_FILE}:"
    log "  STRATUM_GITHUB_TOKEN=ghp_...   # fine-grained: Contents Read"
    log "  # либо deploy key (SSH) — см. docs/INSTALL.md §3"
  else
    log "hint: токен есть, но fetch failed — проверьте Contents: Read и STRATUM_REPO_URL / remote"
  fi
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
HOST_HDR=()
if [[ -n "${STRATUM_SERVER_NAME:-}" && "${STRATUM_SERVER_NAME}" != "_" ]]; then
  HOST_HDR=(-H "Host: ${STRATUM_SERVER_NAME}")
fi
if curl -fsS "${HOST_HDR[@]}" http://127.0.0.1/api/health >/dev/null 2>&1 \
  || curl -fsS http://127.0.0.1:8000/api/health >/dev/null 2>&1 \
  || curl -fsS http://127.0.0.1:8001/api/health >/dev/null 2>&1; then
  log "health ok"
else
  log "WARN: health check не прошёл сразу после обновления"
  exit 1
fi
