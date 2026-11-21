"""Maturity assessment: min-aspect rule + operating mode."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import MaturityAspectId, MaturityDomainId, MaturityScore
from app.services.maturity import compute_assessment, get_matrix
from app.services.store import store


def setup_function() -> None:
    store.reset()


def test_matrix_has_48_cells() -> None:
    matrix = get_matrix()
    assert len(matrix.domains) == 4
    assert len(matrix.aspects) == 3
    assert len(matrix.cells) == 4 * 3 * 4


def test_domain_score_is_min_not_average() -> None:
    scores = [
        MaturityScore(
            domain_id=MaturityDomainId.GOVERNANCE,
            aspect_id=MaturityAspectId.TECHNOLOGY,
            level=4,
        ),
        MaturityScore(
            domain_id=MaturityDomainId.GOVERNANCE,
            aspect_id=MaturityAspectId.ACCOUNTABILITY,
            level=4,
        ),
        MaturityScore(
            domain_id=MaturityDomainId.GOVERNANCE,
            aspect_id=MaturityAspectId.RULES,
            level=1,
        ),
    ]
    # fill other domains at 3 so governance min drives system
    for d in MaturityDomainId:
        if d == MaturityDomainId.GOVERNANCE:
            continue
        for a in MaturityAspectId:
            scores.append(MaturityScore(domain_id=d, aspect_id=a, level=3))
    result = compute_assessment(scores)
    gov = next(r for r in result.domain_results if r.domain_id == MaturityDomainId.GOVERNANCE)
    assert gov.domain_level == 1
    assert gov.weakest_aspect == MaturityAspectId.RULES


def test_api_seed_and_update() -> None:
    client = TestClient(app)
    snap = client.get("/api/snapshot").json()
    assert snap["maturity"]["system_level"] >= 1
    assert len(snap["maturity"]["scores"]) == 12
    assert "режим" in snap["maturity"]["mode_label"].lower() or "Режим" in snap["maturity"]["mode_label"] or "Ниже" in snap["maturity"]["mode_label"]

    matrix = client.get("/api/maturity/matrix").json()
    assert len(matrix["cells"]) == 48

    updated = client.put(
        "/api/maturity/scores",
        json={
            "scores": [
                {
                    "domain_id": "governance",
                    "aspect_id": "rules",
                    "level": 3,
                }
            ]
        },
    )
    assert updated.status_code == 200
    gov = next(
        d
        for d in updated.json()["maturity"]["domain_results"]
        if d["domain_id"] == "governance"
    )
    assert gov["scores"]["rules"] == 3
