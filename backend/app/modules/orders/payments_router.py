from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.orders.schemas import MockPaymentFailIn, PaymentCheckoutIn, PaymentVerifyIn
from app.modules.orders.service import PaymentService


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post("/checkout")
def initiate_payment(
    payload: PaymentCheckoutIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("payments.create")),
):
    result = PaymentService(db).initiate(user=current_user, payload=payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Payment attempt created",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/verify")
def verify_payment(
    payload: PaymentVerifyIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("payments.create")),
):
    result = PaymentService(db).verify(user=current_user, payload=payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Payment verified",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me")
def list_my_payments(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("payments.read")),
):
    service = PaymentService(db)

    items, total = service.list_my_payments(
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


@router.get("/{payment_id}")
def get_my_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("payments.read")),
):
    service = PaymentService(db)

    result = service.get_my_payment(
        user=current_user,
        payment_id=payment_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{payment_id}/mock/pay")
def mock_pay(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("payments.create")),
):
    service = PaymentService(db)

    result = service.mock_pay(
        user=current_user,
        payment_id=payment_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Payment marked as paid",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{payment_id}/mock/fail")
def mock_fail(
    payment_id: int,
    payload: MockPaymentFailIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("payments.create")),
):
    service = PaymentService(db)

    result = service.mock_fail(
        user=current_user,
        payment_id=payment_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Payment marked as failed",
        meta={"trace_id": request.state.trace_id},
    )
