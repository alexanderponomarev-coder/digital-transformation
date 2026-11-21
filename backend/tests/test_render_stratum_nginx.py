"""render_stratum_nginx.py must re-attach LE cert so update does not hand :443 to Klaris."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "deploy" / "debian" / "render_stratum_nginx.py"


def test_http_only_without_cert(tmp_path: Path, monkeypatch) -> None:
    le = tmp_path / "live"
    le.mkdir()
    monkeypatch.setenv("STRATUM_LE_LIVE", str(le))
    out = tmp_path / "stratum.conf"
    subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--output",
            str(out),
            "--server-name",
            "1-web.ru",
            "--http-port",
            "80",
            "--api-port",
            "8001",
            "--default-server",
            "",
        ],
        check=True,
        env={**os.environ, "STRATUM_LE_LIVE": str(le)},
    )
    text = out.read_text()
    assert "listen 443" not in text
    assert "server_name 1-web.ru" in text
    assert "stratum_api" in text


def test_tls_preserved_when_cert_exists(tmp_path: Path) -> None:
    le = tmp_path / "live" / "1-web.ru"
    le.mkdir(parents=True)
    (le / "fullchain.pem").write_text("CERT")
    (le / "privkey.pem").write_text("KEY")
    out = tmp_path / "stratum.conf"
    subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--output",
            str(out),
            "--server-name",
            "1-web.ru",
            "--api-port",
            "8001",
        ],
        check=True,
        env={**os.environ, "STRATUM_LE_LIVE": str(tmp_path / "live")},
    )
    text = out.read_text()
    assert "listen 443 ssl" in text
    assert str(le / "fullchain.pem") in text
    assert "return 301 https" in text
    assert "location /hooks/github" in text
    # second render (simulating update.sh) still keeps TLS
    subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--output",
            str(out),
            "--server-name",
            "1-web.ru",
            "--api-port",
            "8001",
        ],
        check=True,
        env={**os.environ, "STRATUM_LE_LIVE": str(tmp_path / "live")},
    )
    assert "listen 443 ssl" in out.read_text()
