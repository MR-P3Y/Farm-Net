from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from app.common.search import SearchResultType, UnifiedSearchQuery, search_relevance_score
from app.main import app
from app.modules.products.enums import ProductDiscoverySort
from app.modules.products.search_provider import ProductSearchProvider
from app.modules.stores.enums import StoreDiscoverySort
from app.modules.stores.search_provider import StoreSearchProvider


def test_relevance_score_uses_normalized_persian_text() -> None:
    assert search_relevance_score("كود ۱۲", "کود 12") == Decimal("100")
    assert search_relevance_score("کود", "کود کشاورزی") == Decimal("80")
    assert search_relevance_score("کشاورزی", "فروشگاه", "لوازم كشاورزي") == Decimal("30")


def test_product_provider_maps_shared_filters_and_public_result() -> None:
    repository = Mock()
    repository.list_public_products.return_value = (
        [
            SimpleNamespace(
                id=7,
                name="سم پاش",
                slug="sprayer",
                short_description="سم پاش باغی",
                description=None,
                price=Decimal("250000"),
                currency="TOMAN",
                store=SimpleNamespace(name="فروشگاه سبز", province_id=1, city_id=2),
            )
        ],
        1,
    )
    query = UnifiedSearchQuery(
        q="سم پاش",
        types=["product"],
        filters={
            "province_id": 1,
            "city_id": 2,
            "product_category_id": 3,
            "min_price": 100,
            "max_price": 300000,
        },
        sort="price_asc",
    )

    group = ProductSearchProvider(None, repository).search(query)

    repository.list_public_products.assert_called_once_with(
        q="سم پاش",
        category_id=3,
        province_id=1,
        city_id=2,
        min_price=Decimal("100"),
        max_price=Decimal("300000"),
        sort=ProductDiscoverySort.PRICE_ASC,
        page=1,
        page_size=20,
    )
    assert group.type == SearchResultType.PRODUCT
    assert group.items[0].route == "/products/7"
    assert group.items[0].currency.value == "TOMAN"


def test_store_provider_falls_back_to_relevance_for_price_sort() -> None:
    repository = Mock()
    repository.list_public_stores.return_value = (
        [
            SimpleNamespace(
                id=9,
                name="بازار کشاورزی",
                slug="agri-market",
                description="فروش نهاده",
                province_id=1,
                city_id=2,
            )
        ],
        1,
    )
    query = UnifiedSearchQuery(q="بازار", types=["store"], sort="price_desc")

    group = StoreSearchProvider(None, repository).search(query)

    assert repository.list_public_stores.call_args.kwargs["sort"] == StoreDiscoverySort.RELEVANCE
    assert group.items[0].route == "/stores/agri-market"


def test_public_product_openapi_exposes_hardened_filters() -> None:
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/public/products"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert {"min_price", "max_price", "sort"}.issubset(parameters)
    sort_schema = parameters["sort"]["schema"]
    enum_schema = schema["components"]["schemas"][sort_schema["anyOf"][0]["$ref"].split("/")[-1]]
    assert enum_schema["enum"] == [
        "relevance",
        "newest",
        "price_asc",
        "price_desc",
    ]


def test_public_store_openapi_exposes_safe_sort() -> None:
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/public/stores"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    sort_schema = parameters["sort"]["schema"]
    enum_schema = schema["components"]["schemas"][sort_schema["anyOf"][0]["$ref"].split("/")[-1]]
    assert enum_schema["enum"] == ["relevance", "newest"]
