from typing import Any


def success_response(
    data: Any = None,
    message: str = "OK",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": True,
        "data": data if data is not None else {},
        "message": message,
        "meta": meta or {},
    }


def error_response(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "meta": meta or {},
    }
