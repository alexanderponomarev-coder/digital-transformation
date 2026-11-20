from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.settings import settings
from app.main import app
from app.services.store import store

client = TestClient(app)


def setup_function() -> None:
    store.reset()
    settings.api_token = ""
    settings.disable_reset = False


def test_health_public_even_with_token(monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_token", "secret-token")
    res = client.get("/api/health")
    assert res.status_code == 200


def test_snapshot_requires_bearer_when_token_set(monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_token", "secret-token")
    assert client.get("/api/snapshot").status_code == 401
    res = client.get(
        "/api/snapshot",
        headers={"Authorization": "Bearer secret-token", "X-Stratum-User": "alice"},
    )
    assert res.status_code == 200


def test_reset_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "disable_reset", True)
    res = client.post("/api/reset")
    assert res.status_code == 403


def test_tc06_acl_deny_and_revoke() -> None:
    """TC-06: B cannot read A's restricted doc; after revoke A also cannot."""
    # A uploads restricted document
    up = client.post(
        "/api/documents/upload",
        headers={"X-Stratum-User": "user-a"},
        json={
            "title": "Секретный регламент кредитного лимита",
            "format": "pdf",
            "summary": "внутренний лимит клиентов",
            "content_hint": "process регламент",
            "acl_readers": ["user-a"],
        },
    )
    assert up.status_code == 200
    doc_id = up.json()["document"]["id"]
    assert up.json()["document"]["owner_id"] == "user-a"

    # B: snapshot must not contain doc or its facts
    snap_b = client.get("/api/snapshot", headers={"X-Stratum-User": "user-b"}).json()
    assert doc_id not in {d["id"] for d in snap_b["documents"]}
    assert all(f["source"]["document_id"] != doc_id for f in snap_b["facts"])

    # B: direct get → 404 (no existence leak via 403)
    assert (
        client.get(
            f"/api/documents/{doc_id}", headers={"X-Stratum-User": "user-b"}
        ).status_code
        == 404
    )

    # A still sees it
    snap_a = client.get("/api/snapshot", headers={"X-Stratum-User": "user-a"}).json()
    assert doc_id in {d["id"] for d in snap_a["documents"]}
    assert (
        client.get(
            f"/api/documents/{doc_id}", headers={"X-Stratum-User": "user-a"}
        ).status_code
        == 200
    )

    # Revoke: empty readers + clear access for A by setting readers to other user only
    rev = client.patch(
        f"/api/documents/{doc_id}/acl",
        headers={"X-Stratum-User": "user-a"},
        json={"acl_readers": ["nobody"], "owner_id": "user-a"},
    )
    assert rev.status_code == 200
    # Owner still sees (owner bypass)
    assert doc_id in {d["id"] for d in rev.json()["documents"]}

    # Transfer ownership away and exclude A
    rev2 = client.patch(
        f"/api/documents/{doc_id}/acl",
        headers={"X-Stratum-User": "user-a"},
        json={"acl_readers": ["user-c"], "owner_id": "user-c"},
    )
    assert rev2.status_code == 200
    snap_a2 = client.get("/api/snapshot", headers={"X-Stratum-User": "user-a"}).json()
    assert doc_id not in {d["id"] for d in snap_a2["documents"]}
    assert (
        client.get(
            f"/api/documents/{doc_id}", headers={"X-Stratum-User": "user-a"}
        ).status_code
        == 404
    )


def test_b_cannot_patch_acl() -> None:
    up = client.post(
        "/api/documents/upload",
        headers={"X-Stratum-User": "user-a"},
        json={
            "title": "ACL ownership doc",
            "format": "pdf",
            "summary": "governance",
            "acl_readers": ["user-a"],
        },
    )
    doc_id = up.json()["document"]["id"]
    res = client.patch(
        f"/api/documents/{doc_id}/acl",
        headers={"X-Stratum-User": "user-b"},
        json={"acl_readers": ["user-b"]},
    )
    assert res.status_code == 403
