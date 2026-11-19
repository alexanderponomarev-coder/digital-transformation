from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.methodology import COVERAGE_THRESHOLD_DEFAULT, LAYER_KEYWORDS, LAYERS
from app.models.schemas import (
    ApprovalStatus,
    BlindZone,
    ClassifyResult,
    Confidence,
    CoverageStatus,
    DocumentRecord,
    Fact,
    Insight,
    LayerCoverage,
    LayerId,
    PlatformSnapshot,
    SourceRef,
)


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def classify_document(
    title: str,
    format_value: str,
    summary: str = "",
    content_hint: str = "",
) -> ClassifyResult:
    """Deterministic classifier: keyword → methodology layers + extracted facts.

    MVP stand-in for LLM extraction. Never invents beyond provided text —
    unknown layers become clarifying-question candidates via coverage recalc.
    """
    blob = f"{title} {summary} {content_hint}".lower()
    matched: list[LayerId] = []
    for layer_id, keywords in LAYER_KEYWORDS.items():
        if any(k in blob for k in keywords):
            matched.append(layer_id)
    if not matched:
        # Default soft assignment to strategy when nothing matches — still partial.
        matched = [LayerId.STRATEGY]

    doc_id = _uid("doc")
    document = DocumentRecord(
        id=doc_id,
        title=title,
        format=format_value,  # type: ignore[arg-type]
        uploaded_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        version=1,
        layers=matched,
        freshness_days=0,
        size_label="загрузка",
        summary=summary or content_hint or "Документ загружен пользователем.",
        status="ready",
    )

    facts: list[Fact] = []
    # Extract lightweight facts from non-empty provided text only.
    for layer_id in matched:
        layer = next(l for l in LAYERS if l.id == layer_id)
        snippet = summary or content_hint or title
        facts.append(
            Fact(
                id=_uid("fact"),
                text=f"[{layer.short_title}] Извлечено из документа: {snippet[:220]}",
                entity_type="other",
                layers=[layer_id],
                source=SourceRef(
                    document_id=doc_id,
                    document_title=title,
                    fragment=(summary or content_hint or title)[:160],
                ),
                confidence=Confidence.MEDIUM if (summary or content_hint) else Confidence.LOW,
            )
        )

    return ClassifyResult(
        document=document,
        facts=facts,
        layers=matched,
        message=(
            f"Документ отнесён к слоям: {', '.join(l.value for l in matched)}. "
            "Выводы по слою появятся только при покрытии выше порога."
        ),
    )


def recompute_coverage(snapshot: PlatformSnapshot) -> list[LayerCoverage]:
    threshold = snapshot.overview.coverage_threshold or COVERAGE_THRESHOLD_DEFAULT
    docs_by_layer: dict[LayerId, list[str]] = {layer.id: [] for layer in LAYERS}
    for doc in snapshot.documents:
        for layer_id in doc.layers:
            docs_by_layer[layer_id].append(doc.id)

    facts_by_layer: dict[LayerId, int] = {layer.id: 0 for layer in LAYERS}
    for fact in snapshot.facts:
        for layer_id in fact.layers:
            facts_by_layer[layer_id] += 1

    open_q_by_layer: dict[LayerId, list[str]] = {layer.id: [] for layer in LAYERS}
    for q in snapshot.questions:
        if q.status == "open":
            open_q_by_layer[q.layer_id].append(q.id)

    result: list[LayerCoverage] = []
    for layer in LAYERS:
        doc_ids = docs_by_layer[layer.id]
        fact_count = facts_by_layer[layer.id]
        # Score: documents weight + facts weight − open questions penalty
        doc_score = min(1.0, len(doc_ids) / 2.0) * 0.55
        fact_score = min(1.0, fact_count / 3.0) * 0.45
        penalty = min(0.35, len(open_q_by_layer[layer.id]) * 0.08)
        score = round(max(0.0, doc_score + fact_score - penalty), 2)

        if score >= 0.75 and not open_q_by_layer[layer.id]:
            status = CoverageStatus.CLOSED
        elif score >= threshold:
            status = CoverageStatus.PARTIAL
        else:
            status = CoverageStatus.MISSING

        # Preserve known blind zones from previous coverage when possible
        prev = next((c for c in snapshot.coverage if c.layer_id == layer.id), None)
        blind_zones = prev.blind_zones if prev else []
        if open_q_by_layer[layer.id] and not blind_zones:
            blind_zones = [
                BlindZone(
                    id=_uid("bz"),
                    title=f"Незакрытые вопросы: {layer.short_title}",
                    reason="Покрытие ниже полноты — требуются ответы ответственных.",
                    question_ids=open_q_by_layer[layer.id],
                )
            ]

        result.append(
            LayerCoverage(
                layer_id=layer.id,
                status=status,
                score=score,
                threshold=threshold,
                document_ids=doc_ids,
                blind_zones=blind_zones,
                can_infer=score >= threshold and layer.mvp,
            )
        )
    return result


