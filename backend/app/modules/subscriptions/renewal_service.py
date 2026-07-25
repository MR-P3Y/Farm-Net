from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
from app.modules.subscriptions.audit_service import (
    BillingAuditService,
    subscription_snapshot,
)
from app.modules.subscriptions.lifecycle_service import (
    FREE_PERIOD_DAYS,
    SubscriptionLifecycleService,
)
from app.modules.subscriptions.models import (
    BillingEntitlement,
    BillingPlan,
    BillingPlanFeature,
    BillingSubscription,
    BillingSubscriptionPeriod,
)


PAID_GRACE_DAYS = 3


class SubscriptionRenewalService:
    def __init__(
        self,
        db: Session,
        notifier: NotificationService | None = None,
        auditor: BillingAuditService | None = None,
    ) -> None:
        self.db = db
        self.notifier = notifier or NotificationService(db)
        self.auditor = auditor or BillingAuditService(db)
        self.lifecycle = SubscriptionLifecycleService(db)

    def process_due(self, *, now: datetime | None = None, limit: int = 100) -> dict[str, int]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        now = now or _utcnow()
        rows = (
            self.db.query(BillingSubscription)
            .options(
                joinedload(BillingSubscription.plan)
                .joinedload(BillingPlan.features)
                .joinedload(BillingPlanFeature.feature)
            )
            .filter(
                or_(
                    and_(
                        BillingSubscription.status == "active",
                        BillingSubscription.current_period_ends_at <= now,
                    ),
                    and_(
                        BillingSubscription.status == "grace",
                        BillingSubscription.grace_ends_at <= now,
                    ),
                )
            )
            .order_by(BillingSubscription.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
            .all()
        )
        result = {"renewed": 0, "grace_started": 0, "cancelled": 0, "expired": 0}
        for subscription in rows:
            period = self._current_period(subscription.id)
            if subscription.status == "grace":
                self._expire(subscription, period, now)
                result["expired"] += 1
            elif subscription.cancel_at_period_end:
                self._cancel(subscription, period, now)
                result["cancelled"] += 1
            elif subscription.plan.billing_period == "free":
                self._renew_free(subscription, period, now)
                result["renewed"] += 1
            else:
                self._enter_grace(subscription, period, now)
                result["grace_started"] += 1
        if rows:
            self.db.commit()
        return result

    def _renew_free(
        self,
        subscription: BillingSubscription,
        period: BillingSubscriptionPeriod,
        now: datetime,
    ) -> None:
        period.status = "closed"
        start = max(now, period.ends_at)
        end = start + timedelta(days=FREE_PERIOD_DAYS)
        next_period = BillingSubscriptionPeriod(
            subscription_id=subscription.id,
            sequence=period.sequence + 1,
            status="active",
            starts_at=start,
            ends_at=end,
            plan_code_snapshot=subscription.plan.code,
            plan_version_snapshot=subscription.plan.version,
            price_toman_snapshot=subscription.plan.price_toman,
            currency=subscription.plan.currency,
        )
        self.db.add(next_period)
        self.db.flush()
        self.lifecycle._snapshot_entitlements(
            user_id=subscription.user_id,
            subscription=subscription,
            period=next_period,
            values=subscription.plan.features,
        )
        subscription.current_period_starts_at = start
        subscription.current_period_ends_at = end
        subscription.version += 1
        self._notify(
            subscription,
            period_sequence=next_period.sequence,
            event_type=NotificationEventType.SUBSCRIPTION_RENEWED.value,
            title="اشتراک رایگان تمدید شد",
            body="دوره جدید اشتراک رایگان شما فعال شد.",
        )

    def _enter_grace(
        self,
        subscription: BillingSubscription,
        period: BillingSubscriptionPeriod,
        now: datetime,
    ) -> None:
        grace_end = max(now, period.ends_at) + timedelta(days=PAID_GRACE_DAYS)
        period.status = "closed"
        subscription.status = "grace"
        subscription.grace_ends_at = grace_end
        subscription.version += 1
        (
            self.db.query(BillingEntitlement)
            .filter(
                BillingEntitlement.period_id == period.id,
                BillingEntitlement.ends_at < grace_end,
            )
            .update({BillingEntitlement.ends_at: grace_end}, synchronize_session=False)
        )
        self._notify(
            subscription,
            period_sequence=period.sequence,
            event_type=NotificationEventType.SUBSCRIPTION_GRACE_STARTED.value,
            title="مهلت تمدید اشتراک آغاز شد",
            body="برای حفظ دسترسی، اشتراک خود را تا پایان مهلت سه‌روزه تمدید کنید.",
            priority="high",
        )

    def _cancel(
        self,
        subscription: BillingSubscription,
        period: BillingSubscriptionPeriod,
        now: datetime,
    ) -> None:
        effective_end = max(period.starts_at + timedelta(seconds=1), period.ends_at)
        period.status = "closed"
        subscription.status = "cancelled"
        subscription.cancelled_at = now
        subscription.ended_at = effective_end
        subscription.auto_renew = False
        subscription.grace_ends_at = None
        subscription.version += 1
        self._close_entitlements(period.id, effective_end)
        self._notify(
            subscription,
            period_sequence=period.sequence,
            event_type=NotificationEventType.SUBSCRIPTION_CANCELLED.value,
            title="اشتراک پایان یافت",
            body="اشتراک شما طبق درخواست در پایان دوره متوقف شد.",
        )

    def _expire(
        self,
        subscription: BillingSubscription,
        period: BillingSubscriptionPeriod,
        now: datetime,
    ) -> None:
        effective_end = subscription.grace_ends_at or now
        subscription.status = "expired"
        subscription.ended_at = effective_end
        subscription.auto_renew = False
        subscription.version += 1
        self._close_entitlements(period.id, effective_end)
        self._notify(
            subscription,
            period_sequence=period.sequence,
            event_type=NotificationEventType.SUBSCRIPTION_EXPIRED.value,
            title="اشتراک منقضی شد",
            body="مهلت تمدید اشتراک شما به پایان رسید.",
            priority="high",
        )

    def _current_period(self, subscription_id: int) -> BillingSubscriptionPeriod:
        return (
            self.db.query(BillingSubscriptionPeriod)
            .filter(
                BillingSubscriptionPeriod.subscription_id == subscription_id,
                BillingSubscriptionPeriod.status.in_(("active", "closed")),
            )
            .order_by(BillingSubscriptionPeriod.sequence.desc())
            .with_for_update()
            .first()
        )

    def _close_entitlements(self, period_id: int, effective_end: datetime) -> None:
        (
            self.db.query(BillingEntitlement)
            .filter(
                BillingEntitlement.period_id == period_id,
                BillingEntitlement.ends_at > effective_end,
            )
            .update({BillingEntitlement.ends_at: effective_end}, synchronize_session=False)
        )

    def _notify(
        self,
        subscription: BillingSubscription,
        *,
        period_sequence: int,
        event_type: str,
        title: str,
        body: str,
        priority: str = "normal",
    ) -> None:
        self.auditor.record(
            event_key=(
                f"billing-subscription:{subscription.id}:period:"
                f"{period_sequence}:system:{event_type}"
            ),
            action=event_type,
            target_type="subscription",
            target_id=subscription.id,
            subscription_id=subscription.id,
            plan_id=subscription.plan_id,
            actor_type="system",
            actor_user_id=None,
            new_value=subscription_snapshot(subscription),
        )
        self.notifier.create_event_and_notify_user(
            event_type=event_type,
            recipient_user_id=subscription.user_id,
            title=title,
            body=body,
            source_type="billing_subscription",
            source_id=str(subscription.id),
            payload_json={
                "subscription_id": subscription.id,
                "plan_code": subscription.plan.code,
                "status": subscription.status,
                "period_sequence": period_sequence,
            },
            action_url="/subscription",
            priority=priority,
            event_key=(
                f"subscription:{subscription.id}:period:{period_sequence}:{event_type}"
            ),
            allow_self_notification=True,
            commit=False,
        )


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
