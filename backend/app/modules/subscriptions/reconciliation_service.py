from sqlalchemy.orm import Session, joinedload

from app.modules.finance.models import BillingInvoice, LedgerTransaction
from app.modules.subscriptions.admin_schemas import (
    BillingReconciliationIssueOut,
    BillingReconciliationOut,
)
from app.modules.subscriptions.models import (
    BillingEntitlement,
    BillingFeature,
    BillingFeatureUsage,
    BillingSubscription,
    BillingSubscriptionPaymentAttempt,
)


MAX_SUBSCRIPTIONS = 1000
MAX_ISSUES = 200


class BillingReconciliationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run(self) -> BillingReconciliationOut:
        rows = (
            self.db.query(BillingSubscription)
            .options(
                joinedload(BillingSubscription.periods),
                joinedload(BillingSubscription.entitlements),
            )
            .order_by(BillingSubscription.id)
            .limit(MAX_SUBSCRIPTIONS + 1)
            .all()
        )
        truncated = len(rows) > MAX_SUBSCRIPTIONS
        rows = rows[:MAX_SUBSCRIPTIONS]
        issues: list[BillingReconciliationIssueOut] = []
        period_count = 0
        entitlement_count = 0
        usage_count = 0
        attempt_count = 0

        for subscription in rows:
            periods = subscription.periods
            entitlements = subscription.entitlements
            period_count += len(periods)
            entitlement_count += len(entitlements)
            active_periods = [period for period in periods if period.status == "active"]
            if subscription.status in {"active", "grace"} and len(active_periods) != 1:
                self._issue(
                    issues,
                    "CURRENT_PERIOD_CARDINALITY",
                    "critical",
                    "subscription",
                    subscription.id,
                    f"Expected one active period, found {len(active_periods)}",
                )
            if active_periods:
                period = active_periods[0]
                if (
                    subscription.current_period_starts_at != period.starts_at
                    or subscription.current_period_ends_at != period.ends_at
                ):
                    self._issue(
                        issues,
                        "PERIOD_BOUNDARY_MISMATCH",
                        "critical",
                        "subscription",
                        subscription.id,
                        "Subscription and active-period boundaries differ",
                    )
            for period in periods:
                if (
                    period.price_toman_snapshot > 0
                    and subscription.activation_source != "admin"
                    and period.invoice_id is None
                ):
                    self._issue(
                        issues,
                        "PAID_PERIOD_INVOICE_MISSING",
                        "critical",
                        "period",
                        period.id,
                        "Paid non-Admin period has no invoice",
                    )
                if (
                    period.invoice_id is not None
                    and subscription.status in {"active", "grace"}
                    and period.status == "active"
                ):
                    invoice = self.db.get(BillingInvoice, period.invoice_id)
                    if invoice is None or invoice.status != "paid":
                        self._issue(
                            issues,
                            "ACTIVE_PERIOD_INVOICE_UNPAID",
                            "critical",
                            "period",
                            period.id,
                            "Active paid period does not have a paid invoice",
                        )
            for entitlement in entitlements:
                if entitlement.user_id != subscription.user_id:
                    self._issue(
                        issues,
                        "ENTITLEMENT_OWNER_MISMATCH",
                        "critical",
                        "entitlement",
                        entitlement.id,
                        "Entitlement owner differs from subscription owner",
                    )
                usage = (
                    self.db.query(BillingFeatureUsage)
                    .filter(BillingFeatureUsage.entitlement_id == entitlement.id)
                    .one_or_none()
                )
                if usage:
                    usage_count += 1
                    self._check_usage(issues, entitlement, usage)
                else:
                    feature = self.db.get(BillingFeature, entitlement.feature_id)
                    if (
                        feature is not None
                        and feature.is_metered
                        and entitlement.is_enabled
                    ):
                        self._issue(
                            issues,
                            "METERED_USAGE_MISSING",
                            "critical",
                            "entitlement",
                            entitlement.id,
                            "Enabled metered Entitlement has no usage row",
                        )

            attempts = (
                self.db.query(BillingSubscriptionPaymentAttempt)
                .filter(
                    BillingSubscriptionPaymentAttempt.subscription_id
                    == subscription.id
                )
                .all()
            )
            attempt_count += len(attempts)
            for attempt in attempts:
                self._check_payment(issues, subscription, attempt)

        truncated = truncated or len(issues) >= MAX_ISSUES
        return BillingReconciliationOut(
            clean=not issues and not truncated,
            checked_subscriptions=len(rows),
            checked_periods=period_count,
            checked_entitlements=entitlement_count,
            checked_usage=usage_count,
            checked_payment_attempts=attempt_count,
            issue_count=len(issues),
            truncated=truncated,
            issues=issues,
        )

    def _check_usage(
        self,
        issues: list[BillingReconciliationIssueOut],
        entitlement: BillingEntitlement,
        usage: BillingFeatureUsage,
    ) -> None:
        if (
            usage.user_id != entitlement.user_id
            or usage.period_id != entitlement.period_id
            or usage.feature_id != entitlement.feature_id
        ):
            self._issue(
                issues,
                "USAGE_SCOPE_MISMATCH",
                "critical",
                "usage",
                usage.id,
                "Usage owner, period, or feature differs from Entitlement",
            )
        if (
            not entitlement.is_unlimited
            and entitlement.limit_value is not None
            and usage.used_value + usage.reserved_value > entitlement.limit_value
        ):
            self._issue(
                issues,
                "USAGE_LIMIT_EXCEEDED",
                "critical",
                "usage",
                usage.id,
                "Used plus reserved quota exceeds the Entitlement limit",
            )

    def _check_payment(
        self,
        issues: list[BillingReconciliationIssueOut],
        subscription: BillingSubscription,
        attempt: BillingSubscriptionPaymentAttempt,
    ) -> None:
        invoice = self.db.get(BillingInvoice, attempt.invoice_id)
        if invoice is None:
            self._issue(
                issues,
                "PAYMENT_INVOICE_MISSING",
                "critical",
                "payment",
                attempt.id,
                "Payment attempt references no invoice",
            )
            return
        if (
            invoice.payer_user_id != subscription.user_id
            or invoice.currency != "TOMAN"
            or invoice.total_amount != attempt.amount_toman
        ):
            self._issue(
                issues,
                "PAYMENT_INVOICE_MISMATCH",
                "critical",
                "payment",
                attempt.id,
                "Payment and invoice owner, currency, or amount differ",
            )
        if attempt.status == "succeeded":
            journal = (
                self.db.query(LedgerTransaction)
                .filter(
                    LedgerTransaction.idempotency_key
                    == f"subscription-payment:{attempt.id}"
                )
                .one_or_none()
            )
            if journal is None:
                self._issue(
                    issues,
                    "PAYMENT_LEDGER_MISSING",
                    "critical",
                    "payment",
                    attempt.id,
                    "Succeeded payment has no exact-once ledger journal",
                )
            elif (
                journal.currency != "TOMAN"
                or journal.total_debit != attempt.amount_toman
                or journal.total_credit != attempt.amount_toman
            ):
                self._issue(
                    issues,
                    "PAYMENT_LEDGER_MISMATCH",
                    "critical",
                    "payment",
                    attempt.id,
                    "Ledger currency or balanced totals differ from payment",
                )

    @staticmethod
    def _issue(
        issues: list[BillingReconciliationIssueOut],
        code: str,
        severity: str,
        entity_type: str,
        entity_id: int,
        detail: str,
    ) -> None:
        if len(issues) >= MAX_ISSUES:
            return
        issues.append(
            BillingReconciliationIssueOut(
                code=code,
                severity=severity,
                entity_type=entity_type,
                entity_id=entity_id,
                detail=detail,
            )
        )
