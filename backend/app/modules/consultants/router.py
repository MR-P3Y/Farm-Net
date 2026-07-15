from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.consultants.schemas import (
    ConsultProfileCreateIn,
    ConsultProfileUpdateIn,
    ConsultRequestCreateIn,
    ConsultRequestStatusUpdateIn,
)
from app.modules.consultants.service import ConsultantService


router = APIRouter(
    prefix="/consultants",
    tags=["Consultants"],
)


@router.get("/specialties")
def list_consult_specialties(
    request: Request,
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = ConsultantService(db)
    items = service.list_specialties(active_only=True, q=q)

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.get("")
def list_consultants(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    specialty_id: int | None = Query(default=None, ge=1),
    province_id: int | None = Query(default=None, ge=1),
    city_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = ConsultantService(db)
    items, total = service.list_public_profiles(
        specialty_id=specialty_id,
        province_id=province_id,
        city_id=city_id,
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


@router.get("/me/profile")
def get_my_consultant_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consultants.profile_manage")),
):
    service = ConsultantService(db)
    result = service.get_my_profile(user=current_user)

    return success_response(
        data=result.model_dump(mode="json") if result else None,
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/me/profile")
def upsert_my_consultant_profile(
    payload: ConsultProfileUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consultants.profile_manage")),
):
    service = ConsultantService(db)
    result = service.create_or_update_my_profile(user=current_user, payload=payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consultant profile saved",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/me/profile")
def create_my_consultant_profile(
    payload: ConsultProfileCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consultants.profile_manage")),
):
    service = ConsultantService(db)
    result = service.create_or_update_my_profile(user=current_user, payload=payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consultant profile saved",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/me/profile/submit")
def submit_my_consultant_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consultants.profile_manage")),
):
    service = ConsultantService(db)
    result = service.submit_my_profile(user=current_user)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consultant profile submitted",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/requests")
def create_consult_request(
    payload: ConsultRequestCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consult_requests.create")),
):
    service = ConsultantService(db)
    result = service.create_request(user=current_user, payload=payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consult request created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/me")
def list_my_consult_requests(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consult_requests.read_own")),
):
    service = ConsultantService(db)
    items, total = service.list_my_requests(
        user=current_user,
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


@router.patch("/requests/{request_id}/cancel")
def cancel_my_consult_request(
    request_id: int,
    payload: ConsultRequestStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consult_requests.manage_own")),
):
    service = ConsultantService(db)
    result = service.cancel_my_request(
        request_id=request_id,
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consult request cancelled",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/assigned")
def list_my_assigned_consult_requests(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consult_requests.manage_assigned")),
):
    service = ConsultantService(db)
    items, total = service.list_my_consultant_requests(
        user=current_user,
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


@router.get("/requests/assigned/{request_id}")
def get_my_assigned_consult_request_detail(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consult_requests.manage_assigned")),
):
    service = ConsultantService(db)
    result = service.get_my_assigned_request_detail(
        request_id=request_id,
        user=current_user,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/{request_id}")
def get_my_consult_request_detail(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consult_requests.read_own")),
):
    service = ConsultantService(db)
    result = service.get_my_request_detail(
        request_id=request_id,
        user=current_user,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/requests/{request_id}/status")
def update_assigned_consult_request_status(
    request_id: int,
    payload: ConsultRequestStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("consult_requests.manage_assigned")),
):
    service = ConsultantService(db)
    result = service.update_consultant_request_status(
        request_id=request_id,
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Consult request status updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/{profile_id}")
def get_consultant_detail(
    profile_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    service = ConsultantService(db)
    result = service.get_public_profile(profile_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )
