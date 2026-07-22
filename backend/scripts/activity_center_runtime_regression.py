import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


REQUIRED_METHODS = {
    "/api/v1/auth/me": {"get"},
    "/api/v1/verifications/me": {"get"},
    "/api/v1/notifications/me": {"get"},
    "/api/v1/finance/wallet/me": {"get"},
    "/api/v1/orders/me": {"get"},
    "/api/v1/seller/orders": {"get"},
    "/api/v1/seller/orders/{order_id}": {"get"},
    "/api/v1/seller/orders/{order_id}/status": {"patch"},
    "/api/v1/services/me/provider-profile": {"get", "post", "put"},
    "/api/v1/services/me/offers": {"get", "post"},
    "/api/v1/services/requests/assigned": {"get"},
    "/api/v1/rentals/me/lessor-profile": {"get", "put"},
    "/api/v1/rentals/me/equipment": {"get", "post"},
    "/api/v1/rentals/requests/assigned": {"get"},
    "/api/v1/consultants/me/profile": {"get", "post", "put"},
    "/api/v1/consultants/requests/assigned": {"get"},
}

PRIVATE_GET_PATHS = [
    "/api/v1/auth/me",
    "/api/v1/verifications/me",
    "/api/v1/notifications/me",
    "/api/v1/finance/wallet/me",
    "/api/v1/orders/me",
    "/api/v1/seller/orders",
    "/api/v1/services/me/provider-profile",
    "/api/v1/rentals/me/lessor-profile",
    "/api/v1/consultants/me/profile",
]


def get_json(base_url: str, path: str):
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310 - operator URL
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def run(base_url: str) -> None:
    status, health = get_json(base_url, "/health")
    assert status == 200
    assert health["data"] == {"app": "ok", "database": "ok", "redis": "ok"}

    status, openapi = get_json(base_url, "/openapi.json")
    assert status == 200
    paths = openapi["paths"]
    for path, methods in REQUIRED_METHODS.items():
        assert path in paths, path
        assert methods.issubset(paths[path]), (path, methods, set(paths[path]))

    unauthorized = {}
    for path in PRIVATE_GET_PATHS:
        status, body = get_json(base_url, path)
        assert status == 401, (path, status, body)
        assert body["success"] is False
        unauthorized[path] = status

    print(
        json.dumps(
            {
                "health": health["data"],
                "openapi_paths": len(paths),
                "activity_contracts": len(REQUIRED_METHODS),
                "unauthenticated_private_contracts": unauthorized,
                "mutations_performed": 0,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run read-only Activity Center runtime regression"
    )
    parser.add_argument("--base-url", default="http://localhost:8000")
    run(parser.parse_args().base_url)
