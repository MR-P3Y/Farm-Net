import re
import unicodedata
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field, field_validator, model_validator

from app.common.money import CurrencyCode, toman_currency


_SEARCH_CHARACTER_MAP = str.maketrans(
    {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "ه",
        "ـ": "",
        "\u200c": " ",
        "\u200d": " ",
        "\u00a0": " ",
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
        "٠": "0",
        "١": "1",
        "٢": "2",
        "٣": "3",
        "٤": "4",
        "٥": "5",
        "٦": "6",
        "٧": "7",
        "٨": "8",
        "٩": "9",
    }
)
_WHITESPACE = re.compile(r"\s+")


def normalize_search_text(value: str) -> str:
    """Return the deterministic canonical form used by every search provider."""
    normalized = unicodedata.normalize("NFKC", value).translate(_SEARCH_CHARACTER_MAP)
    normalized = "".join(
        character
        for character in unicodedata.normalize("NFKD", normalized)
        if unicodedata.category(character) != "Mn"
    ).translate(_SEARCH_CHARACTER_MAP)
    return _WHITESPACE.sub(" ", normalized).strip().casefold()


def search_relevance_score(query: str, title: str, *secondary_values: str | None) -> Decimal:
    normalized_query = normalize_search_text(query)
    normalized_title = normalize_search_text(title)
    if normalized_title == normalized_query:
        return Decimal("100")
    if normalized_title.startswith(normalized_query):
        return Decimal("80")
    if normalized_query in normalized_title:
        return Decimal("60")
    if any(
        normalized_query in normalize_search_text(value)
        for value in secondary_values
        if value
    ):
        return Decimal("30")
    return Decimal("0")


class SearchResultType(StrEnum):
    PRODUCT = "product"
    STORE = "store"
    SERVICE = "service"
    RENTAL_EQUIPMENT = "rental_equipment"
    CONSULTANT = "consultant"
    SOCIAL_POST = "social_post"


class SearchSort(StrEnum):
    RELEVANCE = "relevance"
    NEWEST = "newest"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    RATING = "rating"


class UnifiedSearchFilters(BaseModel):
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    product_category_id: int | None = Field(default=None, ge=1)
    service_category_id: int | None = Field(default=None, ge=1)
    rental_category_id: int | None = Field(default=None, ge=1)
    consultant_specialty_id: int | None = Field(default=None, ge=1)
    social_category_id: int | None = Field(default=None, ge=1)
    service_pricing_type: str | None = Field(
        default=None,
        pattern="^(fixed|hourly|daily|hectare|project|negotiable)$",
    )
    rental_operator_mode: str | None = Field(
        default=None,
        pattern="^(without_operator|with_operator|either)$",
    )
    rental_available_from: datetime | None = None
    rental_available_to: datetime | None = None
    min_price: Decimal | None = Field(default=None, ge=0, max_digits=18, decimal_places=2)
    max_price: Decimal | None = Field(default=None, ge=0, max_digits=18, decimal_places=2)
    currency: CurrencyCode = CurrencyCode.TOMAN

    model_config = {"extra": "forbid"}

    _currency = field_validator("currency", mode="before")(toman_currency)

    @model_validator(mode="after")
    def validate_price_range(self):
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError("min_price must be less than or equal to max_price")
        if (self.rental_available_from is None) != (self.rental_available_to is None):
            raise ValueError("Rental availability range requires both start and end")
        if (
            self.rental_available_from is not None
            and self.rental_available_to is not None
            and self.rental_available_to <= self.rental_available_from
        ):
            raise ValueError("Rental availability end must be after start")
        return self


class UnifiedSearchQuery(BaseModel):
    q: str = Field(min_length=2, max_length=100)
    types: list[SearchResultType] = Field(
        default_factory=lambda: list(SearchResultType), min_length=1, max_length=6
    )
    filters: UnifiedSearchFilters = Field(default_factory=UnifiedSearchFilters)
    sort: SearchSort = SearchSort.RELEVANCE
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)

    model_config = {"extra": "forbid"}

    @field_validator("q", mode="before")
    @classmethod
    def normalize_query(cls, value):
        if not isinstance(value, str):
            return value
        return normalize_search_text(value)

    @field_validator("types")
    @classmethod
    def reject_duplicate_types(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Search result types must be unique")
        return value


class UnifiedSearchResult(BaseModel):
    type: SearchResultType
    resource_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=250)
    subtitle: str | None = Field(default=None, max_length=500)
    image_url: str | None = Field(default=None, max_length=1000)
    route: str = Field(min_length=1, max_length=500)
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    price: Decimal | None = Field(default=None, ge=0, max_digits=18, decimal_places=2)
    currency: CurrencyCode | None = None
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    relevance_score: Decimal = Field(default=Decimal("0"), ge=0)

    model_config = {"extra": "forbid"}

    @field_validator("route")
    @classmethod
    def validate_internal_route(cls, value: str) -> str:
        if not value.startswith("/") or value.startswith("//"):
            raise ValueError("Search result route must be an internal absolute path")
        return value

    @model_validator(mode="after")
    def validate_money_pair(self):
        if (self.price is None) != (self.currency is None):
            raise ValueError("Search result price and currency must be provided together")
        return self


class UnifiedSearchGroup(BaseModel):
    type: SearchResultType
    items: list[UnifiedSearchResult]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=50)

    model_config = {"extra": "forbid"}


class UnifiedSearchResponse(BaseModel):
    query: str
    groups: list[UnifiedSearchGroup]
    total: int = Field(ge=0)

    model_config = {"extra": "forbid"}


@runtime_checkable
class SearchProvider(Protocol):
    result_type: SearchResultType

    def search(self, query: UnifiedSearchQuery) -> UnifiedSearchGroup: ...


class UnifiedSearchEngine:
    """One orchestrator for every public Farm-Net search provider."""

    def __init__(self, providers: list[SearchProvider]) -> None:
        self._providers: dict[SearchResultType, SearchProvider] = {}
        for provider in providers:
            if provider.result_type in self._providers:
                raise ValueError(f"Duplicate search provider: {provider.result_type.value}")
            self._providers[provider.result_type] = provider

    def search(self, query: UnifiedSearchQuery) -> UnifiedSearchResponse:
        groups = [
            self._providers[result_type].search(query)
            for result_type in query.types
            if result_type in self._providers
        ]
        for group in groups:
            if any(item.type != group.type for item in group.items):
                raise ValueError("Search provider returned an item from another result type")
        return UnifiedSearchResponse(
            query=query.q,
            groups=groups,
            total=sum(group.total for group in groups),
        )
