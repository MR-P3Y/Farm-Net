from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from app.common.search import SearchResultType, UnifiedSearchQuery
from app.main import app
from app.modules.consultants.enums import ConsultantDiscoverySort
from app.modules.consultants.search_provider import ConsultantSearchProvider


def test_consultant_provider_maps_filters_and_safe_public_result() -> None:
    repository = Mock()
    specialty = SimpleNamespace(title="گیاه‌پزشکی", code="plant_health", is_active=True)
    repository.list_profiles.return_value = (
        [SimpleNamespace(
            id=9,
            display_name="دکتر کاظمی",
            title="مشاور گیاه‌پزشکی",
            bio="مشاوره تخصصی باغ",
            province_id=1,
            city_id=2,
            province_name="تهران",
            city_name="تهران",
            rating_average=Decimal("4.80"),
            specialty_links=[SimpleNamespace(specialty=specialty)],
        )],
        1,
    )
    query = UnifiedSearchQuery(
        q="گياه پزشکي",
        types=["consultant"],
        filters={"consultant_specialty_id": 3, "province_id": 1, "city_id": 2},
        sort="rating",
    )

    group = ConsultantSearchProvider(None, repository).search(query)

    repository.list_profiles.assert_called_once_with(
        public_only=True,
        specialty_id=3,
        q="گیاه پزشکی",
        province_id=1,
        city_id=2,
        sort=ConsultantDiscoverySort.RATING,
        page=1,
        page_size=20,
    )
    assert group.type == SearchResultType.CONSULTANT
    assert group.items[0].route == "/consultants/9"
    assert group.items[0].rating == Decimal("4.80")
    assert group.items[0].price is None


def test_consultant_openapi_exposes_allow_listed_sort() -> None:
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/consultants"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}

    assert {"province_id", "city_id", "specialty_id", "q", "sort"}.issubset(parameters)
    sort_schema = parameters["sort"]["schema"]
    enum_name = sort_schema["anyOf"][0]["$ref"].split("/")[-1]
    assert schema["components"]["schemas"][enum_name]["enum"] == [
        "relevance",
        "newest",
        "rating",
    ]
