from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.ai.models import AIRequestMedia
from app.modules.media.models import MediaFile


ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MIN_IMAGE_DIMENSION = 256


@dataclass(frozen=True)
class ValidatedAIImage:
    media_file_id: int
    checksum_sha256: str
    mime_type: str
    size_bytes: int
    width: int
    height: int


class AIImageAnalysisService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def validate_owned_image(self, *, user_id: int, file_key: str) -> ValidatedAIImage:
        row = self.db.scalar(
            select(MediaFile).where(
                MediaFile.file_key == file_key,
                MediaFile.owner_user_id == user_id,
                MediaFile.status == "active",
            )
        )
        if row is None:
            raise AppException("AI_IMAGE_NOT_FOUND", "Image not found", 404)
        if row.mime_type not in ALLOWED_IMAGE_MIME_TYPES:
            raise AppException("AI_IMAGE_TYPE_UNSUPPORTED", "Unsupported image type", 422)
        if not 1 <= row.size_bytes <= MAX_IMAGE_BYTES:
            raise AppException("AI_IMAGE_SIZE_INVALID", "Image size is invalid", 422)
        if (
            row.width is None
            or row.height is None
            or row.width < MIN_IMAGE_DIMENSION
            or row.height < MIN_IMAGE_DIMENSION
        ):
            raise AppException(
                "AI_IMAGE_EVIDENCE_INSUFFICIENT",
                "Image dimensions are insufficient for analysis",
                422,
            )
        return ValidatedAIImage(
            media_file_id=row.id,
            checksum_sha256=row.checksum_sha256,
            mime_type=row.mime_type,
            size_bytes=row.size_bytes,
            width=row.width,
            height=row.height,
        )

    def bind(self, *, request_id: int, image: ValidatedAIImage) -> AIRequestMedia:
        row = AIRequestMedia(
            request_id=request_id,
            media_file_id=image.media_file_id,
            checksum_sha256=image.checksum_sha256,
            mime_type=image.mime_type,
            size_bytes=image.size_bytes,
            width=image.width,
            height=image.height,
        )
        self.db.add(row)
        return row
