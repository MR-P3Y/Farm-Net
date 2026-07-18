from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.rentals.schemas import LessorProfileInput
from app.modules.rentals.service import RentalService


router = APIRouter(prefix="/rentals", tags=["Equipment Rental"])


@router.get("/categories")
def list_rental_categories(
    request: Request, q: str | None = Query(default=None), db: Session = Depends(get_db)
):
    items = RentalService(db).list_categories(active_only=True, q=q)
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"total": len(items), "trace_id": request.state.trace_id},
    )


@router.get("/me/lessor-profile")
def get_my_lessor_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_lessors.profile_manage")),
):
    result = RentalService(db).get_my_profile(user)
    return success_response(
        data=result.model_dump(mode="json") if result else None,
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/me/lessor-profile")
def save_my_lessor_profile(
    payload: LessorProfileInput,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_lessors.profile_manage")),
):
    result = RentalService(db).save_my_profile(user, payload)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Lessor profile saved",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/me/lessor-profile/submit")
def submit_my_lessor_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("rental_lessors.profile_manage")),
):
    result = RentalService(db).submit_my_profile(user)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Lessor profile submitted",
        meta={"trace_id": request.state.trace_id},
    )
