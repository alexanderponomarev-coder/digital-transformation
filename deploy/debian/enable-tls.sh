#!/usr/bin/env bash
# Issue / renew Let's Encrypt cert for STRATUM nginx vhost (certbot --nginx).
# Usage:
#   sudo bash /opt/stratum/deploy/debian/enable-tls.sh 1-web.ru
#   sudo bash /opt/stratum/deploy/debian/enable-tls.sh stratum.example.com --email ops@example.com
set -euo pipefail

DOMAIN="${1:-}"
shift || true
EMAIL=""
EXTRA=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --email)
      EMAIL="${2:-}"
      shift 2
      ;;
    *)
      EXTRA+=("$1")
      shift
      ;;
  esac
done

if [[ -z "${DOMAIN}" || "${DOMAIN}" == "_" ]]; then
  echo "Usage: $0 <server_name> [--email you@example.com]" >&2
  echo "  server_name must match STRATUM_SERVER_NAME / nginx server_name (not '_')." >&2
  exit 1
fi

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

ENV_FILE="${STRATUM_ENV_FILE:-/etc/stratum/stratum.env}"
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  set -a
  # shellcheck disable=SC1091
  source "${ENV_FILE}"
  set +a
fi

API_PORT="${STRATUM_API_PORT:-8000}"
echo "==> Preflight HTTP for Host: ${DOMAIN}"
if ! curl -fsS -H "Host: ${DOMAIN}" "http://127.0.0.1/api/health" >/tmp/stratum-tls-health.json; then
  echo "FAIL: nginx/API not answering on :80 for Host=${DOMAIN}." >&2
  echo "  Check: systemctl status nginx stratum-api; nginx -t; STRATUM_SERVER_NAME=${DOMAIN}" >&2
  exit 1
fi
python3 - <<'PY' || true
import json
print("health:", open("/tmp/stratum-tls-health.json").read().strip()[:200])
PY

echo "==> Ensure certbot"
apt-get update -qq
apt-get install -y -qq certbot python3-certbot-nginx

CERTBOT_ARGS=(--nginx -d "${DOMAIN}" --non-interactive --agree-tos --redirect)
if [[ -n "${EMAIL}" ]]; then
  CERTBOT_ARGS+=(--email "${EMAIL}")
else
  CERTBOT_ARGS+=(--register-unsafely-without-email)
fi
if [[ ${#EXTRA[@]} -gt 0 ]]; then
  CERTBOT_ARGS+=("${EXTRA[@]}")
fi

echo "==> certbot ${CERTBOT_ARGS[*]}"
certbot "${CERTBOT_ARGS[@]}"

echo "==> Verify HTTPS"
curl -fsS "https://${DOMAIN}/api/health" | head -c 300
echo
echo "OK: https://${DOMAIN} — if browser still warns, wait for DNS/CDN or check cohost Klaris cert on :443."
echo "    Renew: certbot renew --dry-run"
echo "    Cohost: run this script once per domain (Klaris and STRATUM separately)."
