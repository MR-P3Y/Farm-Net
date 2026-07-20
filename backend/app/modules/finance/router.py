from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.finance.models import SettlementRequest
from app.modules.finance.schemas import SettlementCreateIn
from app.modules.finance.settlement_service import (
    LedgerMovementService,
    SettlementContractError,
    SettlementService,
)

router = APIRouter(prefix="/finance", tags=["Finance"])


@router.get("/wallet/me")
def own_wallet(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("wallet.read_own")),
):
    result = LedgerMovementService(db).balance(user.id)
    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/settlements/me")
def own_settlements(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("settlements.read_own")),
):
    query = db.query(SettlementRequest).filter(SettlementRequest.requester_user_id == user.id)
    total = query.count()
    rows = (
        query.order_by(SettlementRequest.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    data = [SettlementService.output(row).model_dump(mode="json") for row in rows]
    return success_response(
        data=data,
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "trace_id": request.state.trace_id,
        },
    )


@router.post("/settlements")
def request_settlement(
    payload: SettlementCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("settlements.create_own")),
):
    service = SettlementService(db)
    try:
        row = service.create(
            user_id=user.id,
            amount=payload.amount,
            currency=payload.currency,
            idempotency_key=payload.idempotency_key,
            note=payload.note,
            trace_id=request.state.trace_id,
        )
    except SettlementContractError as exc:
        raise ValidationAuthError(message=str(exc)) from exc
    db.commit()
    return success_response(
        data=service.output(row).model_dump(mode="json"),
        message="Settlement requested; balance reserved",
        meta={"trace_id": request.state.trace_id},
    )
