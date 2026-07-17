from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
from app.modules.services.enums import ServiceRequestStatus
from app.modules.services.schemas import (
    ServiceRequestAdminDetailOut,
    ServiceRequestCreateIn,
    ServiceRequestDetailOut,
    ServiceRequestListOut,
    ServiceRequestStatusLogOut,
)
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


def notification_request(**overrides):
    values = {
        "id": 55,
        "requester_user_id": 10,
        "provider_profile_id": 20,
        "offer_id": 30,
        "category_id": 40,
        "title": "Soil test",
        "offer": SimpleNamespace(title="Laboratory soil test"),
        "provider_profile": SimpleNamespace(user_id=99),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("status", "event_type"),
    [
        (ServiceRequestStatus.ACCEPTED.value, "service_request.accepted"),
        (ServiceRequestStatus.REJECTED.value, "service_request.rejected"),
        (ServiceRequestStatus.IN_PROGRESS.value, "service_request.in_progress"),
        (ServiceRequestStatus.COMPLETED.value, "service_request.completed"),
        (ServiceRequestStatus.CANCELLED.value, "service_request.cancelled"),
    ],
)
def test_request_transition_uses_stable_event_contract(status, event_type) -> None:
    service = request_service()
    service.db = Mock()
    notifier = Mock()
    with patch(
        "app.modules.services.service.NotificationService",
        return_value=notifier,
    ):
        service._notify_request_transition(
            notification_request(),
            old_status=ServiceRequestStatus.OPEN.value,
            new_status=status,
            actor_user_id=88,
            recipient_user_ids=[10, 10, 88],
            provider_action=False,
        )

    call = notifier.create_event_and_notify_many.call_args.kwargs
    assert call["event_type"] == event_type
    assert call["event_key"] == f"service_request:55:open:{status}"
    assert call["recipient_user_ids"] == [10]
    assert call["commit"] is False
    assert set(call["payload_json"]) == {
        "request_id",
        "offer_id",
        "offer_title",
        "provider_profile_id",
        "requester_user_id",
        "old_status",
        "new_status",
        "category_id",
    }


def test_request_create_notification_prevents_self_notification() -> None:
    service = request_service()
    service.db = Mock()
    notifier = Mock()
    with patch(
        "app.modules.services.service.NotificationService",
        return_value=notifier,
    ):
        service._notify_request_created(
            notification_request(provider_profile=SimpleNamespace(user_id=10)),
            actor_user_id=10,
        )
    notifier.create_event_and_notify_many.assert_not_called()


def test_request_create_notification_contract() -> None:
    service = request_service()
    service.db = Mock()
    notifier = Mock()
    with patch(
        "app.modules.services.service.NotificationService",
        return_value=notifier,
    ):
        service._notify_request_created(notification_request(), actor_user_id=10)
    call = notifier.create_event_and_notify_many.call_args.kwargs
    assert call["event_type"] == NotificationEventType.SERVICE_REQUEST_CREATED.value
    assert call["event_key"] == "service_request:55:created"
    assert call["recipient_user_ids"] == [99]
    assert call["commit"] is False


def test_notification_service_reuses_existing_recipient_notification() -> None:
    service = NotificationService.__new__(NotificationService)
    service.repo = Mock()
    service.create_event = Mock(return_value=SimpleNamespace(id=7))
    existing = SimpleNamespace(
        id=8,
        event_id=7,
        recipient_user_id=10,
        channel="in_app",
        title="Existing",
        body="Existing notification",
        action_url=None,
        priority="normal",
        status="unread",
        read_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    service.repo.get_notification_for_event.return_value = existing
    service.repo.get_recipient.return_value = SimpleNamespace(
        email=None,
        phone=None,
        is_email_verified=False,
        is_phone_verified=False,
    )
    service.repo.list_routing_preferences.return_value = []
    service.notify_user = Mock()

    rows = service.create_event_and_notify_many(
        event_type="service_request.created",
        event_key="service_request:55:created",
        recipient_user_ids=[10, 10],
        title="Created",
        body="Created",
        commit=False,
    )

    assert len(rows) == 1
    service.notify_user.assert_not_called()


def test_role_specific_request_contracts_hide_private_fields() -> None:
    now = datetime.utcnow()
    common = {
        "id": 1,
        "provider_profile_id": 2,
        "offer_id": 3,
        "category_id": 4,
        "title": "Request",
        "status": "open",
        "budget_amount": Decimal("100"),
        "currency": "TOMAN",
        "created_at": now,
        "updated_at": now,
    }
    list_payload = ServiceRequestListOut(**common).model_dump()
    assert "description" not in list_payload
    assert "address_text" not in list_payload
    assert "contact_method" not in list_payload
    assert "latitude" not in list_payload
    assert "longitude" not in list_payload

    log = ServiceRequestStatusLogOut(
        id=1,
        request_id=1,
        changed_by_user_id=9,
        old_status=None,
        new_status="open",
        created_at=now,
    )
    detail = ServiceRequestDetailOut(
        **common,
        requester_user_id=9,
        description="Private description",
        contact_method="in_app",
        status_logs=[log],
    ).model_dump()
    assert "admin_note" not in detail
    assert set(detail["status_logs"][0]) == {
        "id",
        "request_id",
        "changed_by_user_id",
        "old_status",
        "new_status",
        "note",
        "created_at",
    }
    admin = ServiceRequestAdminDetailOut(**detail, admin_note="internal").model_dump()
    assert admin["admin_note"] == "internal"
