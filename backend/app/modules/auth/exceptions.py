class AuthError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class InvalidCredentialsError(AuthError):
    def __init__(self) -> None:
        super().__init__(
            code="AUTH_INVALID_CREDENTIALS",
            message="Invalid email, phone, or password",
        )


class UserAlreadyExistsError(AuthError):
    def __init__(self) -> None:
        super().__init__(
            code="AUTH_USER_ALREADY_EXISTS",
            message="User already exists",
        )


class UserNotFoundError(AuthError):
    def __init__(self) -> None:
        super().__init__(
            code="AUTH_USER_NOT_FOUND",
            message="User not found",
        )


class UserSuspendedError(AuthError):
    def __init__(self) -> None:
        super().__init__(
            code="USER_SUSPENDED",
            message="User account is suspended",
        )


class OtpInvalidError(AuthError):
    def __init__(self) -> None:
        super().__init__(
            code="AUTH_OTP_INVALID",
            message="Invalid OTP code",
        )


class OtpExpiredError(AuthError):
    def __init__(self) -> None:
        super().__init__(
            code="AUTH_OTP_EXPIRED",
            message="OTP code has expired",
        )


class OtpTooManyAttemptsError(AuthError):
    def __init__(self) -> None:
        super().__init__(
            code="AUTH_OTP_TOO_MANY_ATTEMPTS",
            message="Too many OTP attempts",
        )