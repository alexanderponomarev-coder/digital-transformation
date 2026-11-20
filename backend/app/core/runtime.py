"""Runtime stand metadata (lab vs demo, in-memory persistence)."""

from __future__ import annotations

from app.core.settings import STORAGE_DISCLAIMER, settings
from app.models.schemas import PlatformSnapshot, ProjectOverview


def annotate_overview(overview: ProjectOverview) -> ProjectOverview:
    return overview.model_copy(
        update={
            "deploy_mode": settings.deploy_mode,
            "persistence": "in_memory",
            "storage_disclaimer": STORAGE_DISCLAIMER,
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
        "deploy_mode": settings.deploy_mode,
        "persistence": "in_memory",
        "auth_enabled": settings.auth_enabled,
        "reset_disabled": settings.disable_reset,
        "disclaimer": STORAGE_DISCLAIMER,
    }
