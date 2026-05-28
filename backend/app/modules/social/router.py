from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.social.schemas import (
    SocialPostCreateIn,
    SocialPostListFilter,
)
from app.modules.social.service import SocialService


router = APIRouter(
    prefix="/social",
    tags=["Social"],
)


@router.get("/categories")
def list_social_categories(
    request: Request,
    db: Session = Depends(get_db),
):
    service = SocialService(db)
    items = service.list_categories()

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "total": len(items),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/posts")
def list_social_posts(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: int | None = Query(default=None, ge=1),
    post_type: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = SocialService(db)

    items, total = service.list_published_posts(
        filters=SocialPostListFilter(
            category_id=category_id,
            post_type=post_type,
            q=q,
            page=page,
            page_size=page_size,
        )
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


@router.post("/posts")
def create_social_post(
    payload: SocialPostCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("social.post_create")),
):
    service = SocialService(db)

    result = service.create_post(
        author_user_id=current_user.id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Social post created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/posts/{post_id}")
def get_social_post_detail(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    service = SocialService(db)

    result = service.get_published_post(post_id=post_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me/posts")
def list_my_social_posts(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("social.read")),
):
    service = SocialService(db)

    items, total = service.list_my_posts(
        user_id=current_user.id,
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


@router.delete("/posts/{post_id}")
def delete_own_social_post(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("social.post_manage_own")),
):
    service = SocialService(db)

    result = service.soft_delete_own_post(
        user_id=current_user.id,
        post_id=post_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Social post deleted",
        meta={"trace_id": request.state.trace_id},
    )
