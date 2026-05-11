from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.admin.schemas import AdminUpdateVerificationStatusIn
from app.modules.admin.verification_service import AdminVerificationService
from app.modules.auth.dependencies import get_current_active_user, require_permission
from app.modules.auth.exceptions import PermissionDeniedError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository


router = APIRouter(
    prefix="/verifications",
    tags=["Admin Verifications"],
)


def _permission_for_status(status: str) -> str:
    if status == "under_review":
        return "verification.review"

    if status == "needs_revision":
        return "verification.needs_revision"

    if status == "approved":
        return "verification.approve"

    if status == "rejected":
        return "verification.reject"

    return "verification.review"


@router.get("")
def list_verifications(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    target_role: str | None = Query(default=None),
    user_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("verification.read")),
):
    service = AdminVerificationService(db)

    items, total = service.list_verifications(
        page=page,
        page_size=page_size,
        status=status,
        target_role=target_role,
        user_id=user_id,
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


@router.get("/{request_id}")
def get_verification_detail(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("verification.read")),
):
    service = AdminVerificationService(db)
    result = service.get_verification_detail(request_id=request_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{request_id}/status")
def update_verification_status(
    request_id: int,
    payload: AdminUpdateVerificationStatusIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    required_permission = _permission_for_status(payload.status)

    repo = AuthRepository(db)
    permissions = set(repo.get_user_permission_codes(current_user.id))

    if required_permission not in permissions:
        raise PermissionDeniedError()

    service = AdminVerificationService(db)

    result = service.update_verification_status(
        request_id=request_id,
        status=payload.status,
        note=payload.note,
        reviewer=current_user,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Verification status updated",
        meta={"trace_id": request.state.trace_id},
    )
