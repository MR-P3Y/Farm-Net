from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.common.search import SearchResultType, UnifiedSearchQuery
from app.main import app
from app.modules.social.enums import SocialDiscoverySort
from app.modules.social.search_provider import SocialSearchProvider


def test_social_provider_maps_public_filters_and_safe_route() -> None:
    repository = Mock()
    repository.list_published_posts.return_value = (
        [SimpleNamespace(
            id=14,
            title="آفت گندم",
            body="راهنمای کنترل آفت در مزرعه",
            province_id=1,
            city_id=2,
            province_name="تهران",
            city_name="ری",
            village_name=None,
        )],
        1,
    )
    query = UnifiedSearchQuery(
        q="آفت",
        types=["social_post"],
        filters={
            "social_category_id": 3,
            "social_post_type": "guide",
            "province_id": 1,
            "city_id": 2,
        },
        sort="newest",
    )

    group = SocialSearchProvider(None, repository).search(query)

    repository.list_published_posts.assert_called_once_with(
        category_id=3,
        post_type="guide",
        q="افت",
        province_id=1,
        city_id=2,
        sort=SocialDiscoverySort.NEWEST,
        page=1,
        page_size=20,
    )
    assert group.type == SearchResultType.SOCIAL_POST
    assert group.items[0].route == "/social/detail/14"
    assert group.items[0].price is None


def test_social_post_type_is_allow_listed() -> None:
    with pytest.raises(ValidationError):
        UnifiedSearchQuery(q="آفت", filters={"social_post_type": "private"})


def test_social_openapi_exposes_hardened_filters() -> None:
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/social/posts"]["get"]
    parameters = {parameter["name"]: parameter for parameter in operation["parameters"]}
    assert {"category_id", "post_type", "province_id", "city_id", "q", "sort"}.issubset(
        parameters
    )
    sort_schema = parameters["sort"]["schema"]
    enum_name = sort_schema["anyOf"][0]["$ref"].split("/")[-1]
    assert schema["components"]["schemas"][enum_name]["enum"] == [
        "relevance",
        "newest",
    ]
