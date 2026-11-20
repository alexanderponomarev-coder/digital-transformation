from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app import __version__
from app.core.security import AuthContext, assert_reset_allowed, get_auth_context
from app.models.schemas import (
    AnswerQuestionRequest,
    ApprovalRequest,
    ClassifyResult,
    ConfirmVersionRequest,
    DocumentAclRequest,
    DocumentUploadRequest,
    Opportunity,
    PlatformSnapshot,
    ProjectOverview,
)
from app.services import engine
from app.services.acl import filter_snapshot_for_user, set_document_acl, user_can_read_document
from app.services.regulatory import is_admissible, screen_opportunity
from app.services.store import store

router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Public liveness — no auth (load balancers / smoke)."""
    return {"status": "ok", "version": __version__, "product": "STRATUM"}


@router.get("/snapshot", response_model=PlatformSnapshot)
def get_snapshot(auth: AuthContext = Depends(get_auth_context)) -> PlatformSnapshot:
    return filter_snapshot_for_user(store.get(), auth.user_id)


@router.get("/overview", response_model=ProjectOverview)
def get_overview(auth: AuthContext = Depends(get_auth_context)) -> ProjectOverview:
    return filter_snapshot_for_user(store.get(), auth.user_id).overview


@router.post("/documents/upload", response_model=ClassifyResult)
def upload_document(
    payload: DocumentUploadRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> ClassifyResult:
    holder: dict[str, ClassifyResult] = {}

    def mutator(snap: PlatformSnapshot) -> PlatformSnapshot:
        updated, result = engine.ingest_document(
            snap,
            title=payload.title,
            format_value=payload.format.value,
            summary=payload.summary,
            content_hint=payload.content_hint,
            owner_id=auth.user_id,
            acl_readers=payload.acl_readers,
            read_error=payload.read_error,
            read_error_detail=payload.read_error_detail,
        )
        holder["result"] = result
        return updated

    store.mutate(mutator)
    return holder["result"]


@router.post("/documents/{document_id}/confirm-version", response_model=PlatformSnapshot)
def confirm_version(
    document_id: str,
    payload: ConfirmVersionRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> PlatformSnapshot:
    """Confirm active regulation version among conflicts (TC-03)."""
    _ = payload

    def mutator(snap: PlatformSnapshot) -> PlatformSnapshot:
        doc = next((d for d in snap.documents if d.id == document_id), None)
        if doc is None:
            raise KeyError(f"Document {document_id} not found")
        if doc.owner_id and doc.owner_id != auth.user_id:
            # Seed docs have no owner — any authenticated/lab user may confirm
            raise PermissionError("Только владелец может подтвердить версию")
        return engine.confirm_document_version(snap, document_id)

    try:
        updated = store.mutate(mutator)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return filter_snapshot_for_user(updated, auth.user_id)


@router.patch("/documents/{document_id}/acl", response_model=PlatformSnapshot)
def patch_document_acl(
    document_id: str,
    payload: DocumentAclRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> PlatformSnapshot:
    """Update ACL. Only current owner (or open lab without owner) may change."""

    def mutator(snap: PlatformSnapshot) -> PlatformSnapshot:
        doc = next((d for d in snap.documents if d.id == document_id), None)
        if doc is None:
            raise KeyError(f"Document {document_id} not found")
        if doc.owner_id and doc.owner_id != auth.user_id:
            raise PermissionError("Только владелец документа может менять ACL")
        owner = payload.owner_id if payload.owner_id is not None else doc.owner_id
        return set_document_acl(
            snap,
            document_id,
            owner_id=owner,
            acl_readers=payload.acl_readers,
        )

    try:
        updated = store.mutate(mutator)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return filter_snapshot_for_user(updated, auth.user_id)


@router.post("/questions/{question_id}/answer", response_model=PlatformSnapshot)
def answer_question(
    question_id: str,
    payload: AnswerQuestionRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> PlatformSnapshot:
    try:
        updated = store.mutate(
            lambda snap: engine.answer_question(snap, question_id, payload.answer)
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return filter_snapshot_for_user(updated, auth.user_id)


@router.post("/insights/{insight_id}/approval", response_model=PlatformSnapshot)
def approve_insight(
    insight_id: str,
    payload: ApprovalRequest,
    auth: AuthContext = Depends(get_auth_context),
) -> PlatformSnapshot:
    try:
        updated = store.mutate(
            lambda snap: engine.set_insight_approval(snap, insight_id, payload.status)
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return filter_snapshot_for_user(updated, auth.user_id)


@router.get("/model/as-is")
def get_as_is(auth: AuthContext = Depends(get_auth_context)) -> dict:
    return engine.as_is_summary(filter_snapshot_for_user(store.get(), auth.user_id))


@router.get("/model/to-be")
def get_to_be(auth: AuthContext = Depends(get_auth_context)) -> dict:
    return engine.to_be_summary(filter_snapshot_for_user(store.get(), auth.user_id))


@router.post("/regulatory/screen")
def screen(
    payload: Opportunity,
    auth: AuthContext = Depends(get_auth_context),
) -> dict:
    _ = auth
    checks = screen_opportunity(payload)
    return {
        "admissible": is_admissible(checks),
        "checks": [c.model_dump() for c in checks],
        "opportunity": payload.model_dump(),
    }


@router.get("/documents/{document_id}")
def get_document(
    document_id: str,
    auth: AuthContext = Depends(get_auth_context),
) -> dict:
    snap = store.get()
    doc = next((d for d in snap.documents if d.id == document_id), None)
    if doc is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    if not user_can_read_document(doc, auth.user_id):
        raise HTTPException(status_code=404, detail="Документ не найден")
    facts = [f.model_dump() for f in snap.facts if f.source.document_id == document_id]
    return {"document": doc.model_dump(), "facts": facts}


@router.post("/reset", response_model=PlatformSnapshot)
def reset(auth: AuthContext = Depends(get_auth_context)) -> PlatformSnapshot:
    assert_reset_allowed(auth)
    return store.reset()
