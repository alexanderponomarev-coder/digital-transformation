#!/usr/bin/env bash
# Issue / renew Let's Encrypt cert for STRATUM and wire nginx :443 (cohost-safe).
# Survives later auto-update via render_stratum_nginx.py.
#
#   sudo bash /opt/stratum/deploy/debian/enable-tls.sh 1-web.ru
#   sudo bash /opt/stratum/deploy/debian/enable-tls.sh 1-web.ru --email ops@example.com
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
  exit 1
fi

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

ENV_FILE="${STRATUM_ENV_FILE:-/etc/stratum/stratum.env}"
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  set -a && source "${ENV_FILE}" && set +a
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="${APP_ROOT:-/opt/stratum}"
HTTP_PORT="${STRATUM_HTTP_PORT:-80}"
API_PORT="${STRATUM_API_PORT:-8000}"
DEFAULT_SERVER=""
if [[ ! -f /etc/nginx/sites-enabled/klaris && ! -d /opt/klaris ]]; then
  DEFAULT_SERVER=" default_server"
else
  API_PORT="${STRATUM_API_PORT:-8001}"
fi

echo "==> Preflight HTTP for Host: ${DOMAIN}"
if ! curl -fsS -H "Host: ${DOMAIN}" "http://127.0.0.1/api/health" >/tmp/stratum-tls-health.json \
  && ! curl -fsS -H "Host: ${DOMAIN}" "http://127.0.0.1:${HTTP_PORT}/api/health" >/tmp/stratum-tls-health.json; then
  # After previous broken TLS, :80 may already redirect — allow ACME on bare IP path later
  echo "WARN: HTTP health for Host=${DOMAIN} failed; continuing if nginx listens on :80" >&2
fi

echo "==> Ensure certbot + webroot for ACME"
apt-get update -qq
apt-get install -y -qq certbot python3-certbot-nginx
mkdir -p /var/www/html/.well-known/acme-challenge
# Temporary HTTP-only render so certbot/nginx plugin has a STRATUM server_name to attach to
python3 "${SCRIPT_DIR}/render_stratum_nginx.py" \
  --output /etc/nginx/sites-available/stratum \
  --server-name "${DOMAIN}" \
  --http-port "${HTTP_PORT}" \
  --api-port "${API_PORT}" \
  --default-server "${DEFAULT_SERVER}"
# Force HTTP-only for issuance: if cert missing render is already HTTP; if stale Klaris-only :443, OK
ln -sfn /etc/nginx/sites-available/stratum /etc/nginx/sites-enabled/stratum
nginx -t && systemctl reload nginx

CERTBOT_ARGS=(certonly --nginx -d "${DOMAIN}" --non-interactive --agree-tos --keep-until-expiring)
if [[ -n "${EMAIL}" ]]; then
  CERTBOT_ARGS+=(--email "${EMAIL}")
else
  CERTBOT_ARGS+=(--register-unsafely-without-email)
fi
if [[ ${#EXTRA[@]} -gt 0 ]]; then
  CERTBOT_ARGS+=("${EXTRA[@]}")
fi

echo "==> certbot ${CERTBOT_ARGS[*]}"
if ! certbot "${CERTBOT_ARGS[@]}"; then
  echo "==> nginx plugin failed — try webroot"
  WR=(certonly --webroot -w /var/www/html -d "${DOMAIN}" --non-interactive --agree-tos)
  if [[ -n "${EMAIL}" ]]; then
    WR+=(--email "${EMAIL}")
  else
    WR+=(--register-unsafely-without-email)
  fi
  certbot "${WR[@]}"
fi

if [[ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]]; then
  echo "ERROR: cert not found at /etc/letsencrypt/live/${DOMAIN}/" >&2
  exit 1
fi

echo "==> Render STRATUM nginx with TLS (owned by us — survives update.sh)"
python3 "${SCRIPT_DIR}/render_stratum_nginx.py" \
  --output /etc/nginx/sites-available/stratum \
  --server-name "${DOMAIN}" \
  --http-port "${HTTP_PORT}" \
  --api-port "${API_PORT}" \
  --default-server "${DEFAULT_SERVER}"

# Persist domain in env
if [[ -f "${ENV_FILE}" ]]; then
  if grep -q '^STRATUM_SERVER_NAME=' "${ENV_FILE}"; then
    sed -i "s|^STRATUM_SERVER_NAME=.*|STRATUM_SERVER_NAME=${DOMAIN}|" "${ENV_FILE}"
  else
    echo "STRATUM_SERVER_NAME=${DOMAIN}" >>"${ENV_FILE}"
  fi
fi

nginx -t && systemctl reload nginx

echo "==> Verify"
echo | openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" 2>/dev/null \
  | openssl x509 -noout -subject -ext subjectAltName || true
curl -fsS "https://${DOMAIN}/api/health"
echo
# Must be STRATUM, not Klaris HTML
BODY="$(curl -fsS "https://${DOMAIN}/" | head -c 200)"
if echo "${BODY}" | grep -qi 'Klaris'; then
  echo "ERROR: https://${DOMAIN}/ still serves Klaris — check nginx server_name / default_server" >&2
  exit 1
fi
echo "OK: https://${DOMAIN} serves STRATUM with matching certificate."
echo "    Klaris remains on its own server_name (e.g. klaris.1-web.ru)."
