from sqlalchemy import CheckConstraint, UniqueConstraint

from app.main import app
from app.modules.auth.seed import BASE_PERMISSIONS
from app.modules.subscriptions.models import (
    BillingEntitlement,
    BillingFeature,
    BillingFeatureUsage,
    BillingPlan,
    BillingPlanFeature,
    BillingSubscription,
    BillingSubscriptionPeriod,
    BillingUsageReservation,
)
from app.modules.subscriptions.seed import FEATURES, FREE_VALUES


def test_subscription_foundation_has_eight_separate_tables() -> None:
    assert {
        BillingPlan.__tablename__,
        BillingFeature.__tablename__,
        BillingPlanFeature.__tablename__,
        BillingSubscription.__tablename__,
        BillingSubscriptionPeriod.__tablename__,
        BillingEntitlement.__tablename__,
        BillingFeatureUsage.__tablename__,
        BillingUsageReservation.__tablename__,
    } == {
        "billing_plans",
        "billing_features",
        "billing_plan_features",
        "billing_subscriptions",
        "billing_subscription_periods",
        "billing_entitlements",
        "billing_feature_usage",
        "billing_usage_reservations",
    }


def test_subscription_contract_preserves_toman_and_exact_once_keys() -> None:
    plan_checks = {
        constraint.name
        for constraint in BillingPlan.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    reservation_uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in BillingUsageReservation.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    entitlement_uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in BillingEntitlement.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    plan_uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in BillingPlan.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert "ck_billing_plans_currency_toman" in plan_checks
    assert ("code", "version") in plan_uniques
    assert ("idempotency_key",) in reservation_uniques
    assert ("period_id", "feature_id") in entitlement_uniques


def test_subscription_user_permissions_are_seeded() -> None:
    codes = {permission.code for permission in BASE_PERMISSIONS}

    assert {
        "billing.plans.public_read",
        "billing.subscription.read_own",
        "billing.subscription.manage_own",
        "billing.usage.read_own",
        "billing.entitlements.read",
    }.issubset(codes)


def test_subscription_read_routes_match_public_and_owner_boundaries() -> None:
    operations = {
        path: set(value)
        for path, value in app.openapi()["paths"].items()
        if path.startswith("/api/v1/billing/")
    }

    assert operations == {
        "/api/v1/billing/plans": {"get"},
        "/api/v1/billing/plans/{plan_code}": {"get"},
        "/api/v1/billing/subscription/me": {"get"},
        "/api/v1/billing/entitlements/me": {"get"},
        "/api/v1/billing/usage/me": {"get"},
    }


def test_free_catalog_defines_every_registered_feature_once() -> None:
    codes = [feature.code for feature in FEATURES]

    assert len(codes) == len(set(codes)) == 15
    assert set(FREE_VALUES) == set(codes)
    assert FREE_VALUES["ai.image_analysis"] == 1
    assert FREE_VALUES["farms.max_count"] == 1
