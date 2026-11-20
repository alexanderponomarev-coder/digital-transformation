from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services.store import store

client = TestClient(app)


def setup_function() -> None:
    store.reset()


def test_tc02_norm_and_observed_separated() -> None:
    snap = client.get("/api/snapshot").json()
    kinds = {f["id"]: f["evidence_kind"] for f in snap["facts"]}
    assert kinds.get("f3") == "norm"
    assert kinds.get("f4") == "norm"
    assert kinds.get("f3o") == "observed"
    assert kinds.get("f4o") == "observed"
    observed = next(f for f in snap["facts"] if f["id"] == "f3o")
    assert observed["period"]
    assert observed["sample_size"] == 120

    as_is = client.get("/api/model/as-is").json()
    assert as_is["norm_facts"]
    assert as_is["observed_facts"]
    assert all(f["evidence_kind"] == "norm" for f in as_is["norm_facts"])
    assert all(f["evidence_kind"] == "observed" for f in as_is["observed_facts"])


def test_tc03_version_conflict_requires_confirm() -> None:
    title = "Регламент процесса «Заказ → Отгрузка»"
    res = client.post(
        "/api/documents/upload",
        headers={"X-Stratum-User": "owner-otc"},
        json={
            "title": title,
            "format": "docx",
            "summary": "Иной порядок согласования кредита, SLA 24 ч",
            "content_hint": "process регламент",
        },
    )
    assert res.status_code == 200
    new_id = res.json()["document"]["id"]
    assert res.json()["document"]["version_status"] == "conflict"
    assert "Конфликт версий" in res.json()["message"]

    snap = client.get("/api/snapshot").json()
    bpm = [d for d in snap["documents"] if d["title"] == title]
    assert len(bpm) >= 2
    assert all(d["version_status"] == "conflict" for d in bpm)
    # Must not auto-pick by upload — processes can_infer blocked while conflict
    proc = next(c for c in snap["coverage"] if c["layer_id"] == "processes")
    assert proc["can_infer"] is False

    conf = client.post(
        f"/api/documents/{new_id}/confirm-version",
        headers={"X-Stratum-User": "owner-otc"},
        json={"note": "Утверждаем новую редакцию"},
    )
    assert conf.status_code == 200
    after = conf.json()
    chosen = next(d for d in after["documents"] if d["id"] == new_id)
    assert chosen["version_status"] == "active"
    old = next(d for d in after["documents"] if d["id"] == "doc-bpm-sales")
    assert old["version_status"] == "superseded"
    proc2 = next(c for c in after["coverage"] if c["layer_id"] == "processes")
    assert proc2["can_infer"] is True


def test_tc08_read_error_no_full_coverage_claim() -> None:
    res = client.post(
        "/api/documents/upload",
        json={
            "title": "Повреждённый сканер регламента",
            "format": "pdf",
            "read_error": True,
            "read_error_detail": "CRC error in PDF stream",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["document"]["status"] == "failed"
    assert body["facts"] == []
    assert "неполный" in body["message"].lower() or "Охват неполный" in body["message"]

    snap = client.get("/api/snapshot").json()
    doc_id = body["document"]["id"]
    failed = next(d for d in snap["documents"] if d["id"] == doc_id)
    assert failed["ingest_error"]
    # Failed read must not appear as covered source on any layer
    for layer in snap["coverage"]:
        assert doc_id not in layer["document_ids"]
    assert all(f["source"]["document_id"] != doc_id for f in snap["facts"])
