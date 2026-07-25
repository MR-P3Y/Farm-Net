from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint

from app.core.exceptions import AppException
from app.main import app
from app.modules.farms.enums import FarmStatus
from app.modules.farms.models import Farm
from app.modules.farms.schemas import FarmArchiveIn, FarmCreateIn, FarmUpdateIn
from app.modules.farms.service import FarmService


def _row(*, status: str = "active"):
    now = datetime.now(UTC).replace(tzinfo=None)
    return SimpleNamespace(
        id=11,
        owner_user_id=7,
        name="مزرعه نمونه",
        description=None,
        status=status,
        archived_at=now if status == "archived" else None,
        archive_reason="پایان فعالیت" if status == "archived" else None,
        created_at=now,
        updated_at=now,
    )


def _service(row=None) -> FarmService:
    db = Mock()
    service = FarmService(db)
    service.repo = Mock()
    service.repo.get_owned.return_value = row
    return service


def test_farm_database_archive_contracts_are_registered() -> None:
    checks = {
        constraint.name
        for constraint in Farm.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert Farm.__tablename__ == "farms"
    assert {"ck_farms_status", "ck_farms_archive_state"} <= checks
    assert Farm.__table__.c.owner_user_id.foreign_keys


def test_payloads_normalize_and_reject_blank_or_empty_updates() -> None:
    assert FarmCreateIn(name="  مزرعه الف  ").name == "مزرعه الف"
    assert FarmUpdateIn(description="   ").description is None
    with pytest.raises(ValidationError):
        FarmCreateIn(name="   ")
    with pytest.raises(ValidationError):
        FarmUpdateIn()


def test_cross_owner_lookup_is_indistinguishable_from_missing() -> None:
    service = _service(row=None)
    with pytest.raises(AppException) as exc_info:
        service.get_own(user=SimpleNamespace(id=99), farm_id=11)
    assert exc_info.value.code == "FARM_NOT_FOUND"
    assert exc_info.value.status_code == 404
    service.repo.get_owned.assert_called_once_with(
        farm_id=11,
        owner_user_id=99,
        for_update=False,
    )


def test_archived_farm_cannot_be_edited() -> None:
    service = _service(row=_row(status="archived"))
    with pytest.raises(AppException) as exc_info:
        service.update(
            user=SimpleNamespace(id=7),
            farm_id=11,
            payload=FarmUpdateIn(name="نام جدید"),
        )
    assert exc_info.value.code == "FARM_ARCHIVED"
    service.db.commit.assert_not_called()


def test_archive_and_restore_keep_history_without_delete() -> None:
    row = _row()
    service = _service(row=row)
    service.archive(
        user=SimpleNamespace(id=7),
        farm_id=11,
        payload=FarmArchiveIn(reason="  پایان فعالیت  "),
    )
    assert row.status == FarmStatus.ARCHIVED.value
    assert row.archived_at is not None
    assert row.archive_reason == "پایان فعالیت"

    service.restore(user=SimpleNamespace(id=7), farm_id=11)
    assert row.status == FarmStatus.ACTIVE.value
    assert row.archived_at is None
    assert row.archive_reason is None


def test_farm_openapi_contract_contains_only_owner_routes() -> None:
    paths = app.openapi()["paths"]
    expected = {
        "/api/v1/farms",
        "/api/v1/farms/{farm_id}",
        "/api/v1/farms/{farm_id}/archive",
        "/api/v1/farms/{farm_id}/restore",
    }
    assert expected <= set(paths)
    assert all(not path.startswith("/api/v1/public/farms") for path in paths)
    assert set(paths["/api/v1/farms"]) == {"get", "post"}
    assert set(paths["/api/v1/farms/{farm_id}"]) == {"get", "patch"}
