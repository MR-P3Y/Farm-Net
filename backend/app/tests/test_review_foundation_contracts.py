from sqlalchemy import CheckConstraint, UniqueConstraint

from app.modules.auth.seed import BASE_PERMISSIONS
from app.modules.reviews.enums import (
    ReviewReportReason,
    ReviewReportStatus,
    ReviewSourceType,
    ReviewStatus,
    ReviewSubjectType,
)
from app.modules.reviews.models import (
    MarketplaceRatingAggregate,
    MarketplaceReview,
    MarketplaceReviewModerationLog,
    MarketplaceReviewReport,
)


def _constraint_names(model: type, constraint_type: type) -> set[str]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, constraint_type) and constraint.name is not None
    }


def test_review_tables_and_exact_once_constraints_are_explicit() -> None:
    assert MarketplaceReview.__tablename__ == "marketplace_reviews"
    assert MarketplaceRatingAggregate.__tablename__ == "marketplace_rating_aggregates"
    assert MarketplaceReviewReport.__tablename__ == "marketplace_review_reports"
    assert (
        MarketplaceReviewModerationLog.__tablename__
        == "marketplace_review_moderation_logs"
    )

    assert "uq_marketplace_review_eligibility" in _constraint_names(
        MarketplaceReview, UniqueConstraint
    )
    assert "uq_marketplace_rating_subject" in _constraint_names(
        MarketplaceRatingAggregate, UniqueConstraint
    )
    assert "uq_marketplace_review_reporter" in _constraint_names(
        MarketplaceReviewReport, UniqueConstraint
    )
    assert any(
        constraint.name is None
        and tuple(column.name for column in constraint.columns) == ("event_key",)
        for constraint in MarketplaceReviewModerationLog.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    )


def test_review_database_checks_cover_score_types_state_and_aggregates() -> None:
    review_checks = _constraint_names(MarketplaceReview, CheckConstraint)
    assert {
        "ck_marketplace_review_score",
        "ck_marketplace_review_source_id_positive",
        "ck_marketplace_review_subject_id_positive",
        "ck_marketplace_review_source_type",
        "ck_marketplace_review_subject_type",
        "ck_marketplace_review_source_subject",
        "ck_marketplace_review_status",
        "ck_marketplace_review_deleted_state",
    } <= review_checks

    aggregate_checks = _constraint_names(
        MarketplaceRatingAggregate, CheckConstraint
    )
    assert {
        "ck_marketplace_rating_subject_type",
        "ck_marketplace_rating_count_nonnegative",
        "ck_marketplace_rating_subject_id_positive",
        "ck_marketplace_rating_sum_range",
        "ck_marketplace_rating_average_range",
        "ck_marketplace_rating_empty_or_scored",
    } <= aggregate_checks

    report_checks = _constraint_names(MarketplaceReviewReport, CheckConstraint)
    assert {
        "ck_marketplace_review_report_reason",
        "ck_marketplace_review_report_status",
        "ck_marketplace_review_report_review_state",
    } <= report_checks


def test_review_enums_define_only_the_approved_foundation_boundary() -> None:
    assert {item.value for item in ReviewSourceType} == {
        "order",
        "service_request",
        "rental_request",
        "consult_request",
    }
    assert {item.value for item in ReviewSubjectType} == {
        "product",
        "store",
        "service_offer",
        "service_provider",
        "rental_equipment",
        "rental_lessor",
        "consultant",
    }
    assert {item.value for item in ReviewStatus} == {
        "active",
        "hidden",
        "deleted",
    }
    assert {item.value for item in ReviewReportStatus} == {
        "open",
        "reviewed",
        "resolved",
        "dismissed",
    }
    assert {item.value for item in ReviewReportReason} == {
        "spam",
        "abuse",
        "harassment",
        "privacy",
        "fraud",
        "other",
    }


def test_review_permissions_are_dedicated_and_complete() -> None:
    permission_codes = {permission.code for permission in BASE_PERMISSIONS}
    assert {
        "reviews.create",
        "reviews.read_own",
        "reviews.manage_own",
        "review_reports.create",
        "reviews.admin_read",
        "reviews.admin_moderate",
        "review_reports.admin_read",
        "review_reports.admin_resolve",
    } <= permission_codes
