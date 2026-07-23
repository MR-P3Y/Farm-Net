from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.modules.auth.exceptions import PermissionDeniedError
from app.modules.consultants.enums import ConsultRequestStatus
from app.modules.orders.enums import OrderStatus
from app.modules.rentals.enums import RentalRequestStatus
from app.modules.reviews.enums import (
    ReviewSourceType,
    ReviewStatus,
    ReviewSubjectType,
)
from app.modules.reviews.exceptions import (
    ReviewConflictError,
    ReviewEligibilityError,
    ReviewLifecycleError,
)
from app.modules.reviews.schemas import ReviewCreateIn, ReviewUpdateIn
from app.modules.reviews.service import ReviewsService
from app.modules.services.enums import ServiceRequestStatus


class FakeReviewsRepository:
    def __init__(self) -> None:
        self.order = SimpleNamespace(
            id=10,
            buyer_user_id=1,
            store_id=20,
            status=OrderStatus.DELIVERED.value,
        )
        self.service_request = SimpleNamespace(
            id=11,
            requester_user_id=1,
            offer_id=30,
            provider_profile_id=31,
            status=ServiceRequestStatus.COMPLETED.value,
        )
        self.rental_request = SimpleNamespace(
            id=12,
            requester_user_id=1,
            equipment_id=40,
            lessor_profile_id=41,
            status=RentalRequestStatus.COMPLETED.value,
        )
        self.consult_request = SimpleNamespace(
            id=13,
            requester_user_id=1,
            consultant_profile_id=50,
            status=ConsultRequestStatus.COMPLETED.value,
        )
        self.own_review = None
        self.existing = None
        self.commits = 0
        self.aggregate = None
        self.legacy_projection = None

    def get_order_for_update(self, source_id: int):
        return self.order if source_id == self.order.id else None

    def order_has_product(self, *, order_id: int, product_id: int) -> bool:
        return order_id == self.order.id and product_id == 21

    def get_store(self, store_id: int):
        return SimpleNamespace(id=store_id, owner_user_id=2)

    def get_service_request_for_update(self, source_id: int):
        return self.service_request if source_id == self.service_request.id else None

    def get_service_provider(self, profile_id: int):
        return SimpleNamespace(id=profile_id, user_id=3)

    def get_rental_request_for_update(self, source_id: int):
        return self.rental_request if source_id == self.rental_request.id else None

    def get_lessor_profile(self, profile_id: int):
        return SimpleNamespace(id=profile_id, user_id=4)

    def get_consult_request_for_update(self, source_id: int):
        return self.consult_request if source_id == self.consult_request.id else None

    def get_consultant_profile(self, profile_id: int):
        return SimpleNamespace(id=profile_id, user_id=5)

    def get_existing(self, **_kwargs):
        return self.existing

    def add(self, row):
        now = datetime(2026, 7, 23, 8, 0, 0)
        row.id = 100
        row.created_at = now
        row.updated_at = now
        self.own_review = row
        return row

    def list_own(self, **_kwargs):
        rows = [] if self.own_review is None else [self.own_review]
        return rows, len(rows)

    def get_own(self, **_kwargs):
        return self.own_review

    def get_aggregate(self, **_kwargs):
        return self.aggregate

    def add_aggregate(self, row):
        self.aggregate = row
        return row

    def sync_legacy_rating_projection(self, **kwargs):
        self.legacy_projection = kwargs

    def public_subject_exists(self, **_kwargs):
        return True

    def list_public(self, **_kwargs):
        if self.own_review is None:
            return [], 0
        return [(self.own_review, SimpleNamespace(display_name="کاربر آزمون"))], 1

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        pass


def _service() -> tuple[ReviewsService, FakeReviewsRepository]:
    service = ReviewsService.__new__(ReviewsService)
    repository = FakeReviewsRepository()
    service.db = None
    service.repo = repository
    return service, repository


@pytest.mark.parametrize(
    ("source_type", "source_id", "subject_type", "subject_id", "owner_id"),
    [
        (ReviewSourceType.ORDER, 10, ReviewSubjectType.PRODUCT, 21, 2),
        (ReviewSourceType.ORDER, 10, ReviewSubjectType.STORE, 20, 2),
        (
            ReviewSourceType.SERVICE_REQUEST,
            11,
            ReviewSubjectType.SERVICE_OFFER,
            30,
            3,
        ),
        (
            ReviewSourceType.SERVICE_REQUEST,
            11,
            ReviewSubjectType.SERVICE_PROVIDER,
            31,
            3,
        ),
        (
            ReviewSourceType.RENTAL_REQUEST,
            12,
            ReviewSubjectType.RENTAL_EQUIPMENT,
            40,
            4,
        ),
        (
            ReviewSourceType.RENTAL_REQUEST,
            12,
            ReviewSubjectType.RENTAL_LESSOR,
            41,
            4,
        ),
        (
            ReviewSourceType.CONSULT_REQUEST,
            13,
            ReviewSubjectType.CONSULTANT,
            50,
            5,
        ),
    ],
)
def test_all_review_subjects_resolve_from_real_completed_sources(
    source_type,
    source_id,
    subject_type,
    subject_id,
    owner_id,
) -> None:
    service, _ = _service()
    assert (
        service._validate_eligibility(
            reviewer_user_id=1,
            source_type=source_type,
            source_id=source_id,
            subject_type=subject_type,
            subject_id=subject_id,
        )
        == owner_id
    )


