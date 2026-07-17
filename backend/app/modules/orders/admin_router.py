from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.orders.schemas import AdminOrderStatusUpdateIn, RefundCreateIn, RefundProcessIn
from app.modules.orders.service import AdminOrderService, RefundService


router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin Orders"],
)


@router.post("/refunds")
def create_refund(
    payload: RefundCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("finance.refunds.create")),
):
    result = RefundService(db).create(
        user=current_user, payload=payload,
        audit_context={
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "trace_id": request.state.trace_id,
        },
    )
    return success_response(
        data=result.model_dump(mode="json"), message="Refund requested",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/refunds/{refund_id}/complete")
def complete_refund(
    refund_id: int,
    payload: RefundProcessIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("finance.refunds.create")),
):
    result = RefundService(db).complete_mock(
        user=current_user, refund_id=refund_id, payload=payload,
        audit_context={
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "trace_id": request.state.trace_id,
        },
    )
    return success_response(
        data=result.model_dump(mode="json"), message="Refund completed",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("")
def list_admin_orders(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    payment_status: str | None = Query(default=None),
    store_id: int | None = Query(default=None, ge=1),
    buyer_user_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("orders.admin_read")),
):
    service = AdminOrderService(db)

    items, total = service.list_admin_orders(
        status=status,
        payment_status=payment_status,
        store_id=store_id,
        buyer_user_id=buyer_user_id,
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


@router.get("/{order_id}")
def get_admin_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("orders.admin_read")),
):
    service = AdminOrderService(db)

    result = service.get_admin_order(order_id=order_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{order_id}/status")
def update_admin_order_status(
    order_id: int,
    payload: AdminOrderStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("orders.admin_update")),
):
    service = AdminOrderService(db)

    result = service.update_admin_order_status(
        user=current_user,
        order_id=order_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Admin order status updated",
        meta={"trace_id": request.state.trace_id},
    )
