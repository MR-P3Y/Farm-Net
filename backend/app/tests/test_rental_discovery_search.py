from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.common.search import SearchResultType, UnifiedSearchQuery
from app.main import app
from app.modules.rentals.enums import RentalDiscoverySort
from app.modules.rentals.search_provider import RentalSearchProvider


def test_rental_provider_maps_price_availability_and_public_result() -> None:
    repository = Mock()
    repository.list_equipment.return_value = (
        [
            SimpleNamespace(
                id=21,
                title="تراکتور باغی",
                slug="orchard-tractor",
                description="تراکتور آماده اجاره",
                manufacturer="تبریز",
                model_name="T1",
                province_id=1,
                city_id=2,
                lessor_profile=SimpleNamespace(display_name="موجر سبز"),
                category=SimpleNamespace(title="تراکتور"),
                pricing_rules=[
                    SimpleNamespace(
                        is_active=True,
                        currency="TOMAN",
                        price_amount=Decimal("2500000"),
                    ),
                    SimpleNamespace(
                        is_active=True,
                        currency="TOMAN",
                        price_amount=Decimal("2000000"),
                    ),
                ],
            )
        ],
        1,
    )
    starts_at = datetime(2026, 8, 1, tzinfo=timezone.utc)
    ends_at = datetime(2026, 8, 2, tzinfo=timezone.utc)
    query = UnifiedSearchQuery(
        q="تراکتور",
        types=["rental_equipment"],
        filters={
            "province_id": 1,
            "city_id": 2,
            "rental_category_id": 3,
            "rental_operator_mode": "either",
            "rental_available_from": starts_at,
            "rental_available_to": ends_at,
            "min_price": 100,
            "max_price": 3000000,
        },
        sort="price_asc",
    )

    ratings = Mock()
    ratings.rating_values_by_subject_ids.return_value = {21: (Decimal("4.75"), 8)}
    group = RentalSearchProvider(None, repository, ratings).search(query)

    repository.list_equipment.assert_called_once_with(
        public=True,
        q="تراکتور",
        category_id=3,
        province_id=1,
        city_id=2,
        operator_mode="either",
        min_price=Decimal("100"),
        max_price=Decimal("3000000"),
        available_from=starts_at,
        available_to=ends_at,
        sort=RentalDiscoverySort.PRICE_ASC,
        page=1,
        page_size=20,
    )
    assert group.type == SearchResultType.RENTAL_EQUIPMENT
    assert group.items[0].route == "/rentals/equipment/21"
    assert group.items[0].price == Decimal("2000000")
    assert group.items[0].rating == Decimal("4.75")


def test_rental_availability_filter_requires_valid_pair() -> None:
    with pytest.raises(ValidationError):
        UnifiedSearchQuery(
            q="تراکتور",
            filters={"rental_available_from": "2026-08-01T00:00:00Z"},
        )
    with pytest.raises(ValidationError):
        UnifiedSearchQuery(
            q="تراکتور",
            filters={
                "rental_available_from": "2026-08-02T00:00:00Z",
                "rental_available_to": "2026-08-01T00:00:00Z",
            },
        )


def test_rental_operator_filter_is_allow_listed() -> None:
    with pytest.raises(ValidationError):
        UnifiedSearchQuery(q="تراکتور", filters={"rental_operator_mode": "invalid"})


def test_rental_openapi_exposes_hardened_discovery_filters() -> None:
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/rentals/equipment"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert {"min_price", "max_price", "available_from", "available_to", "sort"}.issubset(parameters)
    sort_schema = parameters["sort"]["schema"]
    enum_name = sort_schema["anyOf"][0]["$ref"].split("/")[-1]
    assert schema["components"]["schemas"][enum_name]["enum"] == [
        "relevance",
        "newest",
        "price_asc",
        "price_desc",
    ]