def refresh_overview(snapshot: PlatformSnapshot) -> PlatformSnapshot:
    coverage = recompute_coverage(snapshot)
    overall = round(sum(c.score for c in coverage) / len(coverage), 2) if coverage else 0.0
    overview = snapshot.overview.model_copy(
        update={
            "open_questions_count": sum(1 for q in snapshot.questions if q.status == "open"),
            "approved_insights_count": sum(
                1 for i in snapshot.insights if i.approval == ApprovalStatus.APPROVED
            ),
            "blocked_cases_count": sum(1 for o in snapshot.opportunities if not o.admissible)
            + sum(1 for r in snapshot.regulatory if r.status == "block"),
            "overall_coverage": overall,
        }
    )
    metrics = snapshot.engine_metrics.model_copy(update={"coverage_completeness": overall})
    return snapshot.model_copy(
        update={"coverage": coverage, "overview": overview, "engine_metrics": metrics}
    )


def ingest_document(
    snapshot: PlatformSnapshot,
    title: str,
    format_value: str,
    summary: str = "",
    content_hint: str = "",
) -> tuple[PlatformSnapshot, ClassifyResult]:
    classified = classify_document(title, format_value, summary, content_hint)

    # Versioning: same title → bump version, keep history via replaces_id
    existing = next(
        (d for d in snapshot.documents if d.title.lower() == title.lower()),
        None,
    )
    document = classified.document
    if existing:
        document = document.model_copy(
            update={
                "version": existing.version + 1,
                "replaces_id": existing.id,
            }
        )

    docs = [document, *snapshot.documents]
    facts = [*classified.facts, *snapshot.facts]
    updated = snapshot.model_copy(update={"documents": docs, "facts": facts})
    updated = refresh_overview(updated)
    return updated, classified.model_copy(update={"document": document})


def answer_question(
    snapshot: PlatformSnapshot, question_id: str, answer: str
) -> PlatformSnapshot:
    questions = []
    answered = None
    for q in snapshot.questions:
        if q.id == question_id:
            answered = q.model_copy(
                update={
                    "status": "answered",
                    "answer": answer,
                    "answered_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
            )
            questions.append(answered)
        else:
            questions.append(q)
    if answered is None:
        raise KeyError(f"Question {question_id} not found")

    # Answers become first-class sources (as facts)
    fact = Fact(
        id=_uid("fact"),
        text=f"Ответ ({answered.to_role}): {answer}",
        entity_type="other",
        layers=[answered.layer_id],
        source=SourceRef(
            document_id=f"answer:{answered.id}",
            document_title=f"Ответ на вопрос {answered.id}",
            fragment=answer[:200],
        ),
        confidence=Confidence.HIGH,
    )
    insights = list(snapshot.insights)
    insights.append(
        Insight(
            id=_uid("ins"),
            layer_id=answered.layer_id,
            kind="finding",
            title=f"Уточнение: {answered.question[:80]}",
            body=answer,
            sources=[fact.source],
            confidence=Confidence.HIGH,
            approval=ApprovalStatus.PENDING,
            owner_role=answered.to_role,
        )
    )
    updated = snapshot.model_copy(
        update={
            "questions": questions,
            "facts": [fact, *snapshot.facts],
            "insights": insights,
        }
    )
    return refresh_overview(updated)


def set_insight_approval(
    snapshot: PlatformSnapshot, insight_id: str, status: str
) -> PlatformSnapshot:
    insights = []
    found = False
    for insight in snapshot.insights:
        if insight.id == insight_id:
            found = True
            insights.append(
                insight.model_copy(update={"approval": ApprovalStatus(status)})
            )
        else:
            insights.append(insight)
    if not found:
        raise KeyError(f"Insight {insight_id} not found")
    return refresh_overview(snapshot.model_copy(update={"insights": insights}))


def as_is_summary(snapshot: PlatformSnapshot) -> dict:
    """AS-IS model projection from approved/pending findings only when can_infer."""
    inferable = {c.layer_id for c in snapshot.coverage if c.can_infer}
    findings = [
        i
        for i in snapshot.insights
        if i.kind == "finding" and i.layer_id in inferable
    ]
    return {
        "company": snapshot.overview.company_name,
        "layers_ready": [lid.value for lid in inferable],
        "findings": [i.model_dump() for i in findings],
        "facts_count": len(snapshot.facts),
        "rule": "Выводы только по слоям с покрытием ≥ порога; иначе — только вопросы.",
    }


def to_be_summary(snapshot: PlatformSnapshot) -> dict:
    proposals = [i for i in snapshot.insights if i.kind == "proposal"]
    admissible = [o for o in snapshot.opportunities if o.admissible]
    blocked = [o for o in snapshot.opportunities if not o.admissible]
    return {
        "target_pattern": "Агент-рекомендатель + HITL на деньги, договоры, доступы и ПДн",
        "proposals": [p.model_dump() for p in proposals],
        "admissible_opportunities": [o.model_dump() for o in admissible],
        "blocked_opportunities": [o.model_dump() for o in blocked],
        "approval_gate": "Неутверждённое остаётся гипотезой и не входит в единую модель.",
    }
