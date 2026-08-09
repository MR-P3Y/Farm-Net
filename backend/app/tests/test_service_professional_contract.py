import pytest
from pydantic import ValidationError

from app.modules.services.models import ServiceOfferMedia, ServiceProviderProfile
from app.modules.services.schemas import (
    ServiceOfferMediaIn,
    ServiceProviderProfileCreateIn,
)


def test_provider_availability_columns_are_persisted() -> None:
    columns = ServiceProviderProfile.__table__.columns
    assert "accepting_requests" in columns
    assert "availability_status" in columns
    assert "typical_response_minutes" in columns


def test_provider_availability_contract_is_bounded() -> None:
    payload = ServiceProviderProfileCreateIn(
        accepting_requests=False,
        availability_status="busy",
        typical_response_minutes=90,
    )
    assert payload.availability_status == "busy"
    assert payload.typical_response_minutes == 90

    with pytest.raises(ValidationError):
        ServiceProviderProfileCreateIn(typical_response_minutes=0)


def test_offer_media_supports_before_and_after_portfolio_stages() -> None:
    assert "portfolio_stage" in ServiceOfferMedia.__table__.columns
    assert ServiceOfferMediaIn(media_file_id=1, portfolio_stage="before").portfolio_stage == (
        "before"
    )
    assert ServiceOfferMediaIn(media_file_id=2, portfolio_stage="after").portfolio_stage == (
        "after"
    )

    with pytest.raises(ValidationError):
        ServiceOfferMediaIn(media_file_id=3, portfolio_stage="during")
