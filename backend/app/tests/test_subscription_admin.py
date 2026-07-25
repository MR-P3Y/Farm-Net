from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.core.exceptions import AppException
from app.main import app
from app.modules.subscriptions.admin_schemas import (
    AdminManualActivateIn,
    AdminPlanCreateIn,
    AdminPlanFeatureIn,
)
from app.modules.subscriptions.admin_service import AdminSubscriptionService
from app.modules.subscriptions.models import BillingFeature


def test_admin_subscription_routes_are_explicit_and_typed() -> None:
    operations = {
        path: set(value)
        for path, value in app.openapi()["paths"].items()
        if path.startswith("/api/v1/admin/billing/")
    }
    assert operations == {
        "/api/v1/admin/billing/plans": {"get", "post"},
        "/api/v1/admin/billing/plans/{plan_id}": {"patch"},
        "/api/v1/admin/billing/plans/{plan_id}/status": {"patch"},
        "/api/v1/admin/billing/subscriptions": {"get"},
        "/api/v1/admin/billing/subscriptions/{subscription_id}": {"get"},
        "/api/v1/admin/billing/subscriptions/manual-activate": {"post"},
        "/api/v1/admin/billing/subscriptions/{subscription_id}/cancel": {"patch"},
        "/api/v1/admin/billing/audit": {"get"},
        "/api/v1/admin/billing/reconciliation": {"get"},
    }


def test_plan_input_enforces_toman_shape_and_normalizes_code() -> None:
    payload = AdminPlanCreateIn(
        code="Farmer_Plus",
        name="Farmer Plus",
        billing_period="monthly",
        price_toman=Decimal("250000"),
        features=[
            AdminPlanFeatureIn(
                feature_code="ai.text_chat",
                numeric_value=Decimal("100"),
            )
        ],
    )
    assert payload.code == "farmer_plus"
    assert payload.price_toman == Decimal("250000")

    with pytest.raises(ValidationError):
        AdminManualActivateIn(user_id=1, plan_id=1, reason="x")


def test_feature_value_validation_rejects_missing_or_invalid_unlimited() -> None:
    metered = BillingFeature(
        code="ai.text_chat",
        name="AI",
        module="ai",
        value_kind="integer",
        is_metered=True,
        is_safety_exempt=False,
        status="active",
    )
    with pytest.raises(AppException) as missing:
        AdminSubscriptionService._validate_feature_value(
            metered,
            AdminPlanFeatureIn(feature_code=metered.code),
        )
    assert missing.value.code == "BILLING_FEATURE_VALUE_REQUIRED"

    boolean = BillingFeature(
        code="reports.export_pdf",
        name="PDF",
        module="reports",
        value_kind="boolean",
        is_metered=False,
        is_safety_exempt=False,
        status="active",
    )
    with pytest.raises(AppException) as unlimited:
        AdminSubscriptionService._validate_feature_value(
            boolean,
            AdminPlanFeatureIn(
                feature_code=boolean.code,
                unlimited=True,
            ),
        )
    assert unlimited.value.code == "BILLING_FEATURE_UNLIMITED_INVALID"


def test_admin_subscription_summary_exposes_provenance_without_raw_user() -> None:
    plan = SimpleNamespace(
        id=7,
        code="professional",
        name="Professional",
        price_toman=Decimal("900000"),
        currency="TOMAN",
    )
    row = SimpleNamespace(
        id=20,
        user_id=5,
        status="active",
        plan_id=7,
        plan=plan,
        starts_at=datetime(2026, 7, 26),
        current_period_ends_at=datetime(2026, 8, 25),
        grace_ends_at=None,
        auto_renew=False,
        cancel_at_period_end=False,
        activation_source="admin",
        activated_by_user_id=1,
        activation_reason="Support grant",
        version=1,
        created_at=datetime(2026, 7, 26),
    )
    output = AdminSubscriptionService._subscription_summary(row, {5: "farmer@example.test"})
    assert output.user_label == "farmer@example.test"
    assert output.activation_source == "admin"
    assert output.currency == "TOMAN"
