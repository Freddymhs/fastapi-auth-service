import json
from datetime import UTC, datetime

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

SKIP_PATHS = {"/docs", "/redoc", "/openapi.json"}


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        if _should_skip(request.url.path, response):
            return response

        body = await _read_body(response)
        if not body:
            return response

        try:
            original = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return response

        wrapped = {
            "statusCode": response.status_code,
            "data": original,
            "meta": {
                "timestamp": datetime.now(UTC).isoformat(),
                "path": request.url.path,
            },
        }

        content = json.dumps(wrapped, ensure_ascii=False).encode()
        headers = dict(response.headers)
        headers["content-length"] = str(len(content))

        return Response(
            content=content,
            status_code=response.status_code,
            headers=headers,
            media_type="application/json",
        )


def _should_skip(path: str, response: Response) -> bool:
    if path in SKIP_PATHS:
        return True
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type:
        return True
    return response.status_code >= 400


async def _read_body(response: Response) -> bytes:
    body_parts: list[bytes] = []
    body_iterator = getattr(response, "body_iterator", None)
    if body_iterator is not None:
        async for chunk in body_iterator:
            body_parts.append(chunk if isinstance(chunk, bytes) else chunk.encode())
    elif hasattr(response, "body"):
        body_parts.append(response.body)
    return b"".join(body_parts)
