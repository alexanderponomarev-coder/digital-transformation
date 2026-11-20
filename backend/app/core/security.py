from __future__ import annotations

import secrets
from dataclasses import dataclass

from fastapi import Header, HTTPException, status

from app.core.settings import settings


@dataclass(frozen=True)
class AuthContext:
    """Authenticated caller. user_id used for ACL; empty token mode → open lab."""

    user_id: str
    authenticated: bool


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def parse_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


async def get_auth_context(
    authorization: str | None = Header(default=None),
    x_stratum_user: str | None = Header(default=None, alias="X-Stratum-User"),
) -> AuthContext:
    """Require Bearer when STRATUM_API_TOKEN is set; always resolve user for ACL."""
    expected = (settings.api_token or "").strip()
    user_id = (x_stratum_user or "").strip() or "anonymous"

    if not expected:
        # Open lab (local/dev). Still honor X-Stratum-User for ACL tests.
        return AuthContext(user_id=user_id, authenticated=False)

    provided = parse_bearer(authorization)
    if not provided or not secrets.compare_digest(provided, expected):
        raise _unauthorized("Требуется Authorization: Bearer <STRATUM_API_TOKEN>")

    if user_id == "anonymous":
        # Authenticated but no user header → shared operator identity
        user_id = "operator"
    return AuthContext(user_id=user_id, authenticated=True)


def assert_reset_allowed(auth: AuthContext) -> None:
    if settings.disable_reset:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="POST /api/reset отключён (STRATUM_DISABLE_RESET=1)",
        )
    if settings.api_token.strip() and not auth.authenticated:
        raise _unauthorized("reset требует Bearer-токен")
