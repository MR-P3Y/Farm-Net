from __future__ import annotations

import json
import threading
import time
from collections import OrderedDict
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from hashlib import sha256
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from redis.exceptions import RedisError

from app.core.config import Settings, get_settings
from app.core.exceptions import AppException
from app.core.redis import get_redis_client


_ATTRIBUTION = "© OpenStreetMap contributors"


@dataclass(frozen=True)
class GeocodingPlace:
    reference: str
    display_name: str
    short_name: str
    latitude: Decimal
    longitude: Decimal
    category: str | None
    place_type: str | None
    country_code: str | None
    address: dict[str, str]
    provider: str = "openstreetmap"
    attribution: str = _ATTRIBUTION

    def to_cache(self) -> dict[str, Any]:
        value = asdict(self)
        value["latitude"] = str(self.latitude)
        value["longitude"] = str(self.longitude)
        return value

    @classmethod
    def from_cache(cls, value: dict[str, Any]) -> GeocodingPlace:
        raw_address = value.get("address")
        address = raw_address if isinstance(raw_address, dict) else {}
        return cls(
            reference=str(value["reference"]),
            display_name=str(value["display_name"]),
            short_name=str(value["short_name"]),
            latitude=Decimal(str(value["latitude"])),
            longitude=Decimal(str(value["longitude"])),
            category=_optional_text(value.get("category"), 80),
            place_type=_optional_text(value.get("place_type"), 80),
            country_code=_optional_text(value.get("country_code"), 2),
            address={
                str(key)[:80]: str(item)[:180] for key, item in address.items() if item is not None
            },
            provider="openstreetmap",
            attribution=_ATTRIBUTION,
        )


class NominatimGeocodingClient:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        request_json: Callable[[str, dict[str, str]], Any] | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._request_json = request_json

    def search(
        self,
        *,
        query: str,
        language: str,
        limit: int,
    ) -> list[GeocodingPlace]:
        payload = self._get_json(
            "/search",
            params={
                "q": query,
                "format": "jsonv2",
                "addressdetails": "1",
                "limit": str(limit),
                "countrycodes": self.settings.geocoding_country_codes,
                "layer": "address",
                "accept-language": _provider_language(language),
            },
        )
        if not isinstance(payload, list):
            raise _provider_unavailable()
        results: list[GeocodingPlace] = []
        for row in payload[:limit]:
            if not isinstance(row, dict):
                continue
            place = _parse_place(row)
            if place is not None:
                results.append(place)
        return results

    def reverse(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
        language: str,
    ) -> GeocodingPlace | None:
        try:
            payload = self._get_json(
                "/reverse",
                params={
                    "lat": str(latitude),
                    "lon": str(longitude),
                    "format": "jsonv2",
                    "addressdetails": "1",
                    "zoom": "15",
                    "layer": "address",
                    "accept-language": _provider_language(language),
                },
            )
        except AppException as exc:
            if exc.code == "GEO_LOCATION_NOT_FOUND":
                return None
            raise
        return _parse_place(payload) if isinstance(payload, dict) else None

    def _get_json(self, path: str, *, params: dict[str, str]) -> Any:
        if not self.settings.geocoding_enabled:
            raise AppException(
                "GEO_PROVIDER_DISABLED",
                "Location search is temporarily unavailable",
                503,
            )
        url = f"{self.settings.geocoding_base_url.rstrip('/')}{path}"
        if self._request_json is not None:
            return self._request_json(url, params)
        request = Request(
            f"{url}?{urlencode(params)}",
            headers={
                "Accept": "application/json",
                "User-Agent": self.settings.geocoding_user_agent,
            },
            method="GET",
        )
        try:
            with urlopen(
                request,
                timeout=self.settings.geocoding_timeout_seconds,
            ) as response:
                if not response.geturl().lower().startswith("https://"):
                    raise _provider_unavailable()
                body = response.read(1_000_001)
                if len(body) > 1_000_000:
                    raise _provider_unavailable()
                return json.loads(body)
        except HTTPError as exc:
            if exc.code == 404:
                raise AppException(
                    "GEO_LOCATION_NOT_FOUND",
                    "No readable location was found for this point",
                    404,
                ) from exc
            raise _provider_unavailable() from exc
        except AppException:
            raise
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise _provider_unavailable() from exc


