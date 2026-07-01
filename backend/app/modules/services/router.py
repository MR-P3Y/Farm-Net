from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.services.schemas import (
    ServiceProviderProfileCreateIn,
    ServiceProviderProfileUpdateIn,
)
from app.modules.services.service import ServicesService


router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.get("/categories")
def list_service_categories(
    request: Request,
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = ServicesService(db)
    items = service.list_categories(active_only=True, q=q)

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.get("/me/provider-profile")
def get_my_service_provider_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_providers.profile_manage")),
):
    service = ServicesService(db)
    result = service.get_my_provider_profile(user=current_user)

    return success_response(
        data=result.model_dump(mode="json") if result else None,
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/me/provider-profile")
def create_my_service_provider_profile(
    payload: ServiceProviderProfileCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_providers.profile_manage")),
):
    service = ServicesService(db)
    result = service.create_or_update_my_provider_profile(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service provider profile saved",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/me/provider-profile")
def update_my_service_provider_profile(
    payload: ServiceProviderProfileUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_providers.profile_manage")),
):
    service = ServicesService(db)
    result = service.create_or_update_my_provider_profile(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service provider profile saved",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/me/provider-profile/submit")
def submit_my_service_provider_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_providers.profile_manage")),
):
    service = ServicesService(db)
    result = service.submit_my_provider_profile(user=current_user)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service provider profile submitted",
        meta={"trace_id": request.state.trace_id},
    )
