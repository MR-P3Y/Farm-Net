from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.farms.enums import FarmCalculatorType, FarmPlanStatus
from app.modules.farms.toolbox_schemas import (
    FarmFinancialEntryCreateIn,
    FarmFinancialEntryDetailResponse,
    FarmFinancialEntryListResponse,
    FarmFinancialEntryVoidIn,
    FarmFinancialSummaryResponse,
    FarmPlanCancelIn,
    FarmPlanCompleteIn,
    FarmPlanCreateIn,
    FarmPlanDetailResponse,
    FarmPlanListResponse,
    FarmToolCalculationCreateIn,
    FarmToolCalculationDetailResponse,
    FarmToolCalculationListResponse,
)
from app.modules.farms.toolbox_service import FarmToolboxService


router = APIRouter(prefix="/farms", tags=["Farm Toolbox"])


@router.post(
    "/{farm_id}/toolbox/calculations",
    response_model=FarmToolCalculationDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_calculation(
    farm_id: int,
    payload: FarmToolCalculationCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmToolboxService(db).create_calculation(
        user=user, farm_id=farm_id, payload=payload
    )
    return _detail(result, "Farm calculation saved", request)


@router.get(
    "/{farm_id}/toolbox/calculations",
    response_model=FarmToolCalculationListResponse,
)
def list_calculations(
    farm_id: int,
    request: Request,
    plot_id: int | None = Query(default=None, ge=1),
    cycle_id: int | None = Query(default=None, ge=1),
    calculator_type: FarmCalculatorType | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items = FarmToolboxService(db).list_calculations(
        user=user,
        farm_id=farm_id,
        plot_id=plot_id,
        cycle_id=cycle_id,
        calculator_type=calculator_type,
        limit=limit,
    )
    return _list(items, request)


@router.post(
    "/{farm_id}/toolbox/costs",
    response_model=FarmFinancialEntryDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_financial_entry(
    farm_id: int,
    payload: FarmFinancialEntryCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmToolboxService(db).create_financial_entry(
        user=user, farm_id=farm_id, payload=payload
    )
    return _detail(result, "Farm financial entry created", request)


@router.get(
    "/{farm_id}/toolbox/costs",
    response_model=FarmFinancialEntryListResponse,
)
def list_financial_entries(
    farm_id: int,
    request: Request,
    plot_id: int | None = Query(default=None, ge=1),
    cycle_id: int | None = Query(default=None, ge=1),
    include_voided: bool = False,
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items = FarmToolboxService(db).list_financial_entries(
        user=user,
        farm_id=farm_id,
        plot_id=plot_id,
        cycle_id=cycle_id,
        include_voided=include_voided,
        limit=limit,
    )
    return _list(items, request)


@router.post(
    "/{farm_id}/toolbox/costs/{entry_id}/void",
    response_model=FarmFinancialEntryDetailResponse,
)
def void_financial_entry(
    farm_id: int,
    entry_id: int,
    payload: FarmFinancialEntryVoidIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmToolboxService(db).void_financial_entry(
        user=user, farm_id=farm_id, entry_id=entry_id, reason=payload.reason
    )
    return _detail(result, "Farm financial entry voided", request)


@router.get(
    "/{farm_id}/toolbox/cost-summary",
    response_model=FarmFinancialSummaryResponse,
)
def financial_summary(
    farm_id: int,
    request: Request,
    plot_id: int | None = Query(default=None, ge=1),
    cycle_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    result = FarmToolboxService(db).financial_summary(
        user=user, farm_id=farm_id, plot_id=plot_id, cycle_id=cycle_id
    )
    return _detail(result, "OK", request)


@router.post(
    "/{farm_id}/toolbox/plans",
    response_model=FarmPlanDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_plan(
    farm_id: int,
    payload: FarmPlanCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmToolboxService(db).create_plan(user=user, farm_id=farm_id, payload=payload)
    return _detail(result, "Farm plan created", request)


@router.get("/{farm_id}/toolbox/plans", response_model=FarmPlanListResponse)
def list_plans(
    farm_id: int,
    request: Request,
    plot_id: int | None = Query(default=None, ge=1),
    cycle_id: int | None = Query(default=None, ge=1),
    plan_status: FarmPlanStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.read_own")),
):
    items = FarmToolboxService(db).list_plans(
        user=user,
        farm_id=farm_id,
        plot_id=plot_id,
        cycle_id=cycle_id,
        status=plan_status,
        limit=limit,
    )
    return _list(items, request)


@router.post(
    "/{farm_id}/toolbox/plans/{plan_id}/complete",
    response_model=FarmPlanDetailResponse,
)
def complete_plan(
    farm_id: int,
    plan_id: int,
    payload: FarmPlanCompleteIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmToolboxService(db).complete_plan(
        user=user, farm_id=farm_id, plan_id=plan_id, payload=payload
    )
    return _detail(result, "Farm plan completed", request)


@router.post(
    "/{farm_id}/toolbox/plans/{plan_id}/cancel",
    response_model=FarmPlanDetailResponse,
)
def cancel_plan(
    farm_id: int,
    plan_id: int,
    payload: FarmPlanCancelIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("farms.manage_own")),
):
    result = FarmToolboxService(db).cancel_plan(
        user=user, farm_id=farm_id, plan_id=plan_id, payload=payload
    )
    return _detail(result, "Farm plan cancelled", request)


def _detail(result, message: str, request: Request):
    return success_response(
        data=result.model_dump(mode="json"),
        message=message,
        meta={"trace_id": request.state.trace_id},
    )


def _list(items, request: Request):
    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={"count": len(items), "trace_id": request.state.trace_id},
    )
