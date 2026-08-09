from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.favorites.enums import FavoriteSubjectType
from app.modules.favorites.service import FavoritesService


router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("")
def list_my_favorites(
    request: Request,
    subject_type: FavoriteSubjectType | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("favorites.read_own")),
):
    items, total = FavoritesService(db).list_own(
        user_id=user.id,
        subject_type=subject_type,
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


@router.get("/status/{subject_type}")
def favorite_status(
    subject_type: FavoriteSubjectType,
    request: Request,
    subject_ids: list[int] = Query(min_length=1, max_length=100),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("favorites.read_own")),
):
    result = FavoritesService(db).status(
        user_id=user.id,
        subject_type=subject_type,
        subject_ids=subject_ids,
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/{subject_type}/{subject_id}")
def add_favorite(
    subject_type: FavoriteSubjectType,
    subject_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("favorites.manage_own")),
):
    result, created = FavoritesService(db).add(
        user_id=user.id,
        subject_type=subject_type,
        subject_id=subject_id,
    )
    return success_response(
        data=result.model_dump(mode="json"),
        message="Favorite created" if created else "Favorite already exists",
        meta={"created": created, "trace_id": request.state.trace_id},
    )


@router.delete("/{subject_type}/{subject_id}")
def remove_favorite(
    subject_type: FavoriteSubjectType,
    subject_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("favorites.manage_own")),
):
    removed = FavoritesService(db).remove(
        user_id=user.id,
        subject_type=subject_type,
        subject_id=subject_id,
    )
    return success_response(
        data={"subject_type": subject_type.value, "subject_id": subject_id},
        message="Favorite removed" if removed else "Favorite did not exist",
        meta={"removed": removed, "trace_id": request.state.trace_id},
    )
