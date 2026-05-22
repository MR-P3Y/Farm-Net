from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.notifications.schemas import NotificationSystemMessageIn
from app.modules.notifications.service import NotificationService


router = APIRouter(
    prefix="/admin/notifications",
    tags=["Admin Notifications"],
)


@router.get("")
def list_admin_notifications(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    channel: str | None = Query(default=None),
    recipient_user_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("notifications.admin_read")),
):
    service = NotificationService(db)

    items, total = service.list_admin_notifications(
        status=status,
        channel=channel,
        recipient_user_id=recipient_user_id,
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


@router.post("/system-message")
def create_system_message(
    payload: NotificationSystemMessageIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(
        require_permission("notifications.system_message")
    ),
):
    service = NotificationService(db)

    result = service.create_system_message(
        payload=payload,
        actor_user_id=current_user.id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="System message created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/{notification_id}")
def get_admin_notification(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("notifications.admin_read")),
):
    service = NotificationService(db)

    result = service.get_admin_notification(
        notification_id=notification_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )
