from datetime import UTC, date, datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy import event
from sqlalchemy.orm.attributes import set_committed_value

from app.modules.farms.models import (
    FarmAuditLog,
    FarmCropCycle,
    FarmHarvestObservation,
    FarmLabObservation,
    FarmOperation,
    FarmOperationInput,
    FarmRecordMedia,
    _protect_closed_cycle_update,
    _reject_retained_farm_record_mutation,
)
from app.modules.farms.schemas import FarmArchiveIn
from app.modules.farms.service import FarmService


def test_farm_audit_log_has_restricted_identity_contracts() -> None:
    table = FarmAuditLog.__table__
    assert table.c.farm_id.foreign_keys
    assert table.c.actor_user_id.foreign_keys
    assert {
        fk.ondelete
        for column in (table.c.farm_id, table.c.actor_user_id)
        for fk in column.foreign_keys
    } == {"RESTRICT"}
    assert "ix_farm_audit_logs_farm_created" in {index.name for index in table.indexes}
    assert "ix_farm_audit_logs_target" in {index.name for index in table.indexes}


@pytest.mark.parametrize(
    "model",
    [
        FarmOperation,
        FarmOperationInput,
        FarmHarvestObservation,
        FarmRecordMedia,
        FarmLabObservation,
        FarmAuditLog,
    ],
)
def test_retained_records_have_orm_update_and_delete_guards(model) -> None:
    assert event.contains(model, "before_update", _reject_retained_farm_record_mutation)
    assert event.contains(model, "before_delete", _reject_retained_farm_record_mutation)


def test_closed_crop_cycle_cannot_be_reopened_through_orm() -> None:
    row = FarmCropCycle(
        plot_id=1,
        crop_id=1,
        planned_start_date=date(2026, 1, 1),
        planned_end_date=date(2026, 2, 1),
        cultivation_mode="single",
        status="completed",
    )
    set_committed_value(row, "status", "completed")
    row.status = "active"
    with pytest.raises(RuntimeError, match="immutable"):
        _protect_closed_cycle_update(None, None, row)


def test_farm_archive_writes_audit_in_same_unit_of_work() -> None:
    now = datetime.now(UTC).replace(tzinfo=None)
    row = SimpleNamespace(
        id=11, owner_user_id=7, name="farm", description=None,
        declared_area_sqm=None, status="active", archived_at=None,
        archive_reason=None, created_at=now, updated_at=now,
    )
    service = FarmService(Mock())
    service.repo = Mock()
    service.repo.get_owned.return_value = row

    service.archive(
        user=SimpleNamespace(id=7), farm_id=11, payload=FarmArchiveIn(reason="closed")
    )

    service.repo.add_audit.assert_called_once_with(
        farm_id=11, actor_user_id=7, action="farm.archived",
        target_type="farm", target_id=11,
    )
    service.db.commit.assert_called_once()


def test_audit_details_do_not_store_sensitive_farm_values() -> None:
    service = FarmService(Mock())
    service.repo = Mock()
    service.repo.add.return_value = SimpleNamespace(
        id=8, owner_user_id=7, name="secret name", description="private",
        declared_area_sqm=None, status="active", archived_at=None,
        archive_reason=None, created_at=datetime.now(UTC).replace(tzinfo=None),
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )
    from app.modules.farms.schemas import FarmCreateIn

    service.create(user=SimpleNamespace(id=7), payload=FarmCreateIn(name="secret name"))
    kwargs = service.repo.add_audit.call_args.kwargs
    assert kwargs.get("details") is None
    assert "secret name" not in repr(kwargs)
