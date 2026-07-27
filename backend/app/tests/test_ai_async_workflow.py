import hashlib
import inspect

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.main import app
from app.modules.ai.models import AIMessage, AIRequest
from app.modules.ai.schemas import AIRequestCreateIn, AIRequestOut
from app.modules.ai.workflow_service import AIWorkflowService
from app.modules.ai.workflow_service import AIWorkerService


def _constraint_names(model, kind) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def test_async_queue_has_lease_retry_and_exact_once_message_constraints() -> None:
    assert "ck_ai_requests_attempts" in _constraint_names(AIRequest, CheckConstraint)
    assert "ck_ai_requests_lease" in _constraint_names(AIRequest, CheckConstraint)
    assert "ix_ai_requests_queue" in {index.name for index in AIRequest.__table__.indexes}
    assert "uq_ai_message_request_kind" in _constraint_names(AIMessage, UniqueConstraint)
    assert "ck_ai_messages_request_kind" in _constraint_names(AIMessage, CheckConstraint)


def test_request_fingerprint_is_deterministic_and_payload_sensitive() -> None:
    first = AIWorkflowService._fingerprint(
        conversation_id=1,
        feature_code="ai.text_chat",
        request_kind="text",
        content="سلام برزگر",
    )
    replay = AIWorkflowService._fingerprint(
        conversation_id=1,
        feature_code="ai.text_chat",
        request_kind="text",
        content="سلام برزگر",
    )
    changed = AIWorkflowService._fingerprint(
        conversation_id=1,
        feature_code="ai.text_chat",
        request_kind="text",
        content="سؤال دیگر",
    )
    assert first == replay
    assert first != changed
    assert len(first) == 64
    assert (
        first
        == hashlib.sha256(
            (
                '{"content":"سلام برزگر","conversation_id":1,'
                '"feature_code":"ai.text_chat","prompt_policy_version":'
                '"barzegar-v1","request_kind":"text",'
                '"routing_policy_version":"routing-v1"}'
            ).encode()
        ).hexdigest()
    )


def test_request_input_is_closed_and_bounded() -> None:
    payload = AIRequestCreateIn(
        idempotency_key="request-123",
        content="سلام",
    )
    assert payload.feature_code == "ai.text_chat"
    with pytest.raises(ValidationError):
        AIRequestCreateIn(
            idempotency_key="short",
            content="سلام",
        )
    with pytest.raises(ValidationError):
        AIRequestCreateIn(
            idempotency_key="request-123",
            content="سلام",
            unknown=True,  # type: ignore[call-arg]
        )


def test_owner_response_hides_queue_and_idempotency_internals() -> None:
    assert {
        "idempotency_key",
        "request_fingerprint",
        "locked_by",
        "lease_expires_at",
        "attempt_count",
        "max_attempts",
    }.isdisjoint(AIRequestOut.model_fields)


def test_worker_claim_uses_skip_locked_lease_recovery_and_attempt_exhaustion() -> None:
    source = inspect.getsource(AIWorkerService.claim)
    assert "skip_locked=True" in source
    assert "WORKER_LEASE_EXPIRED" in source
    assert "AI_MAX_ATTEMPTS_EXHAUSTED" in source
    assert "attempt_count += 1" in source


def test_barzegar_owner_routes_are_registered_with_typed_contracts() -> None:
    paths = app.openapi()["paths"]
    expected = {
        ("post", "/api/v1/ai/conversations"),
        ("get", "/api/v1/ai/conversations"),
        ("get", "/api/v1/ai/conversations/{conversation_id}"),
        ("post", "/api/v1/ai/conversations/{conversation_id}/requests"),
        ("get", "/api/v1/ai/requests/{request_id}"),
        ("post", "/api/v1/ai/requests/{request_id}/cancel"),
    }
    assert all(method in paths[path] for method, path in expected)
    assert all(
        paths[path][method]["responses"].get("200")
        or paths[path][method]["responses"].get("201")
        or paths[path][method]["responses"].get("202")
        for method, path in expected
    )
