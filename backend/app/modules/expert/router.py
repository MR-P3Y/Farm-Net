from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.expert.schemas import ExpertAnswerCreateIn
from app.modules.expert.service import ExpertAnswerService


router = APIRouter(
    tags=["Expert Answers"],
)


@router.get("/social/posts/{post_id}/expert-answers")
def list_published_expert_answers_for_post(
    post_id: int,
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ExpertAnswerService(db)

    items, total = service.list_published_answers_for_post(
        post_id=post_id,
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


@router.post("/social/posts/{post_id}/expert-answers")
def create_expert_answer_for_post(
    post_id: int,
    payload: ExpertAnswerCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("expert_answer.create")),
):
    service = ExpertAnswerService(db)

    result = service.create_answer(
        post_id=post_id,
        expert_user_id=current_user.id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Expert answer created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/expert/me/answers")
def list_my_expert_answers(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("expert_answer.manage_own")),
):
    service = ExpertAnswerService(db)

    items, total = service.list_my_answers(
        expert_user_id=current_user.id,
        status=status,
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


@router.delete("/expert/answers/{answer_id}")
def delete_my_expert_answer(
    answer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("expert_answer.manage_own")),
):
    service = ExpertAnswerService(db)

    result = service.soft_delete_own_answer(
        answer_id=answer_id,
        expert_user_id=current_user.id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Expert answer deleted",
        meta={"trace_id": request.state.trace_id},
    )
