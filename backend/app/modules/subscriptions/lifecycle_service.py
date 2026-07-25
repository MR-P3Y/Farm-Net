from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import AppException
from app.modules.auth.models import AuthUser
from app.modules.subscriptions.models import (
    BillingEntitlement,
    BillingFeatureUsage,
    BillingPlan,
    BillingPlanFeature,
    BillingSubscription,
    BillingSubscriptionPeriod,
)
from app.modules.subscriptions.schemas import SubscriptionOut
from app.modules.subscriptions.service import SubscriptionReadService


FREE_PERIOD_DAYS = 30


class SubscriptionLifecycleService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def activate_free(self, user_id: int) -> SubscriptionOut:
        now = _utcnow()
        self._lock_user(user_id)
        current = self._current_locked(user_id, now)
        if current is not None:
            if current.plan.billing_period != "free":
                raise AppException(
                    "BILLING_ACTIVE_SUBSCRIPTION_EXISTS",
                    "An active paid subscription already exists",
                    409,
                )
            return SubscriptionReadService.subscription_output(current)

        plan = (
            self.db.query(BillingPlan)
            .options(joinedload(BillingPlan.features).joinedload(BillingPlanFeature.feature))
            .filter(
                BillingPlan.is_default_free.is_(True),
                BillingPlan.status == "active",
                BillingPlan.effective_from.is_(None) | (BillingPlan.effective_from <= now),
                BillingPlan.effective_until.is_(None) | (BillingPlan.effective_until > now),
            )
            .order_by(BillingPlan.version.desc())
            .first()
        )
        if plan is None:
            raise AppException(
                "BILLING_FREE_PLAN_UNAVAILABLE",
                "Default free plan is unavailable",
                503,
            )

        ends_at = now + timedelta(days=FREE_PERIOD_DAYS)
        subscription = BillingSubscription(
            user_id=user_id,
            plan_id=plan.id,
            plan=plan,
            status="active",
            starts_at=now,
            current_period_starts_at=now,
            current_period_ends_at=ends_at,
            auto_renew=False,
            cancel_at_period_end=False,
            version=1,
        )
        self.db.add(subscription)
        self.db.flush()
        period = BillingSubscriptionPeriod(
            subscription_id=subscription.id,
            sequence=1,
            status="active",
            starts_at=now,
            ends_at=ends_at,
            plan_code_snapshot=plan.code,
            plan_version_snapshot=plan.version,
            price_toman_snapshot=plan.price_toman,
            currency=plan.currency,
        )
        self.db.add(period)
        self.db.flush()
        self._snapshot_entitlements(
            user_id=user_id,
            subscription=subscription,
            period=period,
            values=plan.features,
        )
        self.db.commit()
        return SubscriptionReadService.subscription_output(subscription)

    def cancel(
        self,
        *,
        user_id: int,
        expected_version: int,
        cancel_at_period_end: bool,
        reason: str,
    ) -> SubscriptionOut:
        now = _utcnow()
        self._lock_user(user_id)
        subscription = self._require_current_locked(user_id, now)
        self._check_version(subscription, expected_version)

        if cancel_at_period_end:
            subscription.cancel_at_period_end = True
            subscription.auto_renew = False
            subscription.cancellation_reason = reason.strip()
        else:
            if subscription.plan.billing_period != "free":
                raise AppException(
                    "BILLING_IMMEDIATE_PAID_CANCEL_UNSUPPORTED",
                    "Paid subscriptions can only be cancelled at period end",
                    409,
                )
            subscription.status = "cancelled"
            subscription.cancelled_at = now
            subscription.ended_at = now
            subscription.cancellation_reason = reason.strip()
            subscription.cancel_at_period_end = False
            subscription.auto_renew = False
            self._close_current_period(subscription.id, now)
        subscription.version += 1
        self.db.commit()
        return SubscriptionReadService.subscription_output(subscription)

    def resume(self, *, user_id: int, expected_version: int) -> SubscriptionOut:
        now = _utcnow()
        self._lock_user(user_id)
        subscription = self._require_current_locked(user_id, now)
        self._check_version(subscription, expected_version)
        if not subscription.cancel_at_period_end:
            raise AppException(
                "BILLING_SUBSCRIPTION_NOT_PENDING_CANCEL",
                "Subscription is not pending cancellation",
                409,
            )
        subscription.cancel_at_period_end = False
        subscription.cancellation_reason = None
        subscription.auto_renew = subscription.plan.billing_period != "free"
        subscription.version += 1
        self.db.commit()
        return SubscriptionReadService.subscription_output(subscription)

    def _snapshot_entitlements(
        self,
        *,
        user_id: int,
        subscription: BillingSubscription,
        period: BillingSubscriptionPeriod,
        values: list[BillingPlanFeature],
    ) -> None:
        for value in values:
            feature = value.feature
            if feature.status != "active":
                continue
            enabled = value.is_enabled
            limit_value: Decimal | None = None
            policy_value: dict | list | None = None
            if feature.value_kind == "boolean":
                enabled = enabled and bool(value.boolean_value)
            elif feature.value_kind in {"integer", "decimal"}:
                limit_value = value.numeric_value
            elif feature.value_kind == "string":
                policy_value = {"value": value.string_value}
            else:
                policy_value = value.json_value
            entitlement = BillingEntitlement(
                user_id=user_id,
                subscription_id=subscription.id,
                period_id=period.id,
                feature_id=feature.id,
                feature_code_snapshot=feature.code,
                source="plan",
                is_enabled=enabled,
                is_unlimited=value.is_unlimited,
                limit_value=limit_value,
                policy_value=policy_value,
                starts_at=period.starts_at,
                ends_at=period.ends_at,
            )
            self.db.add(entitlement)
            self.db.flush()
            if feature.is_metered and enabled:
                self.db.add(
                    BillingFeatureUsage(
                        entitlement_id=entitlement.id,
                        user_id=user_id,
                        period_id=period.id,
                        feature_id=feature.id,
                        used_value=Decimal("0"),
                        reserved_value=Decimal("0"),
                        version=1,
                    )
                )

    def _lock_user(self, user_id: int) -> None:
        exists = (
            self.db.query(AuthUser.id)
            .filter(AuthUser.id == user_id)
            .with_for_update()
            .one_or_none()
        )
        if exists is None:
            raise AppException("BILLING_USER_NOT_FOUND", "User not found", 404)

    def _current_locked(self, user_id: int, now: datetime) -> BillingSubscription | None:
        return (
            self.db.query(BillingSubscription)
            .options(
                joinedload(BillingSubscription.plan)
                .joinedload(BillingPlan.features)
                .joinedload(BillingPlanFeature.feature)
            )
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

    def _require_current_locked(self, user_id: int, now: datetime) -> BillingSubscription:
        row = self._current_locked(user_id, now)
        if row is None:
            raise AppException(
                "BILLING_ACTIVE_SUBSCRIPTION_NOT_FOUND",
                "Active subscription not found",
                404,
            )
        return row

    def _close_current_period(self, subscription_id: int, now: datetime) -> None:
        period = (
            self.db.query(BillingSubscriptionPeriod)
            .filter(
                BillingSubscriptionPeriod.subscription_id == subscription_id,
                BillingSubscriptionPeriod.status == "active",
            )
            .with_for_update()
            .one()
        )
        effective_end = max(now, period.starts_at + timedelta(seconds=1))
        period.status = "closed"
        period.ends_at = effective_end
        (
            self.db.query(BillingEntitlement)
            .filter(
                BillingEntitlement.subscription_id == subscription_id,
                BillingEntitlement.ends_at > effective_end,
            )
            .update(
                {BillingEntitlement.ends_at: effective_end},
                synchronize_session=False,
            )
        )

    @staticmethod
    def _check_version(subscription: BillingSubscription, expected_version: int) -> None:
        if subscription.version != expected_version:
            raise AppException(
                "BILLING_SUBSCRIPTION_VERSION_CONFLICT",
                "Subscription was changed; refresh and retry",
                409,
                {"current_version": subscription.version},
            )


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
