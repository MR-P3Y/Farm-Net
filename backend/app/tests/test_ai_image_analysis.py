from types import SimpleNamespace

import pytest
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.core.exceptions import AppException
from app.modules.ai.image_analysis import AIImageAnalysisService
from app.modules.ai.models import AIRequestMedia


class _DB:
    def __init__(self, row) -> None:
        self.row = row
        self.added = []

    def scalar(self, _query):
        return self.row

    def add(self, row) -> None:
        self.added.append(row)


def _media(**changes):
    values = {
        "id": 7,
        "checksum_sha256": "a" * 64,
        "mime_type": "image/jpeg",
        "size_bytes": 500_000,
        "width": 1024,
        "height": 768,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def test_image_snapshot_has_exact_once_restrict_evidence_contract() -> None:
    uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in AIRequestMedia.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    checks = {
        constraint.name
        for constraint in AIRequestMedia.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert {("request_id",), ("media_file_id",)} <= uniques
    assert {
        "ck_ai_request_media_mime",
        "ck_ai_request_media_size",
        "ck_ai_request_media_dimensions",
    } <= checks


def test_owned_active_image_validation_is_bounded() -> None:
    service = AIImageAnalysisService(_DB(_media()))
    image = service.validate_owned_image(user_id=1, file_key="owned-image")
    assert image.width == 1024

    for row, code in (
        (None, "AI_IMAGE_NOT_FOUND"),
        (_media(mime_type="image/svg+xml"), "AI_IMAGE_TYPE_UNSUPPORTED"),
        (_media(size_bytes=20_000_000), "AI_IMAGE_SIZE_INVALID"),
        (_media(width=100), "AI_IMAGE_EVIDENCE_INSUFFICIENT"),
    ):
        with pytest.raises(AppException) as error:
            AIImageAnalysisService(_DB(row)).validate_owned_image(
                user_id=1, file_key="hidden"
            )
        assert error.value.code == code
