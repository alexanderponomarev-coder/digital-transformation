from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import RoiBenefitLine, RoiComputeRequest
from app.services.roi import compute_roi
from app.services.store import store

client = TestClient(app)


def setup_function() -> None:
    store.reset()


def test_seed_roi_is_illustrative_not_proven() -> None:
    snap = client.get("/api/snapshot").json()
    roi = snap["roi"]
    assert roi["kind"] == "illustrative"
    assert roi["monetary_roi"] is None
    assert "иллюстрац" in roi["disclaimer"].lower() or "Illustrat" in roi["disclaimer"]


def test_tc04_hours_without_rate_no_monetary_roi() -> None:
    result = compute_roi(
        RoiComputeRequest(
            investment=None,
            benefits=[
                RoiBenefitLine(
                    id="b1",
                    description="Очередь кредита",
                    process_step_id="otc.credit_control",
                    hours_per_year=1000,
                    hourly_rate=None,
                )
            ],
        )
    )
    assert result.kind == "hours_only"
    assert result.monetary_roi is None
    assert result.hours_saved_per_year == 1000
    assert result.missing_inputs

    res = client.post(
        "/api/roi/compute",
        json={
            "benefits": [
                {
                    "id": "b1",
                    "description": "Очередь",
                    "process_step_id": "otc.credit_control",
                    "hours_per_year": 500,
                }
            ]
        },
    )
    assert res.status_code == 200
    assert res.json()["kind"] == "hours_only"
    assert res.json()["monetary_roi"] is None


def test_tc05_double_count_hours_on_same_step() -> None:
    result = compute_roi(
        RoiComputeRequest(
            investment=10_000_000,
            benefits=[
                RoiBenefitLine(
                    id="b1",
                    description="Агент A",
                    process_step_id="otc.credit_control",
                    opportunity_id="opp-1",
                    hours_per_year=1000,
                    hourly_rate=2000,
                ),
                RoiBenefitLine(
                    id="b2",
                    description="Агент B на том же шаге",
                    process_step_id="otc.credit_control",
                    opportunity_id="opp-x",
                    hours_per_year=800,
                    hourly_rate=2000,
                ),
            ],
        )
    )
    assert "otc.credit_control" in result.overlapping_steps
    included = [b for b in result.benefit_lines if b.included]
    excluded = [b for b in result.benefit_lines if not b.included]
    assert len(included) == 1
    assert len(excluded) == 1
    assert excluded[0].id == "b2"
    # Only first line monetized: 1000*2000 = 2e6
    assert result.kind == "calculated"
    assert result.annual_benefit_mln == 2.0
    assert result.monetary_roi is not None


def test_calculated_roi_formula() -> None:
    # benefits 5_000_000 / year, invest 10_000_000, horizon 12m
    # ROI = (5e6 - 10e6) / 10e6 = -0.5
    result = compute_roi(
        RoiComputeRequest(
            investment=10_000_000,
            horizon_months=12,
            benefits=[
                RoiBenefitLine(
                    id="b1",
                    description="Эффект",
                    process_step_id="step.a",
                    cash_benefit=5_000_000,
                )
            ],
        )
    )
    assert result.kind == "calculated"
    assert result.monetary_roi == -0.5
