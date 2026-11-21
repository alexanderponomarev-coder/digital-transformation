#!/usr/bin/env python3
"""Render STRATUM nginx site; re-attach Let's Encrypt SSL if cert already exists.

Why: update.sh used to overwrite sites-available/stratum with HTTP-only template,
wiping certbot's :443 block. Then https://1-web.ru fell through to Klaris cert/vhost.

Usage:
  python3 render_stratum_nginx.py \\
    --template deploy/debian/nginx-stratum.conf \\
    --output /etc/nginx/sites-available/stratum \\
    --server-name 1-web.ru \\
    --http-port 80 \\
    --api-port 8001 \\
    --default-server ""
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

LE_LIVE = Path(__import__("os").environ.get("STRATUM_LE_LIVE", "/etc/letsencrypt/live"))
SSL_OPTIONS = Path(
    __import__("os").environ.get(
        "STRATUM_SSL_OPTIONS", "/etc/letsencrypt/options-ssl-nginx.conf"
    )
)
SSL_DHPARAM = Path(
    __import__("os").environ.get(
        "STRATUM_SSL_DHPARAM", "/etc/letsencrypt/ssl-dhparams.pem"
    )
)

LOCATION_BODY = r"""
    root /var/www/stratum;
    index index.html;

    client_max_body_size 32m;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://stratum_api;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 120s;
    }

    location /docs {
        proxy_pass http://stratum_api;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://stratum_api;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://stratum_api;
        proxy_set_header Host $host;
    }

    location /api/health {
        proxy_pass http://stratum_api;
        proxy_set_header Host $host;
        access_log off;
    }

    location /hooks/github {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Hub-Signature-256 $http_x_hub_signature_256;
        proxy_set_header X-GitHub-Event $http_x_github_event;
        proxy_read_timeout 10s;
    }

    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;
"""


def cert_paths(domain: str) -> tuple[Path, Path] | None:
    if not domain or domain == "_":
        return None
    full = LE_LIVE / domain / "fullchain.pem"
    key = LE_LIVE / domain / "privkey.pem"
    if full.is_file() and key.is_file():
        return full, key
    return None


def render_http_only(
    *,
    server_name: str,
    http_port: str,
    api_port: str,
    default_server: str,
) -> str:
    return f"""# Managed by STRATUM render_stratum_nginx.py (HTTP only — no LE cert for {server_name})
upstream stratum_api {{
    server 127.0.0.1:{api_port};
    keepalive 8;
}}

server {{
    listen {http_port}{default_server};
    listen [::]:{http_port}{default_server};
    server_name {server_name};
{LOCATION_BODY}
}}
"""


def render_with_tls(
    *,
    server_name: str,
    http_port: str,
    api_port: str,
    default_server: str,
    fullchain: Path,
    privkey: Path,
) -> str:
    ssl_extra = ""
    if SSL_OPTIONS.is_file():
        ssl_extra += f"    include {SSL_OPTIONS};\n"
    if SSL_DHPARAM.is_file():
        ssl_extra += f"    ssl_dhparam {SSL_DHPARAM};\n"

    return f"""# Managed by STRATUM render_stratum_nginx.py (HTTP→HTTPS + LE cert {server_name})
# Cohost-safe: does not touch Klaris vhosts. Survives auto-update.
upstream stratum_api {{
    server 127.0.0.1:{api_port};
    keepalive 8;
}}

server {{
    listen {http_port}{default_server};
    listen [::]:{http_port}{default_server};
    server_name {server_name};

    location /.well-known/acme-challenge/ {{
        root /var/www/html;
    }}

    location / {{
        return 301 https://$host$request_uri;
    }}
}}

server {{
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name {server_name};

    ssl_certificate {fullchain};
    ssl_certificate_key {privkey};
{ssl_extra}{LOCATION_BODY}
}}
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--template", type=Path, help="unused legacy; kept for CLI compat")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--server-name", required=True)
    p.add_argument("--http-port", default="80")
    p.add_argument("--api-port", default="8000")
    p.add_argument("--default-server", default="")
    args = p.parse_args()

    domain = args.server_name.strip()
    default_server = args.default_server  # may be " default_server"
    certs = cert_paths(domain)

    if certs:
        fullchain, privkey = certs
        text = render_with_tls(
            server_name=domain,
            http_port=args.http_port,
            api_port=args.api_port,
            default_server=default_server,
            fullchain=fullchain,
            privkey=privkey,
        )
        mode = f"TLS preserved ({fullchain})"
    else:
        text = render_http_only(
            server_name=domain,
            http_port=args.http_port,
            api_port=args.api_port,
            default_server=default_server,
        )
        mode = "HTTP only (no LE cert — https may hit Klaris on cohost)"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    # drop stale `# managed by Certbot` duplicates risk: we own the whole file now
    print(f"wrote {args.output} · {mode}")
    if not certs and domain != "_":
        print(
            f"HINT: sudo bash /opt/stratum/deploy/debian/enable-tls.sh {domain}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
