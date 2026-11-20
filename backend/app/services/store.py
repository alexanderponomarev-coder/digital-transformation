from __future__ import annotations

from threading import Lock
from typing import Callable

from app.core.runtime import annotate_snapshot
from app.data.seed import build_snapshot
from app.models.schemas import PlatformSnapshot


class PlatformStore:
    """In-memory project store (MVP). Thread-safe for local lab/demo use."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._snapshot: PlatformSnapshot = build_snapshot()

    def get(self) -> PlatformSnapshot:
        with self._lock:
            return annotate_snapshot(self._snapshot.model_copy(deep=True))

    def set(self, snapshot: PlatformSnapshot) -> PlatformSnapshot:
        with self._lock:
            self._snapshot = snapshot.model_copy(deep=True)
            return annotate_snapshot(self._snapshot.model_copy(deep=True))

    def mutate(
        self, mutator: Callable[[PlatformSnapshot], PlatformSnapshot]
    ) -> PlatformSnapshot:
        with self._lock:
            working = self._snapshot.model_copy(deep=True)
            updated = mutator(working)
            self._snapshot = updated.model_copy(deep=True)
            return annotate_snapshot(self._snapshot.model_copy(deep=True))

    def reset(self) -> PlatformSnapshot:
        from app.services import audit_log

        with self._lock:
            self._snapshot = build_snapshot()
            audit_log.clear()
            return annotate_snapshot(self._snapshot.model_copy(deep=True))


store = PlatformStore()
