from datetime import date, datetime, timedelta
from decimal import Decimal
import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.main import app
from app.modules.ai.context_service import AIContextService, CONSENT_VERSION
from app.modules.ai.models import AIContextConsent
from app.modules.ai.schemas import AIContextConsentOut, AIRequestOut
from app.modules.ai import router as ai_router_module


def _constraint_names(model, kind) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def test_consent_idempotency_active_scope_and_hierarchy_are_database_enforced() -> None:
    assert "uq_ai_context_user_idempotency" in _constraint_names(AIContextConsent, UniqueConstraint)
    assert "uq_ai_context_active_scope" in _constraint_names(AIContextConsent, UniqueConstraint)
    assert "ck_ai_context_consents_active_scope" in _constraint_names(
        AIContextConsent, CheckConstraint
    )
    assert "ck_ai_context_consents_cycle_requires_plot" in _constraint_names(
        AIContextConsent, CheckConstraint
    )


def test_context_manifest_is_selected_minimal_and_freshness_bound() -> None:
    now = datetime.utcnow()
    consent = SimpleNamespace(
        id=8,
        user_id=7,
        farm_id=10,
        plot_id=20,
        crop_cycle_id=30,
        purpose="answer_question",
        consent_version=CONSENT_VERSION,
        status="active",
        expires_at=now + timedelta(hours=1),
    )
    farm = SimpleNamespace(
        id=10,
        name="مزرعه من",
        status="active",
        declared_area_sqm=Decimal("1200"),
        updated_at=now,
        description="private free text",
    )
    plot = SimpleNamespace(
        id=20,
        farm_id=10,
        name="قطعه شمالی",
        status="active",
        area_sqm=Decimal("600"),
        province_id=1,
        city_id=2,
        updated_at=now,
        boundary=[{"lat": 1, "lng": 2}],
    )
    cycle = SimpleNamespace(
        id=30,
        plot_id=20,
        crop_id=4,
        variety_id=5,
        title="گندم",
        status="active",
        planned_start_date=date(2026, 1, 1),
        planned_end_date=date(2026, 6, 1),
        updated_at=now,
        notes="private notes",
    )
    db = MagicMock()
    db.scalar.side_effect = [consent, farm, plot, cycle]

    _, manifest, captured_at = AIContextService(db).capture_manifest(
        user_id=7,
        consent_id=8,
        request_kind="text",
    )

    assert captured_at >= now
    assert manifest["farm"]["id"] == 10
    assert manifest["plot"]["id"] == 20
    assert manifest["crop_cycle"]["id"] == 30
    assert len(manifest["freshness_sha256"]) == 64
    serialized = str(manifest)
    assert "private free text" not in serialized
    assert "private notes" not in serialized
    assert "boundary" not in serialized


def test_consent_and_request_owner_contracts_hide_private_internals() -> None:
    assert {
        "idempotency_key",
        "selection_fingerprint",
        "active_scope",
        "revocation_reason",
        "user_id",
    }.isdisjoint(AIContextConsentOut.model_fields)
    assert {
        "context_manifest",
        "context_captured_at",
        "context_consent_id",
    }.isdisjoint(AIRequestOut.model_fields)


def test_selected_context_routes_are_typed_and_permission_protected() -> None:
    paths = app.openapi()["paths"]
    expected = {
        ("post", "/api/v1/ai/context-consents"),
        ("get", "/api/v1/ai/context-consents"),
        ("post", "/api/v1/ai/context-consents/{consent_id}/revoke"),
    }
    assert all(method in paths[path] for method, path in expected)
    source = inspect.getsource(ai_router_module)
    assert source.count('require_permission("ai.context.use_own")') == 3


def test_cross_user_or_archived_farm_is_indistinguishable_from_missing() -> None:
    db = MagicMock()
    db.scalar.return_value = None
    with pytest.raises(Exception) as error:
        AIContextService(db)._owned_selection(
            user_id=7,
            farm_id=999,
            plot_id=None,
            crop_cycle_id=None,
        )
    assert getattr(error.value, "code", None) == "AI_FARM_SELECTION_NOT_FOUND"
