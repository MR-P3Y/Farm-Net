from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.weather.schemas import WeatherProviderConfigUpdateIn
from app.modules.weather.service import WeatherService


router = APIRouter(
    prefix="/admin/weather",
    tags=["Admin Weather"],
)


@router.get("/provider-configs")
def list_weather_provider_configs(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("weather.admin_read")),
):
    service = WeatherService(db)

    items = service.list_provider_configs()

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "total": len(items),
            "trace_id": request.state.trace_id,
        },
    )


@router.patch("/provider-configs/{config_id}")
def update_weather_provider_config(
    config_id: int,
    payload: WeatherProviderConfigUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("weather.provider_manage")),
):
    service = WeatherService(db)

    result = service.update_provider_config(
        config_id=config_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Weather provider config updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/locations")
def list_admin_weather_locations(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
    country_code: str | None = Query(default=None, min_length=2, max_length=2),
    location_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("weather.admin_read")),
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


@router.get("/locations/{location_id}")
def get_admin_weather_location(
    location_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("weather.admin_read")),
):
    service = WeatherService(db)

    result = service.get_location_admin(location_id=location_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/locations/{location_id}/cache-status")
def get_admin_weather_cache_status(
    location_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("weather.admin_read")),
):
    service = WeatherService(db)

    location = service.get_location_admin(location_id=location_id)

    current_stale = service.is_current_weather_stale(location_id=location.id)
    forecast_stale = service.is_forecast_stale(location_id=location.id)

    return success_response(
        data={
            "location_id": location.id,
            "current_stale": current_stale,
            "forecast_stale": forecast_stale,
            "weather_stale": current_stale or forecast_stale,
            "current_ttl_minutes": service.CURRENT_WEATHER_TTL_MINUTES,
            "forecast_ttl_minutes": service.FORECAST_TTL_MINUTES,
        },
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/refresh")
def refresh_admin_weather_location(
    request: Request,
    location_id: int = Query(..., ge=1),
    provider: str | None = Query(default=None),
    force: bool = Query(default=True),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("weather.admin_manage")),
):
    service = WeatherService(db)

    snapshot, forecasts, refreshed = service.refresh_location_weather_if_stale(
        location_id=location_id,
        provider_override=provider,
        force=force,
    )

    return success_response(
        data={
            "snapshot": snapshot.model_dump(mode="json") if snapshot else None,
            "forecasts": [item.model_dump(mode="json") for item in forecasts],
        },
        message="Weather refreshed" if refreshed else "Weather cache is fresh",
        meta={
            "refreshed": refreshed,
            "force": force,
            "forecasts_count": len(forecasts),
            "trace_id": request.state.trace_id,
        },
    )
