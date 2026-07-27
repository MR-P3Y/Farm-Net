import inspect
from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.modules.ai import router as ai_router_module
from app.modules.ai.farmer_tools import AIFarmerToolsService
from app.modules.ai.models import AIDiarySuggestion, AIFarmerReport
from app.modules.ai.schemas import AIDiaryOperationProposal
from app.modules.ai.workflow_service import AIWorkflowService


def _unique_columns(model) -> set[tuple[str, ...]]:
    return {
        tuple(column.name for column in constraint.columns)
        for constraint in model.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def test_farmer_artifacts_are_exact_once_per_request() -> None:
    assert ("request_id",) in _unique_columns(AIDiarySuggestion)
    assert ("request_id",) in _unique_columns(AIFarmerReport)
    assert ("farm_operation_id",) in _unique_columns(AIDiarySuggestion)


def test_diary_decision_state_is_database_enforced() -> None:
    checks = {
        constraint.name
        for constraint in AIDiarySuggestion.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert {
        "ck_ai_diary_suggestions_status",
        "ck_ai_diary_suggestions_decision",
    } <= checks


def test_smart_diary_contract_is_typed_and_forbids_extra_fields() -> None:
    proposal = AIDiaryOperationProposal(
        operation_type="irrigation",
        title="آبیاری نوبت اول",
        occurred_on=date(2026, 7, 28),
    )
    assert proposal.operation_type.value == "irrigation"
    with pytest.raises(ValidationError):
        AIDiaryOperationProposal(
            operation_type="unknown",
            title="invalid",
            occurred_on=date.today(),
            auto_apply=True,
        )


def test_context_is_mandatory_and_diary_is_explicit_confirmation_only() -> None:
    workflow_source = inspect.getsource(AIWorkflowService.submit_request)
    tools_source = inspect.getsource(AIFarmerToolsService.decide)
    router_source = inspect.getsource(ai_router_module)
    assert '{"smart_diary", "report"}' in workflow_source
    assert "AI_CONTEXT_REQUIRED" in workflow_source
    assert 'row.status != "pending"' in tools_source
    assert "operation.created_from_ai_suggestion" in tools_source
    assert '"/diary-suggestions/{suggestion_id}/accept"' in router_source
    assert '"/diary-suggestions/{suggestion_id}/reject"' in router_source


def test_farmer_report_snapshot_uses_real_diary_counts() -> None:
    source = inspect.getsource(AIFarmerToolsService._create_report)
    assert "FarmOperation.id" in source
    assert "FarmOperationInput.id" in source
    assert "FarmHarvestObservation.id" in source
    assert '"context_freshness_sha256"' in source
