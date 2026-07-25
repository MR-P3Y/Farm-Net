from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.modules.subscriptions.models import (
    BillingEntitlement,
    BillingFeatureUsage,
    BillingPlan,
    BillingPlanFeature,
    BillingSubscription,
)


class SubscriptionReadRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def active_plans(self, now: datetime) -> list[BillingPlan]:
        return (
            self.db.query(BillingPlan)
            .options(joinedload(BillingPlan.features).joinedload(BillingPlanFeature.feature))
            .filter(
                BillingPlan.status == "active",
                or_(BillingPlan.effective_from.is_(None), BillingPlan.effective_from <= now),
                or_(BillingPlan.effective_until.is_(None), BillingPlan.effective_until > now),
            )
            .order_by(BillingPlan.price_toman, BillingPlan.code, BillingPlan.version.desc())
            .all()
        )

    def active_plan_by_code(self, code: str, now: datetime) -> BillingPlan | None:
        return (
            self.db.query(BillingPlan)
            .options(joinedload(BillingPlan.features).joinedload(BillingPlanFeature.feature))
            .filter(
                BillingPlan.code == code,
                BillingPlan.status == "active",
                or_(BillingPlan.effective_from.is_(None), BillingPlan.effective_from <= now),
                or_(BillingPlan.effective_until.is_(None), BillingPlan.effective_until > now),
            )
            .order_by(BillingPlan.version.desc())
            .first()
        )

    def own_current(self, user_id: int, now: datetime) -> BillingSubscription | None:
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
                or_(
                    and_(
                        BillingSubscription.status == "active",
                        BillingSubscription.current_period_starts_at <= now,
                        BillingSubscription.current_period_ends_at > now,
                    ),
                    and_(
                        BillingSubscription.status == "grace",
                        BillingSubscription.grace_ends_at > now,
                    ),
                ),
            )
            .order_by(BillingSubscription.id.desc())
            .first()
        )

    def own_entitlements(self, user_id: int, now: datetime) -> list[BillingEntitlement]:
        return (
            self.db.query(BillingEntitlement)
            .filter(
                BillingEntitlement.user_id == user_id,
                BillingEntitlement.starts_at <= now,
                BillingEntitlement.ends_at > now,
            )
            .order_by(BillingEntitlement.feature_code_snapshot)
            .all()
        )

    def own_usage(self, user_id: int, now: datetime) -> list[BillingFeatureUsage]:
        return (
            self.db.query(BillingFeatureUsage)
            .options(
                joinedload(BillingFeatureUsage.entitlement),
            )
            .join(BillingFeatureUsage.entitlement)
            .filter(
                BillingFeatureUsage.user_id == user_id,
                BillingEntitlement.starts_at <= now,
                BillingEntitlement.ends_at > now,
            )
            .order_by(BillingEntitlement.feature_code_snapshot)
            .all()
        )
