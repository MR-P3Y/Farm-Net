from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.services.enums import ServiceRequestStatus
from app.modules.services.schemas import ServiceRequestCreateIn
from app.modules.services.service import ServicesService


def request_service() -> ServicesService:
    service = ServicesService.__new__(ServicesService)
    service.repo = Mock()
    return service


def test_request_create_contract_rejects_fields_missing_from_model() -> None:
    with pytest.raises(ValidationError):
        ServiceRequestCreateIn(
            offer_id=10,
            title="Soil test",
            description="Test this field before planting",
            quantity=5,
        )


def test_provider_request_transition_sequence_is_explicit() -> None:
    service = request_service()
    service._validate_request_transition(
        ServiceRequestStatus.OPEN.value,
        ServiceRequestStatus.ACCEPTED.value,
        service.PROVIDER_REQUEST_TRANSITIONS,
    )
    service._validate_request_transition(
        ServiceRequestStatus.ACCEPTED.value,
        ServiceRequestStatus.IN_PROGRESS.value,
        service.PROVIDER_REQUEST_TRANSITIONS,
    )
    service._validate_request_transition(
        ServiceRequestStatus.IN_PROGRESS.value,
        ServiceRequestStatus.COMPLETED.value,
        service.PROVIDER_REQUEST_TRANSITIONS,
    )


def test_terminal_request_cannot_transition() -> None:
    service = request_service()
    with pytest.raises(ValidationAuthError):
        service._validate_request_transition(
            ServiceRequestStatus.COMPLETED.value,
            ServiceRequestStatus.CANCELLED.value,
            service.PROVIDER_REQUEST_TRANSITIONS,
        )


def test_status_change_records_real_status_log_fields() -> None:
    service = request_service()
    offer = SimpleNamespace(completed_requests_count=4)
    provider = SimpleNamespace(completed_requests_count=7)
    row = SimpleNamespace(
        id=55,
        status=ServiceRequestStatus.IN_PROGRESS.value,
        accepted_at=None,
        completed_at=None,
        cancelled_at=None,
        offer=offer,
        provider_profile=provider,
    )

    service._set_request_status(
        row,
        ServiceRequestStatus.COMPLETED.value,
        changed_by=91,
        note="Work completed",
    )

    assert row.status == ServiceRequestStatus.COMPLETED.value
    assert row.completed_at is not None
    assert offer.completed_requests_count == 5
    assert provider.completed_requests_count == 8
    log = service.repo.add_request_status_log.call_args.args[0]
    assert log.request_id == 55
    assert log.changed_by == 91
    assert log.from_status == ServiceRequestStatus.IN_PROGRESS.value
    assert log.to_status == ServiceRequestStatus.COMPLETED.value
    assert log.note == "Work completed"
