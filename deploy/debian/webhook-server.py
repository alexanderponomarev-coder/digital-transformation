#!/usr/bin/env python3
"""Минимальный GitHub webhook → auto-update.sh.

Слушает 127.0.0.1:9000 (за nginx /hooks/github).
Проверяет X-Hub-Signature-256 при заданном STRATUM_WEBHOOK_SECRET.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get("STRATUM_WEBHOOK_HOST", "127.0.0.1")
PORT = int(os.environ.get("STRATUM_WEBHOOK_PORT", "9000"))
SECRET = os.environ.get("STRATUM_WEBHOOK_SECRET", "").encode()
AUTO_UPDATE = os.environ.get(
    "STRATUM_AUTO_UPDATE_SCRIPT", "/opt/stratum/deploy/debian/auto-update.sh"
)
BRANCH = os.environ.get("STRATUM_GIT_BRANCH", "main")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("stratum-webhook")


def verify_signature(body: bytes, header: str | None) -> bool:
    if not SECRET:
        # без секрета принимаем только с localhost — всё равно биндимся на 127.0.0.1
        return True
    if not header or not header.startswith("sha256="):
        return False
    digest = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(header, f"sha256={digest}")


def trigger_update() -> None:
    log.info("starting auto-update")
    try:
        subprocess.run(["bash", AUTO_UPDATE, "--force"], check=True)
        log.info("auto-update finished")
    except Exception:
        log.exception("auto-update failed")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        log.info("%s - %s", self.address_string(), fmt % args)

    def _json(self, code: int, payload: dict) -> None:
        data = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/health", "/hooks/github/health"):
            self._json(200, {"status": "ok", "service": "stratum-webhook"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in ("/hooks/github", "/"):
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        sig = self.headers.get("X-Hub-Signature-256")
        if not verify_signature(body, sig):
            self._json(401, {"error": "invalid signature"})
            return

        event = self.headers.get("X-GitHub-Event", "")
        try:
            payload = json.loads(body.decode() or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return

        if event == "ping":
            self._json(200, {"ok": True, "event": "ping"})
            return

        if event != "push":
            self._json(200, {"ok": True, "ignored": event})
            return

        ref = payload.get("ref", "")
        if ref not in (f"refs/heads/{BRANCH}",):
            self._json(200, {"ok": True, "ignored_ref": ref})
            return

        threading.Thread(target=trigger_update, daemon=True).start()
        self._json(202, {"ok": True, "accepted": True, "ref": ref})


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    log.info("listening on %s:%s branch=%s", HOST, PORT, BRANCH)
    server.serve_forever()


if __name__ == "__main__":
    main()
