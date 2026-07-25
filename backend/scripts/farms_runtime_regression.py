"""Read-only runtime regression for the private Farms module."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


BASE_URL = os.getenv("FARMNET_BASE_URL", "http://localhost:8000").rstrip("/")
REQUIRED = {
    "/api/v1/farms": {"get", "post"},
    "/api/v1/farms/{farm_id}": {"get", "patch"},
    "/api/v1/farms/{farm_id}/plots": {"get", "post"},
    "/api/v1/farms/{farm_id}/plots/{plot_id}/cycles": {"get", "post"},
    "/api/v1/farms/{farm_id}/plots/{plot_id}/weather": {"get"},
    "/api/v1/admin/farms": {"get"},
    "/api/v1/admin/farms/{farm_id}": {"get"},
    "/api/v1/admin/farms/{farm_id}/audit": {"get"},
    "/api/v1/farm-references/measurement-units": {"get"},
}
PRIVATE_READS = (
    "/api/v1/farms",
    "/api/v1/farms/1",
    "/api/v1/farms/1/plots",
    "/api/v1/farms/1/plots/1/cycles",
    "/api/v1/farms/1/plots/1/weather",
    "/api/v1/admin/farms",
)


def get_json(path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=15) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def main() -> None:
    health_status, health = get_json("/health")
    assert health_status == 200
    assert health["data"]["app"] == "ok"
    assert health["data"]["database"] == "ok"
    assert health["data"]["redis"] == "ok"

    openapi_status, openapi = get_json("/openapi.json")
    assert openapi_status == 200
    paths = openapi["paths"]
    for path, methods in REQUIRED.items():
        assert methods.issubset(paths[path]), (path, methods, paths.get(path))

    farm_operations = sum(
        len(
            {
                method
                for method in operations
                if method in {"get", "post", "put", "patch", "delete"}
            }
        )
        for path, operations in paths.items()
        if path.startswith("/api/v1/farms")
        or path.startswith("/api/v1/admin/farms")
    )
    assert farm_operations == 41, farm_operations

    for path in PRIVATE_READS:
        status, _ = get_json(path)
        assert status == 401, (path, status)

    print(
        json.dumps(
            {
                "health": "ok",
                "farm_operations": farm_operations,
                "private_reads_401": len(PRIVATE_READS),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
