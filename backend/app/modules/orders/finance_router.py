from math import ceil
import json

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.orders.finance_service import AdminFinanceService
from app.modules.finance.service import LedgerReconciliationService
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.finance.models import (
    BillingRefund,
    LedgerTransaction,
    SettlementRequest,
    WalletAccount,
)
from app.modules.finance.refund_service import (
    BillingRefundContractError,
    BillingRefundService,
)
from app.modules.finance.schemas import (
    AdjustmentCreateIn,
    AdminLedgerJournalOut,
    AdminWalletAccountOut,
    BillingRefundCompleteIn,
    BillingRefundDecisionIn,
    SettlementDecisionIn,
)
from app.modules.finance.settlement_service import (
    LedgerMovementService, SettlementContractError, SettlementService,
)
from app.modules.orders.models import AdminAuditLog
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
from app.modules.services.service import ServicesService

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


@router.get("/billing-refunds")
def billing_refunds(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("finance.refunds.create")),
):
    query = db.query(BillingRefund)
    total = query.count()
    rows = (
        query.order_by(BillingRefund.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return success_response(
        data=[BillingRefundService.output(row).model_dump(mode="json") for row in rows],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.patch("/billing-refunds/{refund_id}/decision")
def decide_billing_refund(
    refund_id: int,
    payload: BillingRefundDecisionIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("finance.refunds.create")),
):
    service = BillingRefundService(db)
    try:
        row = service.decide(
            refund_id=refund_id,
            approve=payload.decision == "approve",
            admin_user_id=user.id,
            admin_note=payload.admin_note,
        )
    except BillingRefundContractError as exc:
        raise ValidationAuthError(message=str(exc)) from exc
    _audit_billing_refund(
        db=db,
        request=request,
        user=user,
        row=row,
        action="FINANCE_BILLING_REFUND_DECIDED",
    )
    db.commit()
    db.refresh(row)
    return success_response(
        data=service.output(row).model_dump(mode="json"),
        message="Billing refund decision recorded",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/billing-refunds/{refund_id}/complete-mock")
def complete_mock_billing_refund(
    refund_id: int,
    payload: BillingRefundCompleteIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("finance.refunds.create")),
):
    service = BillingRefundService(db)
    try:
        row = service.complete_mock(
            refund_id=refund_id,
            admin_user_id=user.id,
            provider_reference=payload.provider_reference,
            trace_id=request.state.trace_id,
        )
    except BillingRefundContractError as exc:
        raise ValidationAuthError(message=str(exc)) from exc
    _audit_billing_refund(
        db=db,
        request=request,
        user=user,
        row=row,
        action="FINANCE_BILLING_REFUND_COMPLETED",
    )
    ServicesService(db).finalize_refunded_service_request(
        refund=row,
        admin_user=user,
    )
    return success_response(
        data=service.output(row).model_dump(mode="json"),
        message="Mock billing refund completed; no real gateway transfer occurred",
        meta={"trace_id": request.state.trace_id},
    )


def _audit_billing_refund(
    *,
    db: Session,
    request: Request,
    user: AuthUser,
    row: BillingRefund,
    action: str,
) -> None:
    exists = db.query(AdminAuditLog.id).filter(
        AdminAuditLog.action == action,
        AdminAuditLog.target_type == "finance_billing_refund",
        AdminAuditLog.target_id == str(row.id),
    ).scalar()
    if exists is not None:
        return
    db.add(
        AdminAuditLog(
            admin_user_id=user.id,
            action=action,
            target_type="finance_billing_refund",
            target_id=str(row.id),
            old_value=None,
            new_value=json.dumps({"status": row.status, "amount": str(row.amount_toman)}),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            trace_id=request.state.trace_id,
        )
    )


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


@router.get("/ledger")
def ledger_journals(
    request: Request, page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("finance.ledger.read")),
):
    query = db.query(LedgerTransaction)
    total = query.count()
    rows = query.order_by(LedgerTransaction.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return success_response(
        data=[AdminLedgerJournalOut.model_validate(row, from_attributes=True).model_dump(mode="json") for row in rows],
        message="OK", meta={"page": page, "page_size": page_size, "total": total,
                            "total_pages": ceil(total / page_size) if total else 0,
                            "trace_id": request.state.trace_id},
    )


@router.get("/wallets")
def wallet_accounts(
    request: Request, page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("finance.wallets.read")),
):
    query = db.query(WalletAccount)
    total = query.count()
    rows = query.order_by(WalletAccount.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return success_response(
        data=[AdminWalletAccountOut.model_validate(row, from_attributes=True).model_dump(mode="json") for row in rows],
        message="OK", meta={"page": page, "page_size": page_size, "total": total,
                            "total_pages": ceil(total / page_size) if total else 0,
                            "trace_id": request.state.trace_id},
    )


@router.get("/settlements")
def settlements(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), _: AuthUser = Depends(require_permission("finance.settlements.read"))):
    query = db.query(SettlementRequest)
    total = query.count()
    rows = query.order_by(SettlementRequest.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success_response(
        data=[SettlementService.output(row).model_dump(mode="json") for row in rows],
        message="OK",
        meta={"page": page, "page_size": page_size, "total": total,
              "total_pages": ceil(total / page_size) if total else 0,
              "trace_id": request.state.trace_id},
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
    audit_exists = db.query(AdminAuditLog.id).filter(
        AdminAuditLog.action == "FINANCE_SETTLEMENT_DECIDED",
        AdminAuditLog.target_type == "finance_settlement_request",
        AdminAuditLog.target_id == str(row.id),
    ).scalar()
    if audit_exists is None:
        db.add(AdminAuditLog(
            admin_user_id=user.id, action="FINANCE_SETTLEMENT_DECIDED",
            target_type="finance_settlement_request", target_id=str(row.id),
            old_value=json.dumps({"status": "requested"}),
            new_value=json.dumps({"status": row.status}),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            trace_id=request.state.trace_id,
        ))
    db.commit()
    return success_response(data=service.output(row).model_dump(mode="json"), message="Settlement decision recorded", meta={"trace_id": request.state.trace_id})


@router.post("/settlements/{settlement_id}/simulate-payout")
def simulate_settlement_payout(settlement_id: int, request: Request, db: Session = Depends(get_db), user: AuthUser = Depends(require_permission("finance.settlements.manage"))):
    service = SettlementService(db)
    try:
        row = service.simulate_payout(settlement_id=settlement_id, admin_user_id=user.id, trace_id=request.state.trace_id)
    except SettlementContractError as exc:
        raise ValidationAuthError(message=str(exc)) from exc
    audit_exists = db.query(AdminAuditLog.id).filter(
        AdminAuditLog.action == "FINANCE_SETTLEMENT_SIMULATED",
        AdminAuditLog.target_type == "finance_settlement_request",
        AdminAuditLog.target_id == str(row.id),
    ).scalar()
    if audit_exists is None:
        db.add(AdminAuditLog(
            admin_user_id=user.id, action="FINANCE_SETTLEMENT_SIMULATED",
            target_type="finance_settlement_request", target_id=str(row.id),
            old_value=json.dumps({"status": "approved"}),
            new_value=json.dumps({"status": row.status, "bank_transfer": False}),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            trace_id=request.state.trace_id,
        ))
    db.commit()
    return success_response(data=service.output(row).model_dump(mode="json"), message="Moved to simulated payout clearing; no bank transfer occurred", meta={"trace_id": request.state.trace_id})


@router.post("/adjustments")
def create_adjustment(
    payload: AdjustmentCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("finance.adjustments.create")),
):
    service = LedgerMovementService(db)
    try:
        journal = service.post_adjustment(
            provider_user_id=payload.provider_user_id,
            amount=payload.amount,
            direction=payload.direction,
            idempotency_key=payload.idempotency_key,
            reason=payload.reason,
            actor_user_id=user.id,
            trace_id=request.state.trace_id,
        )
    except SettlementContractError as exc:
        raise ValidationAuthError(message=str(exc)) from exc
    audit_exists = db.query(AdminAuditLog.id).filter(
        AdminAuditLog.action == "FINANCE_WALLET_ADJUSTMENT",
        AdminAuditLog.target_type == "finance_ledger_transaction",
        AdminAuditLog.target_id == str(journal.id),
    ).scalar()
    if audit_exists is None:
        db.add(AdminAuditLog(
            admin_user_id=user.id,
            action="FINANCE_WALLET_ADJUSTMENT",
            target_type="finance_ledger_transaction",
            target_id=str(journal.id),
            old_value=None,
            new_value=json.dumps({
                "provider_user_id": payload.provider_user_id,
                "amount": str(payload.amount),
                "currency": payload.currency,
                "direction": payload.direction,
                "reason": payload.reason,
            }),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            trace_id=request.state.trace_id,
        ))
    NotificationService(db).create_event_and_notify_user(
        event_type=NotificationEventType.WALLET_ADJUSTED.value,
        recipient_user_id=payload.provider_user_id,
        title="Wallet balance adjusted",
        body="An authorized accounting adjustment was applied to your wallet.",
        actor_user_id=user.id,
        source_type="finance_ledger_transaction",
        source_id=str(journal.id),
        payload_json={
            "journal_id": journal.id,
            "direction": payload.direction,
            "currency": payload.currency,
        },
        action_url="/finance/wallet",
        priority="high",
        commit=False,
    )
    db.commit()
    return success_response(
        data={
            "journal_id": journal.id,
            "journal_number": journal.journal_number,
            "provider_user_id": payload.provider_user_id,
            "amount": payload.amount,
            "currency": payload.currency,
            "direction": payload.direction,
        },
        message="Audited wallet adjustment posted",
        meta={"trace_id": request.state.trace_id},
    )
