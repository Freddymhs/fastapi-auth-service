from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.context import REQUEST_ID


def _build_error_response(
    status_code: int,
    error_code: str,
    message: str,
    path: str,
    details: list[dict[str, str]] | None = None,
) -> JSONResponse:
    from datetime import UTC, datetime

    body: dict[str, Any] = {
        "statusCode": status_code,
        "error": error_code,
        "message": message,
        "meta": {
            "timestamp": datetime.now(UTC).isoformat(),
            "path": path,
            "requestId": REQUEST_ID.get(""),
        },
    }
    if details:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


class DomainError(Exception):
    def __init__(
        self,
        code: str = "DOMAIN_ERROR",
        message: str = "An error occurred",
        http_status: int = 500,
    ) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(self.message)


class NotFoundError(DomainError):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__("NOT_FOUND", f"{resource} not found", 404)


class ScrapingError(DomainError):
    def __init__(self, message: str = "Scraping failed") -> None:
        super().__init__("SCRAPING_ERROR", message, 502)


class ExternalAPIError(DomainError):
    def __init__(self, message: str = "External API error") -> None:
        super().__init__("EXTERNAL_API_ERROR", message, 502)


class DomainValidationError(DomainError):
    def __init__(self, message: str = "Validation error") -> None:
        super().__init__("VALIDATION_ERROR", message, 400)


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return _build_error_response(
        status_code=exc.http_status,
        error_code=exc.code,
        message=exc.message,
        path=request.url.path,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "field": " -> ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return _build_error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Validation failed",
        path=request.url.path,
        details=details,
    )
