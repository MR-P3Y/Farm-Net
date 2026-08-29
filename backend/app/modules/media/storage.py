from __future__ import annotations

import hashlib
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.media.enums import MediaPurpose, MediaStorageDisk, MediaVisibility
from app.modules.media.schemas import StoredMediaFile


IMAGE_MAX_BYTES = 5 * 1024 * 1024
DOCUMENT_MAX_BYTES = 10 * 1024 * 1024

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

ALLOWED_DOCUMENT_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

DOCUMENT_PURPOSES = {
    MediaPurpose.PROFILE_DOCUMENT.value,
    MediaPurpose.VERIFICATION_DOCUMENT.value,
}

PUBLIC_PURPOSES = {
    MediaPurpose.PROFILE_IMAGE.value,
    MediaPurpose.PRODUCT_IMAGE.value,
    MediaPurpose.SOCIAL_POST_IMAGE.value,
    MediaPurpose.STORE_LOGO.value,
    MediaPurpose.STORE_BANNER.value,
}


@dataclass(frozen=True)
class LocalStorageConfig:
    base_dir: Path


class LocalMediaStorage:
    def __init__(self, *, config: LocalStorageConfig) -> None:
        self.config = config
        self.base_dir = config.base_dir.resolve()

    def store_bytes(
        self,
        *,
        content: bytes,
        original_filename: str,
        mime_type: str | None,
        purpose: str,
        visibility: str,
    ) -> StoredMediaFile:
        self._validate_purpose(purpose)
        self._validate_visibility(purpose=purpose, visibility=visibility)

        safe_mime_type = self._normalize_mime_type(
            original_filename=original_filename,
            mime_type=mime_type,
        )
        extension = self._extension_for_mime_type(
            mime_type=safe_mime_type,
            purpose=purpose,
        )

        self._validate_size(content=content, purpose=purpose)

        checksum = hashlib.sha256(content).hexdigest()
        file_key = uuid4().hex
        stored_filename = f"{file_key}{extension}"

        relative_dir = self._relative_dir_for_purpose(purpose)
        relative_path = f"{relative_dir}/{stored_filename}"

        target_path = self._safe_target_path(relative_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)

        return StoredMediaFile(
            file_key=file_key,
            original_filename=self._safe_original_filename(original_filename),
            stored_filename=stored_filename,
            relative_path=relative_path,
            storage_disk=MediaStorageDisk.LOCAL.value,
            mime_type=safe_mime_type,
            extension=extension.lstrip("."),
            size_bytes=len(content),
            checksum_sha256=checksum,
            width=None,
            height=None,
        )

    def absolute_path(self, *, relative_path: str) -> Path:
        return self._safe_target_path(relative_path)

    def _safe_target_path(self, relative_path: str) -> Path:
        if (
            not relative_path
            or relative_path.startswith(("/", "\\"))
            or "\\" in relative_path
        ):
            raise ValidationAuthError(
                message="Invalid media path",
                details={"relative_path": relative_path},
            )

        normalized = Path(relative_path)

        if ".." in normalized.parts:
            raise ValidationAuthError(
                message="Invalid media path traversal",
                details={"relative_path": relative_path},
            )

        target = (self.base_dir / normalized).resolve()

        try:
            target.relative_to(self.base_dir)
        except ValueError as exc:
            raise ValidationAuthError(
                message="Invalid media storage target",
                details={"relative_path": relative_path},
            ) from exc

        return target

    def _validate_purpose(self, purpose: str) -> None:
        allowed = {item.value for item in MediaPurpose}
        if purpose not in allowed:
            raise ValidationAuthError(
                message="Invalid media purpose",
                details={"allowed": sorted(allowed)},
            )

    def _validate_visibility(self, *, purpose: str, visibility: str) -> None:
        allowed = {item.value for item in MediaVisibility}
        if visibility not in allowed:
            raise ValidationAuthError(
                message="Invalid media visibility",
                details={"allowed": sorted(allowed)},
            )

        if purpose in DOCUMENT_PURPOSES and visibility != MediaVisibility.PRIVATE.value:
            raise ValidationAuthError(
                message="Document media must be private",
                details={"purpose": purpose, "visibility": visibility},
            )

        if purpose in PUBLIC_PURPOSES and visibility != MediaVisibility.PUBLIC.value:
            raise ValidationAuthError(
                message="Public image media must be public",
                details={"purpose": purpose, "visibility": visibility},
            )

    def _normalize_mime_type(
        self,
        *,
        original_filename: str,
        mime_type: str | None,
    ) -> str:
        if mime_type:
            return mime_type.split(";")[0].strip().lower()

        guessed, _ = mimetypes.guess_type(original_filename)
        if not guessed:
            raise ValidationAuthError(
                message="Unable to detect file mime type",
                details={"filename": original_filename},
            )

        return guessed.lower()

    def _extension_for_mime_type(self, *, mime_type: str, purpose: str) -> str:
        allowed = (
            ALLOWED_DOCUMENT_MIME_TYPES
            if purpose in DOCUMENT_PURPOSES
            else ALLOWED_IMAGE_MIME_TYPES
        )

        extension = allowed.get(mime_type)
        if extension is None:
            raise ValidationAuthError(
                message="File type is not allowed",
                details={
                    "mime_type": mime_type,
                    "allowed": sorted(allowed.keys()),
                },
            )

        return extension

    def _validate_size(self, *, content: bytes, purpose: str) -> None:
        size = len(content)
        max_size = DOCUMENT_MAX_BYTES if purpose in DOCUMENT_PURPOSES else IMAGE_MAX_BYTES

        if size <= 0:
            raise ValidationAuthError(
                message="File is empty",
                details={"size_bytes": size},
            )

        if size > max_size:
            raise ValidationAuthError(
                message="File is too large",
                details={
                    "size_bytes": size,
                    "max_size_bytes": max_size,
                },
            )

    def _relative_dir_for_purpose(self, purpose: str) -> str:
        if purpose == MediaPurpose.PROFILE_IMAGE.value:
            return "profiles/images"

        if purpose == MediaPurpose.PRODUCT_IMAGE.value:
            return "products/images"

        if purpose == MediaPurpose.SOCIAL_POST_IMAGE.value:
            return "social/posts/images"

        if purpose == MediaPurpose.STORE_LOGO.value:
            return "stores/logos"

        if purpose == MediaPurpose.STORE_BANNER.value:
            return "stores/banners"

        if purpose == MediaPurpose.PROFILE_DOCUMENT.value:
            return "profiles/documents"

        if purpose == MediaPurpose.VERIFICATION_DOCUMENT.value:
            return "verifications/documents"

        return "general"

    def _safe_original_filename(self, filename: str) -> str:
        name = os.path.basename(filename or "uploaded-file")
        name = name.replace("\\", "_").replace("/", "_").strip()

        if not name:
            return "uploaded-file"

        return name[:255]


def get_local_media_storage() -> LocalMediaStorage:
    base_dir = Path(get_settings().media_storage_dir)
    return LocalMediaStorage(config=LocalStorageConfig(base_dir=base_dir))
