from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.api.v1.router import v1_router
from app.config import settings
from app.core.context import REQUEST_ID
from app.core.exceptions import (
    DomainError,
    domain_error_handler,
    validation_exception_handler,
)
from app.core.http_client import close_http_client, get_http_client
from app.core.logging import setup_logging
from app.core.rate_limit import limiter
from app.dependencies import get_db_session
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.response_wrapper import ResponseWrapperMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    await get_http_client()
    yield
    await close_http_client()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ResponseWrapperMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(DomainError, domain_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.include_router(v1_router)


@app.get("/health")
async def health_check() -> dict[str, object]:
    db_status = "disconnected"
    try:
        async for session in get_db_session():
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "db": db_status,
        "timestamp": datetime.now(UTC).isoformat(),
        "requestId": REQUEST_ID.get(""),
    }
