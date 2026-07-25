from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.common.utils.trace import generate_trace_id
from app.core.observability import RequestObservation


TRACE_HEADER = "X-Trace-Id"


async def trace_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    candidate = request.headers.get(TRACE_HEADER, "")
    trace_id = candidate if _valid_trace_id(candidate) else generate_trace_id()
    request.state.trace_id = trace_id
    observation = RequestObservation(request)
    try:
        response = await call_next(request)
    except Exception:
        observation.fail(trace_id=trace_id)
        raise
    observation.finish(status_code=response.status_code, trace_id=trace_id)
    response.headers[TRACE_HEADER] = trace_id
    return response


def _valid_trace_id(value: str) -> bool:
    return bool(value) and len(value) <= 100 and all(
        character.isalnum() or character in "-_." for character in value
    )
