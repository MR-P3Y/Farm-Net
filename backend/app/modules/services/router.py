from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.services.schemas import (
    ServiceOfferCreateIn,
    ServiceOfferUpdateIn,
    ServiceProviderProfileCreateIn,
    ServiceProviderProfileUpdateIn,
    ServiceRequestCancelIn,
    ServiceRequestCreateIn,
    ServiceRequestAssignedDetailResponse,
    ServiceRequestAssignedListResponse,
    ServiceRequestDetailResponse,
    ServiceRequestListResponse,
    ServiceRequestStatusUpdateIn,
)
from app.modules.services.service import ServicesService
from app.modules.finance.schemas import FinalPriceDecisionIn, FinalPriceProposalIn


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


@router.get("/offers")
def list_public_service_offers(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: int | None = Query(default=None, ge=1),
    provider_profile_id: int | None = Query(default=None, ge=1),
    pricing_type: str | None = Query(default=None),
    province_id: int | None = Query(default=None, ge=1),
    city_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = ServicesService(db)
    items, total = service.list_public_offers(
        category_id=category_id,
        provider_profile_id=provider_profile_id,
        pricing_type=pricing_type,
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


@router.get("/offers/{offer_id}")
def get_public_service_offer_detail(
    offer_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    service = ServicesService(db)
    result = service.get_public_offer(offer_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
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


@router.get("/me/offers")
def list_my_service_offers(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    category_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_offers.read")),
):
    service = ServicesService(db)
    items, total = service.list_my_offers(
        user=current_user,
        status=status,
        category_id=category_id,
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


@router.post("/me/offers")
def create_my_service_offer(
    payload: ServiceOfferCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_offers.create")),
):
    service = ServicesService(db)
    result = service.create_my_offer(user=current_user, payload=payload)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service offer created",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/me/offers/{offer_id}")
def update_my_service_offer(
    offer_id: int,
    payload: ServiceOfferUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_offers.update")),
):
    service = ServicesService(db)
    result = service.update_my_offer(
        user=current_user,
        offer_id=offer_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service offer updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/me/offers/{offer_id}/submit")
def submit_my_service_offer(
    offer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_offers.submit")),
):
    service = ServicesService(db)
    result = service.submit_my_offer(user=current_user, offer_id=offer_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Service offer submitted",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/requests", response_model=ServiceRequestDetailResponse)
def create_service_request(
    payload: ServiceRequestCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_requests.create")),
):
    result = ServicesService(db).create_service_request(user=current_user, payload=payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Service request created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/me", response_model=ServiceRequestListResponse)
def list_my_service_requests(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    offer_id: int | None = Query(default=None, ge=1),
    category_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_requests.read_own")),
):
    items, total = ServicesService(db).list_my_service_requests(
        user=current_user,
        status=status,
        offer_id=offer_id,
        category_id=category_id,
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


@router.get("/requests/assigned", response_model=ServiceRequestAssignedListResponse)
def list_assigned_service_requests(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    offer_id: int | None = Query(default=None, ge=1),
    category_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(
        require_permission("service_requests.manage_assigned")
    ),
):
    items, total = ServicesService(db).list_assigned_service_requests(
        user=current_user,
        status=status,
        offer_id=offer_id,
        category_id=category_id,
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


@router.get(
    "/requests/assigned/{request_id}",
    response_model=ServiceRequestAssignedDetailResponse,
)
def get_assigned_service_request_detail(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(
        require_permission("service_requests.manage_assigned")
    ),
):
    result = ServicesService(db).get_assigned_service_request_detail(
        request_id=request_id,
        user=current_user,
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch(
    "/requests/{request_id}/status",
    response_model=ServiceRequestAssignedDetailResponse,
)
def update_assigned_service_request_status(
    request_id: int,
    payload: ServiceRequestStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(
        require_permission("service_requests.manage_assigned")
    ),
):
    result = ServicesService(db).update_assigned_service_request_status(
        request_id=request_id,
        user=current_user,
        payload=payload,
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="Service request status updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/requests/assigned/{request_id}/final-price")
def propose_assigned_service_request_final_price(
    request_id: int,
    payload: FinalPriceProposalIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_requests.manage_assigned")),
):
    result = ServicesService(db).propose_request_final_price(
        request_id=request_id, user=current_user, payload=payload
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="Final price proposed",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/assigned/{request_id}/final-price")
def get_assigned_service_request_final_price(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_requests.manage_assigned")),
):
    result = ServicesService(db).get_request_final_price(
        request_id=request_id, user=current_user, assigned=True
    )
    return success_response(
        data=result.model_dump(mode="json") if result else None,
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/{request_id}/final-price")
def get_own_service_request_final_price(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_requests.read_own")),
):
    result = ServicesService(db).get_request_final_price(
        request_id=request_id, user=current_user, assigned=False
    )
    return success_response(
        data=result.model_dump(mode="json") if result else None,
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/requests/{request_id}/final-price")
def decide_own_service_request_final_price(
    request_id: int,
    payload: FinalPriceDecisionIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_requests.manage_own")),
):
    result = ServicesService(db).decide_request_final_price(
        request_id=request_id, user=current_user, payload=payload
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="Final price decision recorded",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch(
    "/requests/{request_id}/cancel",
    response_model=ServiceRequestDetailResponse,
)
def cancel_my_service_request(
    request_id: int,
    payload: ServiceRequestCancelIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_requests.manage_own")),
):
    result = ServicesService(db).cancel_my_service_request(
        request_id=request_id,
        user=current_user,
        payload=payload,
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="Service request cancelled",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/{request_id}", response_model=ServiceRequestDetailResponse)
def get_my_service_request_detail(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("service_requests.read_own")),
):
    result = ServicesService(db).get_my_service_request_detail(
        request_id=request_id,
        user=current_user,
    )
    return success_response(
        data=result.model_dump(mode="json"),
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
