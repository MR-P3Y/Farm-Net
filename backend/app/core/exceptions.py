from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.responses import error_response
from app.modules.auth.exceptions import AuthError


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def _trace_meta(request: Request) -> dict[str, str]:
    return {"trace_id": getattr(request.state, "trace_id", "")}


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            meta=_trace_meta(request),
        ),
    )


async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST

    if exc.code in {
        "AUTH_INVALID_CREDENTIALS",
        "AUTH_OTP_INVALID",
        "AUTH_OTP_EXPIRED",
        "AUTH_OTP_TOO_MANY_ATTEMPTS",
        "AUTH_TOKEN_INVALID",
        "AUTH_TOKEN_EXPIRED",
    }:
        status_code = status.HTTP_401_UNAUTHORIZED

    if exc.code in {
        "USER_SUSPENDED",
        "PERMISSION_DENIED",
    }:
        status_code = status.HTTP_403_FORBIDDEN

    if exc.code in {
        "AUTH_USER_NOT_FOUND",
    }:
        status_code = status.HTTP_404_NOT_FOUND

    if exc.code in {
        "AUTH_USER_ALREADY_EXISTS",
    }:
        status_code = status.HTTP_409_CONFLICT

    return JSONResponse(
        status_code=status_code,
        content=error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            meta=_trace_meta(request),
        ),
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code="HTTP_ERROR",
            message=str(exc.detail),
            meta=_trace_meta(request),
        ),
    )


def register_exception_handlers(app) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(AuthError, auth_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    fields = [
        {
            "field": ".".join(str(part) for part in error.get("loc", [])),
            "message": error.get("msg", "Invalid value"),
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content=error_response(
            code="VALIDATION_ERROR",
            message="Validation failed",
            details={"fields": fields},
            meta=_trace_meta(request),
        ),
    )
