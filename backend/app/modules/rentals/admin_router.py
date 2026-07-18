from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.rentals.schemas import (
    RentalCategoryCreateIn,
    RentalCategoryUpdateIn,
    LessorProfileStatusIn,
)
from app.modules.rentals.service import RentalService


router = APIRouter(prefix="/admin/rentals", tags=["Admin Equipment Rental"])


@router.get("/categories")
def list_categories(
    request: Request,
    active_only: bool = Query(default=False),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("rental_categories.admin_read")),
):
    items = RentalService(db).list_categories(active_only=active_only, q=q)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.post("/categories")
def create_category(
    payload: RentalCategoryCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("rental_categories.create")),
):
    result = RentalService(db).create_category(payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental category created",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/categories/{category_id}")
def update_category(
    category_id: int,
    payload: RentalCategoryUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("rental_categories.update")),
):
    result = RentalService(db).update_category(category_id, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental category updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/lessor-profiles")
def list_lessor_profiles(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    province_id: int | None = Query(default=None, ge=1),
    city_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("rental_lessors.admin_read")),
):
    items, total = RentalService(db).list_admin_profiles(
        status=status, province_id=province_id, city_id=city_id, q=q, page=page, page_size=page_size
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


@router.patch("/lessor-profiles/{profile_id}/status")
def moderate_lessor_profile(
    profile_id: int,
    payload: LessorProfileStatusIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_lessors.admin_moderate")),
):
    result = RentalService(db).moderate_profile(
        profile_id, status=payload.status, admin_note=payload.admin_note, admin_user=user
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="Lessor profile status updated",
        meta={"trace_id": request.state.trace_id},
    )
