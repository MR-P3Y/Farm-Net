from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.subscriptions.models import (
    BillingEntitlement,
    BillingFeatureUsage,
    BillingPlan,
    BillingPlanFeature,
    BillingSubscription,
)
from app.modules.subscriptions.repository import SubscriptionReadRepository
from app.modules.subscriptions.schemas import (
    EntitlementOut,
    FeatureUsageOut,
    PlanFeatureOut,
    PlanOut,
    SubscriptionOut,
)


class SubscriptionReadService:
    def __init__(self, db: Session) -> None:
        self.repo = SubscriptionReadRepository(db)

    def plans(self) -> list[PlanOut]:
        now = _utcnow()
        return [self.plan_output(row) for row in self.repo.active_plans(now)]

    def plan(self, code: str) -> PlanOut:
        row = self.repo.active_plan_by_code(code.strip().lower(), _utcnow())
        if row is None:
            raise AppException("BILLING_PLAN_NOT_FOUND", "Plan not found", 404)
        return self.plan_output(row)

    def own_subscription(self, user_id: int) -> SubscriptionOut | None:
        row = self.repo.own_current(user_id, _utcnow())
        return None if row is None else self.subscription_output(row)

    def own_entitlements(self, user_id: int) -> list[EntitlementOut]:
        return [
            self.entitlement_output(row) for row in self.repo.own_entitlements(user_id, _utcnow())
        ]

    def own_usage(self, user_id: int) -> list[FeatureUsageOut]:
        return [self.usage_output(row) for row in self.repo.own_usage(user_id, _utcnow())]

    @staticmethod
    def plan_output(row: BillingPlan) -> PlanOut:
        return PlanOut(
            id=row.id,
            code=row.code,
            name=row.name,
            description=row.description,
            billing_period=row.billing_period,
            duration_days=row.duration_days,
            price_toman=row.price_toman,
            currency=row.currency,
            version=row.version,
            is_default_free=row.is_default_free,
            features=[
                SubscriptionReadService.plan_feature_output(value)
                for value in sorted(row.features, key=lambda item: item.feature.code)
                if value.feature.status == "active"
            ],
        )

    @staticmethod
    def plan_feature_output(row: BillingPlanFeature) -> PlanFeatureOut:
        feature = row.feature
        value: bool | int | Decimal | str | dict | list | None
        if row.is_unlimited:
            value = None
        elif feature.value_kind == "boolean":
            value = row.boolean_value
        elif feature.value_kind == "integer":
            value = int(row.numeric_value) if row.numeric_value is not None else None
        elif feature.value_kind == "decimal":
            value = row.numeric_value
        elif feature.value_kind == "string":
            value = row.string_value
        else:
            value = row.json_value
        return PlanFeatureOut(
            code=feature.code,
            name=feature.name,
            module=feature.module,
            value_kind=feature.value_kind,
            unit=feature.unit,
            enabled=row.is_enabled,
            unlimited=row.is_unlimited,
            value=value,
        )

    @staticmethod
    def subscription_output(row: BillingSubscription) -> SubscriptionOut:
        return SubscriptionOut(
            id=row.id,
            status=row.status,
            plan=SubscriptionReadService.plan_output(row.plan),
            starts_at=row.starts_at,
            current_period_starts_at=row.current_period_starts_at,
            current_period_ends_at=row.current_period_ends_at,
            grace_ends_at=row.grace_ends_at,
            auto_renew=row.auto_renew,
            cancel_at_period_end=row.cancel_at_period_end,
            version=row.version,
        )

    @staticmethod
    def entitlement_output(row: BillingEntitlement) -> EntitlementOut:
        return EntitlementOut(
            code=row.feature_code_snapshot,
            enabled=row.is_enabled,
            unlimited=row.is_unlimited,
            limit_value=row.limit_value,
            policy_value=row.policy_value,
            source=row.source,
            starts_at=row.starts_at,
            ends_at=row.ends_at,
        )

    @staticmethod
    def usage_output(row: BillingFeatureUsage) -> FeatureUsageOut:
        entitlement = row.entitlement
        remaining: Decimal | None = None
        if not entitlement.is_unlimited and entitlement.limit_value is not None:
            remaining = max(
                Decimal("0"),
                entitlement.limit_value - row.used_value - row.reserved_value,
            )
        return FeatureUsageOut(
            code=entitlement.feature_code_snapshot,
            used_value=row.used_value,
            reserved_value=row.reserved_value,
            limit_value=entitlement.limit_value,
            unlimited=entitlement.is_unlimited,
            remaining_value=remaining,
            period_ends_at=entitlement.ends_at,
        )


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
