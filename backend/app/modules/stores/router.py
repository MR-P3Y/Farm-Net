from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.stores.schemas import (
    StoreCreateIn,
    StoreMemberCreateIn,
    StoreMemberUpdateIn,
    StoreUpdateIn,
)
from app.modules.stores.service import StoreService


router = APIRouter(
    prefix="/stores",
    tags=["Stores"],
)


@router.post("")
def create_store(
    payload: StoreCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.create")),
):
    service = StoreService(db)

    result = service.create_my_store(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Store created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me")
def get_my_store(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.read")),
):
    service = StoreService(db)
    result = service.get_my_store(user=current_user)

    return success_response(
        data=result.model_dump(mode="json") if result else None,
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/{store_id}")
def get_store(
    store_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.read")),
):
    service = StoreService(db)

    result = service.get_my_store_by_id(
        user=current_user,
        store_id=store_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/{store_id}")
def update_store(
    store_id: int,
    payload: StoreUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.update")),
):
    service = StoreService(db)

    result = service.update_my_store(
        user=current_user,
        store_id=store_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Store updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{store_id}/submit")
def submit_store(
    store_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.submit")),
):
    service = StoreService(db)

    result = service.submit_my_store(
        user=current_user,
        store_id=store_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Store submitted for review",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/{store_id}/status-history")
def list_store_status_history(
    store_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.read")),
):
    service = StoreService(db)

    result = service.list_my_store_status_history(
        user=current_user,
        store_id=store_id,
    )

    return success_response(
        data=[item.model_dump(mode="json") for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/{store_id}/members")
def list_store_members(
    store_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.manage_members")),
):
    service = StoreService(db)

    result = service.list_store_members(
        user=current_user,
        store_id=store_id,
    )

    return success_response(
        data=[item.model_dump(mode="json") for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.post("/{store_id}/members")
def add_store_member(
    store_id: int,
    payload: StoreMemberCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.manage_members")),
):
    service = StoreService(db)

    result = service.add_store_member(
        user=current_user,
        store_id=store_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Store member added",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{store_id}/members/{member_id}")
def update_store_member(
    store_id: int,
    member_id: int,
    payload: StoreMemberUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.manage_members")),
):
    service = StoreService(db)

    result = service.update_store_member(
        user=current_user,
        store_id=store_id,
        member_id=member_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Store member updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/{store_id}/members/{member_id}")
def remove_store_member(
    store_id: int,
    member_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("stores.manage_members")),
):
    service = StoreService(db)

    result = service.remove_store_member(
        user=current_user,
        store_id=store_id,
        member_id=member_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Store member removed",
        meta={"trace_id": request.state.trace_id},
    )
