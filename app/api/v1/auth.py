from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import public
from app.core.guards import AuthError, CurrentUser, get_current_user
from app.dependencies import get_db_session
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=201)
@public
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> UserResponse:
    service = AuthService(session)
    return await service.register(data)


@auth_router.post("/login", response_model=TokenResponse)
@public
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> TokenResponse:
    service = AuthService(session)
    return await service.login(data)


@auth_router.post("/refresh", response_model=TokenResponse)
@public
async def refresh(
    data: RefreshRequest,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> TokenResponse:
    service = AuthService(session)
    return await service.refresh(data)


@auth_router.get("/me", response_model=UserResponse)
async def me(
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
) -> UserResponse:
    if current_user is None:
        raise AuthError()
    from app.core.database import async_session_factory

    async with async_session_factory() as session, session.begin():
        service = AuthService(session)
        return await service.get_me(current_user.user_id)
