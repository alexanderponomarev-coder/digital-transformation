from __future__ import annotations

import hashlib
import hmac
import importlib.util
from pathlib import Path


def _load_webhook_module():
    path = Path(__file__).resolve().parents[2] / "deploy/debian/webhook-server.py"
    spec = importlib.util.spec_from_file_location("stratum_webhook", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_verify_signature_ok(monkeypatch):
    mod = _load_webhook_module()
    secret = b"test-secret"
    monkeypatch.setattr(mod, "SECRET", secret)
    body = b'{"ref":"refs/heads/main"}'
    digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
    assert mod.verify_signature(body, f"sha256={digest}") is True


def test_verify_signature_bad(monkeypatch):
    mod = _load_webhook_module()
    monkeypatch.setattr(mod, "SECRET", b"test-secret")
    assert mod.verify_signature(b"{}", "sha256=deadbeef") is False
