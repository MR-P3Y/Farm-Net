from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.common.utils.trace import generate_trace_id


TRACE_HEADER = "X-Trace-Id"


async def trace_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    trace_id = request.headers.get(TRACE_HEADER) or generate_trace_id()
    request.state.trace_id = trace_id

    response = await call_next(request)
    response.headers[TRACE_HEADER] = trace_id
    return response