from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.common.search import (
    SearchProvider,
    SearchResultType,
    UnifiedSearchEngine,
    UnifiedSearchFilters,
    UnifiedSearchGroup,
    UnifiedSearchQuery,
    UnifiedSearchResult,
    normalize_search_text,
)


def test_persian_search_normalization_is_shared_and_deterministic() -> None:
    assert normalize_search_text("  كِشت\u200cيـار ۱۲۳  ") == "کشت یار 123"
    assert normalize_search_text("يكي") == "یکی"


def test_unified_query_normalizes_text_and_defaults_to_every_type() -> None:
    query = UnifiedSearchQuery(q="  خدمات   كشاورزي ")

    assert query.q == "خدمات کشاورزی"
    assert query.types == list(SearchResultType)
    assert query.filters.currency.value == "TOMAN"


@pytest.mark.parametrize("query", ["", " ", "ی"])
def test_unified_query_rejects_empty_or_too_short_normalized_input(query: str) -> None:
    with pytest.raises(ValidationError):
        UnifiedSearchQuery(q=query)


def test_unified_query_rejects_duplicate_types_and_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        UnifiedSearchQuery(q="تراکتور", types=["product", "product"])
    with pytest.raises(ValidationError):
        UnifiedSearchQuery(q="تراکتور", hidden_filter=True)


def test_shared_filters_are_toman_only_and_validate_price_range() -> None:
    filters = UnifiedSearchFilters(min_price="100", max_price="200", currency="toman")
    assert filters.min_price == Decimal("100")
    assert filters.currency.value == "TOMAN"

    with pytest.raises(ValidationError):
        UnifiedSearchFilters(min_price=300, max_price=200)
    with pytest.raises(ValidationError):
        UnifiedSearchFilters(currency="IRR")


def test_public_result_contract_requires_safe_route_and_money_pair() -> None:
    result = UnifiedSearchResult(
        type="product",
        resource_id=7,
        title="بذر گندم",
        route="/products/7",
        price="250000",
        currency="TOMAN",
    )
    assert result.type == SearchResultType.PRODUCT

    with pytest.raises(ValidationError):
        UnifiedSearchResult(
            type="product", resource_id=7, title="بذر", route="https://example.com"
        )
    with pytest.raises(ValidationError):
        UnifiedSearchResult(
            type="product", resource_id=7, title="بذر", route="/products/7", price=1
        )


def test_provider_protocol_defines_one_engine_adapter_boundary() -> None:
    class ProductProvider:
        result_type = SearchResultType.PRODUCT

        def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
            return UnifiedSearchGroup(
                type=self.result_type,
                items=[],
                total=0,
                page=query.page,
                page_size=query.page_size,
            )

    provider = ProductProvider()
    assert isinstance(provider, SearchProvider)
    assert provider.search(UnifiedSearchQuery(q="کود کشاورزی")).total == 0


def test_unified_engine_orchestrates_selected_providers_in_one_response() -> None:
    class EmptyProvider:
        def __init__(self, result_type: SearchResultType, total: int) -> None:
            self.result_type = result_type
            self.total = total

        def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
            return UnifiedSearchGroup(
                type=self.result_type,
                items=[],
                total=self.total,
                page=query.page,
                page_size=query.page_size,
            )

    engine = UnifiedSearchEngine(
        [
            EmptyProvider(SearchResultType.PRODUCT, 3),
            EmptyProvider(SearchResultType.SERVICE, 2),
        ]
    )
    response = engine.search(
        UnifiedSearchQuery(q="سم پاش", types=["service", "product"])
    )

    assert response.query == "سم پاش"
    assert [group.type for group in response.groups] == [
        SearchResultType.SERVICE,
        SearchResultType.PRODUCT,
    ]
    assert response.total == 5


def test_unified_engine_rejects_duplicate_provider_registration() -> None:
    class Provider:
        result_type = SearchResultType.PRODUCT

        def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup:
            raise AssertionError("not called")

    with pytest.raises(ValueError, match="Duplicate search provider"):
        UnifiedSearchEngine([Provider(), Provider()])
