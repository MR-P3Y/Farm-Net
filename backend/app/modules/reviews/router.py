from math import ceil

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.reviews.enums import ReviewStatus
from app.modules.reviews.schemas import (
    ReviewCreateIn,
    ReviewOwnerDetailResponse,
    ReviewOwnerListResponse,
    ReviewUpdateIn,
)
from app.modules.reviews.service import ReviewsService


router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewOwnerDetailResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("reviews.create")),
):
    result = ReviewsService(db).create(user=user, payload=payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Review created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me", response_model=ReviewOwnerListResponse)
def list_my_reviews(
    request: Request,
    review_status: ReviewStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("reviews.read_own")),
):
    items, total = ReviewsService(db).list_own(
        user=user,
        status=review_status,
        page=page,
        page_size=page_size,
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


@router.get("/me/{review_id}", response_model=ReviewOwnerDetailResponse)
def get_my_review(
    review_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("reviews.read_own")),
):
    result = ReviewsService(db).get_own(user=user, review_id=review_id)
    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/me/{review_id}", response_model=ReviewOwnerDetailResponse)
def update_my_review(
    review_id: int,
    payload: ReviewUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("reviews.manage_own")),
):
    result = ReviewsService(db).update(
        user=user,
        review_id=review_id,
        payload=payload,
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="Review updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/me/{review_id}", response_model=ReviewOwnerDetailResponse)
def delete_my_review(
    review_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("reviews.manage_own")),
):
    result = ReviewsService(db).delete(user=user, review_id=review_id)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Review deleted",
        meta={"trace_id": request.state.trace_id},
    )
