from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.admin.schemas import AdminUpdateStoreStatusIn
from app.modules.admin.store_service import AdminStoreService
from app.modules.auth.dependencies import get_current_active_user, require_permission
from app.modules.auth.exceptions import PermissionDeniedError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository


router = APIRouter(
    prefix="/stores",
    tags=["Admin Stores"],
)


def _permission_for_status(status: str) -> str:
    if status == "approved":
        return "stores.approve"

    if status == "rejected":
        return "stores.reject"

    if status == "suspended":
        return "stores.suspend"

    return "stores.admin_review"


@router.get("")
def list_stores(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    owner_user_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("stores.admin_read")),
):
    service = AdminStoreService(db)

    items, total = service.list_stores(
        page=page,
        page_size=page_size,
        status=status,
        owner_user_id=owner_user_id,
        q=q,
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


@router.get("/{store_id}")
def get_store_detail(
    store_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("stores.admin_read")),
):
    service = AdminStoreService(db)

    result = service.get_store_detail(store_id=store_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{store_id}/status")
def update_store_status(
    store_id: int,
    payload: AdminUpdateStoreStatusIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    required_permission = _permission_for_status(payload.status)

    repo = AuthRepository(db)
    permissions = set(repo.get_user_permission_codes(current_user.id))

    if required_permission not in permissions:
        raise PermissionDeniedError()

    service = AdminStoreService(db)

    result = service.update_store_status(
        store_id=store_id,
        status=payload.status,
        note=payload.note,
        reviewer=current_user,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Store status updated",
        meta={"trace_id": request.state.trace_id},
    )
