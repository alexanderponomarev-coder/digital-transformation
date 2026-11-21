"""Оценка зрелости: правило минимума по аспектам и областям + режим работы."""

from __future__ import annotations

from app.core.maturity_matrix import DOMAINS, build_matrix
from app.models.schemas import (
    MaturityAspectId,
    MaturityAssessment,
    MaturityDomainId,
    MaturityDomainResult,
    MaturityMatrix,
    MaturityScore,
)

_DOMAIN_TITLES = {d.id: d.title for d in DOMAINS}


def _score_map(scores: list[MaturityScore]) -> dict[tuple[MaturityDomainId, MaturityAspectId], int]:
    return {(s.domain_id, s.aspect_id): int(s.level) for s in scores}


def compute_assessment(
    scores: list[MaturityScore],
    *,
    notes: str = "",
) -> MaturityAssessment:
    smap = _score_map(scores)
    domain_results: list[MaturityDomainResult] = []
    for domain in DOMAINS:
        aspect_levels: dict[str, int] = {}
        for aspect in MaturityAspectId:
            aspect_levels[aspect.value] = smap.get((domain.id, aspect), 1)
        domain_level = min(aspect_levels.values())
        weakest = min(aspect_levels.items(), key=lambda kv: (kv[1], kv[0]))[0]
        domain_results.append(
            MaturityDomainResult(
                domain_id=domain.id,
                title=_DOMAIN_TITLES[domain.id],
                scores=aspect_levels,
                domain_level=domain_level,
                weakest_aspect=MaturityAspectId(weakest),
            )
        )

    system_level = min((d.domain_level for d in domain_results), default=1)
    gov = next(d for d in domain_results if d.domain_id == MaturityDomainId.GOVERNANCE)
    infra = next(d for d in domain_results if d.domain_id == MaturityDomainId.INFRASTRUCTURE)
    gov_rules = gov.scores.get("rules", 1)

    # Operating mode from readiness profile (methodology p.3)
    if system_level <= 2 and gov.domain_level <= 2:
        mode, label, nxt = (
            0,
            "Ниже режима 1",
            "До режима 1 — «Управляемая инфраструктура»: утвердить мандат CDO, "
            "назначить владельцев данных и процессов, определить процедуру допуска входящих данных.",
        )
    elif infra.domain_level >= 3 and gov_rules <= 1:
        mode, label, nxt = (
            1,
            "Режим 1 — «Управляемая инфраструктура»",
            "До режима 2 — «Делегированное управление»: проработать онтологию C3, "
            "испытать SHACL в пилоте, устранить пробел в применении правил.",
        )
    elif system_level >= 3:
        mode, label, nxt = (
            2,
            "Режим 2 — «Делегированное управление»",
            "К режиму 3 — «Операционная подотчётность»: сквозной допуск, PROV-O на каждое действие, "
            "независимая проверка с отчётностью перед советом.",
        )
    elif infra.domain_level >= 3 and gov.domain_level <= 2:
        mode, label, nxt = (
            1,
            "Режим 1 — «Управляемая инфраструктура»",
            "Закрыть пробел в управлении (особенно применение правил), затем режим 2.",
        )
    else:
        mode, label, nxt = (
            0,
            "Ниже режима 1 / переходный профиль",
            "Подтянуть самый слабый аспект каждой области; предельный режим задаёт управление.",
        )

    weak_bits = [
        f"{d.title}: {d.domain_level} (слабее — {d.weakest_aspect.value})"
        for d in domain_results
    ]
    profile = (
        f"Уровень системы (min областей) = {system_level}. "
        + "; ".join(weak_bits)
        + ". Правило: оценка области = min(технология, ответственность, применение правил)."
    )

    # normalize scores list (all 12)
    normalized: list[MaturityScore] = []
    for domain in DOMAINS:
        for aspect in MaturityAspectId:
            normalized.append(
                MaturityScore(
                    domain_id=domain.id,
                    aspect_id=aspect,
                    level=smap.get((domain.id, aspect), 1),
                )
            )

    return MaturityAssessment(
        scores=normalized,
        domain_results=domain_results,
        system_level=system_level,
        max_operating_mode=mode,
        mode_label=label,
        next_step=nxt,
        profile_summary=profile,
        notes=notes,
    )


def seed_severprom_maturity() -> MaturityAssessment:
    """Типичный профиль: инфраструктура сильнее, управление/правила отстают."""
    raw = [
        (MaturityDomainId.INFRASTRUCTURE, MaturityAspectId.TECHNOLOGY, 3),
        (MaturityDomainId.INFRASTRUCTURE, MaturityAspectId.ACCOUNTABILITY, 3),
        (MaturityDomainId.INFRASTRUCTURE, MaturityAspectId.RULES, 2),
        (MaturityDomainId.GOVERNANCE, MaturityAspectId.TECHNOLOGY, 2),
        (MaturityDomainId.GOVERNANCE, MaturityAspectId.ACCOUNTABILITY, 2),
        (MaturityDomainId.GOVERNANCE, MaturityAspectId.RULES, 1),
        (MaturityDomainId.AGENTS, MaturityAspectId.TECHNOLOGY, 2),
        (MaturityDomainId.AGENTS, MaturityAspectId.ACCOUNTABILITY, 2),
        (MaturityDomainId.AGENTS, MaturityAspectId.RULES, 1),
        (MaturityDomainId.ORGANIZATION, MaturityAspectId.TECHNOLOGY, 2),
        (MaturityDomainId.ORGANIZATION, MaturityAspectId.ACCOUNTABILITY, 2),
        (MaturityDomainId.ORGANIZATION, MaturityAspectId.RULES, 2),
    ]
    scores = [
        MaturityScore(domain_id=d, aspect_id=a, level=lv) for d, a, lv in raw
    ]
    return compute_assessment(
        scores,
        notes=(
            "Иллюстрация seed «СеверПром»: инфраструктура 3/3/2, управление с отставанием "
            "применения правил (1). Не доказательная оценка заказчика."
        ),
    )


def get_matrix() -> MaturityMatrix:
    return build_matrix()


def apply_score_updates(
    current: MaturityAssessment,
    updates: list[MaturityScore],
) -> MaturityAssessment:
    smap = _score_map(current.scores)
    for u in updates:
        smap[(u.domain_id, u.aspect_id)] = int(u.level)
    scores = [
        MaturityScore(
            domain_id=domain.id,
            aspect_id=aspect,
            level=smap.get((domain.id, aspect), 1),
        )
        for domain in DOMAINS
        for aspect in MaturityAspectId
    ]
    return compute_assessment(scores, notes=current.notes)