def test_eligibility_rejects_wrong_owner_incomplete_and_unrelated_target() -> None:
    service, repository = _service()

    with pytest.raises(PermissionDeniedError):
        service._validate_eligibility(
            reviewer_user_id=99,
            source_type=ReviewSourceType.ORDER,
            source_id=10,
            subject_type=ReviewSubjectType.STORE,
            subject_id=20,
        )

    repository.order.status = OrderStatus.SHIPPED.value
    with pytest.raises(ReviewEligibilityError) as incomplete:
        service._validate_eligibility(
            reviewer_user_id=1,
            source_type=ReviewSourceType.ORDER,
            source_id=10,
            subject_type=ReviewSubjectType.STORE,
            subject_id=20,
        )
    assert incomplete.value.details["required_status"] == OrderStatus.DELIVERED.value

    repository.order.status = OrderStatus.DELIVERED.value
    with pytest.raises(ReviewEligibilityError):
        service._validate_eligibility(
            reviewer_user_id=1,
            source_type=ReviewSourceType.ORDER,
            source_id=10,
            subject_type=ReviewSubjectType.PRODUCT,
            subject_id=999,
        )


def test_create_normalizes_contract_prevents_duplicate_and_exposes_owner_flags() -> None:
    service, repository = _service()
    user = SimpleNamespace(id=1)
    payload = ReviewCreateIn(
        source_type="service_request",
        source_id=11,
        subject_type="service_provider",
        subject_id=31,
        score=5,
        body="  عالی بود  ",
    )
    result = service.create(user=user, payload=payload)
    assert result.id == 100
    assert result.body == "عالی بود"
    assert result.status == ReviewStatus.ACTIVE.value
    assert result.can_edit is True
    assert result.can_delete is True
    assert repository.commits == 1
    assert repository.aggregate.rating_sum == 5
    assert repository.aggregate.reviews_count == 1
    assert repository.aggregate.rating_average == Decimal("5.00")

    repository.existing = SimpleNamespace(id=100)
    with pytest.raises(ReviewConflictError) as duplicate:
        service.create(user=user, payload=payload)
    assert duplicate.value.details == {"review_id": 100}


def test_create_prevents_self_review() -> None:
    service, repository = _service()
    repository.get_service_provider = lambda _profile_id: SimpleNamespace(
        id=31, user_id=1
    )
    with pytest.raises(ReviewEligibilityError):
        service.create(
            user=SimpleNamespace(id=1),
            payload=ReviewCreateIn(
                source_type="service_request",
                source_id=11,
                subject_type="service_provider",
                subject_id=31,
                score=5,
            ),
        )


def test_owner_update_and_idempotent_soft_delete_follow_lifecycle() -> None:
    service, repository = _service()
    user = SimpleNamespace(id=1)
    created = service.create(
        user=user,
        payload=ReviewCreateIn(
            source_type="consult_request",
            source_id=13,
            subject_type="consultant",
            subject_id=50,
            score=4,
        ),
    )

    updated = service.update(
        user=user,
        review_id=created.id,
        payload=ReviewUpdateIn(score=5, body="  دقیق و مفید  "),
    )
    assert updated.score == 5
    assert updated.body == "دقیق و مفید"
    assert repository.aggregate.rating_sum == 5
    assert repository.aggregate.rating_average == Decimal("5.00")

    repository.own_review.status = ReviewStatus.HIDDEN.value
    with pytest.raises(ReviewLifecycleError):
        service.update(
            user=user,
            review_id=created.id,
            payload=ReviewUpdateIn(score=3),
        )

    deleted = service.delete(user=user, review_id=created.id)
    assert deleted.status == ReviewStatus.DELETED.value
    assert deleted.deleted_at is not None
    assert deleted.can_edit is False
    assert deleted.can_delete is False
    commits_after_delete = repository.commits
    repeated = service.delete(user=user, review_id=created.id)
    assert repeated.status == ReviewStatus.DELETED.value
    assert repository.commits == commits_after_delete


def test_public_reviews_hide_identity_and_return_canonical_summary() -> None:
    service, repository = _service()
    service.create(
        user=SimpleNamespace(id=1),
        payload=ReviewCreateIn(
            source_type="order",
            source_id=10,
            subject_type="product",
            subject_id=21,
            score=4,
            body="خوب",
        ),
    )
    items, total, summary = service.list_public(
        subject_type=ReviewSubjectType.PRODUCT,
        subject_id=21,
        page=1,
        page_size=20,
    )
    assert total == 1
    assert items[0].author.display_name == "کاربر آزمون"
    assert "reviewer_user_id" not in items[0].model_dump()
    assert summary.rating_average == Decimal("4.00")
    assert summary.reviews_count == 1


def test_review_crud_routes_and_owner_contract_are_typed() -> None:
    from app.main import app
    from app.modules.reviews.schemas import ReviewOwnerOut

    paths = app.openapi()["paths"]
    assert {"post"} <= set(paths["/api/v1/reviews"])
    assert {"get"} <= set(paths["/api/v1/reviews/me"])
    assert {"get", "patch", "delete"} <= set(
        paths["/api/v1/reviews/me/{review_id}"]
    )
    assert {"get"} <= set(
        paths["/api/v1/reviews/subjects/{subject_type}/{subject_id}"]
    )
    assert set(ReviewOwnerOut.model_fields) == {
        "id",
        "source_type",
        "source_id",
        "subject_type",
        "subject_id",
        "score",
        "body",
        "status",
        "can_edit",
        "can_delete",
        "created_at",
        "updated_at",
        "deleted_at",
    }
