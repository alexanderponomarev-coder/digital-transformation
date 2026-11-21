from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services.store import store

client = TestClient(app)


def setup_function() -> None:
    store.reset()


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["product"] == "STRATUM"


def test_snapshot():
    res = client.get("/api/snapshot")
    assert res.status_code == 200
    data = res.json()
    assert "СеверПром" in data["overview"]["company_name"]
    assert data["overview"]["is_demo"] is True
    assert len(data["layers"]) == 5
    assert len(data["documents"]) >= 20


def test_upload_and_coverage_change():
    before = client.get("/api/overview").json()["overall_coverage"]
    res = client.post(
        "/api/documents/upload",
        json={
            "title": "Политика надзора и аудита агентов",
            "format": "pdf",
            "summary": "guardrail hitl аудит ответственность роли доступ инцидент",
            "content_hint": "governance policy",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert "governance" in body["layers"] or "strategy" in body["layers"]
    after = client.get("/api/overview").json()
    assert after["overall_coverage"] >= before


def test_answer_question_endpoint():
    snap = client.get("/api/snapshot").json()
    qid = next(q["id"] for q in snap["questions"] if q["status"] == "open")
    res = client.post(
        f"/api/questions/{qid}/answer",
        json={"answer": "Уровень 3 с обязательным HITL"},
    )
    assert res.status_code == 200
    updated = res.json()
    q = next(q for q in updated["questions"] if q["id"] == qid)
    assert q["status"] == "answered"


def test_approval_endpoint():
    snap = client.get("/api/snapshot").json()
    insight = next(i for i in snap["insights"] if i["approval"] == "pending")
    res = client.post(
        f"/api/insights/{insight['id']}/approval",
        json={"status": "approved"},
    )
    assert res.status_code == 200
    updated = next(i for i in res.json()["insights"] if i["id"] == insight["id"])
    assert updated["approval"] == "approved"


def test_regulatory_screen_endpoint():
    res = client.post(
        "/api/regulatory/screen",
        json={
            "id": "t1",
            "title": "Автономное изменение денежных лимитов",
            "process": "Финансы",
            "autonomy_level": 5,
            "impact": "high",
            "effort": "high",
            "regulatory_flags": ["деньги"],
            "admissible": True,
            "roi_hint": "",
        },
    )
    assert res.status_code == 200
    assert res.json()["admissible"] is False


def test_as_is_to_be():
    assert client.get("/api/model/as-is").status_code == 200
    assert client.get("/api/model/to-be").status_code == 200
