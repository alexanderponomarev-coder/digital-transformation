from __future__ import annotations

from app.data.seed import build_snapshot
from app.models.schemas import ApprovalStatus, LayerId
from app.services import engine
from app.services.regulatory import is_admissible, screen_opportunity


def test_seed_snapshot_has_five_layers():
    snap = build_snapshot()
    assert len(snap.layers) == 5
    assert snap.overview.company_name == "СеверПром"
    assert snap.overview.open_questions_count >= 1


def test_classify_maps_process_document():
    result = engine.classify_document(
        title="Регламент процесса согласования счетов",
        format_value="docx",
        summary="Описание workflow и decision points SLA",
    )
    assert LayerId.PROCESSES in result.layers
    assert result.document.status == "ready"
    assert result.facts


def test_classify_does_not_invent_empty_summary_as_high_confidence():
    result = engine.classify_document(
        title="Прочее",
        format_value="pdf",
        summary="",
        content_hint="",
    )
    assert all(f.confidence.value in {"low", "medium"} for f in result.facts)


def test_coverage_threshold_gates_inference():
    snap = build_snapshot()
    tools = next(c for c in snap.coverage if c.layer_id == LayerId.TOOLS)
    gov = next(c for c in snap.coverage if c.layer_id == LayerId.GOVERNANCE)
    assert tools.can_infer is False
    assert gov.can_infer is False
    strategy = next(c for c in snap.coverage if c.layer_id == LayerId.STRATEGY)
    assert strategy.can_infer is True


def test_ingest_versions_same_title():
    snap = build_snapshot()
    updated, first = engine.ingest_document(
        snap, title="Новый отчёт по данным", format_value="xlsx", summary="каталог данных качество"
    )
    updated2, second = engine.ingest_document(
        updated,
        title="Новый отчёт по данным",
        format_value="xlsx",
        summary="каталог данных качество обновлён",
    )
    assert second.document.version == first.document.version + 1
    assert second.document.replaces_id == first.document.id
    assert updated2.documents[0].title == "Новый отчёт по данным"


def test_answer_becomes_fact_and_insight():
    snap = build_snapshot()
    qid = snap.questions[0].id
    updated = engine.answer_question(snap, qid, "Целевой уровень автономии — 3 с HITL")
    answered = next(q for q in updated.questions if q.id == qid)
    assert answered.status == "answered"
    assert any(f.source.document_id == f"answer:{qid}" for f in updated.facts)
    assert updated.overview.open_questions_count == snap.overview.open_questions_count - 1


def test_approval_updates_overview():
    snap = build_snapshot()
    pending = next(i for i in snap.insights if i.approval == ApprovalStatus.PENDING)
    updated = engine.set_insight_approval(snap, pending.id, "approved")
    assert updated.overview.approved_insights_count == snap.overview.approved_insights_count + 1


def test_as_is_only_inferable_layers():
    snap = build_snapshot()
    summary = engine.as_is_summary(snap)
    assert "strategy" in summary["layers_ready"]
    assert "governance" not in summary["layers_ready"]


def test_regulatory_blocks_autonomous_money_write():
    from app.models.schemas import Opportunity

    opp = Opportunity(
        id="x",
        title="Автономное изменение денежных лимитов",
        process="Финансы / лимиты",
        autonomy_level=5,
        impact="high",
        effort="high",
        regulatory_flags=["деньги"],
        admissible=True,
    )
    checks = screen_opportunity(opp)
    assert is_admissible(checks) is False
    assert any(c.status == "block" for c in checks)


def test_refresh_overview_recomputes_coverage():
    snap = build_snapshot()
    refreshed = engine.refresh_overview(snap)
    assert len(refreshed.coverage) == 5
    assert 0 <= refreshed.overview.overall_coverage <= 1
