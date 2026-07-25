from math import ceil

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.farms.schemas import (
    FarmArchiveIn,
    FarmCreateIn,
    FarmOwnerDetailResponse,
    FarmOwnerListResponse,
    FarmUpdateIn,
)
from app.modules.farms.service import FarmService


router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post("", response_model=FarmOwnerDetailResponse, status_code=status.HTTP_201_CREATED)
def create_farm(
    payload: FarmCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmService(db).create(user=user, payload=payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Farm created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("", response_model=FarmOwnerListResponse)
def list_my_farms(
    request: Request,
    include_archived: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items, total = FarmService(db).list_own(
        user=user,
        include_archived=include_archived,
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


@router.get("/{farm_id}", response_model=FarmOwnerDetailResponse)
def get_my_farm(
    farm_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    result = FarmService(db).get_own(user=user, farm_id=farm_id)
    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{farm_id}", response_model=FarmOwnerDetailResponse)
def update_my_farm(
    farm_id: int,
    payload: FarmUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmService(db).update(user=user, farm_id=farm_id, payload=payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Farm updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{farm_id}/archive", response_model=FarmOwnerDetailResponse)
def archive_my_farm(
    farm_id: int,
    payload: FarmArchiveIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmService(db).archive(user=user, farm_id=farm_id, payload=payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Farm archived",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{farm_id}/restore", response_model=FarmOwnerDetailResponse)
def restore_my_farm(
    farm_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmService(db).restore(user=user, farm_id=farm_id)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Farm restored",
        meta={"trace_id": request.state.trace_id},
    )
