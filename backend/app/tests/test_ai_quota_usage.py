from decimal import Decimal
from types import SimpleNamespace

from sqlalchemy import CheckConstraint

from app.modules.ai.contracts import AIProviderUsage
from app.modules.ai.models import AIModelConfiguration, AIUsageRecord
from app.modules.ai.quota_bridge import METERED_AI_FEATURES
from app.modules.ai.reconciliation import AIUsageReconciliationService
from app.modules.ai.workflow_service import AIWorkerService


def _constraint_names(model, kind) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def test_ai_metering_uses_existing_subscription_feature_contract() -> None:
    assert METERED_AI_FEATURES == {
        "ai.text_chat",
        "ai.farm_context",
        "ai.deep_analysis",
        "ai.image_analysis",
    }
    assert "ai.smart_diary" not in METERED_AI_FEATURES
    assert "ai.report_export" not in METERED_AI_FEATURES


def test_technical_cost_is_toman_only_and_requires_complete_versioned_rates() -> None:
    assert AIUsageRecord.__table__.c.provider_cost_currency.type.length == 5
    assert "ck_ai_usage_cost_pair" in _constraint_names(AIUsageRecord, CheckConstraint)
    assert "ck_ai_model_configuration_toman_rates" in _constraint_names(
        AIModelConfiguration, CheckConstraint
    )

    model = SimpleNamespace(
        input_cost_per_million_toman=Decimal("100000"),
        cached_input_cost_per_million_toman=Decimal("20000"),
        output_cost_per_million_toman=Decimal("300000"),
    )
    db = SimpleNamespace(get=lambda _model, _id: model)
    cost = AIWorkerService(db)._provider_cost_toman(
        model_configuration_id=5,
        usage=AIProviderUsage(
            input_tokens=1000,
            cached_input_tokens=200,
            output_tokens=500,
        ),
    )
    assert cost == Decimal("234.00000000")

    model.output_cost_per_million_toman = None
    assert (
        AIWorkerService(db)._provider_cost_toman(
            model_configuration_id=5,
            usage=AIProviderUsage(input_tokens=1, output_tokens=1),
        )
        is None
    )


def test_usage_and_request_exact_once_links_remain_unique() -> None:
    assert AIUsageRecord.__table__.c.request_id.unique is True
    assert AIUsageRecord.__table__.c.attempt_id.unique is True


def test_reconciliation_requires_finalize_only_for_usable_success() -> None:
    request = SimpleNamespace(
        id=10,
        user_id=3,
        feature_code="ai.text_chat",
        status="succeeded",
        billing_reservation_id=7,
    )
    reservation = SimpleNamespace(
        user_id=3,
        feature_code_snapshot="ai.text_chat",
        status="finalized",
    )
    technical = SimpleNamespace(request_id=10)
    assert (
        AIUsageReconciliationService._issue_code(
            request=request,
            reservation=reservation,
            technical_usage=technical,
        )
        is None
    )
    reservation.status = "reserved"
    assert (
        AIUsageReconciliationService._issue_code(
            request=request,
            reservation=reservation,
            technical_usage=technical,
        )
        == "AI_BILLING_SUCCESS_NOT_FINALIZED"
    )
    request.status = "failed"
    reservation.status = "released"
    assert (
        AIUsageReconciliationService._issue_code(
            request=request,
            reservation=reservation,
            technical_usage=None,
        )
        is None
    )
