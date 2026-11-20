from __future__ import annotations

from collections import defaultdict

from app.models.schemas import (
    KpiDelta,
    RoiBenefitLine,
    RoiComputeRequest,
    RoiModel,
)


def _find_overlaps(lines: list[RoiBenefitLine]) -> dict[str, list[str]]:
    by_step: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        if line.hours_per_year or line.cash_benefit:
            by_step[line.process_step_id].append(line.id)
    return {step: ids for step, ids in by_step.items() if len(ids) > 1}


def compute_roi(req: RoiComputeRequest) -> RoiModel:
    """Audit-aligned ROI. Publishes monetary_roi only with confirmed positive cost base
    and monetized benefits without unresolved double-count (unless allow_overlap).
    """
    overlaps = _find_overlaps(req.benefits)
    overlapping_steps = sorted(overlaps.keys())

    resolved: list[RoiBenefitLine] = []
    for line in req.benefits:
        if (
            not req.allow_overlap
            and line.process_step_id in overlaps
            and line.hours_per_year
        ):
            # Keep first line per step; exclude later hour-based duplicates
            peers = overlaps[line.process_step_id]
            if peers and line.id != peers[0]:
                resolved.append(
                    line.model_copy(
                        update={
                            "included": False,
                            "excluded_reason": (
                                f"Пересечение с {peers[0]} на шаге "
                                f"{line.process_step_id}: часы не суммируются без "
                                "доказательства независимости (allow_overlap=true)."
                            ),
                        }
                    )
                )
                continue
        resolved.append(line.model_copy(update={"included": True, "excluded_reason": None}))

    hours_total = 0.0
    cash_from_hours = 0.0
    cash_direct = 0.0
    rates_missing = False
    for line in resolved:
        if not line.included:
            continue
        if line.hours_per_year:
            hours_total += line.hours_per_year
            if line.hourly_rate is None:
                rates_missing = True
            else:
                cash_from_hours += line.hours_per_year * line.hourly_rate
        if line.cash_benefit:
            cash_direct += line.cash_benefit

    annual_benefit = cash_from_hours + cash_direct
    missing: list[str] = []
    investment = req.investment

    if investment is None or investment <= 0:
        missing.append("investment (положительная база затрат)")
    if hours_total > 0 and rates_missing and annual_benefit <= 0:
        missing.append("hourly_rate для монетизации часов")
    if not req.benefits:
        missing.append("benefits (хотя бы одна линия эффекта)")
    if overlapping_steps and not req.allow_overlap:
        # not a missing input — structural; already excluded duplicates
        pass

    assumptions = [
        f"Валюта: {req.currency}",
        f"Горизонт: {req.horizon_months} мес",
        "Денежный ROI публикуется только при kind=calculated",
    ]
    if overlapping_steps:
        assumptions.append(
            "Обнаружены пересечения process_step_id — дубли часов исключены "
            f"({', '.join(overlapping_steps)})"
        )

    # Hours only: have hours, no full monetization and/or no investment
    if hours_total > 0 and (
        investment is None or investment <= 0 or (rates_missing and cash_direct <= 0)
    ):
        return RoiModel(
            investment_mln=(investment or 0) / 1_000_000,
            annual_benefit_mln=0.0,
            payback_months=0,
            tco_3y_mln=0.0,
            kpis=[],
            assumptions=assumptions,
            kind="hours_only",
            currency=req.currency,
            horizon_months=req.horizon_months,
            monetary_roi=None,
            hours_saved_per_year=hours_total,
            benefit_lines=resolved,
            overlapping_steps=overlapping_steps,
            missing_inputs=missing,
            disclaimer=(
                "Показан эффект в часах. Доказательный денежный ROI не публикуется: "
                "не хватает ставки и/или базы затрат."
            ),
        )

    if missing or annual_benefit <= 0:
        return RoiModel(
            investment_mln=(investment or 0) / 1_000_000,
            annual_benefit_mln=0.0,
            payback_months=0,
            tco_3y_mln=0.0,
            kpis=[],
            assumptions=assumptions,
            kind="insufficient_inputs",
            currency=req.currency,
            horizon_months=req.horizon_months,
            monetary_roi=None,
            hours_saved_per_year=hours_total or None,
            benefit_lines=resolved,
            overlapping_steps=overlapping_steps,
            missing_inputs=missing or ["монетизируемые выгоды"],
            disclaimer="Доказательный ROI не рассчитывается — укажите недостающие входы.",
        )

    assert investment is not None and investment > 0
    horizon_years = max(req.horizon_months, 1) / 12.0
    # Scale annual benefit to horizon for ROI on same period as costs if needed;
    # audit formula uses same horizon — treat investment as full period cost base.
    benefits = annual_benefit * horizon_years
    costs = investment
    monetary_roi = (benefits - costs) / costs
    payback = (
        int(round((investment / annual_benefit) * 12)) if annual_benefit > 0 else 0
    )

    return RoiModel(
        investment_mln=investment / 1_000_000,
        annual_benefit_mln=annual_benefit / 1_000_000,
        payback_months=payback,
        tco_3y_mln=(investment * 3 / horizon_years) / 1_000_000 if horizon_years else 0,
        kpis=[
            KpiDelta(
                name="Часы / год (включённые)",
                as_is="—",
                to_be=f"{hours_total:.0f}" if hours_total else "—",
            )
        ],
        assumptions=assumptions,
        kind="calculated",
        currency=req.currency,
        horizon_months=req.horizon_months,
        monetary_roi=round(monetary_roi, 4),
        hours_saved_per_year=hours_total or None,
        benefit_lines=resolved,
        overlapping_steps=overlapping_steps,
        missing_inputs=[],
        disclaimer="Расчёт по введённым входам. Прогноз ≠ достигнутый эффект пилота.",
    )
