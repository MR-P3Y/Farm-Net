from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.money import BillableSourceType, CurrencyCode
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.modules.finance.enums import (
    BillingInvoiceStatus,
    BillingPaymentAttemptStatus,
)
from app.modules.finance.models import BillingInvoice, BillingPaymentAttempt
from app.modules.finance.schemas import BillingPaymentAttemptOut
from app.modules.finance.settlement_service import (
    LedgerMovementService,
    SettlementContractError,
)
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
from app.modules.orders.payment_gateway import PaymentGatewayError, ZarinpalGateway


class BillingInvoicePaymentService:
    PAYABLE_SOURCES = {
        BillableSourceType.SERVICE_REQUEST.value,
        BillableSourceType.CONSULTATION_REQUEST.value,
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def checkout(
        self,
        *,
        invoice_id: int,
        user_id: int,
        provider: str,
        idempotency_key: str,
    ) -> BillingPaymentAttemptOut:
        existing = self._attempt_by_key(idempotency_key)
        if existing is not None:
            if (
                existing.invoice_id != invoice_id
                or existing.user_id != user_id
                or existing.provider != provider
            ):
                raise AppException(
                    "FINANCE_PAYMENT_IDEMPOTENCY_CONFLICT",
                    "Payment idempotency key conflicts with another request",
                    409,
                )
            return self.output(existing)

        settings = get_settings()
        if provider == "mock" and settings.app_env.strip().lower() == "production":
            raise AppException(
                "FINANCE_PAYMENT_PROVIDER_UNAVAILABLE",
                "Mock payment is disabled in production",
                403,
            )
        invoice = self._invoice_for_payer(invoice_id=invoice_id, user_id=user_id)
        self._validate_payable_invoice(invoice)
        now = datetime.now(UTC).replace(tzinfo=None)
        attempt = BillingPaymentAttempt(
            invoice_id=invoice.id,
            user_id=user_id,
            provider=provider,
            status=BillingPaymentAttemptStatus.PENDING.value,
            amount_toman=invoice.total_amount,
            currency=CurrencyCode.TOMAN.value,
            idempotency_key=idempotency_key,
            expires_at=now + timedelta(minutes=30),
        )
        self.db.add(attempt)
        self.db.flush()
        if provider == "mock":
            attempt.status = BillingPaymentAttemptStatus.REDIRECTED.value
            attempt.redirect_url = f"farmnet://finance/mock/{attempt.id}"
        else:
            callback = (
                f"{settings.public_base_url.rstrip('/')}/api/v1/finance/payments/callback/zarinpal"
            )
            try:
                gateway = ZarinpalGateway().request_payment(
                    amount=attempt.amount_toman,
                    invoice_id=invoice.id,
                    description=f"Farm Net invoice {invoice.invoice_number}",
                    callback_url=callback,
                )
            except PaymentGatewayError as exc:
                self.db.rollback()
                raise AppException(exc.code, exc.message, 409 if exc.terminal else 503) from exc
            attempt.status = BillingPaymentAttemptStatus.REDIRECTED.value
            attempt.provider_authority = gateway.authority
            attempt.redirect_url = gateway.redirect_url
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            replay = self._attempt_by_key(idempotency_key)
            if replay is None:
                raise
            if (
                replay.invoice_id != invoice_id
                or replay.user_id != user_id
                or replay.provider != provider
            ):
                raise AppException(
                    "FINANCE_PAYMENT_IDEMPOTENCY_CONFLICT",
                    "Payment idempotency key conflicts with another request",
                    409,
                )
            return self.output(replay)
        self.db.refresh(attempt)
        return self.output(attempt)

    def verify(
        self, *, attempt_id: int, user_id: int, provider_token: str
    ) -> BillingPaymentAttemptOut:
        now = datetime.now(UTC).replace(tzinfo=None)
        attempt = self._attempt_for_user(attempt_id=attempt_id, user_id=user_id)
        if attempt is None:
            raise AppException("FINANCE_PAYMENT_NOT_FOUND", "Payment attempt not found", 404)
        if attempt.status == BillingPaymentAttemptStatus.SUCCEEDED.value:
            return self.output(attempt)
        if attempt.expires_at <= now:
            attempt.status = BillingPaymentAttemptStatus.CANCELLED.value
            attempt.failure_code = "FINANCE_PAYMENT_EXPIRED"
            attempt.failure_message = "Payment attempt expired"
            self.db.commit()
            raise AppException("FINANCE_PAYMENT_EXPIRED", "Payment attempt expired", 409)
        if attempt.status not in {
            BillingPaymentAttemptStatus.PENDING.value,
            BillingPaymentAttemptStatus.REDIRECTED.value,
            BillingPaymentAttemptStatus.VERIFYING.value,
        }:
            raise AppException(
                "FINANCE_PAYMENT_NOT_VERIFIABLE",
                "Payment cannot be verified in its current state",
                409,
            )

        token = provider_token.strip()
        if attempt.provider == "mock":
            if get_settings().app_env.strip().lower() == "production":
                raise AppException(
                    "FINANCE_PAYMENT_PROVIDER_UNAVAILABLE",
                    "Mock payment is disabled in production",
                    403,
                )
            token = f"MOCK-FIN-{attempt.id}-{token}"
        else:
            if not attempt.provider_authority or token != attempt.provider_authority:
                raise AppException(
                    "FINANCE_PAYMENT_AUTHORITY_MISMATCH",
                    "Payment authority does not match",
                    409,
                )
            attempt.status = BillingPaymentAttemptStatus.VERIFYING.value
            try:
                verified = ZarinpalGateway().verify_payment(
                    amount=attempt.amount_toman,
                    authority=attempt.provider_authority,
                )
            except PaymentGatewayError as exc:
                if exc.terminal:
                    attempt.status = BillingPaymentAttemptStatus.FAILED.value
                attempt.failure_code = exc.code
                attempt.failure_message = exc.message
                self.db.commit()
                raise AppException(exc.code, exc.message, 409 if exc.terminal else 503) from exc
            token = verified.reference_id

        invoice = self._invoice_for_attempt(attempt.invoice_id)
        self._validate_payment_contract(invoice=invoice, attempt=attempt)
        invoice.status = BillingInvoiceStatus.PAID.value
        invoice.paid_at = now
        attempt.status = BillingPaymentAttemptStatus.SUCCEEDED.value
        attempt.provider_reference = token
        attempt.verified_at = now
        try:
            LedgerMovementService(self.db).post_billable_invoice_payment(
                invoice=invoice,
                actor_user_id=user_id,
                trace_id=f"billing-payment:{attempt.id}",
            )
        except SettlementContractError as exc:
            raise AppException("FINANCE_PAYMENT_LEDGER_CONFLICT", str(exc), 409) from exc
        self._notify_paid(invoice=invoice, actor_user_id=user_id)
        self.db.commit()
        self.db.refresh(attempt)
        return self.output(attempt)

    def callback(self, *, authority: str, status: str) -> BillingPaymentAttemptOut:
        attempt = (
            self.db.query(BillingPaymentAttempt)
            .filter(
                BillingPaymentAttempt.provider == "zarinpal",
                BillingPaymentAttempt.provider_authority == authority,
            )
            .with_for_update()
            .one_or_none()
        )
        if attempt is None:
            raise AppException("FINANCE_PAYMENT_NOT_FOUND", "Payment attempt not found", 404)
        if attempt.status == BillingPaymentAttemptStatus.SUCCEEDED.value:
            return self.output(attempt)
        if status != "OK":
            attempt.status = BillingPaymentAttemptStatus.CANCELLED.value
            attempt.failure_code = "FINANCE_PAYMENT_CANCELLED_AT_GATEWAY"
            attempt.failure_message = "Payment was cancelled or rejected at gateway"
            self.db.commit()
            self.db.refresh(attempt)
            return self.output(attempt)
        return self.verify(
            attempt_id=attempt.id,
            user_id=attempt.user_id,
            provider_token=authority,
        )

    def output(self, attempt: BillingPaymentAttempt) -> BillingPaymentAttemptOut:
        invoice = (
            self.db.query(BillingInvoice).filter(BillingInvoice.id == attempt.invoice_id).one()
        )
        return BillingPaymentAttemptOut(
            id=attempt.id,
            invoice_id=attempt.invoice_id,
            source_type=invoice.source_type,
            source_id=invoice.source_id,
            user_id=attempt.user_id,
            provider=attempt.provider,
            status=attempt.status,
            amount_toman=attempt.amount_toman,
            currency=attempt.currency,
            redirect_url=attempt.redirect_url,
            failure_code=attempt.failure_code,
            failure_message=attempt.failure_message,
            expires_at=attempt.expires_at,
            verified_at=attempt.verified_at,
            created_at=attempt.created_at,
            updated_at=attempt.updated_at,
        )

    def _attempt_by_key(self, key: str) -> BillingPaymentAttempt | None:
        return (
            self.db.query(BillingPaymentAttempt)
            .filter(BillingPaymentAttempt.idempotency_key == key)
            .one_or_none()
        )

    def _attempt_for_user(self, *, attempt_id: int, user_id: int) -> BillingPaymentAttempt | None:
        return (
            self.db.query(BillingPaymentAttempt)
            .filter(
                BillingPaymentAttempt.id == attempt_id,
                BillingPaymentAttempt.user_id == user_id,
            )
            .with_for_update()
            .one_or_none()
        )

    def _invoice_for_payer(self, *, invoice_id: int, user_id: int) -> BillingInvoice:
        invoice = (
            self.db.query(BillingInvoice)
            .filter(
                BillingInvoice.id == invoice_id,
                BillingInvoice.payer_user_id == user_id,
            )
            .with_for_update()
            .one_or_none()
        )
        if invoice is None:
            raise AppException("FINANCE_INVOICE_NOT_FOUND", "Invoice not found", 404)
        return invoice

    def _invoice_for_attempt(self, invoice_id: int) -> BillingInvoice:
        invoice = (
            self.db.query(BillingInvoice)
            .filter(BillingInvoice.id == invoice_id)
            .with_for_update()
            .one_or_none()
        )
        if invoice is None:
            raise AppException("FINANCE_INVOICE_NOT_FOUND", "Invoice not found", 404)
        return invoice

    def _validate_payable_invoice(self, invoice: BillingInvoice) -> None:
        if invoice.source_type not in self.PAYABLE_SOURCES:
            raise AppException(
                "FINANCE_INVOICE_SOURCE_UNSUPPORTED",
                "Invoice is not payable through this flow",
                409,
            )
        if invoice.status != BillingInvoiceStatus.PAYMENT_PENDING.value:
            raise AppException(
                "FINANCE_INVOICE_NOT_PAYABLE",
                "Invoice cannot start payment in its current state",
                409,
            )
        if (
            invoice.currency != CurrencyCode.TOMAN.value
            or invoice.total_amount <= 0
            or invoice.provider_user_id is None
        ):
            raise AppException(
                "FINANCE_PAYMENT_CONTRACT_CONFLICT",
                "Invoice payment contract is inconsistent",
                409,
            )

    def _validate_payment_contract(
        self, *, invoice: BillingInvoice, attempt: BillingPaymentAttempt
    ) -> None:
        self._validate_payable_invoice(invoice)
        if (
            invoice.payer_user_id != attempt.user_id
            or invoice.total_amount != attempt.amount_toman
            or invoice.currency != attempt.currency
        ):
            raise AppException(
                "FINANCE_PAYMENT_CONTRACT_CONFLICT",
                "Invoice payment contract is inconsistent",
                409,
            )

    def _notify_paid(self, *, invoice: BillingInvoice, actor_user_id: int) -> None:
        service = NotificationService(self.db)
        event_key = f"finance-billing-invoice:{invoice.id}:paid"
        payload = {
            "invoice_id": invoice.id,
            "source_type": invoice.source_type,
            "source_id": invoice.source_id,
            "status": invoice.status,
            "currency": invoice.currency,
        }
        requester_url = (
            f"/services/requests/{invoice.source_id}"
            if invoice.source_type == BillableSourceType.SERVICE_REQUEST.value
            else f"/consultants/requests/{invoice.source_id}"
        )
        provider_url = (
            f"/services/workbench/requests/{invoice.source_id}"
            if invoice.source_type == BillableSourceType.SERVICE_REQUEST.value
            else f"/consultants/workbench/requests/{invoice.source_id}"
        )
        service.create_event_and_notify_user(
            event_type=NotificationEventType.FINANCE_INVOICE_PAID.value,
            recipient_user_id=invoice.payer_user_id,
            title="Invoice paid",
            body="Your payment was verified successfully.",
            actor_user_id=actor_user_id,
            source_type="billing_invoice",
            source_id=str(invoice.id),
            payload_json=payload,
            action_url=requester_url,
            event_key=event_key,
            allow_self_notification=True,
            commit=False,
        )
        if invoice.provider_user_id is not None:
            service.create_event_and_notify_user(
                event_type=NotificationEventType.FINANCE_INVOICE_PAID.value,
                recipient_user_id=invoice.provider_user_id,
                title="Invoice paid",
                body="The requester payment was verified. Work may now start.",
                actor_user_id=actor_user_id,
                source_type="billing_invoice",
                source_id=str(invoice.id),
                payload_json=payload,
                action_url=provider_url,
                event_key=event_key,
                commit=False,
            )
