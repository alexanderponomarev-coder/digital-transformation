"""patch-webhook-nginx.py keeps /hooks/github on HTTP and SSL server blocks."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "deploy" / "debian" / "patch-webhook-nginx.py"


def test_patch_adds_hooks_to_both_server_blocks(tmp_path: Path) -> None:
    site = tmp_path / "stratum"
    site.write_text(
        textwrap.dedent(
            """
            upstream stratum_api { server 127.0.0.1:8001; }
            server {
                listen 80;
                server_name 1-web.ru;
                root /var/www/stratum;
                location /api/ { proxy_pass http://stratum_api; }
            }
            server {
                listen 443 ssl;
                server_name 1-web.ru;
                root /var/www/stratum;
                ssl_certificate /etc/letsencrypt/live/1-web.ru/fullchain.pem;
                location /api/ { proxy_pass http://stratum_api; }
            }
            """
        )
    )
    subprocess.run(["python3", str(SCRIPT), str(site)], check=True)
    text = site.read_text()
    assert text.count("location /hooks/github") == 2
    assert "proxy_pass http://127.0.0.1:9000;" in text


def test_patch_normalizes_old_proxy_pass(tmp_path: Path) -> None:
    site = tmp_path / "stratum"
    site.write_text(
        textwrap.dedent(
            """
            server {
                listen 80;
                server_name 1-web.ru;
                root /var/www/stratum;
                location /hooks/github {
                    proxy_pass http://127.0.0.1:9000/hooks/github;
                }
                location /api/ { proxy_pass http://stratum_api; }
            }
            """
        )
    )
    subprocess.run(["python3", str(SCRIPT), str(site)], check=True)
    text = site.read_text()
    assert "proxy_pass http://127.0.0.1:9000;" in text
    assert "9000/hooks/github" not in text
