#!/usr/bin/env bash
# Удаление native-установки STRATUM (код, сервис, сайт nginx).
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите от root: sudo bash $0"
  exit 1
fi

if command -v systemctl >/dev/null 2>&1 && systemctl list-units >/dev/null 2>&1; then
  systemctl stop stratum-webhook stratum-auto-update.timer stratum-api 2>/dev/null || true
  systemctl disable stratum-webhook stratum-auto-update.timer stratum-api 2>/dev/null || true
fi

rm -f /etc/systemd/system/stratum-api.service
rm -f /etc/systemd/system/stratum-auto-update.service
rm -f /etc/systemd/system/stratum-auto-update.timer
rm -f /etc/systemd/system/stratum-webhook.service
rm -f /etc/nginx/sites-enabled/stratum /etc/nginx/sites-available/stratum
rm -rf /opt/stratum /var/www/stratum /etc/stratum
# /opt/stratum-src (git clone) не трогаем — удалите вручную при необходимости

if command -v systemctl >/dev/null 2>&1 && systemctl list-units >/dev/null 2>&1; then
  systemctl daemon-reload
  systemctl reload nginx 2>/dev/null || true
fi

# пользователь stratum оставляем (может быть нужен); раскомментируйте для полного удаления:
# userdel stratum 2>/dev/null || true

echo "STRATUM native удалён."
