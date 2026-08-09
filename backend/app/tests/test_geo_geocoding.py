import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import parse_qs, urlparse

from app.core.config import Settings
from app.main import app
from app.modules.geo.geocoding import (
    GeocodingGateway,
    GeocodingPlace,
    NominatimGeocodingClient,
)
from app.modules.geo.models import GeoCounty, GeoProvince, GeoVillage
from app.modules.geo.service import GeoLocationSearchService


def _settings(**overrides) -> Settings:
    values = {
        "app_env": "test",
        "database_url": "mysql+pymysql://user:password@mysql/farmnet",
        "rate_limit_backend": "memory",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


def _provider_row() -> dict:
    return {
        "osm_type": "node",
        "osm_id": 42,
        "lat": "29.8051",
        "lon": "52.4897",
        "display_name": "قلات، شهرستان شیراز، استان فارس، ایران",
        "name": "قلات",
        "category": "place",
        "type": "village",
        "address": {
            "village": "قلات",
            "county": "شهرستان شیراز",
            "state": "استان فارس",
            "country": "ایران",
            "country_code": "ir",
        },
    }


def test_nominatim_search_is_explicit_identified_and_iran_bounded() -> None:
    captured: dict[str, str] = {}

    def request_json(url: str, params: dict[str, str]):
        captured["url"] = url
        captured["query"] = params["q"]
        captured["countrycodes"] = params["countrycodes"]
        captured["language"] = params["accept-language"]
        return [_provider_row()]

    provider = NominatimGeocodingClient(
        settings=_settings(),
        request_json=request_json,
    )

    results = provider.search(query="قلات شیراز", language="fa", limit=5)

    assert len(results) == 1
    assert results[0].short_name == "قلات"
    assert results[0].latitude == Decimal("29.8051")
    assert captured == {
        "url": "https://nominatim.openstreetmap.org/search",
        "query": "قلات شیراز",
        "countrycodes": "ir",
        "language": "fa,en",
    }


def test_standard_transport_identifies_the_application_and_encodes_query() -> None:
    response = MagicMock()
    response.__enter__.return_value = response
    response.geturl.return_value = "https://nominatim.openstreetmap.org/search"
    response.read.return_value = json.dumps([_provider_row()]).encode()
    provider = NominatimGeocodingClient(settings=_settings())

    with patch("app.modules.geo.geocoding.urlopen", return_value=response) as opener:
        results = provider.search(query="شیراز", language="fa", limit=1)

    request = opener.call_args.args[0]
    query = parse_qs(urlparse(request.full_url).query)
    assert request.get_header("User-agent") == "FarmNet/0.28 (+https://farmnet.ir)"
    assert query["q"] == ["شیراز"]
    assert query["countrycodes"] == ["ir"]
    assert len(results) == 1


def test_gateway_caches_query_without_a_second_provider_request() -> None:
    class Provider:
        calls = 0

        def search(self, **_kwargs):
            self.calls += 1
            return NominatimGeocodingClient(
                settings=_settings(),
                request_json=lambda _url, _params: [_provider_row()],
            ).search(query="قلات", language="fa", limit=5)

    GeocodingGateway._memory_cache.clear()
    GeocodingGateway._last_upstream_at = 0
    provider = Provider()
    gateway = GeocodingGateway(settings=_settings(), provider=provider)

    first, first_cached = gateway.search(query="قلات", language="fa", limit=5)
    second, second_cached = gateway.search(query="قلات", language="fa", limit=5)

    assert provider.calls == 1
    assert first_cached is False
    assert second_cached is True
    assert first == second


def test_location_service_maps_provider_address_to_internal_geo_ids() -> None:
    place = GeocodingPlace(
        reference="place-1",
        display_name="قلات، شیراز، فارس",
        short_name="قلات",
        latitude=Decimal("29.8051"),
        longitude=Decimal("52.4897"),
        category="place",
        place_type="village",
        country_code="ir",
        address={
            "village": "قلات",
            "county": "شهرستان شیراز",
            "state": "استان فارس",
        },
    )
    gateway = Mock()
    gateway.search.return_value = ([place], False)
    service = GeoLocationSearchService(Mock(), gateway=gateway)
    service.repo = Mock()

    def matched(model, **_kwargs):
        if model is GeoProvince:
            return SimpleNamespace(id=1)
        if model is GeoCounty:
            return SimpleNamespace(id=2)
        if model is GeoVillage:
            return SimpleNamespace(
                id=6,
                province_id=1,
                county_id=2,
                district_id=3,
                rural_district_id=4,
            )
        return None

    service.repo.find_unique_by_names.side_effect = matched
    results, cached = service.search(query="قلات", language="fa", limit=5)

    assert cached is False
    assert results[0].province_id == 1
    assert results[0].county_id == 2
    assert results[0].district_id == 3
    assert results[0].rural_district_id == 4
    assert results[0].village_id == 6


def test_geocoding_routes_are_private_and_no_store() -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/geo/search" in paths
    assert "/api/v1/geo/reverse" in paths
    assert paths["/api/v1/geo/search"]["get"]["security"]
