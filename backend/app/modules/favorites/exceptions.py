from fastapi import status

from app.core.exceptions import AppException


class FavoriteSubjectNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="FAVORITE_SUBJECT_NOT_FOUND",
            message="Favorite subject not found or unavailable",
            status_code=status.HTTP_404_NOT_FOUND,
        )
