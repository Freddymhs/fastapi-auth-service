import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainValidationError, NotFoundError
from app.core.guards import AuthError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


def _user_role_str(role: UserRole | str) -> str:
    return role.value if isinstance(role, UserRole) else role


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)
        self._session = session

    async def register(self, data: RegisterRequest) -> UserResponse:
        existing = await self._repo.get_by_email(data.email)
        if existing:
            raise DomainValidationError("Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=UserRole.USER,
        )
        created = await self._repo.create(user)
        return UserResponse(
            id=str(created.id),
            email=created.email,
            full_name=created.full_name,
            role=_user_role_str(created.role),
            is_active=created.is_active,
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._repo.get_by_email(data.email)
        if not user:
            raise AuthError("Invalid credentials")

        if not verify_password(data.password, user.hashed_password):
            raise AuthError("Invalid credentials")

        if not user.is_active:
            raise AuthError("Account is disabled")

        role = _user_role_str(user.role)
        access = create_access_token(str(user.id), extra={"role": role})
        refresh = create_refresh_token(str(user.id))

        return TokenResponse(access_token=access, refresh_token=refresh)

    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        try:
            payload = decode_token(data.refresh_token)
        except jwt.ExpiredSignatureError as err:
            raise AuthError("Refresh token expired") from err
        except jwt.InvalidTokenError as err:
            raise AuthError("Invalid refresh token") from err

        if payload.get("type") != "refresh":
            raise AuthError("Invalid token type")

        subject = payload.get("sub")
        if not subject:
            raise AuthError("Invalid token payload")

        user = await self._repo.get(subject)
        if not user:
            raise NotFoundError("User")

        if not user.is_active:
            raise AuthError("Account is disabled")

        role = _user_role_str(user.role)
        access = create_access_token(str(user.id), extra={"role": role})
        refresh = create_refresh_token(str(user.id))

        return TokenResponse(access_token=access, refresh_token=refresh)

    async def get_me(self, user_id: str) -> UserResponse:
        user = await self._repo.get(user_id)
        if not user:
            raise NotFoundError("User")

        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=_user_role_str(user.role),
            is_active=user.is_active,
        )
