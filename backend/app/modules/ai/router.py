from math import ceil

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.ai.schemas import (
    AIHumanEscalationCreateIn,
    AIContextConsentCreateIn,
    AIContextConsentListResponse,
    AIContextConsentOut,
    AIContextConsentResponse,
    AIContextConsentRevokeIn,
    AIConversationCreateIn,
    AIConversationDetailOut,
    AIConversationDetailResponse,
    AIConversationListResponse,
    AIConversationOut,
    AIConversationResponse,
    AIRequestCreateIn,
    AIRequestOut,
    AIRequestResponse,
)
from app.modules.ai.context_service import AIContextService
from app.modules.ai.workflow_service import AIWorkflowService
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser


router = APIRouter(prefix="/ai", tags=["Barzegar AI"])


@router.post(
    "/context-consents",
    response_model=AIContextConsentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_context_consent(
    payload: AIContextConsentCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.context.use_own")),
):
    row = AIContextService(db).create_consent(user=user, payload=payload)
    return success_response(
        data=AIContextConsentOut.model_validate(row).model_dump(mode="json"),
        message="Selected Farm context consent created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/context-consents", response_model=AIContextConsentListResponse)
def list_context_consents(
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.context.use_own")),
):
    rows = AIContextService(db).list_consents(user=user)
    return success_response(
        data=[AIContextConsentOut.model_validate(row).model_dump(mode="json") for row in rows],
        meta={"trace_id": request.state.trace_id},
    )


@router.post(
    "/context-consents/{consent_id}/revoke",
    response_model=AIContextConsentResponse,
)
def revoke_context_consent(
    consent_id: int,
    payload: AIContextConsentRevokeIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.context.use_own")),
):
    row = AIContextService(db).revoke(user=user, consent_id=consent_id, reason=payload.reason)
    return success_response(
        data=AIContextConsentOut.model_validate(row).model_dump(mode="json"),
        message="Selected Farm context consent revoked",
        meta={"trace_id": request.state.trace_id},
    )


@router.post(
    "/conversations",
    response_model=AIConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    payload: AIConversationCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.conversations.create")),
):
    row = AIWorkflowService(db).create_conversation(user=user, title=payload.title)
    return success_response(
        data=AIConversationOut.model_validate(row).model_dump(mode="json"),
        message="Barzegar conversation created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/conversations", response_model=AIConversationListResponse)
def list_conversations(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.conversations.read_own")),
):
    rows, total = AIWorkflowService(db).list_conversations(
        user=user, page=page, page_size=page_size
    )
    return success_response(
        data=[AIConversationOut.model_validate(row).model_dump(mode="json") for row in rows],
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=AIConversationDetailResponse,
)
def get_conversation(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.conversations.read_own")),
):
    row = AIWorkflowService(db).get_conversation(user=user, conversation_id=conversation_id)
    data = AIConversationDetailOut.model_validate(row)
    return success_response(
        data=data.model_dump(mode="json"),
        meta={"trace_id": request.state.trace_id},
    )


@router.post(
    "/conversations/{conversation_id}/requests",
    response_model=AIRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_request(
    conversation_id: int,
    payload: AIRequestCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.requests.create")),
):
    row = AIWorkflowService(db).submit_request(
        user=user, conversation_id=conversation_id, payload=payload
    )
    return success_response(
        data=AIRequestOut.model_validate(row).model_dump(mode="json"),
        message="Barzegar request queued",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/requests/{request_id}", response_model=AIRequestResponse)
def get_request(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.requests.read_own")),
):
    row = AIWorkflowService(db).get_request(user=user, request_id=request_id)
    return success_response(
        data=AIRequestOut.model_validate(row).model_dump(mode="json"),
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/requests/{request_id}/cancel", response_model=AIRequestResponse)
def cancel_request(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("ai.requests.cancel_own")),
):
    row = AIWorkflowService(db).cancel_request(user=user, request_id=request_id)
    return success_response(
        data=AIRequestOut.model_validate(row).model_dump(mode="json"),
        message="Barzegar request cancelled",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/requests/{request_id}/escalate", response_model=AIRequestResponse)
def escalate_request(
    request_id: int,
    payload: AIHumanEscalationCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    user: AuthUser = Depends(require_permission("consult.requests.create")),
):
    row = AIWorkflowService(db).escalate_to_consultant(
        user=user,
        request_id=request_id,
        payload=payload,
    )
    return success_response(
        data=AIRequestOut.model_validate(row).model_dump(mode="json"),
        message="Consult request created",
        meta={"trace_id": request.state.trace_id},
    )
