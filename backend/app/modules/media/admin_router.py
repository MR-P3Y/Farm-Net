from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.media.schemas import AdminMediaStatusUpdateIn
from app.modules.media.service import MediaService


router = APIRouter(
    prefix="/admin/media",
    tags=["Admin Media"],
)


@router.get("")
def list_admin_media(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    purpose: str | None = Query(default=None),
    visibility: str | None = Query(default=None),
    status: str | None = Query(default=None),
    owner_user_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("media.admin_read")),
):
    service = MediaService(db)

    items, total = service.list_admin_media(
        purpose=purpose,
        visibility=visibility,
        status=status,
        owner_user_id=owner_user_id,
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


@router.get("/{file_key}")
def get_admin_media(
    file_key: str,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("media.admin_read")),
):
    service = MediaService(db)

    result = service.get_admin_media(file_key=file_key)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{file_key}/status")
def update_admin_media_status(
    file_key: str,
    payload: AdminMediaStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("media.admin_manage")),
):
    service = MediaService(db)

    result = service.update_admin_media_status(
        file_key=file_key,
        payload=payload,
        actor_user_id=current_user.id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Media status updated",
        meta={"trace_id": request.state.trace_id},
    )
