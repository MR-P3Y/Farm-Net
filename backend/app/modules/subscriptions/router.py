from fastapi import APIRouter, Depends, Request
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
)
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
