from typing import Any
from uuid import UUID

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.decorators import PUBLIC_ROUTE_KEY
from app.core.exceptions import DomainError
from app.core.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


class AuthError(DomainError):
    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__("AUTH_ERROR", message, 401)


class ForbiddenError(DomainError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__("FORBIDDEN", message, 403)


class CurrentUser:
    def __init__(self, user_id: str, role: str) -> None:
        self.user_id = user_id
        self.role = role

    @property
    def uuid(self) -> UUID:
        return UUID(self.user_id)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),  # noqa: B008
) -> CurrentUser | None:
    endpoint = request.scope.get("endpoint")
    if endpoint and getattr(endpoint, PUBLIC_ROUTE_KEY, False):
        return None

    if credentials is None:
        raise AuthError()

    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError as err:
        raise AuthError("Token expired") from err
    except jwt.InvalidTokenError as err:
        raise AuthError("Invalid token") from err

    if payload.get("type") != "access":
        raise AuthError("Invalid token type")

    subject = payload.get("sub")
    if not subject:
        raise AuthError("Invalid token payload")

    return CurrentUser(
        user_id=subject,
        role=payload.get("role", "user"),
    )


def require_roles(*allowed_roles: str) -> Any:
    async def guard(
        current_user: CurrentUser | None = Depends(get_current_user),  # noqa: B008
    ) -> CurrentUser:
        if current_user is None:
            raise AuthError()
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                f"Role '{current_user.role}' not in {list(allowed_roles)}"
            )
        return current_user

    return Depends(guard)
