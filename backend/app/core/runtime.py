"""Runtime stand metadata (lab vs demo, in-memory persistence)."""

from __future__ import annotations

from app.core.settings import STORAGE_DISCLAIMER, settings
from app.models.schemas import PlatformSnapshot, ProjectOverview


def annotate_overview(overview: ProjectOverview) -> ProjectOverview:
    demo_bit = ""
    if overview.is_demo:
        demo_bit = (overview.demo_label or "Демо-версия · синтетические данные") + " "
    return overview.model_copy(
        update={
            "deploy_mode": settings.deploy_mode,
            "persistence": "in_memory",
            "storage_disclaimer": f"{demo_bit}{STORAGE_DISCLAIMER}",
            "is_demo": True if overview.is_demo else overview.is_demo,
            "demo_label": overview.demo_label
            or ("Демо-версия · синтетические данные" if overview.is_demo else ""),
        }
    )


def annotate_snapshot(snapshot: PlatformSnapshot) -> PlatformSnapshot:
    return snapshot.model_copy(
        update={"overview": annotate_overview(snapshot.overview)}
    )


def health_payload(*, version: str) -> dict:
    return {
        "status": "ok",
        "version": version,
        "product": "STRATUM",
        "edition": "demo",
        "demo": True,
        "demo_label": "Демо-версия · синтетические данные СеверПром",
        "deploy_mode": settings.deploy_mode,
        "persistence": "in_memory",
        "auth_enabled": settings.auth_enabled,
        "reset_disabled": settings.disable_reset,
        "disclaimer": STORAGE_DISCLAIMER,
    }
