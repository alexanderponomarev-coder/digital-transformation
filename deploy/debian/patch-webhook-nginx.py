#!/usr/bin/env python3
"""Ensure /hooks/github proxy exists in every STRATUM nginx server block (HTTP + Certbot SSL)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SITE = Path(sys.argv[1] if len(sys.argv) > 1 else "/etc/nginx/sites-available/stratum")

LOCATION = """
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
"""


def ensure_hooks(server_body: str) -> str:
    if re.search(r"location\s+/hooks/github\b", server_body):
        # Normalize proxy_pass to upstream root so /hooks/github/health works
        server_body = re.sub(
            r"(location\s+/hooks/github\s*\{[^}]*?proxy_pass\s+)[^;]+;",
            r"\1http://127.0.0.1:9000;",
            server_body,
            count=1,
            flags=re.S,
        )
        return server_body
    # Insert before gzip or before closing of server — prefer before location /api/
    if "location /api/" in server_body:
        return server_body.replace("location /api/", LOCATION + "\n    location /api/", 1)
    if "location / {" in server_body:
        return server_body.replace("location / {", LOCATION + "\n    location / {", 1)
    # last resort: before final }
    return server_body.rstrip() + "\n" + LOCATION + "\n"


def main() -> int:
    if not SITE.is_file():
        print(f"skip: {SITE} missing", file=sys.stderr)
        return 0
    text = SITE.read_text()
    parts = re.split(r"(?m)^(server\s*\{)", text)
    # parts: [preamble, 'server {', body1, 'server {', body2, ...]
    if len(parts) < 3:
        print("skip: no server blocks", file=sys.stderr)
        return 0
    out = [parts[0]]
    changed = False
    for i in range(1, len(parts), 2):
        header = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        # Only STRATUM vhosts (avoid touching unrelated includes if any)
        if "stratum_api" in body or "root /var/www/stratum" in body or "1-web.ru" in body:
            new_body = ensure_hooks(body)
            if new_body != body:
                changed = True
            body = new_body
        out.append(header + body)
    if not changed:
        print("hooks location already present")
        return 0
    SITE.write_text("".join(out))
    print(f"patched {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
