from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_active_user, require_permission
from app.modules.auth.exceptions import PermissionDeniedError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.consultants.schemas import (
    ConsultProfileStatusUpdateIn,
    ConsultRequestStatusUpdateIn,
    ConsultSpecialtyCreateIn,
    ConsultSpecialtyUpdateIn,
)
from app.modules.consultants.service import ConsultantService


router = APIRouter(
    prefix="/admin/consultants",
    tags=["Admin Consultants"],
)


def _permission_for_profile_status(status: str) -> str:
    if status == "approved":
        return "consultants.approve"
    if status == "rejected":
        return "consultants.reject"
    if status == "suspended":
        return "consultants.suspend"
    return "consultants.approve"


@router.get("/specialties")
def list_admin_consult_specialties(
    request: Request,
    active_only: bool = Query(default=False),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("consult_specialties.read")),
):
    service = ConsultantService(db)
    items = service.list_specialties(active_only=active_only, q=q)

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.post("/specialties")
def create_admin_consult_specialty(
    payload: ConsultSpecialtyCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("consult_specialties.create")),
):
    service = ConsultantService(db)
    result = service.create_specialty(payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consult specialty created",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/specialties/{specialty_id}")
def update_admin_consult_specialty(
    specialty_id: int,
    payload: ConsultSpecialtyUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("consult_specialties.update")),
):
    service = ConsultantService(db)
    result = service.update_specialty(specialty_id=specialty_id, payload=payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consult specialty updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests")
def list_admin_consult_requests(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    requester_user_id: int | None = Query(default=None, ge=1),
    consultant_profile_id: int | None = Query(default=None, ge=1),
    specialty_id: int | None = Query(default=None, ge=1),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("consult_requests.read")),
):
    service = ConsultantService(db)
    items, total = service.list_admin_requests(
        requester_user_id=requester_user_id,
        consultant_profile_id=consultant_profile_id,
        specialty_id=specialty_id,
        status=status,
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


@router.patch("/requests/{request_id}/status")
def update_admin_consult_request_status(
    request_id: int,
    payload: ConsultRequestStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consult_requests.manage")),
):
    service = ConsultantService(db)
    result = service.update_request_status_admin(
        request_id=request_id,
        admin_user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consult request status updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("")
def list_admin_consultants(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    specialty_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("consultants.read")),
):
    service = ConsultantService(db)
    items, total = service.list_admin_profiles(
        status=status,
        specialty_id=specialty_id,
        q=q,
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


@router.get("/{profile_id}")
def get_admin_consultant_detail(
    profile_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("consultants.read")),
):
    service = ConsultantService(db)
    result = service.get_admin_profile(profile_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{profile_id}/status")
def update_admin_consultant_status(
    profile_id: int,
    payload: ConsultProfileStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    required_permission = _permission_for_profile_status(payload.status)
    permissions = set(AuthRepository(db).get_user_permission_codes(current_user.id))

    if required_permission not in permissions:
        raise PermissionDeniedError()

    service = ConsultantService(db)
    result = service.update_profile_status_admin(
        profile_id=profile_id,
        admin_user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consultant profile status updated",
        meta={"trace_id": request.state.trace_id},
    )
