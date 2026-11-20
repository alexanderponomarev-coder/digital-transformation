from __future__ import annotations

from app.models.schemas import (
    AlternativeOutcome,
    ComparisonCase,
    ComparisonCaseResult,
    ComparisonRequest,
    ComparisonResponse,
)


def _rules_decision(case: ComparisonCase) -> AlternativeOutcome:
    """Classic automation in 1С-style: deterministic thresholds, no LLM."""
    if case.debt_ratio >= 0.85 or case.overdue_days >= 60:
        decision = "reject"
        reason = "Правило: высокий долг/просрочка → отказ"
    elif case.credit_score >= 75 and case.debt_ratio < 0.5:
        decision = "approve"
        reason = "Правило: score≥75 и долг<50% → авто-одобрение"
    else:
        decision = "escalate"
        reason = "Правило: серая зона → эскалация кредитному контролёру"
    return AlternativeOutcome(
        kind="rules_engine",
        decision=decision,
        requires_hitl=decision == "escalate",
        writes_to_erp=decision in {"approve", "reject"},
        latency_hours=0.1,
        rationale=reason,
    )


def _agent_decision(case: ComparisonCase) -> AlternativeOutcome:
    """Agent L3 + HITL: may recommend, never autonomous write on money."""
    if case.debt_ratio >= 0.85 or case.overdue_days >= 60:
        decision = "recommend_reject"
        reason = "Агент: риск высокий — рекомендация отказать, HITL обязателен"
    elif case.credit_score >= 75 and case.debt_ratio < 0.5:
        decision = "recommend_approve"
        reason = "Агент: профиль низкого риска — рекомендация одобрить, HITL"
    else:
        decision = "recommend_escalate"
        reason = "Агент: недостаточно сигнала — эскалация человеку"
    return AlternativeOutcome(
        kind="agent_hitl",
        decision=decision,
        requires_hitl=True,
        writes_to_erp=False,
        latency_hours=0.3,
        rationale=reason,
    )


def _as_is_outcome(case: ComparisonCase) -> AlternativeOutcome:
    return AlternativeOutcome(
        kind="as_is",
        decision="manual_review",
        requires_hitl=True,
        writes_to_erp=False,
        latency_hours=case.queue_hours_as_is if case.queue_hours_as_is is not None else 9.0,
        rationale="AS-IS: ручная очередь кредитного контроля",
    )


def _agree(rules: AlternativeOutcome, agent: AlternativeOutcome) -> bool:
    mapping = {
        "approve": "recommend_approve",
        "reject": "recommend_reject",
        "escalate": "recommend_escalate",
    }
    return mapping.get(rules.decision) == agent.decision


def compare_alternatives(req: ComparisonRequest) -> ComparisonResponse:
    results: list[ComparisonCaseResult] = []
    agree = 0
    for case in req.cases:
        as_is = _as_is_outcome(case)
        rules = _rules_decision(case)
        agent = _agent_decision(case)
        ok = _agree(rules, agent)
        if ok:
            agree += 1
        note = (
            "Согласованы recommendation vs правило"
            if ok
            else "Расхождение агента и правил — нужен разбор эталона"
        )
        if rules.writes_to_erp and not agent.writes_to_erp:
            note += "; агент не пишет в ERP без HITL (безопаснее на пилоте)"
        results.append(
            ComparisonCaseResult(
                case_id=case.id,
                as_is=as_is,
                rules_engine=rules,
                agent_hitl=agent,
                rules_agent_agree=ok,
                notes=note,
            )
        )
    n = len(results) or 1
    return ComparisonResponse(
        process_step_id=req.process_step_id,
        cases=results,
        agreement_rate=round(agree / n, 3),
        summary=(
            f"Сравнение на {len(results)} кейсах ({req.process_step_id}): "
            f"согласие правил и агента {agree}/{len(results)}. "
            "AS-IS остаётся ручным; агент не заменяет write правил без HITL."
        ),
    )


def default_otc_cases() -> list[ComparisonCase]:
    """Synthetic pack aligned with СеверПром OTC credit control."""
    return [
        ComparisonCase(
            id="c-low-risk",
            credit_score=82,
            debt_ratio=0.3,
            overdue_days=0,
            queue_hours_as_is=6.0,
        ),
        ComparisonCase(
            id="c-grey",
            credit_score=68,
            debt_ratio=0.55,
            overdue_days=5,
            queue_hours_as_is=11.0,
        ),
        ComparisonCase(
            id="c-high-risk",
            credit_score=40,
            debt_ratio=0.9,
            overdue_days=75,
            queue_hours_as_is=14.0,
        ),
    ]
