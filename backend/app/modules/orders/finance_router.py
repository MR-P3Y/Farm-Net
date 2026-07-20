from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.orders.finance_service import AdminFinanceService
from app.modules.finance.service import LedgerReconciliationService
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.finance.models import SettlementRequest
from app.modules.finance.schemas import SettlementDecisionIn
from app.modules.finance.settlement_service import SettlementContractError, SettlementService

router = APIRouter(prefix="/admin/finance", tags=["Admin Finance"])


def _list(resource: str, request: Request, page: int, page_size: int, db: Session):
    rows, total = AdminFinanceService(db).list_rows(
        resource=resource, page=page, page_size=page_size
    )
    return success_response(
        data=[row.model_dump(mode="json") for row in rows], message="OK",
        meta={"page": page, "page_size": page_size, "total": total,
              "total_pages": ceil(total / page_size) if total else 0,
              "trace_id": request.state.trace_id},
    )


@router.get("/invoices")
def invoices(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: AuthUser = Depends(require_permission("finance.invoices.read"))):
    return _list("invoices", request, page, page_size, db)


@router.get("/invoices/{invoice_id}")
def invoice(invoice_id: int, request: Request, db: Session = Depends(get_db), _: AuthUser = Depends(require_permission("finance.invoices.read_detail"))):
    row = AdminFinanceService(db).get_invoice(invoice_id=invoice_id)
    return success_response(data=row.model_dump(mode="json"), message="OK", meta={"trace_id": request.state.trace_id})


@router.get("/payment-attempts")
def attempts(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: AuthUser = Depends(require_permission("finance.payments.read"))):
    return _list("payment_attempts", request, page, page_size, db)


@router.get("/transactions")
def transactions(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: AuthUser = Depends(require_permission("finance.transactions.read"))):
    return _list("transactions", request, page, page_size, db)


@router.get("/refunds")
def refunds(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: AuthUser = Depends(require_permission("finance.refunds.create"))):
    return _list("refunds", request, page, page_size, db)


@router.get("/audit-logs")
def audits(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: AuthUser = Depends(require_permission("finance.transactions.read"))):
    return _list("audit_logs", request, page, page_size, db)


@router.get("/reconciliation")
def reconciliation(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("finance.ledger.reconcile")),
):
    result = LedgerReconciliationService(db).run()
    data = result.model_dump(mode="json")
    data["is_clean"] = result.is_clean
    return success_response(data=data, message="OK", meta={"trace_id": request.state.trace_id})


@router.get("/settlements")
def settlements(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: AuthUser = Depends(require_permission("finance.settlements.read"))):
    query = db.query(SettlementRequest)
    total = query.count()
    rows = query.order_by(SettlementRequest.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success_response(
        data=[SettlementService.output(row).model_dump(mode="json") for row in rows],
        message="OK",
        meta={"page": page, "page_size": page_size, "total": total, "trace_id": request.state.trace_id},
    )


@router.patch("/settlements/{settlement_id}/decision")
def decide_settlement(settlement_id: int, payload: SettlementDecisionIn, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("finance.settlements.manage"))):
    service = SettlementService(db)
    try:
        row = service.decide(
            settlement_id=settlement_id, approve=payload.decision == "approve",
            admin_user_id=user.id, admin_note=payload.admin_note,
            trace_id=request.state.trace_id,
        )
    except SettlementContractError as exc:
        raise ValidationAuthError(message=str(exc)) from exc
    db.commit()
    return success_response(data=service.output(row).model_dump(mode="json"), message="Settlement decision recorded", meta={"trace_id": request.state.trace_id})


@router.post("/settlements/{settlement_id}/simulate-payout")
def simulate_settlement_payout(settlement_id: int, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("finance.settlements.manage"))):
    service = SettlementService(db)
    try:
        row = service.simulate_payout(settlement_id=settlement_id, admin_user_id=user.id, trace_id=request.state.trace_id)
    except SettlementContractError as exc:
        raise ValidationAuthError(message=str(exc)) from exc
    db.commit()
    return success_response(data=service.output(row).model_dump(mode="json"), message="Moved to simulated payout clearing; no bank transfer occurred", meta={"trace_id": request.state.trace_id})
