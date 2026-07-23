from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.reviews.enums import ReviewReportStatus, ReviewStatus
from app.modules.reviews.schemas import ReviewModerationIn, ReviewReportResolutionIn
from app.modules.reviews.service import ReviewsService


router = APIRouter(prefix="/admin/reviews", tags=["Admin Reviews"])


@router.get("/reports")
def list_reports(
    request: Request,
    status: ReviewReportStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("review_reports.admin_read")),
):
    items, total = ReviewsService(db).list_admin_reports(
        status=status, page=page, page_size=page_size
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.patch("/reports/{report_id}/status")
def resolve_report(
    report_id: int,
    payload: ReviewReportResolutionIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("review_reports.admin_resolve")),
):
    item = ReviewsService(db).resolve_report(
        admin_user_id=user.id, report_id=report_id, payload=payload
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Review report updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("")
def list_reviews(
    request: Request,
    status: ReviewStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("reviews.admin_read")),
):
    items, total = ReviewsService(db).list_admin_reviews(
        status=status, page=page, page_size=page_size
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.patch("/{review_id}/status")
def moderate_review(
    review_id: int,
    payload: ReviewModerationIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("reviews.admin_moderate")),
):
    item = ReviewsService(db).moderate_review(
        admin_user_id=user.id, review_id=review_id, payload=payload
    )
    return success_response(
        data=item.model_dump(mode="json"),
        message="Review moderated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/{review_id}/moderation-logs")
def list_moderation_logs(
    review_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("reviews.admin_read")),
):
    items = ReviewsService(db).moderation_logs(review_id=review_id)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )
