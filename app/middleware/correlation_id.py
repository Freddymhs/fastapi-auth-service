from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import REQUEST_ID, generate_request_id

HEADER_NAME = "X-Request-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get(HEADER_NAME, generate_request_id())
        REQUEST_ID.set(request_id)
        response = await call_next(request)
        response.headers[HEADER_NAME] = request_id
        return response
