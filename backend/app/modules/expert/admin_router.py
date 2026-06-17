from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.expert.schemas import ExpertAnswerStatusUpdateIn
from app.modules.expert.service import ExpertAnswerService


router = APIRouter(
    prefix="/admin/expert",
    tags=["Admin Expert Answers"],
)


@router.get("/answers")
def list_expert_answers_admin(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    post_id: int | None = Query(default=None, ge=1),
    expert_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("expert_answer.admin_read")),
):
    service = ExpertAnswerService(db)

    items, total = service.list_admin_answers(
        status=status,
        post_id=post_id,
        expert_user_id=expert_id,
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


@router.patch("/answers/{answer_id}/status")
def update_expert_answer_status_admin(
    answer_id: int,
    payload: ExpertAnswerStatusUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(
        require_permission("expert_answer.admin_moderate")
    ),
):
    service = ExpertAnswerService(db)

    result = service.update_answer_status_admin(
        answer_id=answer_id,
        admin_user_id=current_user.id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Expert answer status updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/answers/{answer_id}")
def delete_expert_answer_admin(
    answer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(
        require_permission("expert_answer.admin_moderate")
    ),
):
    service = ExpertAnswerService(db)

    result = service.soft_delete_answer_admin(
        answer_id=answer_id,
        admin_user_id=current_user.id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Expert answer deleted",
        meta={"trace_id": request.state.trace_id},
    )
