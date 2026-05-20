from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.orders.schemas import CheckoutIn
from app.modules.orders.service import CheckoutService


router = APIRouter(
    tags=["Checkout & Orders"],
)


@router.post("/checkout")
def checkout(
    payload: CheckoutIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("orders.create")),
):
    service = CheckoutService(db)

    result = service.checkout(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Checkout completed",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/orders/me")
def list_my_orders(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("orders.read")),
):
    service = CheckoutService(db)

    items, total = service.list_my_orders(
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


@router.get("/orders/{order_id}")
def get_my_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("orders.read")),
):
    service = CheckoutService(db)

    result = service.get_my_order(
        user=current_user,
        order_id=order_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )
