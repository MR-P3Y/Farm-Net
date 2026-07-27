from math import ceil

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.ai.admin_schemas import (
    AIAdminAuditOut,
    AIAdminFeedbackOut,
    AIAdminKnowledgeReviewIn,
    AIAdminKnowledgeSourceCreateIn,
    AIAdminKnowledgeSourceOut,
    AIAdminModelOut,
    AIAdminPolicyOut,
    AIAdminRequestOut,
    AIAdminUsageOut,
    AIEvaluationRunIn,
    AIEvaluationRunOut,
    AIEvaluationSuiteCreateIn,
)
from app.modules.ai.admin_service import AIAdminService
from app.modules.ai.evaluation import AIEvaluationService, EvaluationCandidate
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser


router = APIRouter(prefix="/admin/ai", tags=["Admin Barzegar AI"])


def _meta(request: Request, page: int | None = None, page_size: int | None = None, total: int = 0):
    value = {"trace_id": request.state.trace_id}
    if page is not None and page_size is not None:
        value.update(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if total else 0,
        )
    return value


@router.get("/overview")
def overview(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.requests.read")),
):
    return success_response(
        data=AIAdminService(db).overview().model_dump(mode="json"),
        meta=_meta(request),
    )


@router.get("/requests")
def list_requests(
    request: Request,
    status_filter: str | None = Query(default=None, alias="status"),
    request_kind: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.requests.read")),
):
    rows, total = AIAdminService(db).requests(
        status=status_filter, request_kind=request_kind, page=page, page_size=page_size
    )
    return success_response(
        data=[AIAdminRequestOut.model_validate(row).model_dump(mode="json") for row in rows],
        meta=_meta(request, page, page_size, total),
    )


@router.get("/usage")
def list_usage(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.usage.read")),
):
    rows, total = AIAdminService(db).usage(page=page, page_size=page_size)
    return success_response(
        data=[AIAdminUsageOut.model_validate(row).model_dump(mode="json") for row in rows],
        meta=_meta(request, page, page_size, total),
    )


@router.get("/feedback")
def list_feedback(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.feedback.read")),
):
    rows, total = AIAdminService(db).feedback(page=page, page_size=page_size)
    return success_response(
        data=[AIAdminFeedbackOut.model_validate(row).model_dump(mode="json") for row in rows],
        meta=_meta(request, page, page_size, total),
    )


@router.get("/knowledge-sources")
def list_sources(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.knowledge_sources.read")),
):
    rows = AIAdminService(db).knowledge_sources()
    return success_response(
        data=[
            AIAdminKnowledgeSourceOut.model_validate(row).model_dump(mode="json")
            for row in rows
        ],
        meta=_meta(request),
    )


@router.post("/knowledge-sources", status_code=status.HTTP_201_CREATED)
def create_source(
    payload: AIAdminKnowledgeSourceCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.knowledge_sources.create")),
):
    row = AIAdminService(db).create_source(actor=user, payload=payload)
    return success_response(
        data=AIAdminKnowledgeSourceOut.model_validate(row).model_dump(mode="json"),
        meta=_meta(request),
    )


@router.post("/knowledge-sources/{source_id}/submit")
def submit_source(
    source_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.knowledge_sources.update")),
):
    row = AIAdminService(db).submit_source(actor=user, source_id=source_id)
    return success_response(
        data=AIAdminKnowledgeSourceOut.model_validate(row).model_dump(mode="json"),
        meta=_meta(request),
    )


@router.post("/knowledge-sources/{source_id}/review")
def review_source(
    source_id: int,
    payload: AIAdminKnowledgeReviewIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.knowledge_sources.review")),
):
    row = AIAdminService(db).review_source(actor=user, source_id=source_id, payload=payload)
    return success_response(
        data=AIAdminKnowledgeSourceOut.model_validate(row).model_dump(mode="json"),
        meta=_meta(request),
    )


@router.get("/audit")
def list_audit(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.audit.read")),
):
    rows, total = AIAdminService(db).audits(page=page, page_size=page_size)
    return success_response(
        data=[AIAdminAuditOut.model_validate(row).model_dump(mode="json") for row in rows],
        meta=_meta(request, page, page_size, total),
    )


@router.get("/policies")
def list_policies(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.audit.read")),
):
    return success_response(
        data=[
            AIAdminPolicyOut.model_validate(row).model_dump(mode="json")
            for row in AIAdminService(db).policies()
        ],
        meta=_meta(request),
    )


@router.get("/models")
def list_models(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.usage.read")),
):
    return success_response(
        data=[
            AIAdminModelOut.model_validate(row).model_dump(mode="json")
            for row in AIAdminService(db).models()
        ],
        meta=_meta(request),
    )


@router.post("/evaluation/suites", status_code=status.HTTP_201_CREATED)
def create_evaluation_suite(
    payload: AIEvaluationSuiteCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.evaluation.manage")),
):
    row = AIEvaluationService(db).create_suite(actor=user, payload=payload)
    return success_response(
        data={
            "id": row.id,
            "suite_key": row.suite_key,
            "version": row.version,
            "title": row.title,
            "status": row.status,
            "minimum_pass_rate": str(row.minimum_pass_rate),
        },
        meta=_meta(request),
    )


@router.post("/evaluation/suites/{suite_id}/activate")
def activate_evaluation_suite(
    suite_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.evaluation.manage")),
):
    row = AIEvaluationService(db).activate_suite(suite_id=suite_id)
    return success_response(
        data={
            "id": row.id,
            "suite_key": row.suite_key,
            "version": row.version,
            "title": row.title,
            "status": row.status,
            "minimum_pass_rate": str(row.minimum_pass_rate),
        },
        meta=_meta(request),
    )


@router.post("/evaluation/runs")
def run_evaluation(
    payload: AIEvaluationRunIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("ai.evaluation.manage")),
):
    row = AIEvaluationService(db).run(
        suite_id=payload.suite_id,
        idempotency_key=payload.idempotency_key,
        model_configuration_id=payload.model_configuration_id,
        candidates=[
            EvaluationCandidate(case_key=item.case_key, output=item.output)
            for item in payload.candidates
        ],
    )
    return success_response(
        data=AIEvaluationRunOut.model_validate(row).model_dump(mode="json"),
        meta=_meta(request),
    )
