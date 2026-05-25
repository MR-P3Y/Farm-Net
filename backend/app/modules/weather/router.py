from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.weather.schemas import WeatherGpsLocationIn
from app.modules.weather.service import WeatherService


router = APIRouter(
    prefix="/weather",
    tags=["Weather"],
)


@router.get("/locations")
def list_weather_locations(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
    country_code: str | None = Query(default=None, min_length=2, max_length=2),
    location_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)

    items, total = service.list_locations(
        q=q,
        country_code=country_code,
        location_type=location_type,
        page=page,
        page_size=page_size,
    )

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.post("/locations/gps")
def create_gps_weather_location(
    payload: WeatherGpsLocationIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("weather.read")),
):
    service = WeatherService(db)

    result = service.create_gps_location(payload=payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Weather GPS location created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/current")
def get_current_weather(
    request: Request,
    location_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)

    result = service.current_weather(location_id=location_id)

    return success_response(
        data=result.model_dump(mode="json") if result else None,
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/forecast")
def get_weather_forecast(
    request: Request,
    location_id: int = Query(..., ge=1),
    forecast_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)

    items = service.forecast(
        location_id=location_id,
        forecast_type=forecast_type,
    )

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "total": len(items),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/alerts")
def get_weather_alerts(
    request: Request,
    location_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    service = WeatherService(db)

    items = service.active_alerts(location_id=location_id)

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "total": len(items),
            "trace_id": request.state.trace_id,
        },
    )


@router.post("/refresh")
def refresh_weather_location(
    request: Request,
    location_id: int = Query(..., ge=1),
    provider: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("weather.read")),
):
    service = WeatherService(db)

    snapshot, forecasts = service.refresh_location_weather(
        location_id=location_id,
        provider_override=provider,
    )

    return success_response(
        data={
            "snapshot": snapshot.model_dump(mode="json"),
            "forecasts": [item.model_dump(mode="json") for item in forecasts],
        },
        message="Weather refreshed",
        meta={
            "forecasts_count": len(forecasts),
            "trace_id": request.state.trace_id,
        },
    )
