from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.notifications.service import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("/me")
def list_my_notifications(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    channel: str | None = Query(default="in_app"),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("notifications.read")),
):
    service = NotificationService(db)

    items, total = service.list_user_notifications(
        recipient_user_id=current_user.id,
        status=status,
        channel=channel,
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


@router.get("/me/unread-count")
def my_unread_count(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("notifications.read")),
):
    service = NotificationService(db)

    count = service.unread_count(recipient_user_id=current_user.id)

    return success_response(
        data={"unread_count": count},
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/read-all")
def mark_all_notifications_read(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("notifications.manage")),
):
    service = NotificationService(db)

    count = service.mark_all_read(recipient_user_id=current_user.id)

    return success_response(
        data={"updated_count": count},
        message="All notifications marked as read",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("notifications.manage")),
):
    service = NotificationService(db)

    result = service.mark_read(
        notification_id=notification_id,
        recipient_user_id=current_user.id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Notification marked as read",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("notifications.manage")),
):
    service = NotificationService(db)

    result = service.soft_delete(
        notification_id=notification_id,
        recipient_user_id=current_user.id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Notification deleted",
        meta={"trace_id": request.state.trace_id},
    )
