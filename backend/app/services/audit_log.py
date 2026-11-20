from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from app.models.schemas import AuditEvent

_MAX = 500
_lock = Lock()
_events: deque[AuditEvent] = deque(maxlen=_MAX)


def clear() -> None:
    with _lock:
        _events.clear()


def record(
    *,
    actor: str,
    action: str,
    resource: str = "",
    tools_invoked: list[str] | None = None,
    allowed: bool = True,
    detail: str = "",
) -> AuditEvent:
    event = AuditEvent(
        id=f"run-{uuid4().hex[:10]}",
        ts=datetime.now(timezone.utc).isoformat(),
        actor=actor,
        action=action,
        resource=resource,
        tools_invoked=list(tools_invoked or []),
        allowed=allowed,
        detail=detail,
    )
    with _lock:
        _events.appendleft(event)
    return event


def list_events(limit: int = 100) -> list[AuditEvent]:
    with _lock:
        return list(_events)[: max(1, min(limit, _MAX))]
