from decimal import Decimal
from math import ceil

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.geo.geocoding import GeocodingGateway, get_geocoding_gateway
from app.modules.geo.schemas import GeoPlaceReverseResponse, GeoPlaceSearchResponse
from app.modules.geo.service import GeoLocationSearchService, GeoService


router = APIRouter(
    prefix="/geo",
    tags=["Geo"],
)


@router.get("/search", response_model=GeoPlaceSearchResponse)
def search_places(
    request: Request,
    response: Response,
    q: str = Query(min_length=2, max_length=120),
    language: str = Query(default="fa", pattern="^(fa|en)$"),
    limit: int = Query(default=5, ge=1, le=5),
    db: Session = Depends(get_db),
    gateway: GeocodingGateway = Depends(get_geocoding_gateway),
    _user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    items, cached = GeoLocationSearchService(db, gateway=gateway).search(
        query=q,
        language=language,
        limit=limit,
    )
    response.headers["Cache-Control"] = "no-store"
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "count": len(items),
            "cached": cached,
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/reverse", response_model=GeoPlaceReverseResponse)
def reverse_place(
    request: Request,
    response: Response,
    latitude: Decimal = Query(ge=-90, le=90, decimal_places=7),
    longitude: Decimal = Query(ge=-180, le=180, decimal_places=7),
    language: str = Query(default="fa", pattern="^(fa|en)$"),
    db: Session = Depends(get_db),
    gateway: GeocodingGateway = Depends(get_geocoding_gateway),
    _user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    item, cached = GeoLocationSearchService(db, gateway=gateway).reverse(
        latitude=latitude,
        longitude=longitude,
        language=language,
    )
    response.headers["Cache-Control"] = "no-store"
    return success_response(
        data=item.model_dump(mode="json"),
        message="OK",
        meta={"cached": cached, "trace_id": request.state.trace_id},
    )


@router.get("/provinces")
def list_provinces(
    request: Request,
    db: Session = Depends(get_db),
):
    service = GeoService(db)
    result = service.list_provinces()

    return success_response(
        data=[item.model_dump() for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/counties")
def list_counties(
    request: Request,
    province_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    service = GeoService(db)
    result = service.list_counties(province_id=province_id)

    return success_response(
        data=[item.model_dump() for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/districts")
def list_districts(
    request: Request,
    province_id: int | None = Query(default=None, ge=1),
    county_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    service = GeoService(db)
    result = service.list_districts(
        province_id=province_id,
        county_id=county_id,
    )

    return success_response(
        data=[item.model_dump() for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/rural-districts")
def list_rural_districts(
    request: Request,
    province_id: int | None = Query(default=None, ge=1),
    county_id: int | None = Query(default=None, ge=1),
    district_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    service = GeoService(db)
    result = service.list_rural_districts(
        province_id=province_id,
        county_id=county_id,
        district_id=district_id,
    )

    return success_response(
        data=[item.model_dump() for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/cities")
def list_cities(
    request: Request,
    province_id: int | None = Query(default=None, ge=1),
    county_id: int | None = Query(default=None, ge=1),
    district_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    service = GeoService(db)
    result = service.list_cities(
        province_id=province_id,
        county_id=county_id,
        district_id=district_id,
        q=q,
    )

    return success_response(
        data=[item.model_dump() for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/villages")
def list_villages(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    province_id: int | None = Query(default=None, ge=1),
    county_id: int | None = Query(default=None, ge=1),
    district_id: int | None = Query(default=None, ge=1),
    rural_district_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    service = GeoService(db)
    items, total = service.list_villages(
        page=page,
        page_size=page_size,
        province_id=province_id,
        county_id=county_id,
        district_id=district_id,
        rural_district_id=rural_district_id,
        q=q,
    )

    return success_response(
        data=[item.model_dump() for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )
