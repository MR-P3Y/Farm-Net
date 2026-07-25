from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.subscriptions.admin_schemas import (
    AdminManualActivateIn,
    AdminPlanCreateIn,
    AdminPlanListResponse,
    AdminPlanResponse,
    AdminPlanStatusIn,
    AdminPlanUpdateIn,
    AdminSubscriptionCancelIn,
    AdminSubscriptionListResponse,
    AdminSubscriptionResponse,
    BillingAuditListResponse,
    BillingAuditOut,
    BillingReconciliationResponse,
)
from app.modules.subscriptions.admin_service import (
    AdminSubscriptionService,
    page_meta,
)
from app.modules.subscriptions.audit_service import BillingAuditService
from app.modules.subscriptions.reconciliation_service import BillingReconciliationService


router = APIRouter(prefix="/admin/billing", tags=["Admin Billing Subscriptions"])


@router.get("/plans", response_model=AdminPlanListResponse)
def list_plans(
    request: Request,
    q: str | None = Query(default=None, max_length=160),
    status: str | None = Query(default=None, pattern="^(draft|active|retired)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("billing.plans.read")),
):
    items, total = AdminSubscriptionService(db).list_plans(
        q=q, status=status, page=page, page_size=page_size
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta=page_meta(
            page=page,
            page_size=page_size,
            total=total,
            trace_id=request.state.trace_id,
        ),
    )


@router.post("/plans", response_model=AdminPlanResponse)
def create_plan(
    payload: AdminPlanCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: AuthUser = Depends(require_permission("billing.plans.create")),
):
    item = AdminSubscriptionService(db).create_plan(
        payload, admin_user_id=admin.id, trace_id=request.state.trace_id
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Billing plan draft created",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/plans/{plan_id}", response_model=AdminPlanResponse)
def update_plan(
    plan_id: int,
    payload: AdminPlanUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: AuthUser = Depends(require_permission("billing.plans.update")),
):
    item = AdminSubscriptionService(db).update_plan(
        plan_id,
        payload,
        admin_user_id=admin.id,
        trace_id=request.state.trace_id,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Billing plan draft updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/plans/{plan_id}/status", response_model=AdminPlanResponse)
def update_plan_status(
    plan_id: int,
    payload: AdminPlanStatusIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: AuthUser = Depends(require_permission("billing.plans.update")),
):
    item = AdminSubscriptionService(db).set_plan_status(
        plan_id,
        expected_version=payload.expected_version,
        status=payload.status,
        admin_user_id=admin.id,
        trace_id=request.state.trace_id,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Billing plan status updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/subscriptions", response_model=AdminSubscriptionListResponse)
def list_subscriptions(
    request: Request,
    q: str | None = Query(default=None, max_length=255),
    status: str | None = Query(default=None, pattern="^(pending|active|grace|cancelled|expired)$"),
    plan_id: int | None = Query(default=None, ge=1),
    user_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("billing.subscriptions.read")),
):
    items, total = AdminSubscriptionService(db).list_subscriptions(
        q=q,
        status=status,
        plan_id=plan_id,
        user_id=user_id,
        page=page,
        page_size=page_size,
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta=page_meta(
            page=page,
            page_size=page_size,
            total=total,
            trace_id=request.state.trace_id,
        ),
    )


@router.get(
    "/subscriptions/{subscription_id}",
    response_model=AdminSubscriptionResponse,
)
def subscription_detail(
    subscription_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("billing.subscriptions.read")),
):
    item = AdminSubscriptionService(db).subscription_detail(subscription_id)
    return success_response(
        data=item.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.post(
    "/subscriptions/manual-activate",
    response_model=AdminSubscriptionResponse,
)
def manual_activate(
    payload: AdminManualActivateIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: AuthUser = Depends(require_permission("billing.subscriptions.activate")),
):
    item = AdminSubscriptionService(db).manual_activate(
        admin_user_id=admin.id,
        payload=payload,
        trace_id=request.state.trace_id,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Subscription manually activated",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch(
    "/subscriptions/{subscription_id}/cancel",
    response_model=AdminSubscriptionResponse,
)
def cancel_subscription(
    subscription_id: int,
    payload: AdminSubscriptionCancelIn,
    request: Request,
    db: Session = Depends(get_db),
    admin: AuthUser = Depends(require_permission("billing.subscriptions.cancel")),
):
    item = AdminSubscriptionService(db).cancel_subscription(
        subscription_id,
        payload,
        admin_user_id=admin.id,
        trace_id=request.state.trace_id,
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Subscription cancelled",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/audit", response_model=BillingAuditListResponse)
def list_billing_audit(
    request: Request,
    action: str | None = Query(default=None, max_length=100),
    target_type: str | None = Query(
        default=None, pattern="^(plan|subscription|payment|quota)$"
    ),
    target_id: int | None = Query(default=None, ge=1),
    actor_user_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("billing.audit.read")),
):
    rows, total = BillingAuditService(db).list(
        action=action,
        target_type=target_type,
        target_id=target_id,
        actor_user_id=actor_user_id,
        page=page,
        page_size=page_size,
    )
    return success_response(
        data=[
            BillingAuditOut.model_validate(row).model_dump(mode="json")
            for row in rows
        ],
        message="OK",
        meta=page_meta(
            page=page,
            page_size=page_size,
            total=total,
            trace_id=request.state.trace_id,
        ),
    )


@router.get("/reconciliation", response_model=BillingReconciliationResponse)
def reconcile_billing(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("billing.reconciliation.read")),
):
    result = BillingReconciliationService(db).run()
    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )
