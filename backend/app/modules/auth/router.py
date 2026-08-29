from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_active_user, get_current_session_id
from app.modules.auth.models import AuthUser
from app.modules.auth.schemas import (
    EmailLoginIn,
    EmailRegisterIn,
    ChangePasswordIn,
    LogoutIn,
    OtpRequestIn,
    OtpVerifyIn,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    RefreshTokenIn,
)
from app.modules.auth.service import AuthService
from app.modules.profiles.schemas import ProfileUpdateIn


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
        profile=ProfileUpdateIn(
            first_name=payload.first_name,
            last_name=payload.last_name,
            display_name=payload.display_name,
            national_id=payload.national_id,
            province_id=payload.province_id,
            county_id=payload.county_id,
            city_id=payload.city_id,
            address=payload.address,
            postal_code=payload.postal_code,
        ),
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


@router.get("/sessions")
def list_my_sessions(
    request: Request,
    current_user: AuthUser = Depends(get_current_active_user),
    current_session_id: int = Depends(get_current_session_id),
    db: Session = Depends(get_db),
):
    result = AuthService(db).list_my_sessions(
        user=current_user,
        current_session_id=current_session_id,
    )
    return success_response(
        data=[item.model_dump(mode="json") for item in result],
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/sessions/{session_id}")
def revoke_my_session(
    session_id: int,
    request: Request,
    current_user: AuthUser = Depends(get_current_active_user),
    current_session_id: int = Depends(get_current_session_id),
    db: Session = Depends(get_db),
):
    AuthService(db).revoke_my_session(
        user=current_user,
        session_id=session_id,
        current_session_id=current_session_id,
    )
    return success_response(
        data=None,
        message="Session revoked",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/sessions/revoke-others")
def revoke_my_other_sessions(
    request: Request,
    current_user: AuthUser = Depends(get_current_active_user),
    current_session_id: int = Depends(get_current_session_id),
    db: Session = Depends(get_db),
):
    revoked_count = AuthService(db).revoke_my_other_sessions(
        user=current_user,
        current_session_id=current_session_id,
    )
    return success_response(
        data={"revoked_count": revoked_count},
        message="Other sessions revoked",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/password/change")
def change_my_password(
    payload: ChangePasswordIn,
    request: Request,
    current_user: AuthUser = Depends(get_current_active_user),
    current_session_id: int = Depends(get_current_session_id),
    db: Session = Depends(get_db),
):
    revoked_count = AuthService(db).change_my_password(
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
        current_session_id=current_session_id,
    )
    return success_response(
        data={"revoked_sessions": revoked_count},
        message="Password changed",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/password/reset/request")
def request_password_reset(
    payload: PasswordResetRequestIn,
    request: Request,
    db: Session = Depends(get_db),
):
    result = AuthService(db).request_password_reset(
        identifier=payload.identifier,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )
    return success_response(
        data=result.model_dump(),
        message=(
            "If an active account matches this identifier, a reset code was sent"
        ),
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/password/reset/confirm")
def confirm_password_reset(
    payload: PasswordResetConfirmIn,
    request: Request,
    db: Session = Depends(get_db),
):
    revoked_sessions = AuthService(db).confirm_password_reset(
        identifier=payload.identifier,
        code=payload.code,
        new_password=payload.new_password,
    )
    return success_response(
        data={"revoked_sessions": revoked_sessions},
        message="Password reset successfully",
        meta={"trace_id": request.state.trace_id},
    )
