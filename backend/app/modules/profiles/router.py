from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import AuthUser
from app.modules.profiles.schemas import ProfileUpdateIn
from app.modules.profiles.service import ProfileService


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.get("/me")
def get_my_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)
    result = service.get_my_profile(current_user)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/me")
def update_my_profile(
    payload: ProfileUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    service = ProfileService(db)

    result = service.update_my_profile(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Profile updated",
        meta={"trace_id": request.state.trace_id},
    )
