from __future__ import annotations

from app.models.schemas import Opportunity, RegulatoryCheck


SENSITIVE_MARKERS = ("пдн", "персональн", "гостайн", "деньг", "договор", "доступ", "лимит")


def screen_opportunity(opportunity: Opportunity) -> list[RegulatoryCheck]:
    """Admissibility filter for agentic use-cases against RF regulatory baseline."""
    checks: list[RegulatoryCheck] = []
    text = f"{opportunity.title} {opportunity.process} {' '.join(opportunity.regulatory_flags)}".lower()

    if opportunity.autonomy_level >= 5 and any(m in text for m in ("деньг", "лимит", "договор")):
        checks.append(
            RegulatoryCheck(
                id="dyn-hitl-money",
                title="HITL для денежных write-действий",
                basis="Политика платформы / риск-аппетит",
                status="block",
                detail="Автономия уровня 5 на денежных операциях недопустима без HITL.",
            )
        )

    if "пдн" in text or "персональн" in text:
        checks.append(
            RegulatoryCheck(
                id="dyn-pdn",
                title="ПДн и облачные ИИ",
                basis="152-ФЗ, запрет передачи чувствительных данных в облачные ИИ",
                status="warn",
                detail="Требуется on-prem / доверенный контур; облачные LLM на ПДн запрещены.",
            )
        )

    if opportunity.autonomy_level >= 4 and "hitl" not in text:
        checks.append(
            RegulatoryCheck(
                id="dyn-hitl-high",
                title="Высокая автономия без HITL",
                basis="NIST AI RMF / внутренняя матрица",
                status="warn",
                detail="Для уровней 4–5 явно зафиксируйте режим надзора.",
            )
        )

    if not checks:
        checks.append(
            RegulatoryCheck(
                id="dyn-ok",
                title="Предварительный скрининг пройден",
                basis="Встроенный регуляторный фильтр MVP",
                status="pass",
                detail="Критических блокировок не обнаружено; финальное утверждение — за человеком.",
            )
        )
    return checks


def is_admissible(checks: list[RegulatoryCheck]) -> bool:
    return not any(c.status == "block" for c in checks)
