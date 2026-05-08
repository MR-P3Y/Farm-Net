from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import AuthUser
from app.modules.auth.schemas import (
    EmailLoginIn,
    EmailRegisterIn,
    LogoutIn,
    OtpRequestIn,
    OtpVerifyIn,
    RefreshTokenIn,
)
from app.modules.auth.service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def _client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


def _user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


@router.post("/register/email", status_code=status.HTTP_201_CREATED)
def register_with_email(
    payload: EmailRegisterIn,
    request: Request,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    result = service.register_with_email(
        email=payload.email,
        password=payload.password,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )

    return success_response(
        data=result.model_dump(),
        message="User registered successfully",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/login/email")
def login_with_email(
    payload: EmailLoginIn,
    request: Request,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    result = service.login_with_email(
        email=payload.email,
        password=payload.password,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )

    return success_response(
        data=result.model_dump(),
        message="Login successful",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/otp/request")
def request_otp(
    payload: OtpRequestIn,
    request: Request,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    result = service.request_otp(
        phone=payload.phone,
        purpose=payload.purpose,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )

    return success_response(
        data=result.model_dump(),
        message="OTP requested successfully",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/otp/verify")
def verify_otp(
    payload: OtpVerifyIn,
    request: Request,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    result = service.verify_otp(
        phone=payload.phone,
        code=payload.code,
        purpose=payload.purpose,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )

    return success_response(
        data=result.model_dump(),
        message="OTP verified successfully",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/refresh")
def refresh_token(
    payload: RefreshTokenIn,
    request: Request,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    result = service.refresh_access_token(
        refresh_token=payload.refresh_token,
    )

    return success_response(
        data=result.model_dump(),
        message="Token refreshed successfully",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/logout")
def logout(
    payload: LogoutIn,
    request: Request,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    service.logout(
        refresh_token=payload.refresh_token,
    )

    return success_response(
        data=None,
        message="Logout successful",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me")
def me(
    request: Request,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    result = service.get_current_user_out(current_user)

    return success_response(
        data=result.model_dump(),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )
