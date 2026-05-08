from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.admin.service import AdminAuthService
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser


router = APIRouter(
    tags=["Admin Roles"],
)


@router.get("/roles")
def list_roles(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("roles.read")),
):
    service = AdminAuthService(db)
    result = service.list_roles()

    return success_response(
        data=[item.model_dump() for item in result],
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/permissions")
def list_permissions(
    request: Request,
    module: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("permissions.read")),
):
    service = AdminAuthService(db)
    result = service.list_permissions(module=module)

    return success_response(
        data=[item.model_dump() for item in result],
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )
