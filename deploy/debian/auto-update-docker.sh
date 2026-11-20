#!/usr/bin/env bash
# Автообновление Docker-стека с GitHub.
# sudo bash deploy/debian/auto-update-docker.sh [--force]
set -euo pipefail

FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

ENV_FILE="${ENV_FILE:-/etc/stratum/stratum.env}"
# shellcheck disable=SC1090
[[ -f "${ENV_FILE}" ]] && set -a && source "${ENV_FILE}" && set +a

GIT_DIR="${STRATUM_GIT_DIR:-/opt/stratum}"
REMOTE="${STRATUM_GIT_REMOTE:-origin}"
BRANCH="${STRATUM_GIT_BRANCH:-main}"
LOCK_FILE=/var/lock/stratum-auto-update-docker.lock

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root"
  exit 1
fi

exec 9>"${LOCK_FILE}"
flock -n 9 || { echo "already running"; exit 0; }

cd "${GIT_DIR}"
git fetch --prune "${REMOTE}" "${BRANCH}"
LOCAL="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse "${REMOTE}/${BRANCH}")"

if [[ "${FORCE}" -eq 0 && "${LOCAL}" == "${REMOTE_SHA}" ]]; then
  echo "нет обновлений (${LOCAL:0:8})"
  exit 0
fi

git checkout "${BRANCH}"
git merge --ff-only "${REMOTE}/${BRANCH}"
docker compose up -d --build
curl -fsS http://127.0.0.1/api/health || curl -fsS http://127.0.0.1:8080/api/health
echo
echo "docker update done: $(git rev-parse --short HEAD)"