class GeocodingGateway:
    _memory_lock = threading.Lock()
    _memory_cache: OrderedDict[str, tuple[float, str]] = OrderedDict()
    _last_upstream_at = 0.0
    _memory_cache_limit = 512

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        provider: NominatimGeocodingClient | None = None,
        redis_client: Any | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.provider = provider or NominatimGeocodingClient(settings=self.settings)
        self.redis = redis_client
        if self.redis is None and self.settings.rate_limit_backend == "redis":
            self.redis = get_redis_client()

    def search(
        self,
        *,
        query: str,
        language: str,
        limit: int,
    ) -> tuple[list[GeocodingPlace], bool]:
        cache_key = self._cache_key("search", language, str(limit), query)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return [GeocodingPlace.from_cache(item) for item in cached], True
        self._acquire_upstream_slot()
        results = self.provider.search(query=query, language=language, limit=limit)
        self._cache_set(cache_key, [item.to_cache() for item in results])
        return results, False

    def reverse(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
        language: str,
    ) -> tuple[GeocodingPlace | None, bool]:
        rounded_latitude = latitude.quantize(Decimal("0.0001"))
        rounded_longitude = longitude.quantize(Decimal("0.0001"))
        cache_key = self._cache_key(
            "reverse",
            language,
            str(rounded_latitude),
            str(rounded_longitude),
        )
        cached = self._cache_get(cache_key)
        if cached is not None:
            if not cached:
                return None, True
            return GeocodingPlace.from_cache(cached[0]), True
        self._acquire_upstream_slot()
        result = self.provider.reverse(
            latitude=latitude,
            longitude=longitude,
            language=language,
        )
        self._cache_set(cache_key, [] if result is None else [result.to_cache()])
        return result, False

    def _cache_get(self, key: str) -> list[dict[str, Any]] | None:
        if self.redis is not None:
            try:
                value = self.redis.get(key)
                return _decode_cache(value) if value is not None else None
            except (RedisError, TypeError, ValueError) as exc:
                if self.settings.rate_limit_backend == "redis":
                    raise _cache_unavailable() from exc
        now = time.monotonic()
        with self._memory_lock:
            item = self._memory_cache.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at <= now:
                del self._memory_cache[key]
                return None
            self._memory_cache.move_to_end(key)
        try:
            return _decode_cache(value)
        except (TypeError, ValueError):
            return None

    def _cache_set(self, key: str, value: list[dict[str, Any]]) -> None:
        serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        if self.redis is not None:
            try:
                self.redis.setex(
                    key,
                    self.settings.geocoding_cache_ttl_seconds,
                    serialized,
                )
                return
            except RedisError as exc:
                if self.settings.rate_limit_backend == "redis":
                    raise _cache_unavailable() from exc
        with self._memory_lock:
            self._memory_cache[key] = (
                time.monotonic() + self.settings.geocoding_cache_ttl_seconds,
                serialized,
            )
            self._memory_cache.move_to_end(key)
            while len(self._memory_cache) > self._memory_cache_limit:
                self._memory_cache.popitem(last=False)

    def _acquire_upstream_slot(self) -> None:
        interval_ms = self.settings.geocoding_min_interval_ms
        if self.redis is not None:
            try:
                allowed = self.redis.set(
                    "farmnet:geocoding:upstream-slot",
                    "1",
                    nx=True,
                    px=interval_ms,
                )
                if not allowed:
                    raise _provider_limited()
                return
            except AppException:
                raise
            except RedisError as exc:
                if self.settings.rate_limit_backend == "redis":
                    raise _cache_unavailable() from exc
        with self._memory_lock:
            now = time.monotonic()
            minimum_interval = interval_ms / 1000
            if now - type(self)._last_upstream_at < minimum_interval:
                raise _provider_limited()
            type(self)._last_upstream_at = now

    @staticmethod
    def _cache_key(*parts: str) -> str:
        digest = sha256("\x1f".join(parts).encode("utf-8")).hexdigest()
        return f"farmnet:geocoding:cache:{digest}"


@lru_cache
def get_geocoding_gateway() -> GeocodingGateway:
    return GeocodingGateway()


def _parse_place(row: dict[str, Any]) -> GeocodingPlace | None:
    try:
        latitude = Decimal(str(row["lat"]))
        longitude = Decimal(str(row["lon"]))
    except (KeyError, InvalidOperation, TypeError, ValueError):
        return None
    if not latitude.is_finite() or not longitude.is_finite():
        return None
    if not Decimal("-90") <= latitude <= Decimal("90"):
        return None
    if not Decimal("-180") <= longitude <= Decimal("180"):
        return None
    display_name = _required_text(row.get("display_name"), 500)
    if display_name is None:
        return None
    raw_address = row.get("address")
    provider_address = raw_address if isinstance(raw_address, dict) else {}
    address = {
        str(key)[:80]: str(value).strip()[:180]
        for key, value in provider_address.items()
        if value is not None and str(value).strip()
    }
    short_name = _short_name(row=row, address=address, fallback=display_name)
    identity = "|".join(
        (
            str(row.get("osm_type") or ""),
            str(row.get("osm_id") or ""),
            str(latitude),
            str(longitude),
        )
    )
    return GeocodingPlace(
        reference=sha256(identity.encode("utf-8")).hexdigest()[:24],
        display_name=display_name,
        short_name=short_name,
        latitude=latitude,
        longitude=longitude,
        category=_optional_text(row.get("category"), 80),
        place_type=_optional_text(row.get("type"), 80),
        country_code=_optional_text(address.get("country_code"), 2),
        address=address,
    )


def _short_name(*, row: dict[str, Any], address: dict[str, str], fallback: str) -> str:
    explicit = _optional_text(row.get("name"), 180)
    if explicit:
        return explicit
    for key in ("village", "hamlet", "town", "city", "municipality", "county", "state"):
        value = _optional_text(address.get(key), 180)
        if value:
            return value
    return fallback.split(",", maxsplit=1)[0].strip()[:180]


def _required_text(value: Any, limit: int) -> str | None:
    normalized = " ".join(str(value or "").split()).strip()
    return normalized[:limit] if normalized else None


def _optional_text(value: Any, limit: int) -> str | None:
    return _required_text(value, limit)


def _decode_cache(value: Any) -> list[dict[str, Any]]:
    payload = json.loads(value)
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise ValueError("Invalid geocoding cache payload")
    return payload


def _provider_language(language: str) -> str:
    return "fa,en" if language == "fa" else "en,fa"


def _provider_unavailable() -> AppException:
    return AppException(
        "GEO_PROVIDER_UNAVAILABLE",
        "Location search provider is temporarily unavailable",
        503,
    )


def _cache_unavailable() -> AppException:
    return AppException(
        "GEO_SEARCH_PROTECTION_UNAVAILABLE",
        "Location search protection is temporarily unavailable",
        503,
    )


def _provider_limited() -> AppException:
    return AppException(
        "GEO_PROVIDER_RATE_LIMITED",
        "Please wait a moment before searching again",
        429,
        {"retry_after_seconds": 2},
    )
