import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


RESULT_TYPES = [
    "product",
    "store",
    "service",
    "rental_equipment",
    "consultant",
    "social_post",
]
FORBIDDEN_RESULT_KEYS = {
    "phone",
    "email",
    "admin_note",
    "owner_user_id",
    "author_user_id",
    "requester_user_id",
}


def request_json(base_url: str, path: str, payload: dict | None = None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310 - operator-selected URL
            headers = {key.lower(): value for key, value in response.headers.items()}
            return response.status, headers, json.load(response)
    except HTTPError as error:
        headers = {key.lower(): value for key, value in error.headers.items()}
        return error.code, headers, json.load(error)


def assert_search_result(body: dict, expected_types: list[str]) -> None:
    assert body["success"] is True
    data = body["data"]
    assert [group["type"] for group in data["groups"]] == expected_types
    assert data["total"] == sum(group["total"] for group in data["groups"])
    for group in data["groups"]:
        for item in group["items"]:
            assert item["type"] == group["type"]
            assert item["route"].startswith("/") and not item["route"].startswith("//")
            assert not FORBIDDEN_RESULT_KEYS.intersection(item)
            if item.get("price") is not None:
                assert item["currency"] == "TOMAN"


def run(base_url: str) -> None:
    status, _, health = request_json(base_url, "/health")
    assert status == 200
    assert health["data"] == {"app": "ok", "database": "ok", "redis": "ok"}

    status, _, openapi = request_json(base_url, "/openapi.json")
    assert status == 200
    assert "post" in openapi["paths"]["/api/v1/search"]

    payload = {
        "q": "خدمات كشاورزي",
        "types": RESULT_TYPES,
        "sort": "relevance",
        "page": 1,
        "page_size": 5,
    }
    status, headers, body = request_json(base_url, "/api/v1/search", payload)
    assert status == 200
    assert headers.get("cache-control") == "no-store"
    assert headers.get("x-robots-tag") == "noindex, nofollow"
    assert_search_result(body, RESULT_TYPES)
    assert body["data"]["query"] == "خدمات کشاورزی"
    all_domain_total = body["data"]["total"]

    per_type_totals = {}
    for result_type in RESULT_TYPES:
        status, _, body = request_json(
            base_url,
            "/api/v1/search",
            {"q": "کشاورزی", "types": [result_type], "page_size": 3},
        )
        assert status == 200
        assert_search_result(body, [result_type])
        per_type_totals[result_type] = body["data"]["total"]

    invalid_payloads = [
        {"q": "کود", "types": ["product", "product"]},
        {"q": "کود", "filters": {"currency": "IRR"}},
        {"q": "کود", "types": ["product", "store", "service"], "page_size": 50},
        {"q": "کود", "filters": {"rental_available_from": "2026-08-01T00:00:00Z"}},
    ]
    for invalid in invalid_payloads:
        status, _, body = request_json(base_url, "/api/v1/search", invalid)
        assert status == 422
        assert body["success"] is False

    print(
        json.dumps(
            {
                "health": "ok",
                "openapi_paths": len(openapi["paths"]),
                "result_types": RESULT_TYPES,
                "positive_searches": 1 + len(RESULT_TYPES),
                "negative_contracts": len(invalid_payloads),
                "privacy_headers": "ok",
                "all_domain_total": all_domain_total,
                "per_type_totals": per_type_totals,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Unified Search runtime regression")
    parser.add_argument("--base-url", default="http://localhost:8000")
    run(parser.parse_args().base_url)
