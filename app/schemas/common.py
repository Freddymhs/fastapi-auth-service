from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class MetaResponse(BaseModel):
    timestamp: str
    path: str
    request_id: str = ""


class BaseResponse(BaseModel, Generic[T]):
    status_code: int = 200
    data: T
    meta: MetaResponse


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    status_code: int
    error: str
    message: str
    details: list[ErrorDetail] = []
    meta: MetaResponse


class PaginatedMeta(MetaResponse):
    total: int
    offset: int
    limit: int


class PaginatedResponse(BaseModel, Generic[T]):
    status_code: int = 200
    data: list[T]
    meta: PaginatedMeta


def paginated_meta(
    *, total: int, offset: int, limit: int, path: str, request_id: str = ""
) -> dict[str, Any]:
    from datetime import UTC, datetime

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "path": path,
        "request_id": request_id,
        "total": total,
        "offset": offset,
        "limit": limit,
    }
