from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.common.money import BillableSourceType, CurrencyCode, FinancialEventType
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.modules.auth.models import AuthUser
from app.modules.finance.enums import AccountKind, AccountPurpose, EntrySide, LedgerStatus
from app.modules.finance.models import (
    BillingInvoice,
    BillingInvoiceItem,
    LedgerEntry,
    LedgerTransaction,
    WalletAccount,
)
from app.modules.orders.payment_gateway import PaymentGatewayError, ZarinpalGateway
from app.modules.subscriptions.lifecycle_service import SubscriptionLifecycleService
from app.modules.subscriptions.models import (
    BillingPlan,
    BillingPlanFeature,
    BillingSubscription,
    BillingSubscriptionPaymentAttempt,
    BillingSubscriptionPeriod,
)
from app.modules.subscriptions.schemas import SubscriptionCheckoutOut


class SubscriptionCommerceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def checkout(
        self,
        *,
        user_id: int,
        plan_code: str,
        provider: str,
        idempotency_key: str,
    ) -> SubscriptionCheckoutOut:
        code = plan_code.strip().lower()
        key = idempotency_key.strip()
        provider = provider.strip().lower()
        if provider not in {"mock", "zarinpal"}:
            raise AppException(
                "BILLING_PAYMENT_PROVIDER_UNAVAILABLE",
                "Payment provider is unavailable",
                422,
            )
        if provider == "mock" and get_settings().app_env.lower() == "production":
            raise AppException(
                "BILLING_PAYMENT_PROVIDER_UNAVAILABLE",
                "Mock payment is disabled in production",
                403,
            )
        self._lock_user(user_id)
        existing = (
            self.db.query(BillingSubscriptionPaymentAttempt)
            .filter(BillingSubscriptionPaymentAttempt.idempotency_key == key)
            .one_or_none()
        )
        if existing is not None:
            subscription = self.db.get(BillingSubscription, existing.subscription_id)
            if (
                existing.user_id != user_id
                or existing.provider != provider
                or subscription is None
                or subscription.plan.code != code
            ):
                raise AppException(
                    "BILLING_PAYMENT_IDEMPOTENCY_CONFLICT",
                    "Idempotency key was used for a different checkout",
                    409,
                )
            return self._output(existing)

        now = _utcnow()
        plan = (
            self.db.query(BillingPlan)
            .options(joinedload(BillingPlan.features).joinedload(BillingPlanFeature.feature))
            .filter(
                BillingPlan.code == code,
                BillingPlan.status == "active",
                BillingPlan.billing_period != "free",
                BillingPlan.price_toman > 0,
                BillingPlan.currency == CurrencyCode.TOMAN.value,
                BillingPlan.effective_from.is_(None) | (BillingPlan.effective_from <= now),
                BillingPlan.effective_until.is_(None) | (BillingPlan.effective_until > now),
            )
            .order_by(BillingPlan.version.desc())
            .first()
        )
        if plan is None:
            raise AppException("BILLING_PAID_PLAN_UNAVAILABLE", "Paid plan is unavailable", 404)
        current = self._current(user_id, now)
        if current is not None and current.plan.billing_period != "free":
            raise AppException(
                "BILLING_ACTIVE_PAID_SUBSCRIPTION_EXISTS",
                "An active paid subscription already exists",
                409,
            )

        planned_end = now + timedelta(days=self._duration_days(plan))
        subscription = BillingSubscription(
            user_id=user_id,
            plan_id=plan.id,
            plan=plan,
            status="pending",
            auto_renew=True,
            cancel_at_period_end=False,
            version=1,
        )
        self.db.add(subscription)
        self.db.flush()
        invoice = BillingInvoice(
            invoice_number=f"SUB-{now:%Y%m%d}-{uuid4().hex[:16].upper()}",
            source_type=BillableSourceType.PLATFORM_SUBSCRIPTION.value,
            source_id=subscription.id,
            payer_user_id=user_id,
            provider_user_id=None,
            status="payment_pending",
            currency=CurrencyCode.TOMAN.value,
            subtotal_amount=plan.price_toman,
            discount_amount=Decimal("0"),
            surcharge_amount=Decimal("0"),
            total_amount=plan.price_toman,
            platform_amount=plan.price_toman,
            provider_amount=Decimal("0"),
            issued_at=now,
        )
        self.db.add(invoice)
        self.db.flush()
        self.db.add(
            BillingInvoiceItem(
                invoice_id=invoice.id,
                sequence=1,
                source_item_type="subscription_plan",
                source_item_id=plan.id,
                title_snapshot=f"{plan.name} v{plan.version}",
                description_snapshot=plan.description,
                quantity=Decimal("1"),
                unit_snapshot="subscription_period",
                unit_price=plan.price_toman,
                line_total=plan.price_toman,
            )
        )
        period = BillingSubscriptionPeriod(
            subscription_id=subscription.id,
            sequence=1,
            status="pending",
            starts_at=now,
            ends_at=planned_end,
            invoice_id=invoice.id,
            plan_code_snapshot=plan.code,
            plan_version_snapshot=plan.version,
            price_toman_snapshot=plan.price_toman,
            currency=CurrencyCode.TOMAN.value,
        )
        self.db.add(period)
        self.db.flush()
        attempt = BillingSubscriptionPaymentAttempt(
            subscription_id=subscription.id,
            invoice_id=invoice.id,
            user_id=user_id,
            provider=provider,
            status="pending",
            amount_toman=plan.price_toman,
            currency=CurrencyCode.TOMAN.value,
            idempotency_key=key,
            expires_at=now + timedelta(minutes=30),
        )
        self.db.add(attempt)
        self.db.flush()
        if provider == "mock":
            attempt.status = "redirected"
            attempt.redirect_url = f"farmnet://billing/mock/{attempt.id}"
        else:
            try:
                settings = get_settings()
                gateway = ZarinpalGateway().request_payment(
                    amount=attempt.amount_toman,
                    invoice_id=invoice.id,
                    description=f"Farm Net subscription invoice {invoice.invoice_number}",
                    callback_url=(
                        f"{settings.public_base_url.rstrip('/')}"
                        "/api/v1/billing/payments/callback/zarinpal"
                    ),
                )
            except PaymentGatewayError as exc:
                self.db.rollback()
                raise AppException(exc.code, exc.message, 503) from exc
            attempt.status = "redirected"
            attempt.provider_authority = gateway.authority
            attempt.redirect_url = gateway.redirect_url
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            replay = (
                self.db.query(BillingSubscriptionPaymentAttempt)
                .filter(BillingSubscriptionPaymentAttempt.idempotency_key == key)
                .one_or_none()
            )
            if replay is None:
                raise
            return self._output(replay)
        return self._output(attempt)

    def handle_zarinpal_callback(
        self, *, authority: str, status: str
    ) -> SubscriptionCheckoutOut:
        attempt = (
            self.db.query(BillingSubscriptionPaymentAttempt)
            .filter(
                BillingSubscriptionPaymentAttempt.provider == "zarinpal",
                BillingSubscriptionPaymentAttempt.provider_authority == authority,
            )
            .one_or_none()
        )
        if attempt is None:
            raise AppException("BILLING_PAYMENT_NOT_FOUND", "Payment attempt not found", 404)
        if attempt.status == "succeeded":
            return self._output(attempt)
        if status.strip().upper() != "OK":
            attempt.status = "cancelled"
            attempt.failure_code = "BILLING_PAYMENT_GATEWAY_CANCELLED"
            attempt.failure_message = "Payment was cancelled or rejected at gateway"
            self.db.commit()
            return self._output(attempt)
        return self.verify(
            user_id=attempt.user_id,
            attempt_id=attempt.id,
            provider_token=authority,
        )

    def verify(
        self, *, user_id: int, attempt_id: int, provider_token: str
    ) -> SubscriptionCheckoutOut:
        now = _utcnow()
        self._lock_user(user_id)
        attempt = (
            self.db.query(BillingSubscriptionPaymentAttempt)
            .filter(
                BillingSubscriptionPaymentAttempt.id == attempt_id,
                BillingSubscriptionPaymentAttempt.user_id == user_id,
            )
            .with_for_update()
            .one_or_none()
        )
        if attempt is None:
            raise AppException("BILLING_PAYMENT_NOT_FOUND", "Payment attempt not found", 404)
        if attempt.status == "succeeded":
            return self._output(attempt)
        if attempt.expires_at <= now:
            attempt.status = "cancelled"
            attempt.failure_code = "BILLING_PAYMENT_EXPIRED"
            attempt.failure_message = "Payment attempt expired"
            self.db.commit()
            raise AppException("BILLING_PAYMENT_EXPIRED", "Payment attempt expired", 409)
        if attempt.status not in {"pending", "redirected", "verifying"}:
            raise AppException(
                "BILLING_PAYMENT_NOT_VERIFIABLE",
                "Payment cannot be verified in its current state",
                409,
            )

        reference = provider_token.strip()
        if attempt.provider == "mock":
            if get_settings().app_env.lower() == "production":
                raise AppException(
                    "BILLING_PAYMENT_PROVIDER_UNAVAILABLE",
                    "Mock payment is disabled in production",
                    403,
                )
            if not reference:
                raise AppException("BILLING_PAYMENT_TOKEN_INVALID", "Payment token is required", 422)
            reference = f"MOCK-SUB-{attempt.id}-{reference}"
        else:
            if not attempt.provider_authority or reference != attempt.provider_authority:
                raise AppException(
                    "BILLING_PAYMENT_AUTHORITY_MISMATCH",
                    "Payment authority does not match",
                    409,
                )
            attempt.status = "verifying"
            try:
                verified = ZarinpalGateway().verify_payment(
                    amount=attempt.amount_toman,
                    authority=attempt.provider_authority,
                )
            except PaymentGatewayError as exc:
                if exc.terminal:
                    attempt.status = "failed"
                attempt.failure_code = exc.code
                attempt.failure_message = exc.message
                self.db.commit()
                raise AppException(exc.code, exc.message, 409 if exc.terminal else 503) from exc
            reference = verified.reference_id

        subscription = (
            self.db.query(BillingSubscription)
            .options(
                joinedload(BillingSubscription.plan)
                .joinedload(BillingPlan.features)
                .joinedload(BillingPlanFeature.feature)
            )
            .filter(BillingSubscription.id == attempt.subscription_id)
            .with_for_update()
            .one()
        )
        invoice = (
            self.db.query(BillingInvoice)
            .filter(BillingInvoice.id == attempt.invoice_id)
            .with_for_update()
            .one()
        )
        if (
            subscription.status != "pending"
            or invoice.status != "payment_pending"
            or invoice.currency != CurrencyCode.TOMAN.value
            or invoice.total_amount != attempt.amount_toman
        ):
            raise AppException(
                "BILLING_PAYMENT_CONTRACT_CONFLICT",
                "Payment contract is inconsistent",
                409,
            )
        current = self._current(user_id, now)
        if current is not None:
            if current.plan.billing_period != "free":
                raise AppException(
                    "BILLING_ACTIVE_PAID_SUBSCRIPTION_EXISTS",
                    "An active paid subscription already exists",
                    409,
                )
            current.status = "cancelled"
            current.cancelled_at = now
            current.ended_at = now
            current.cancellation_reason = "upgraded_to_paid_plan"
            current.auto_renew = False
            current.version += 1
            SubscriptionLifecycleService(self.db)._close_current_period(current.id, now)

        period = (
            self.db.query(BillingSubscriptionPeriod)
            .filter(
                BillingSubscriptionPeriod.subscription_id == subscription.id,
                BillingSubscriptionPeriod.status == "pending",
            )
            .with_for_update()
            .one()
        )
        ends_at = now + timedelta(days=self._duration_days(subscription.plan))
        subscription.status = "active"
        subscription.starts_at = now
        subscription.current_period_starts_at = now
        subscription.current_period_ends_at = ends_at
        subscription.auto_renew = True
        subscription.version += 1
        period.status = "active"
        period.starts_at = now
        period.ends_at = ends_at
        invoice.status = "paid"
        invoice.paid_at = now
        attempt.status = "succeeded"
        attempt.provider_reference = reference
        attempt.verified_at = now
        self._post_payment(attempt, user_id)
        SubscriptionLifecycleService(self.db)._snapshot_entitlements(
            user_id=user_id,
            subscription=subscription,
            period=period,
            values=subscription.plan.features,
        )
        self.db.commit()
        return self._output(attempt)

    def _post_payment(
        self, attempt: BillingSubscriptionPaymentAttempt, actor_user_id: int
    ) -> None:
        key = f"subscription-payment:{attempt.id}"
        if (
            self.db.query(LedgerTransaction.id)
            .filter(LedgerTransaction.idempotency_key == key)
            .first()
            is not None
        ):
            return
        journal = LedgerTransaction(
            journal_number=f"JRN-SUB-PAY-{attempt.id}",
            event_type=FinancialEventType.PAYMENT.value,
            source_type=BillableSourceType.PLATFORM_SUBSCRIPTION.value,
            source_id=attempt.subscription_id,
            idempotency_key=key,
            status=LedgerStatus.POSTED.value,
            currency=CurrencyCode.TOMAN.value,
            total_debit=attempt.amount_toman,
            total_credit=attempt.amount_toman,
            actor_user_id=actor_user_id,
            trace_id=f"subscription-payment:{attempt.id}",
            description="Verified platform subscription payment",
            posted_at=attempt.verified_at or _utcnow(),
        )
        self.db.add(journal)
        self.db.flush()
        cash = self._account(AccountPurpose.PLATFORM_CASH, AccountKind.ASSET)
        revenue = self._account(AccountPurpose.PLATFORM_REVENUE, AccountKind.REVENUE)
        self.db.add_all(
            [
                LedgerEntry(
                    transaction_id=journal.id,
                    account_id=cash.id,
                    sequence=1,
                    side=EntrySide.DEBIT.value,
                    amount=attempt.amount_toman,
                    currency=CurrencyCode.TOMAN.value,
                    memo="Subscription payment cash",
                ),
                LedgerEntry(
                    transaction_id=journal.id,
                    account_id=revenue.id,
                    sequence=2,
                    side=EntrySide.CREDIT.value,
                    amount=attempt.amount_toman,
                    currency=CurrencyCode.TOMAN.value,
                    memo="Subscription platform revenue",
                ),
            ]
        )

    def _account(self, purpose: AccountPurpose, kind: AccountKind) -> WalletAccount:
        code = f"system:{purpose.value}:TOMAN"
        row = (
            self.db.query(WalletAccount)
            .filter(WalletAccount.account_code == code)
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            row = WalletAccount(
                owner_user_id=None,
                account_code=code,
                account_kind=kind.value,
                purpose=purpose.value,
                currency=CurrencyCode.TOMAN.value,
            )
            self.db.add(row)
            self.db.flush()
        return row

    def _current(self, user_id: int, now: datetime) -> BillingSubscription | None:
        return (
            self.db.query(BillingSubscription)
            .options(joinedload(BillingSubscription.plan))
            .filter(
                BillingSubscription.user_id == user_id,
                BillingSubscription.status.in_(("active", "grace")),
                BillingSubscription.current_period_starts_at <= now,
                BillingSubscription.current_period_ends_at > now,
            )
            .with_for_update()
            .order_by(BillingSubscription.id.desc())
            .first()
        )

    def _lock_user(self, user_id: int) -> None:
        if (
            self.db.query(AuthUser.id)
            .filter(AuthUser.id == user_id)
            .with_for_update()
            .one_or_none()
            is None
        ):
            raise AppException("BILLING_USER_NOT_FOUND", "User not found", 404)

    @staticmethod
    def _duration_days(plan: BillingPlan) -> int:
        if plan.billing_period == "monthly":
            return 30
        if plan.billing_period == "yearly":
            return 365
        if plan.billing_period == "custom" and plan.duration_days:
            return plan.duration_days
        raise AppException("BILLING_PLAN_PERIOD_INVALID", "Paid plan period is invalid", 409)

    @staticmethod
    def _output(attempt: BillingSubscriptionPaymentAttempt) -> SubscriptionCheckoutOut:
        return SubscriptionCheckoutOut(
            payment_attempt_id=attempt.id,
            subscription_id=attempt.subscription_id,
            invoice_id=attempt.invoice_id,
            provider=attempt.provider,
            status=attempt.status,
            amount_toman=attempt.amount_toman,
            currency=attempt.currency,
            redirect_url=attempt.redirect_url,
            expires_at=attempt.expires_at,
            verified_at=attempt.verified_at,
        )


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
