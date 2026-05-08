from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.admin.schemas import AdminUpdateUserStatusIn
from app.modules.admin.service import AdminAuthService
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser


router = APIRouter(
    prefix="/users",
    tags=["Admin Users"],
)


@router.get("")
def list_users(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("users.read")),
):
    service = AdminAuthService(db)

    items, total = service.list_users(
        page=page,
        page_size=page_size,
        q=q,
        status=status,
    )

    return success_response(
        data=[item.model_dump() for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/{user_id}")
def get_user_detail(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("users.read_detail")),
):
    service = AdminAuthService(db)
    result = service.get_user_detail(user_id)

    return success_response(
        data=result.model_dump(),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: AdminUpdateUserStatusIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("users.update_status")),
):
    service = AdminAuthService(db)

    result = service.update_user_status(
        user_id=user_id,
        status=payload.status,
    )

    return success_response(
        data=result.model_dump(),
        message="User status updated",
        meta={"trace_id": request.state.trace_id},
    )
