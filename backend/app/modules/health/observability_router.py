from fastapi import APIRouter, Request, Response
from fastapi.responses import Response as RawResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.observability import READINESS
from app.core.responses import success_response
from app.db.session import SessionLocal
from app.modules.health.service import get_health_status


router = APIRouter(tags=["Observability"], include_in_schema=False)


@router.get("/live")
def liveness(request: Request):
    return success_response(
        data={"app": "ok"},
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/ready")
def readiness(request: Request, response: Response):
    db = SessionLocal()
    try:
        status = get_health_status(db)
    finally:
        db.close()
    for dependency in ("database", "redis"):
        READINESS.labels(dependency=dependency).set(
            1 if status[dependency] == "ok" else 0
        )
    ready = all(status[item] == "ok" for item in ("database", "redis"))
    response.status_code = 200 if ready else 503
    return success_response(
        data={**status, "ready": ready},
        message="OK" if ready else "Service unavailable",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/metrics")
def metrics() -> RawResponse:
    return RawResponse(
        content=generate_latest(),
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )
