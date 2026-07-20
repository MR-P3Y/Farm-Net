from enum import StrEnum


class ProductStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class ProductUnit(StrEnum):
    KG = "kg"
    GRAM = "gram"
    LITER = "liter"
    ML = "ml"
    PIECE = "piece"
    PACK = "pack"
    BAG = "bag"
    TON = "ton"
    METER = "meter"
    OTHER = "other"


class ProductDiscoverySort(StrEnum):
    RELEVANCE = "relevance"
    NEWEST = "newest"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
