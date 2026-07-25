from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import UniqueConstraint

from app.core.exceptions import AppException
from app.modules.auth.seed import BASE_PERMISSIONS
from app.modules.subscriptions.admin_schemas import BillingReconciliationIssueOut
from app.modules.subscriptions.audit_service import BillingAuditService
from app.modules.subscriptions.models import (
    BillingPlan,
    BillingSubscription,
    _reject_billing_audit_mutation,
)
from app.modules.subscriptions.reconciliation_service import (
    BillingReconciliationService,
)


class _AuditQuery:
    def __init__(self, row=None) -> None:
        self.row = row

    def filter(self, *_args):
        return self

    def one_or_none(self):
        return self.row


class _AuditDb:
    def __init__(self, existing=None) -> None:
        self.existing = existing
        self.added = []

    def query(self, *_args):
        return _AuditQuery(self.existing)

    def add(self, row):
        row.id = 1
        self.added.append(row)

    def flush(self):
        return None


def test_database_generated_slots_enforce_one_active_plan_and_subscription() -> None:
    plan_uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in BillingPlan.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    subscription_uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in BillingSubscription.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert BillingPlan.__table__.c.active_code.computed is not None
    assert BillingSubscription.__table__.c.current_user_id.computed is not None
    assert ("active_code",) in plan_uniques
    assert ("current_user_id",) in subscription_uniques


def test_audit_record_is_exact_once_and_payload_conflicts_are_rejected() -> None:
    db = _AuditDb()
    service = BillingAuditService(db)  # type: ignore[arg-type]
    row = service.record(
        event_key="subscription:1:activated",
        action="ACTIVATED",
        target_type="subscription",
        target_id=1,
        subscription_id=1,
        actor_type="user",
        actor_user_id=9,
    )
    assert row.event_key == "subscription:1:activated"
    assert db.added == [row]

    replay = BillingAuditService(_AuditDb(row)).record(  # type: ignore[arg-type]
        event_key=row.event_key,
        action=row.action,
        target_type=row.target_type,
        target_id=row.target_id,
        actor_type="user",
        actor_user_id=9,
    )
    assert replay is row

    with pytest.raises(AppException) as caught:
        BillingAuditService(_AuditDb(row)).record(  # type: ignore[arg-type]
            event_key=row.event_key,
            action="CANCELLED",
            target_type=row.target_type,
            target_id=row.target_id,
            actor_type="user",
            actor_user_id=9,
        )
    assert caught.value.code == "BILLING_AUDIT_IDEMPOTENCY_CONFLICT"


def test_audit_records_are_immutable_and_non_system_actor_is_required() -> None:
    with pytest.raises(RuntimeError):
        _reject_billing_audit_mutation(
            None, None, SimpleNamespace(id=4)
        )

    with pytest.raises(AppException) as caught:
        BillingAuditService(_AuditDb()).record(  # type: ignore[arg-type]
            event_key="invalid-actor",
            action="TEST",
            target_type="subscription",
            target_id=1,
            actor_type="admin",
            actor_user_id=None,
        )
    assert caught.value.code == "BILLING_AUDIT_ACTOR_REQUIRED"


def test_reconciliation_detects_scope_and_limit_mismatches() -> None:
    service = BillingReconciliationService(SimpleNamespace())  # type: ignore[arg-type]
    issues: list[BillingReconciliationIssueOut] = []
    entitlement = SimpleNamespace(
        user_id=1,
        period_id=2,
        feature_id=3,
        is_unlimited=False,
        limit_value=Decimal("10"),
    )
    usage = SimpleNamespace(
        id=8,
        user_id=9,
        period_id=2,
        feature_id=3,
        used_value=Decimal("8"),
        reserved_value=Decimal("4"),
    )

    service._check_usage(issues, entitlement, usage)

    assert {issue.code for issue in issues} == {
        "USAGE_SCOPE_MISMATCH",
        "USAGE_LIMIT_EXCEEDED",
    }


def test_hardening_permissions_are_seeded() -> None:
    codes = {item.code for item in BASE_PERMISSIONS}
    assert {"billing.audit.read", "billing.reconciliation.read"}.issubset(codes)
