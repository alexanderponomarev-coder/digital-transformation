from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import __version__
from app.models.schemas import (
    AnswerQuestionRequest,
    ApprovalRequest,
    ClassifyResult,
    DocumentUploadRequest,
    Opportunity,
    PlatformSnapshot,
    ProjectOverview,
)
from app.services import engine
from app.services.regulatory import is_admissible, screen_opportunity
from app.services.store import store

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__, "product": "STRATUM"}


@router.get("/snapshot", response_model=PlatformSnapshot)
def get_snapshot() -> PlatformSnapshot:
    return store.get()


@router.get("/overview", response_model=ProjectOverview)
def get_overview() -> ProjectOverview:
    return store.get().overview


@router.post("/documents/upload", response_model=ClassifyResult)
def upload_document(payload: DocumentUploadRequest) -> ClassifyResult:
    holder: dict[str, ClassifyResult] = {}

    def mutator(snap: PlatformSnapshot) -> PlatformSnapshot:
        updated, result = engine.ingest_document(
            snap,
            title=payload.title,
            format_value=payload.format.value,
            summary=payload.summary,
            content_hint=payload.content_hint,
        )
        holder["result"] = result
        return updated

    store.mutate(mutator)
    return holder["result"]


@router.post("/questions/{question_id}/answer", response_model=PlatformSnapshot)
def answer_question(question_id: str, payload: AnswerQuestionRequest) -> PlatformSnapshot:
    try:
        return store.mutate(
            lambda snap: engine.answer_question(snap, question_id, payload.answer)
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/insights/{insight_id}/approval", response_model=PlatformSnapshot)
def approve_insight(insight_id: str, payload: ApprovalRequest) -> PlatformSnapshot:
    try:
        return store.mutate(
            lambda snap: engine.set_insight_approval(snap, insight_id, payload.status)
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/model/as-is")
def get_as_is() -> dict:
    return engine.as_is_summary(store.get())


@router.get("/model/to-be")
def get_to_be() -> dict:
    return engine.to_be_summary(store.get())


@router.post("/regulatory/screen")
def screen(payload: Opportunity) -> dict:
    checks = screen_opportunity(payload)
    return {
        "admissible": is_admissible(checks),
        "checks": [c.model_dump() for c in checks],
        "opportunity": payload.model_dump(),
    }


@router.post("/reset", response_model=PlatformSnapshot)
def reset() -> PlatformSnapshot:
    return store.reset()
