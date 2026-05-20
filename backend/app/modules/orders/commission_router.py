from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.orders.schemas import CommissionSettingUpdateIn
from app.modules.orders.service import CommissionService


router = APIRouter(
    prefix="/admin/commission",
    tags=["Admin Commission"],
)


@router.get("/settings")
def list_commission_settings(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("commission.read")),
):
    service = CommissionService(db)

    result = service.list_settings()

    return success_response(
        data=[item.model_dump(mode="json") for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/settings/default")
def get_default_commission_setting(
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("commission.read")),
):
    service = CommissionService(db)

    result = service.get_default_setting()

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/settings/default")
def update_default_commission_setting(
    payload: CommissionSettingUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("commission.update")),
):
    service = CommissionService(db)

    result = service.update_default_setting(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Default commission setting updated",
        meta={"trace_id": request.state.trace_id},
    )
