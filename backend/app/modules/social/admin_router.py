from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.social.schemas import (
    SocialCategoryCreateIn,
    SocialCategoryUpdateIn,
    SocialPostModerationIn,
    SocialReportStatusUpdateIn,
)
from app.modules.social.service import SocialService


router = APIRouter(
    prefix="/admin/social",
    tags=["Admin Social"],
)


@router.get("/categories")
def list_social_categories_admin(
    request: Request,
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("social_categories.admin_read")),
):
    items = SocialService(db).list_categories_admin(q=q.strip() if q else None)
    return success_response(data=[item.model_dump(mode="json") for item in items], message="OK", meta={"trace_id": request.state.trace_id})


@router.post("/categories")
def create_social_category_admin(
    payload: SocialCategoryCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("social_categories.create")),
):
    item = SocialService(db).create_category(payload)
    return success_response(data=item.model_dump(mode="json"), message="Social category created", meta={"trace_id": request.state.trace_id})


@router.patch("/categories/{category_id}")
def update_social_category_admin(
    category_id: int,
    payload: SocialCategoryUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("social_categories.update")),
):
    item = SocialService(db).update_category(category_id=category_id, payload=payload)
    return success_response(data=item.model_dump(mode="json"), message="Social category updated", meta={"trace_id": request.state.trace_id})


@router.get("/reports")
def list_social_reports_admin(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    target_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("social.admin_read")),
):
    service = SocialService(db)

    items, total = service.list_reports_admin(
        target_type=target_type,
        status=status,
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


@router.patch("/reports/{report_id}/status")
def update_social_report_status_admin(
    report_id: int,
    payload: SocialReportStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("social.admin_moderate")),
):
    service = SocialService(db)

    result = service.update_report_status_admin(
        admin_user_id=current_user.id,
        report_id=report_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Social report status updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/posts")
def list_social_posts_admin(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    post_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("social.admin_read")),
):
    service = SocialService(db)

    items, total = service.list_admin_posts(
        status=status,
        post_type=post_type,
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


@router.patch("/posts/{post_id}/hide")
def hide_social_post_admin(
    post_id: int,
    payload: SocialPostModerationIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("social.admin_moderate")),
):
    service = SocialService(db)

    result = service.hide_post_admin(
        moderator_user_id=current_user.id,
        post_id=post_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Social post hidden",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/posts/{post_id}/unhide")
def unhide_social_post_admin(
    post_id: int,
    payload: SocialPostModerationIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("social.admin_moderate")),
):
    service = SocialService(db)

    result = service.unhide_post_admin(
        moderator_user_id=current_user.id,
        post_id=post_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Social post unhidden",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/comments")
def list_social_comments_admin(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    post_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("social.admin_read")),
):
    service = SocialService(db)

    items, total = service.list_admin_comments(
        status=status,
        post_id=post_id,
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


@router.patch("/comments/{comment_id}/hide")
def hide_social_comment_admin(
    comment_id: int,
    payload: SocialPostModerationIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("social.admin_moderate")),
):
    service = SocialService(db)

    result = service.hide_comment_admin(
        moderator_user_id=current_user.id,
        comment_id=comment_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Social comment hidden",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/comments/{comment_id}/unhide")
def unhide_social_comment_admin(
    comment_id: int,
    payload: SocialPostModerationIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("social.admin_moderate")),
):
    service = SocialService(db)

    result = service.unhide_comment_admin(
        moderator_user_id=current_user.id,
        comment_id=comment_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Social comment unhidden",
        meta={"trace_id": request.state.trace_id},
    )
