from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_active_user, require_permission
from app.modules.auth.exceptions import PermissionDeniedError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.services.schemas import (
    ServiceCategoryCreateIn,
    ServiceCategoryUpdateIn,
    ServiceProviderProfileStatusUpdateIn,
)
from app.modules.services.service import ServicesService


router = APIRouter(
    prefix="/admin/services",
    tags=["Admin Services"],
)


def _permission_for_provider_status(status: str) -> str:
    if status == "approved":
        return "service_providers.approve"
    if status == "rejected":
        return "service_providers.reject"
    if status == "suspended":
        return "service_providers.suspend"
    return "service_providers.approve"


@router.get("/categories")
def list_admin_service_categories(
    request: Request,
    active_only: bool = Query(default=False),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("service_categories.admin_read")),
):
    service = ServicesService(db)
    items = service.list_categories(active_only=active_only, q=q)

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.post("/categories")
def create_admin_service_category(
    payload: ServiceCategoryCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("service_categories.create")),
):
    service = ServicesService(db)
    result = service.create_category(payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service category created",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/categories/{category_id}")
def update_admin_service_category(
    category_id: int,
    payload: ServiceCategoryUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("service_categories.update")),
):
    service = ServicesService(db)
    result = service.update_category(category_id=category_id, payload=payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service category updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/provider-profiles")
def list_admin_service_provider_profiles(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    category_id: int | None = Query(default=None, ge=1),
    province_id: int | None = Query(default=None, ge=1),
    city_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("service_providers.admin_read")),
):
    service = ServicesService(db)
    items, total = service.list_admin_provider_profiles(
        status=status,
        category_id=category_id,
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


@router.get("/provider-profiles/{profile_id}")
def get_admin_service_provider_profile_detail(
    profile_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("service_providers.admin_read")),
):
    service = ServicesService(db)
    result = service.get_admin_provider_profile(profile_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/provider-profiles/{profile_id}/status")
def update_admin_service_provider_profile_status(
    profile_id: int,
    payload: ServiceProviderProfileStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    required_permission = _permission_for_provider_status(payload.status)
    permissions = set(AuthRepository(db).get_user_permission_codes(current_user.id))

    if required_permission not in permissions:
        raise PermissionDeniedError()

    service = ServicesService(db)
    result = service.update_provider_profile_status_admin(
        profile_id=profile_id,
        admin_user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service provider profile status updated",
        meta={"trace_id": request.state.trace_id},
    )
