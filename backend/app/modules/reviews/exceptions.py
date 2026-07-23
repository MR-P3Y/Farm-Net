from fastapi import status

from app.core.exceptions import AppException


class ReviewNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="REVIEW_NOT_FOUND",
            message="Review not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ReviewEligibilityError(AppException):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            code="REVIEW_NOT_ELIGIBLE",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            details=details,
        )


class ReviewConflictError(AppException):
    def __init__(self, *, review_id: int | None = None) -> None:
        details = {} if review_id is None else {"review_id": review_id}
        super().__init__(
            code="REVIEW_ALREADY_EXISTS",
            message="A review already exists for this source and subject",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class ReviewLifecycleError(AppException):
    def __init__(self, *, current_status: str) -> None:
        super().__init__(
            code="REVIEW_INVALID_STATE",
            message="Review cannot be changed in its current state",
            status_code=status.HTTP_409_CONFLICT,
            details={"current_status": current_status},
        )
