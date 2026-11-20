from __future__ import annotations

from app.models.schemas import DocumentRecord, PlatformSnapshot


def user_can_read_document(doc: DocumentRecord, user_id: str) -> bool:
    """Empty acl_readers → visible to any authenticated/lab caller.
    Non-empty → owner or listed readers only.
    """
    readers = doc.acl_readers or []
    if not readers:
        return True
    if doc.owner_id and doc.owner_id == user_id:
        return True
    return user_id in readers


def visible_document_ids(snapshot: PlatformSnapshot, user_id: str) -> set[str]:
    return {
        d.id for d in snapshot.documents if user_can_read_document(d, user_id)
    }


def filter_snapshot_for_user(snapshot: PlatformSnapshot, user_id: str) -> PlatformSnapshot:
    """Hide documents and derivative facts/insights the user cannot read.
    Does not leak restricted titles via coverage document_ids (filtered).
    """
    allowed = visible_document_ids(snapshot, user_id)
    documents = [d for d in snapshot.documents if d.id in allowed]
    facts = [
        f
        for f in snapshot.facts
        if f.source.document_id in allowed
        or f.source.document_id.startswith("answer:")
    ]
    # Insights: keep only if every document source is allowed (answers ok)
    insights = []
    for insight in snapshot.insights:
        src_ids = [s.document_id for s in insight.sources]
        if not src_ids:
            insights.append(insight)
            continue
        if all(
            sid in allowed or sid.startswith("answer:") for sid in src_ids
        ):
            insights.append(insight)

    coverage = []
    for layer in snapshot.coverage:
        doc_ids = [i for i in layer.document_ids if i in allowed]
        coverage.append(layer.model_copy(update={"document_ids": doc_ids}))

    return snapshot.model_copy(
        update={
            "documents": documents,
            "facts": facts,
            "insights": insights,
            "coverage": coverage,
        }
    )


def set_document_acl(
    snapshot: PlatformSnapshot,
    document_id: str,
    *,
    owner_id: str | None = None,
    acl_readers: list[str] | None = None,
) -> PlatformSnapshot:
    docs = []
    found = False
    for doc in snapshot.documents:
        if doc.id == document_id:
            found = True
            updates: dict = {}
            if owner_id is not None:
                updates["owner_id"] = owner_id
            if acl_readers is not None:
                updates["acl_readers"] = acl_readers
            docs.append(doc.model_copy(update=updates))
        else:
            docs.append(doc)
    if not found:
        raise KeyError(f"Document {document_id} not found")
    return snapshot.model_copy(update={"documents": docs})
