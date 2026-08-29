from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.common.money import BillableSourceType, CurrencyCode
from app.core.config import get_settings
from app.modules.finance.enums import (
    BillingInvoiceStatus,
    BillingPaymentAttemptStatus,
    BillingRefundStatus,
)
from app.modules.finance.models import (
    BillingInvoice,
    BillingPaymentAttempt,
    BillingRefund,
)
from app.modules.finance.schemas import BillingRefundOut
from app.modules.finance.settlement_service import (
    LedgerMovementService,
    SettlementContractError,
)
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService


class BillingRefundContractError(ValueError):
    pass


class BillingRefundService:
    SUPPORTED_SOURCES = {BillableSourceType.SERVICE_REQUEST.value}

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        invoice_id: int,
        requester_user_id: int,
        reason: str,
        idempotency_key: str,
        review_required: bool,
    ) -> BillingRefund:
        existing = (
            self.db.query(BillingRefund)
            .filter(BillingRefund.idempotency_key == idempotency_key)
            .one_or_none()
        )
        if existing is not None:
            if (
                existing.invoice_id != invoice_id
                or existing.requested_by_user_id != requester_user_id
                or existing.reason != reason
            ):
                raise BillingRefundContractError("Refund idempotency key payload conflict")
            return existing

        invoice = self._invoice(invoice_id)
        if invoice.source_type not in self.SUPPORTED_SOURCES:
            raise BillingRefundContractError("Invoice source is not refundable here")
        if invoice.payer_user_id != requester_user_id:
            raise BillingRefundContractError("Only the invoice payer may request a refund")
        if invoice.status != BillingInvoiceStatus.PAID.value:
            raise BillingRefundContractError("Only a paid invoice may request a refund")
        if invoice.provider_user_id is None:
            raise BillingRefundContractError("Refund provider contract is incomplete")
        duplicate = (
            self.db.query(BillingRefund)
            .filter(BillingRefund.invoice_id == invoice.id)
            .with_for_update()
            .one_or_none()
        )
        if duplicate is not None:
            raise BillingRefundContractError("A refund already exists for this invoice")
        attempt = (
            self.db.query(BillingPaymentAttempt)
            .filter(
                BillingPaymentAttempt.invoice_id == invoice.id,
                BillingPaymentAttempt.status == BillingPaymentAttemptStatus.SUCCEEDED.value,
            )
            .order_by(BillingPaymentAttempt.id.desc())
            .with_for_update()
            .first()
        )
        if attempt is None:
            raise BillingRefundContractError("Verified payment attempt is required")

        now = datetime.now(UTC).replace(tzinfo=None)
        row = BillingRefund(
            invoice_id=invoice.id,
            payment_attempt_id=attempt.id,
            source_type=invoice.source_type,
            source_id=invoice.source_id,
            payer_user_id=invoice.payer_user_id,
            provider_user_id=invoice.provider_user_id,
            status=(
                BillingRefundStatus.REQUESTED.value
                if review_required
                else BillingRefundStatus.APPROVED.value
            ),
            amount_toman=invoice.total_amount,
            currency=CurrencyCode.TOMAN.value,
            idempotency_key=idempotency_key,
            reason=reason,
            review_required=review_required,
            requested_by_user_id=requester_user_id,
            requested_at=now,
        )
        self.db.add(row)
        invoice.status = BillingInvoiceStatus.REFUND_PENDING.value
        self.db.flush()
        self._notify(
            row=row,
            event_type=NotificationEventType.REFUND_REQUESTED.value,
            title="Service refund requested",
            body=(
                "Your full refund is approved and awaits payment processing."
                if not review_required
                else "Your cancellation and full-refund request awaits admin review."
            ),
            actor_user_id=requester_user_id,
        )
        return row

    def decide(
        self,
        *,
        refund_id: int,
        approve: bool,
        admin_user_id: int,
        admin_note: str | None,
    ) -> BillingRefund:
        row = self._refund(refund_id)
        target = (
            BillingRefundStatus.APPROVED.value
            if approve
            else BillingRefundStatus.REJECTED.value
        )
        if row.status == target:
            return row
        if row.status != BillingRefundStatus.REQUESTED.value:
            raise BillingRefundContractError("Refund is not awaiting admin review")
        invoice = self._invoice(row.invoice_id)
        now = datetime.now(UTC).replace(tzinfo=None)
        row.status = target
        row.decided_by_user_id = admin_user_id
        row.decided_at = now
        row.admin_note = admin_note
        if not approve:
            if invoice.status != BillingInvoiceStatus.REFUND_PENDING.value:
                raise BillingRefundContractError("Refund invoice status is inconsistent")
            invoice.status = BillingInvoiceStatus.PAID.value
        self._notify(
            row=row,
            event_type=(
                NotificationEventType.REFUND_APPROVED.value
                if approve
                else NotificationEventType.REFUND_REJECTED.value
            ),
            title="Service refund approved" if approve else "Service refund rejected",
            body=(
                "Your cancellation and full refund were approved."
                if approve
                else "Your cancellation and refund request was rejected after review."
            ),
            actor_user_id=admin_user_id,
        )
        self.db.flush()
        return row

    def complete_mock(
        self,
        *,
        refund_id: int,
        admin_user_id: int,
        provider_reference: str,
        trace_id: str,
    ) -> BillingRefund:
        row = self._refund(refund_id)
        if row.status == BillingRefundStatus.SUCCEEDED.value:
            return row
        if row.status != BillingRefundStatus.APPROVED.value:
            raise BillingRefundContractError("Refund must be approved before processing")
        attempt = (
            self.db.query(BillingPaymentAttempt)
            .filter(BillingPaymentAttempt.id == row.payment_attempt_id)
            .with_for_update()
            .one_or_none()
        )
        if (
            attempt is None
            or attempt.status != BillingPaymentAttemptStatus.SUCCEEDED.value
            or attempt.provider != "mock"
        ):
            raise BillingRefundContractError(
                "Mock completion is only available for a successful Mock payment"
            )
        if get_settings().app_env.strip().lower() == "production":
            raise BillingRefundContractError("Mock refund is disabled in production")
        invoice = self._invoice(row.invoice_id)
        if invoice.status != BillingInvoiceStatus.REFUND_PENDING.value:
            raise BillingRefundContractError("Refund invoice status is inconsistent")
        try:
            LedgerMovementService(self.db).post_billable_invoice_refund(
                invoice=invoice,
                actor_user_id=admin_user_id,
                trace_id=trace_id,
            )
        except SettlementContractError as exc:
            raise BillingRefundContractError(str(exc)) from exc
        now = datetime.now(UTC).replace(tzinfo=None)
        invoice.status = BillingInvoiceStatus.REFUNDED.value
        invoice.refunded_at = now
        row.status = BillingRefundStatus.SUCCEEDED.value
        row.provider_reference = provider_reference
        row.decided_by_user_id = row.decided_by_user_id or admin_user_id
        row.decided_at = row.decided_at or now
        row.processed_at = now
        self._notify(
            row=row,
            event_type=NotificationEventType.REFUND_COMPLETED.value,
            title="Service refund completed",
            body="The full service payment was refunded successfully.",
            actor_user_id=admin_user_id,
        )
        self.db.flush()
        return row

    def by_source(self, *, source_type: str, source_id: int) -> BillingRefund | None:
        return (
            self.db.query(BillingRefund)
            .filter(
                BillingRefund.source_type == source_type,
                BillingRefund.source_id == source_id,
            )
            .one_or_none()
        )

    def _invoice(self, invoice_id: int) -> BillingInvoice:
        row = (
            self.db.query(BillingInvoice)
            .filter(BillingInvoice.id == invoice_id)
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            raise BillingRefundContractError("Invoice not found")
        return row

    def _refund(self, refund_id: int) -> BillingRefund:
        row = (
            self.db.query(BillingRefund)
            .filter(BillingRefund.id == refund_id)
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            raise BillingRefundContractError("Refund not found")
        return row

    @staticmethod
    def output(row: BillingRefund) -> BillingRefundOut:
        return BillingRefundOut.model_validate(row, from_attributes=True)

    def _notify(
        self,
        *,
        row: BillingRefund,
        event_type: str,
        title: str,
        body: str,
        actor_user_id: int,
    ) -> None:
        service = NotificationService(self.db)
        action_url = f"/services/requests/{row.source_id}"
        payload = {
            "refund_id": row.id,
            "invoice_id": row.invoice_id,
            "source_type": row.source_type,
            "source_id": row.source_id,
            "status": row.status,
            "currency": row.currency,
        }
        for recipient_id in {row.payer_user_id, row.provider_user_id}:
            service.create_event_and_notify_user(
                event_type=event_type,
                recipient_user_id=recipient_id,
                title=title,
                body=body,
                actor_user_id=actor_user_id,
                source_type="billing_refund",
                source_id=str(row.id),
                payload_json=payload,
                action_url=(
                    action_url
                    if recipient_id == row.payer_user_id
                    else f"/services/workbench/requests/{row.source_id}"
                ),
                event_key=f"billing-refund:{row.id}:{row.status}",
                allow_self_notification=recipient_id == actor_user_id,
                commit=False,
            )
