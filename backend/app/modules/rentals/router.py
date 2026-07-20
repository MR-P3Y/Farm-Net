from math import ceil
from datetime import datetime
from decimal import Decimal

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
    RentalRequestCancelIn,
    RentalRequestCreateIn,
    RentalRequestStatusIn,
)
from app.modules.rentals.service import RentalService
from app.modules.rentals.enums import RentalDiscoverySort


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
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    available_from: datetime | None = Query(default=None),
    available_to: datetime | None = Query(default=None),
    sort: RentalDiscoverySort | None = Query(default=None),
    db: Session = Depends(get_db),
):
    items, total = RentalService(db).list_public_equipment(
        category_id=category_id,
        province_id=province_id,
        city_id=city_id,
        operator_mode=operator_mode,
        q=q,
        min_price=min_price,
        max_price=max_price,
        available_from=available_from,
        available_to=available_to,
        sort=sort,
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


@router.post("/requests")
def create_rental_request(
    payload: RentalRequestCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_requests.create")),
):
    result = RentalService(db).create_request(user, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental request created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/me")
def list_my_rental_requests(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    equipment_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_requests.read_own")),
):
    items, total = RentalService(db).list_my_requests(
        user, status=status, equipment_id=equipment_id, page=page, page_size=page_size
    )
    return _page(items, total, page, page_size, request)


@router.get("/requests/me/{request_id}")
def get_my_rental_request(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_requests.read_own")),
):
    result = RentalService(db).get_my_request(user, request_id)
    return success_response(
        data=result.model_dump(mode="json"), message="OK", meta={"trace_id": request.state.trace_id}
    )


@router.post("/requests/me/{request_id}/cancel")
def cancel_my_rental_request(
    request_id: int,
    payload: RentalRequestCancelIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_requests.manage_own")),
):
    result = RentalService(db).cancel_my_request(user, request_id, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental request cancelled",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/assigned")
def list_assigned_rental_requests(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    equipment_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_requests.manage_assigned")),
):
    items, total = RentalService(db).list_assigned_requests(
        user, status=status, equipment_id=equipment_id, page=page, page_size=page_size
    )
    return _page(items, total, page, page_size, request)


@router.get("/requests/assigned/{request_id}")
def get_assigned_rental_request(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_requests.manage_assigned")),
):
    result = RentalService(db).get_assigned_request(user, request_id)
    return success_response(
        data=result.model_dump(mode="json"), message="OK", meta={"trace_id": request.state.trace_id}
    )


@router.patch("/requests/assigned/{request_id}/status")
def update_assigned_rental_request(
    request_id: int,
    payload: RentalRequestStatusIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_requests.manage_assigned")),
):
    result = RentalService(db).update_assigned_request(user, request_id, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Rental request status updated",
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
