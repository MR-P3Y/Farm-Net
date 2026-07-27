import inspect

from app.modules.ai import admin_router
from app.modules.ai.admin_schemas import AIAdminRequestOut
from app.modules.ai.admin_service import AIAdminService


def test_admin_request_contract_excludes_private_prompt_and_context() -> None:
    fields = set(AIAdminRequestOut.model_fields)
    assert {
        "id",
        "user_id",
        "feature_code",
        "request_kind",
        "status",
        "failure_code",
        "safety_code",
    } <= fields
    assert {
        "content",
        "context_manifest",
        "request_fingerprint",
        "idempotency_key",
    }.isdisjoint(fields)


def test_admin_ai_routes_use_separate_permissions() -> None:
    source = inspect.getsource(admin_router)
    assert 'require_permission("ai.requests.read")' in source
    assert 'require_permission("ai.usage.read")' in source
    assert 'require_permission("ai.feedback.read")' in source
    assert 'require_permission("ai.knowledge_sources.review")' in source
    assert 'require_permission("ai.audit.read")' in source


def test_knowledge_review_is_lifecycle_guarded_and_audited() -> None:
    submit = inspect.getsource(AIAdminService.submit_source)
    review = inspect.getsource(AIAdminService.review_source)
    assert 'row.status != "draft"' in submit
    assert 'row.status != "in_review"' in review
    assert "knowledge_source.submitted" in submit
    assert "reviewed_by_user_id" in review


def test_model_admin_contract_never_exposes_api_key() -> None:
    source = inspect.getsource(admin_router.list_models)
    assert "AIAdminModelOut" in source
    assert "api_key" not in source
