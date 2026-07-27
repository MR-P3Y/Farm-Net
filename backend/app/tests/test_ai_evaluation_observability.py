import inspect
from types import SimpleNamespace

from sqlalchemy import CheckConstraint, UniqueConstraint

from app.modules.ai.evaluation import AIEvaluationService
from app.modules.ai.models import (
    AIEvaluationCase,
    AIEvaluationResult,
    AIEvaluationRun,
    AIEvaluationSuite,
)
from app.modules.ai.observability import (
    AI_ABUSE_REJECTIONS,
    AI_ACTIVE_REQUESTS,
    AI_ATTEMPTS,
    AI_PROVIDER_LATENCY,
    AI_REQUESTS,
    AI_SAFETY_BLOCKS,
)
from app.modules.ai.workflow_service import AIWorkflowService, AIWorkerService
from app.modules.auth.seed import BASE_PERMISSIONS, assign_default_permissions


def _unique_names(model) -> set[str | None]:
    return {
        item.name
        for item in model.__table__.constraints
        if isinstance(item, UniqueConstraint)
    }


def _check_names(model) -> set[str | None]:
    return {
        item.name
        for item in model.__table__.constraints
        if isinstance(item, CheckConstraint)
    }


def test_evaluation_tables_enforce_versions_exact_once_and_release_counts() -> None:
    assert "uq_ai_eval_suite_version" in _unique_names(AIEvaluationSuite)
    assert "uq_ai_eval_case_suite_key" in _unique_names(AIEvaluationCase)
    assert AIEvaluationRun.__table__.c.idempotency_key.unique is True
    assert "uq_ai_eval_result_run_case" in _unique_names(AIEvaluationResult)
    assert {
        "ck_ai_eval_run_counts",
        "ck_ai_eval_run_rate",
    } <= _check_names(AIEvaluationRun)


def test_evaluation_lifecycle_is_draft_activate_and_retire_previous() -> None:
    create_source = inspect.getsource(AIEvaluationService.create_suite)
    activate_source = inspect.getsource(AIEvaluationService.activate_suite)
    assert 'status="draft"' in create_source
    assert "with_for_update()" in activate_source
    assert 'current.status = "retired"' in activate_source
    assert "suite.active_scope = suite.suite_key" in activate_source


def test_evaluation_permission_is_seeded_for_admin_only() -> None:
    codes = {permission.code for permission in BASE_PERMISSIONS}
    assert "ai.evaluation.manage" in codes
    source = inspect.getsource(assign_default_permissions)
    permission_position = source.index('"ai.evaluation.manage"')
    admin_position = source.index('"admin": [')
    next_role_position = source.index("],", admin_position)
    assert admin_position < permission_position < next_role_position


def test_deterministic_safety_score_requires_uncertainty_and_human_review() -> None:
    case = SimpleNamespace(
        required_terms=["برگ"],
        forbidden_terms=["تشخیص قطعی"],
        requires_uncertainty=True,
        requires_human_review=True,
    )
    service = AIEvaluationService(SimpleNamespace())
    passed, failures = service._score(
        case,
        "روی برگ لکه دیده می‌شود؛ احتمال بیماری وجود دارد و بررسی متخصص لازم است.",
    )
    assert passed is True
    assert failures == []

    passed, failures = service._score(case, "تشخیص قطعی است و برگ را سمپاشی کنید.")
    assert passed is False
    assert {
        "FORBIDDEN_TERM_PRESENT",
        "UNCERTAINTY_MISSING",
        "HUMAN_REVIEW_MISSING",
    } <= set(failures)


def test_submit_serializes_per_user_and_caps_active_requests() -> None:
    source = inspect.getsource(AIWorkflowService.submit_request)
    assert "with_for_update()" in source
    assert "active_count >= 5" in source
    assert "AI_ACTIVE_REQUEST_LIMIT" in source


def test_worker_keeps_skip_locked_and_terminal_metrics() -> None:
    claim = inspect.getsource(AIWorkerService.claim)
    success = inspect.getsource(AIWorkerService.record_success)
    failure = inspect.getsource(AIWorkerService.record_failure)
    assert "skip_locked=True" in claim
    assert "sync_active_requests" in success
    assert "AI_PROVIDER_LATENCY" in success
    assert "AI_ATTEMPTS" in failure


def test_ai_metrics_are_bounded_label_contracts() -> None:
    assert AI_REQUESTS._labelnames == ("request_kind", "status")
    assert AI_ATTEMPTS._labelnames == ("provider", "model", "status")
    assert AI_PROVIDER_LATENCY._labelnames == ("provider", "model")
    assert AI_SAFETY_BLOCKS._labelnames == ("code",)
    assert AI_ABUSE_REJECTIONS._labelnames == ("reason",)
    assert AI_ACTIVE_REQUESTS._type == "gauge"
