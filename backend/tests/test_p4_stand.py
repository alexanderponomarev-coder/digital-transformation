"""P4: deploy_mode lab|demo + in-memory disclaimer on health/overview."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.settings import STORAGE_DISCLAIMER, settings
from app.main import app
from app.services.store import store


def setup_function() -> None:
    store.reset()


def test_health_exposes_stand_meta() -> None:
    client = TestClient(app)
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["product"] == "STRATUM"
    assert body["demo"] is True
    assert body["edition"] == "demo"
    assert "демо" in body["demo_label"].lower()
    assert body["deploy_mode"] in {"lab", "demo"}
    assert body["persistence"] == "in_memory"
    assert body["disclaimer"]
    assert "RAM" in body["disclaimer"] or "памят" in body["disclaimer"].lower()
    assert "auth_enabled" in body
    assert "reset_disabled" in body


def test_snapshot_overview_annotated() -> None:
    client = TestClient(app)
    ov = client.get("/api/snapshot").json()["overview"]
    assert ov["deploy_mode"] == settings.deploy_mode
    assert ov["persistence"] == "in_memory"
    assert ov["is_demo"] is True
    assert STORAGE_DISCLAIMER in ov["storage_disclaimer"]
    assert "демо" in ov["storage_disclaimer"].lower() or "ДЕМО" in ov["storage_disclaimer"]


def test_deploy_mode_demo_via_settings(monkeypatch) -> None:
    monkeypatch.setattr(settings, "deploy_mode", "demo")
    client = TestClient(app)
    assert client.get("/api/health").json()["deploy_mode"] == "demo"
    assert client.get("/api/overview").json()["deploy_mode"] == "demo"
