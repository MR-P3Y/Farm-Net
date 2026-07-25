from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.subscriptions.schemas import (
    EntitlementListResponse,
    OwnSubscriptionResponse,
    PlanDetailResponse,
    PlanListResponse,
    UsageListResponse,
    QuotaEstimateIn,
    QuotaEstimateResponse,
    SubscriptionCancelIn,
    SubscriptionCheckoutIn,
    SubscriptionCheckoutResponse,
    SubscriptionPaymentVerifyIn,
    SubscriptionResumeIn,
)
from app.modules.subscriptions.commerce_service import SubscriptionCommerceService
from app.modules.subscriptions.lifecycle_service import SubscriptionLifecycleService
from app.modules.subscriptions.quota_service import QuotaService
from app.modules.subscriptions.service import SubscriptionReadService


router = APIRouter(prefix="/billing", tags=["Billing Plans and Subscriptions"])


@router.get("/plans", response_model=PlanListResponse)
def list_plans(request: Request, db: Session = Depends(get_db)):
    items = SubscriptionReadService(db).plans()
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.get("/plans/{plan_code}", response_model=PlanDetailResponse)
def plan_detail(plan_code: str, request: Request, db: Session = Depends(get_db)):
    item = SubscriptionReadService(db).plan(plan_code)
    return success_response(
        data=item.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/subscription/me", response_model=OwnSubscriptionResponse)
def own_subscription(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.subscription.read_own")),
):
    item = SubscriptionReadService(db).own_subscription(user.id)
    return success_response(
        data=None if item is None else item.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/entitlements/me", response_model=EntitlementListResponse)
def own_entitlements(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.entitlements.read")),
):
    items = SubscriptionReadService(db).own_entitlements(user.id)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.get("/usage/me", response_model=UsageListResponse)
def own_usage(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.usage.read_own")),
):
    items = SubscriptionReadService(db).own_usage(user.id)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.post("/usage/estimate", response_model=QuotaEstimateResponse)
def estimate_usage(
    payload: QuotaEstimateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.usage.read_own")),
):
    item = QuotaService(db).estimate(user.id, payload.feature_code, payload.amount)
    return success_response(
        data=item.model_dump(mode="json"),
        message="Quota estimate calculated",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/subscription/free", response_model=OwnSubscriptionResponse)
def activate_free_subscription(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.subscription.manage_own")),
):
    item = SubscriptionLifecycleService(db).activate_free(user.id)
    return success_response(
        data=item.model_dump(mode="json"),
        message="Free subscription active",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/subscription/cancel", response_model=OwnSubscriptionResponse)
def cancel_subscription(
    payload: SubscriptionCancelIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.subscription.manage_own")),
):
    item = SubscriptionLifecycleService(db).cancel(
        user_id=user.id,
        expected_version=payload.expected_version,
        cancel_at_period_end=payload.cancel_at_period_end,
        reason=payload.reason,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Subscription cancellation updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/subscription/resume", response_model=OwnSubscriptionResponse)
def resume_subscription(
    payload: SubscriptionResumeIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.subscription.manage_own")),
):
    item = SubscriptionLifecycleService(db).resume(
        user_id=user.id,
        expected_version=payload.expected_version,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Subscription cancellation removed",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/checkout", response_model=SubscriptionCheckoutResponse)
def checkout_subscription(
    payload: SubscriptionCheckoutIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.subscription.manage_own")),
):
    item = SubscriptionCommerceService(db).checkout(
        user_id=user.id,
        plan_code=payload.plan_code,
        provider=payload.provider,
        idempotency_key=payload.idempotency_key,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Subscription checkout created",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/payments/verify", response_model=SubscriptionCheckoutResponse)
def verify_subscription_payment(
    payload: SubscriptionPaymentVerifyIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("billing.subscription.manage_own")),
):
    item = SubscriptionCommerceService(db).verify(
        user_id=user.id,
        attempt_id=payload.payment_attempt_id,
        provider_token=payload.provider_token,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Subscription payment verified",
        meta={"trace_id": request.state.trace_id},
    )


@router.get(
    "/payments/callback/zarinpal",
    response_model=SubscriptionCheckoutResponse,
    include_in_schema=True,
)
def subscription_zarinpal_callback(
    request: Request,
    authority: str = Query(alias="Authority", min_length=1, max_length=255),
    status: str = Query(alias="Status", min_length=1, max_length=30),
    db: Session = Depends(get_db),
):
    item = SubscriptionCommerceService(db).handle_zarinpal_callback(
        authority=authority,
        status=status,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Subscription payment callback processed",
        meta={"trace_id": request.state.trace_id},
    )
