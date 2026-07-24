from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.modules.reviews.enums import ReviewStatus
from app.modules.reviews.exceptions import (
    ReviewEligibilityError,
    ReviewReportConflictError,
)
from app.modules.reviews.schemas import (
    ReviewModerationIn,
    ReviewReportCreateIn,
    ReviewReportResolutionIn,
)
from app.modules.reviews.service import ReviewsService


class ModerationRepository:
    def __init__(self):
        now = datetime(2026, 7, 23, 12, 0)
        self.review = SimpleNamespace(
            id=10,
            reviewer_user_id=1,
            source_type="order",
            source_id=20,
            subject_type="product",
            subject_id=30,
            score=4,
            body="نظر",
            status="active",
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        self.aggregate = SimpleNamespace(
            rating_sum=4,
            reviews_count=1,
            rating_average=Decimal("4.00"),
        )
        self.report_row = None
        self.logs = []
        self.commits = 0

    def get_review(self, _review_id, **_kwargs):
        return self.review

    def get_report_by_reporter(self, **_kwargs):
        return self.report_row

    def add_report(self, row):
        now = datetime(2026, 7, 23, 12, 1)
        row.id = 11
        row.created_at = now
        row.updated_at = now
        self.report_row = row
        return row

    def get_aggregate(self, **_kwargs):
        return self.aggregate

    def get_or_create_aggregate(self, **_kwargs):
        return self.aggregate

    def sync_legacy_rating_projection(self, **_kwargs):
        pass

    def add_moderation_log(self, row):
        row.id = len(self.logs) + 1
        row.created_at = datetime(2026, 7, 23, 12, row.id)
        self.logs.append(row)
        return row

    def get_report(self, _report_id, **_kwargs):
        return self.report_row

    def list_moderation_logs(self, _review_id):
        return self.logs

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass


def _service():
    service = ReviewsService.__new__(ReviewsService)
    service.db = None
    service.repo = ModerationRepository()
    service._notify_review_reported = lambda **_kwargs: None
    service._notify_review_moderated = lambda **_kwargs: None
    service._notify_report_resolution = lambda **_kwargs: None
    return service


def test_report_rejects_self_and_duplicate_without_exposing_admin_fields():
    service = _service()
    payload = ReviewReportCreateIn(reason="spam", description="  تکراری  ")
    with pytest.raises(ReviewEligibilityError):
        service.report(user=SimpleNamespace(id=1), review_id=10, payload=payload)

    result = service.report(
        user=SimpleNamespace(id=2), review_id=10, payload=payload
    )
    assert result.description == "تکراری"
    assert set(result.model_dump()) == {
        "id",
        "review_id",
        "reason",
        "description",
        "status",
        "created_at",
    }
    with pytest.raises(ReviewReportConflictError):
        service.report(user=SimpleNamespace(id=2), review_id=10, payload=payload)


def test_hide_restore_delete_adjust_aggregate_and_write_audit_logs():
    service = _service()
    hidden = service.moderate_review(
        admin_user_id=99,
        review_id=10,
        payload=ReviewModerationIn(status="hidden", note="حریم خصوصی"),
    )
    assert hidden.status == "hidden"
    assert service.repo.aggregate.reviews_count == 0
    assert service.repo.aggregate.rating_average == Decimal("0.00")
    assert service.repo.logs[-1].action == "hidden"

    restored = service.moderate_review(
        admin_user_id=99,
        review_id=10,
        payload=ReviewModerationIn(status="active", note="بررسی و بازیابی"),
    )
    assert restored.status == "active"
    assert service.repo.aggregate.rating_sum == 4
    assert service.repo.logs[-1].action == "restored"

    deleted = service.moderate_review(
        admin_user_id=99,
        review_id=10,
        payload=ReviewModerationIn(status="deleted", note="تخلف قطعی"),
    )
    assert deleted.status == ReviewStatus.DELETED.value
    assert deleted.deleted_at is not None
    assert service.repo.aggregate.reviews_count == 0
    assert [row.action for row in service.repo.logs] == [
        "hidden",
        "restored",
        "deleted",
    ]


def test_report_resolution_is_audited_and_terminal_is_idempotent():
    service = _service()
    service.report(
        user=SimpleNamespace(id=2),
        review_id=10,
        payload=ReviewReportCreateIn(reason="fraud", description="مدرک دارد"),
    )
    resolved = service.resolve_report(
        admin_user_id=99,
        report_id=11,
        payload=ReviewReportResolutionIn(
            status="resolved", resolution_note="بررسی و تأیید شد"
        ),
    )
    assert resolved.status == "resolved"
    assert resolved.reviewed_by_user_id == 99
    assert service.repo.logs[-1].action == "report_resolved"
    commits = service.repo.commits
    repeated = service.resolve_report(
        admin_user_id=99,
        report_id=11,
        payload=ReviewReportResolutionIn(
            status="resolved", resolution_note="بررسی و تأیید شد"
        ),
    )
    assert repeated.status == "resolved"
    assert service.repo.commits == commits


def test_review_report_and_admin_routes_have_separate_permissions():
    from app.main import app

    paths = app.openapi()["paths"]
    assert "post" in paths["/api/v1/reviews/{review_id}/reports"]
    assert "get" in paths["/api/v1/admin/reviews"]
    assert "patch" in paths["/api/v1/admin/reviews/{review_id}/status"]
    assert "get" in paths["/api/v1/admin/reviews/{review_id}/moderation-logs"]
    assert "get" in paths["/api/v1/admin/reviews/reports"]
    assert "patch" in paths["/api/v1/admin/reviews/reports/{report_id}/status"]
    assert (
        paths["/api/v1/admin/reviews"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/ReviewAdminListResponse"
    )
    assert (
        paths["/api/v1/admin/reviews/reports"]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/ReviewReportAdminListResponse"
    )


def test_review_notifications_use_stable_keys_and_privacy_safe_payloads(
    monkeypatch,
):
    calls = []

    class FakeNotificationService:
        def __init__(self, _db):
            pass

        def create_event_and_notify_many(self, **kwargs):
            calls.append(("many", kwargs))

        def create_event_and_notify_user(self, **kwargs):
            calls.append(("user", kwargs))

    monkeypatch.setattr(
        "app.modules.reviews.service.NotificationService",
        FakeNotificationService,
    )
    service = ReviewsService.__new__(ReviewsService)
    service.db = None
    service.repo = SimpleNamespace(
        list_recipient_user_ids_for_permission=lambda _permission: [50, 51]
    )
    report = SimpleNamespace(
        id=11,
        review_id=10,
        reporter_user_id=2,
        reason="privacy",
        description="متن خصوصی گزارش",
        resolution_note="یادداشت خصوصی مدیر",
        status="resolved",
    )
    review = SimpleNamespace(id=10, reviewer_user_id=1, status="hidden")

    service._notify_review_reported(report=report, actor_user_id=2)
    service._notify_review_moderated(
        review=review,
        actor_user_id=99,
        action="hidden",
        event_key="review-moderation:7",
    )
    service._notify_report_resolution(
        report=report,
        actor_user_id=99,
        event_key="review-report-resolution:8",
    )

    assert [call[1]["event_key"] for call in calls] == [
        "review-report-created:11",
        "review-moderation:7",
        "review-report-resolution:8",
    ]
    serialized = repr([call[1]["payload_json"] for call in calls])
    assert "متن خصوصی گزارش" not in serialized
    assert "یادداشت خصوصی مدیر" not in serialized
    assert calls[0][1]["recipient_user_ids"] == [50, 51]
