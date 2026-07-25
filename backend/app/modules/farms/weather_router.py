from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.farms.schemas import (
    FarmWeatherAlertListResponse,
    FarmWeatherContextResponse,
)
from app.modules.farms.weather_service import FarmWeatherService

router = APIRouter(prefix="/farms", tags=["Farm Weather"])


@router.get(
    "/{farm_id}/plots/{plot_id}/weather",
    response_model=FarmWeatherContextResponse,
)
def farm_weather_context(
    farm_id: int, plot_id: int, request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    result = FarmWeatherService(db).context(
        user=user, farm_id=farm_id, plot_id=plot_id
    )
    return _context_response(result, request)


@router.post(
    "/{farm_id}/plots/{plot_id}/weather/refresh",
    response_model=FarmWeatherContextResponse,
)
def refresh_farm_weather(
    farm_id: int, plot_id: int, request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmWeatherService(db).context(
        user=user, farm_id=farm_id, plot_id=plot_id, force=True
    )
    return _context_response(result, request)


@router.get(
    "/{farm_id}/plots/{plot_id}/weather/alerts",
    response_model=FarmWeatherAlertListResponse,
)
def farm_weather_alerts(
    farm_id: int, plot_id: int, request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items = FarmWeatherService(db).alerts(
        user=user, farm_id=farm_id, plot_id=plot_id
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items], message="OK",
        meta={"count": len(items), "trace_id": request.state.trace_id},
    )


def _context_response(result, request):
    return success_response(
        data=result.model_dump(mode="json"),
        message="Weather refreshed" if result.refreshed else "Weather cache is fresh",
        meta={"trace_id": request.state.trace_id},
    )
