from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import AppException
from app.modules.subscriptions.lifecycle_service import SubscriptionLifecycleService
from app.modules.subscriptions.models import (
    BillingEntitlement,
    BillingFeature,
    BillingFeatureUsage,
    BillingPlanFeature,
)


class _CollectingDb:
    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, item: object) -> None:
        if getattr(item, "id", None) is None:
            item.id = len(self.added) + 1
        self.added.append(item)

    def flush(self) -> None:
        return None


def test_entitlement_snapshot_creates_usage_only_for_enabled_metered_feature() -> None:
    db = _CollectingDb()
    service = SubscriptionLifecycleService(db)  # type: ignore[arg-type]
    feature = BillingFeature(
        id=4,
        code="ai.text_chat",
        name="AI text",
        module="ai",
        value_kind="integer",
        unit="request",
        is_metered=True,
        is_safety_exempt=False,
        status="active",
    )
    value = BillingPlanFeature(
        feature=feature,
        is_enabled=True,
        is_unlimited=False,
        numeric_value=Decimal("20"),
    )
    start = datetime.now()
    subscription = SimpleNamespace(id=10)
    period = SimpleNamespace(id=11, starts_at=start, ends_at=start + timedelta(days=30))

    service._snapshot_entitlements(
        user_id=3,
        subscription=subscription,  # type: ignore[arg-type]
        period=period,  # type: ignore[arg-type]
        values=[value],
    )

    entitlement = next(item for item in db.added if isinstance(item, BillingEntitlement))
    usage = next(item for item in db.added if isinstance(item, BillingFeatureUsage))
    assert entitlement.feature_code_snapshot == "ai.text_chat"
    assert entitlement.limit_value == Decimal("20")
    assert usage.used_value == usage.reserved_value == Decimal("0")


def test_disabled_boolean_snapshot_is_not_metered_or_enabled() -> None:
    db = _CollectingDb()
    service = SubscriptionLifecycleService(db)  # type: ignore[arg-type]
    feature = BillingFeature(
        id=5,
        code="ai.smart_diary",
        name="Smart diary",
        module="ai",
        value_kind="boolean",
        is_metered=False,
        is_safety_exempt=False,
        status="active",
    )
    value = BillingPlanFeature(
        feature=feature,
        is_enabled=True,
        is_unlimited=False,
        boolean_value=False,
    )
    start = datetime.now()

    service._snapshot_entitlements(
        user_id=3,
        subscription=SimpleNamespace(id=10),  # type: ignore[arg-type]
        period=SimpleNamespace(  # type: ignore[arg-type]
            id=11, starts_at=start, ends_at=start + timedelta(days=30)
        ),
        values=[value],
    )

    entitlement = next(item for item in db.added if isinstance(item, BillingEntitlement))
    assert entitlement.is_enabled is False
    assert not any(isinstance(item, BillingFeatureUsage) for item in db.added)


def test_version_conflict_exposes_current_version() -> None:
    with pytest.raises(AppException) as caught:
        SubscriptionLifecycleService._check_version(
            SimpleNamespace(version=4),  # type: ignore[arg-type]
            expected_version=3,
        )

    assert caught.value.code == "BILLING_SUBSCRIPTION_VERSION_CONFLICT"
    assert caught.value.status_code == 409
    assert caught.value.details == {"current_version": 4}
