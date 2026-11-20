#!/usr/bin/env bash
# Debian 12+ install STRATUM via Docker Compose.
# Запуск: sudo bash deploy/debian/install-docker.sh [/path/to/repo]
set -euo pipefail

REPO_DIR="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
APP_ROOT="/opt/stratum"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash $0"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq ca-certificates curl gnupg rsync

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

systemctl enable --now docker

mkdir -p "${APP_ROOT}"
rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'frontend/node_modules' \
  --exclude 'frontend/dist' \
  "${REPO_DIR}/" "${APP_ROOT}/"

cd "${APP_ROOT}"
if [[ ! -f .env ]]; then
  cp .env.example .env
fi

docker compose pull || true
docker compose build
docker compose up -d

echo
echo "STRATUM (Docker) запущен."
echo "  UI:  http://$(hostname -I | awk '{print $1}')/"
echo "  API: http://$(hostname -I | awk '{print $1}')/api/health"
echo "Логи: docker compose -f ${APP_ROOT}/docker-compose.yml logs -f"
