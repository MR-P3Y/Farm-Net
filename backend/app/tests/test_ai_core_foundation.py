from dataclasses import FrozenInstanceError

import pytest
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint

from app.modules.ai.contracts import (
    AIProviderMessage,
    AIProviderRequest,
    AIProviderResult,
    AIProviderUsage,
)
from app.modules.ai.models import (
    AIAuditLog,
    AIContextConsent,
    AIConversation,
    AIDataDeletionRequest,
    AIExecutionAttempt,
    AIFeedback,
    AIMessage,
    AIRequest,
    AIUsageRecord,
)
from app.modules.auth.seed import BASE_PERMISSIONS


AI_TABLES = {
    "ai_conversations",
    "ai_context_consents",
    "ai_requests",
    "ai_messages",
    "ai_execution_attempts",
    "ai_usage_records",
    "ai_feedback",
    "ai_data_deletion_requests",
    "ai_audit_logs",
}


def _constraint_names(model, kind) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def test_barzegar_core_registers_nine_separate_tables() -> None:
    models = {
        AIConversation,
        AIContextConsent,
        AIRequest,
        AIMessage,
        AIExecutionAttempt,
        AIUsageRecord,
        AIFeedback,
        AIDataDeletionRequest,
        AIAuditLog,
    }
    assert {model.__tablename__ for model in models} == AI_TABLES


def test_ai_request_exact_once_context_and_quota_contracts_are_explicit() -> None:
    assert "uq_ai_requests_user_idempotency" in _constraint_names(
        AIRequest, UniqueConstraint
    )
    assert "ck_ai_requests_context_manifest" in _constraint_names(
        AIRequest, CheckConstraint
    )
    assert "ck_ai_requests_lifecycle" in _constraint_names(
        AIRequest, CheckConstraint
    )
    assert AIRequest.__table__.c.billing_reservation_id.unique is True

    foreign_targets = {
        element.target_fullname
        for constraint in AIRequest.__table__.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for element in constraint.elements
    }
    assert {
        "auth_users.id",
        "ai_conversations.id",
        "ai_context_consents.id",
        "billing_usage_reservations.id",
    } <= foreign_targets


def test_private_context_requires_real_farm_foreign_keys_and_consent_state() -> None:
    targets = {
        element.target_fullname
        for constraint in AIContextConsent.__table__.constraints
        if isinstance(constraint, ForeignKeyConstraint)
        for element in constraint.elements
    }
    assert {
        "auth_users.id",
        "farms.id",
        "farm_plots.id",
        "farm_crop_cycles.id",
    } == targets
    assert "ck_ai_context_consents_state" in _constraint_names(
        AIContextConsent, CheckConstraint
    )
    assert "ck_ai_context_consents_expiry" in _constraint_names(
        AIContextConsent, CheckConstraint
    )


def test_retention_feedback_usage_and_audit_have_exact_once_boundaries() -> None:
    assert "ck_ai_conversations_deletion_state" in _constraint_names(
        AIConversation, CheckConstraint
    )
    assert "uq_ai_deletion_user_idempotency" in _constraint_names(
        AIDataDeletionRequest, UniqueConstraint
    )
    assert "uq_ai_feedback_request_user" in _constraint_names(
        AIFeedback, UniqueConstraint
    )
    assert AIUsageRecord.__table__.c.request_id.unique is True
    assert AIUsageRecord.__table__.c.attempt_id.unique is True
    assert AIAuditLog.__table__.c.event_key.unique is True
    assert "ck_ai_audit_actor" in _constraint_names(AIAuditLog, CheckConstraint)


def test_ai_permissions_cover_owner_and_restricted_operations() -> None:
    codes = {permission.code for permission in BASE_PERMISSIONS}
    assert {
        "ai.conversations.create",
        "ai.conversations.read_own",
        "ai.conversations.manage_own",
        "ai.requests.create",
        "ai.requests.read_own",
        "ai.requests.cancel_own",
        "ai.context.use_own",
        "ai.feedback.create_own",
        "ai.data.delete_own",
        "ai.requests.read",
        "ai.feedback.read",
        "ai.usage.read",
        "ai.audit.read",
        "ai.retention.manage",
    } <= codes


def test_provider_contract_is_immutable_and_contains_no_secret_field() -> None:
    request = AIProviderRequest(
        request_id=10,
        messages=(AIProviderMessage(role="user", content="سلام"),),
        model_key="configured-model",
        prompt_policy_version="barzegar-v1",
        timeout_seconds=30,
        metadata={"trace_id": "trace-1"},
    )
    result = AIProviderResult(
        provider_request_id="provider-1",
        model_key="configured-model",
        content="پاسخ",
        finish_reason="stop",
        usage=AIProviderUsage(input_tokens=5, output_tokens=8),
        raw_metadata={},
    )

    assert request.request_id == 10
    assert result.usage.output_tokens == 8
    assert not hasattr(request, "api_key")
    assert not hasattr(result, "api_key")
    with pytest.raises(FrozenInstanceError):
        request.model_key = "changed"  # type: ignore[misc]
