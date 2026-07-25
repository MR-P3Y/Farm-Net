from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.farms.admin_service import AdminFarmSupportService
from app.modules.farms.enums import FarmStatus
from app.modules.farms.schemas import (
    AdminFarmAuditListResponse,
    AdminFarmDetailResponse,
    AdminFarmListResponse,
)

router = APIRouter(prefix="/admin/farms", tags=["Admin Farm Support"])


@router.get("", response_model=AdminFarmListResponse)
def list_farms(
    request: Request,
    q: str | None = Query(default=None, max_length=180),
    owner_user_id: int | None = Query(default=None, ge=1),
    status: FarmStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("farms.admin_read")),
):
    items, total = AdminFarmSupportService(db).list_farms(
        q=q, owner_user_id=owner_user_id, status=status,
        page=page, page_size=page_size,
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items], message="OK",
        meta=_meta(request, page, page_size, total),
    )


@router.get("/{farm_id}", response_model=AdminFarmDetailResponse)
def farm_detail(
    farm_id: int, request: Request, db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("farms.admin_read")),
):
    item = AdminFarmSupportService(db).detail(farm_id)
    return success_response(
        data=item.model_dump(mode="json"), message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/{farm_id}/audit", response_model=AdminFarmAuditListResponse)
def farm_audit(
    farm_id: int, request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("farms.admin_read")),
):
    items, total = AdminFarmSupportService(db).audit(
        farm_id=farm_id, page=page, page_size=page_size
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in items], message="OK",
        meta=_meta(request, page, page_size, total),
    )


def _meta(request: Request, page: int, page_size: int, total: int) -> dict:
    return {
        "page": page, "page_size": page_size, "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
        "trace_id": request.state.trace_id,
    }
