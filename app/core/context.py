import contextvars
import uuid

REQUEST_ID: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


def generate_request_id() -> str:
    return uuid.uuid4().hex[:12]
