from math import ceil
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.rentals.schemas import (
    LessorProfileInput,
    RentalAvailabilityBlockIn,
    RentalEquipmentInput,
    RentalPricingRuleIn,
)
from app.modules.rentals.service import RentalService


router = APIRouter(prefix="/rentals", tags=["Equipment Rental"])


def _page(data, total: int, page: int, page_size: int, request: Request):
    return success_response(
        data=[item.model_dump(mode="json") for item in data],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/categories")
def list_rental_categories(
    request: Request, q: str | None = Query(default=None), db: Session = Depends(get_db)
):
    items = RentalService(db).list_categories(active_only=True, q=q)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.get("/equipment")
def list_public_equipment(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: int | None = Query(default=None, ge=1),
    province_id: int | None = Query(default=None, ge=1),
    city_id: int | None = Query(default=None, ge=1),
    operator_mode: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    items, total = RentalService(db).list_public_equipment(
        category_id=category_id,
        province_id=province_id,
        city_id=city_id,
        operator_mode=operator_mode,
        q=q,
        page=page,
        page_size=page_size,
    )
    return _page(items, total, page, page_size, request)


@router.get("/equipment/{equipment_id}")
def get_public_equipment(equipment_id: int, request: Request, db: Session = Depends(get_db)):
    result = RentalService(db).get_public_equipment(equipment_id)
    return success_response(
        data=result.model_dump(mode="json"), message="OK", meta={"trace_id": request.state.trace_id}
    )


@router.get("/equipment/{equipment_id}/pricing")
def get_public_pricing(equipment_id: int, request: Request, db: Session = Depends(get_db)):
    items = RentalService(db).get_public_pricing(equipment_id)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.get("/equipment/{equipment_id}/availability")
def check_public_availability(
    equipment_id: int,
    starts_at: datetime,
    ends_at: datetime,
    request: Request,
    db: Session = Depends(get_db),
):
    result = RentalService(db).check_public_availability(equipment_id, starts_at, ends_at)
    return success_response(
        data=result.model_dump(mode="json"), message="OK", meta={"trace_id": request.state.trace_id}
    )


@router.get("/me/equipment")
def list_my_equipment(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    category_id: int | None = Query(default=None, ge=1),
    operator_mode: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.read")),
):
    items, total = RentalService(db).list_my_equipment(
        user,
        status=status,
        category_id=category_id,
        operator_mode=operator_mode,
        q=q,
        page=page,
        page_size=page_size,
    )
    return _page(items, total, page, page_size, request)


@router.post("/me/equipment")
def create_my_equipment(
    payload: RentalEquipmentInput,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.create")),
):
    result = RentalService(db).create_my_equipment(user, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental equipment created",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/me/equipment/{equipment_id}")
def update_my_equipment(
    equipment_id: int,
    payload: RentalEquipmentInput,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.update")),
):
    result = RentalService(db).update_my_equipment(user, equipment_id, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental equipment updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/me/equipment/{equipment_id}/submit")
def submit_my_equipment(
    equipment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.submit")),
):
    result = RentalService(db).submit_my_equipment(user, equipment_id)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental equipment submitted",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me/equipment/{equipment_id}/pricing")
def list_my_pricing(
    equipment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.manage_pricing")),
):
    items = RentalService(db).list_my_pricing(user, equipment_id)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.put("/me/equipment/{equipment_id}/pricing")
def replace_my_pricing(
    equipment_id: int,
    payload: list[RentalPricingRuleIn],
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.manage_pricing")),
):
    items = RentalService(db).replace_my_pricing(user, equipment_id, payload)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="Rental pricing updated",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.get("/me/equipment/{equipment_id}/availability")
def list_my_availability(
    equipment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.manage_availability")),
):
    items = RentalService(db).list_my_availability(user, equipment_id)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.post("/me/equipment/{equipment_id}/availability")
def create_my_availability(
    equipment_id: int,
    payload: RentalAvailabilityBlockIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.manage_availability")),
):
    result = RentalService(db).create_my_availability(user, equipment_id, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental availability block created",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/me/equipment/{equipment_id}/availability/{block_id}")
def update_my_availability(
    equipment_id: int,
    block_id: int,
    payload: RentalAvailabilityBlockIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.manage_availability")),
):
    result = RentalService(db).update_my_availability(user, equipment_id, block_id, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental availability block updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/me/equipment/{equipment_id}/availability/{block_id}")
def delete_my_availability(
    equipment_id: int,
    block_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_equipment.manage_availability")),
):
    RentalService(db).delete_my_availability(user, equipment_id, block_id)
    return success_response(
        data=None,
        message="Rental availability block deleted",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me/lessor-profile")
def get_my_lessor_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_lessors.profile_manage")),
):
    result = RentalService(db).get_my_profile(user)
    return success_response(
        data=result.model_dump(mode="json") if result else None,
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/me/lessor-profile")
def save_my_lessor_profile(
    payload: LessorProfileInput,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_lessors.profile_manage")),
):
    result = RentalService(db).save_my_profile(user, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Lessor profile saved",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/me/lessor-profile/submit")
def submit_my_lessor_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_lessors.profile_manage")),
):
    result = RentalService(db).submit_my_profile(user)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Lessor profile submitted",
        meta={"trace_id": request.state.trace_id},
    )
