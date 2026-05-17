from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.stores.enums import StoreType
from app.modules.stores.models import Store
from app.modules.stores.repository import StoreRepository
from app.modules.stores.schemas import PublicStoreOut


router = APIRouter(
    prefix="/public/stores",
    tags=["Public Stores"],
)


@router.get("")
def list_public_stores(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
    province_id: int | None = Query(default=None, ge=1),
    county_id: int | None = Query(default=None, ge=1),
    city_id: int | None = Query(default=None, ge=1),
    store_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if store_type is not None:
        _validate_store_type(store_type)

    repo = StoreRepository(db)

    items, total = repo.list_public_stores(
        q=q.strip() if q else None,
        province_id=province_id,
        county_id=county_id,
        city_id=city_id,
        store_type=store_type,
        page=page,
        page_size=page_size,
    )

    return success_response(
        data=[_public_store_out(item).model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/{slug}")
def get_public_store_by_slug(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    repo = StoreRepository(db)

    store = repo.get_public_store_by_slug(slug=slug)

    if store is None:
        raise ValidationAuthError(
            message="Store not found",
            details={"slug": slug},
        )

    return success_response(
        data=_public_store_out(store).model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


def _validate_store_type(store_type: str) -> None:
    allowed = {item.value for item in StoreType}

    if store_type not in allowed:
        raise ValidationAuthError(
            message="Invalid store_type",
            details={"allowed": sorted(allowed)},
        )


def _public_store_out(store: Store) -> PublicStoreOut:
    return PublicStoreOut(
        id=store.id,
        owner_user_id=store.owner_user_id,
        name=store.name,
        slug=store.slug,
        description=store.description,
        store_type=store.store_type,
        phone=store.phone,
        email=store.email,
        province_id=store.province_id,
        county_id=store.county_id,
        district_id=store.district_id,
        city_id=store.city_id,
        village_id=store.village_id,
        address=store.address,
        postal_code=store.postal_code,
        latitude=str(store.latitude) if store.latitude is not None else None,
        longitude=str(store.longitude) if store.longitude is not None else None,
        logo_file_id=store.logo_file_id,
        banner_file_id=store.banner_file_id,
        created_at=store.created_at.isoformat(),
        updated_at=store.updated_at.isoformat(),
    )
