from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.common.search import SearchResultType, UnifiedSearchQuery
from app.main import app
from app.modules.services.enums import ServiceDiscoverySort
from app.modules.services.search_provider import ServiceSearchProvider


def test_service_provider_maps_shared_filters_and_public_result() -> None:
    repository = Mock()
    provider_profile = SimpleNamespace(
        display_name="خدمات سبز",
        title="متخصص باغ",
        rating_average=Decimal("4.50"),
    )
    repository.list_public_offers.return_value = (
        [
            SimpleNamespace(
                id=11,
                title="سم پاشی باغ",
                slug="orchard-spraying",
                short_description="اجرای حرفه ای",
                description=None,
                service_area="تهران",
                province_id=1,
                city_id=2,
                price_amount=Decimal("800000"),
                currency="TOMAN",
                provider_profile=provider_profile,
                category=SimpleNamespace(title="سم پاشی"),
            )
        ],
        1,
    )
    query = UnifiedSearchQuery(
        q="سم پاشی",
        types=["service"],
        filters={
            "province_id": 1,
            "city_id": 2,
            "service_category_id": 3,
            "service_pricing_type": "fixed",
            "min_price": 100,
            "max_price": 900000,
        },
        sort="rating",
    )

    group = ServiceSearchProvider(None, repository).search(query)

    repository.list_public_offers.assert_called_once_with(
        q="سم پاشی",
        category_id=3,
        provider_profile_id=None,
        pricing_type="fixed",
        province_id=1,
        city_id=2,
        min_price=Decimal("100"),
        max_price=Decimal("900000"),
        sort=ServiceDiscoverySort.RATING,
        page=1,
        page_size=20,
    )
    assert group.type == SearchResultType.SERVICE
    assert group.items[0].route == "/services/11"
    assert group.items[0].rating == Decimal("4.50")


def test_negotiable_service_result_does_not_invent_price() -> None:
    repository = Mock()
    repository.list_public_offers.return_value = (
        [
            SimpleNamespace(
                id=12,
                title="مشاوره مزرعه",
                slug="farm-help",
                short_description=None,
                description=None,
                service_area=None,
                province_id=None,
                city_id=None,
                price_amount=None,
                currency="TOMAN",
                provider_profile=SimpleNamespace(
                    display_name="کشاورز", title=None, rating_average=Decimal("0")
                ),
                category=None,
            )
        ],
        1,
    )

    result = ServiceSearchProvider(None, repository).search(
        UnifiedSearchQuery(q="مشاوره", types=["service"])
    ).items[0]

    assert result.price is None
    assert result.currency is None


def test_service_pricing_filter_is_allow_listed() -> None:
    with pytest.raises(ValidationError):
        UnifiedSearchQuery(q="خدمت", filters={"service_pricing_type": "raw-sql"})


def test_service_openapi_exposes_hardened_discovery_filters() -> None:
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/services/offers"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert {"min_price", "max_price", "sort"}.issubset(parameters)
    sort_schema = parameters["sort"]["schema"]
    enum_schema = schema["components"]["schemas"][sort_schema["anyOf"][0]["$ref"].split("/")[-1]]
    assert enum_schema["enum"] == [
        "relevance",
        "newest",
        "price_asc",
        "price_desc",
        "rating",
    ]
