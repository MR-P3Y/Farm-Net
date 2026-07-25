"""Generate the deterministic Postman collection for all Farm OpenAPI operations."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "postman" / "collections" / "farms.postman_collection.json"
OPERATIONS = (
    ("POST", "/farms", "Create farm"),
    ("GET", "/farms", "List my farms"),
    ("GET", "/farms/:farm_id", "Farm detail"),
    ("PATCH", "/farms/:farm_id", "Update farm"),
    ("POST", "/farms/:farm_id/archive", "Archive farm"),
    ("POST", "/farms/:farm_id/restore", "Restore farm"),
    ("POST", "/farms/:farm_id/plots", "Create plot"),
    ("GET", "/farms/:farm_id/plots", "List plots"),
    ("GET", "/farms/:farm_id/plots/:plot_id", "Plot detail"),
    ("PATCH", "/farms/:farm_id/plots/:plot_id", "Update plot"),
    ("POST", "/farms/:farm_id/plots/:plot_id/archive", "Archive plot"),
    ("POST", "/farms/:farm_id/plots/:plot_id/restore", "Restore plot"),
    ("POST", "/farms/:farm_id/plots/:plot_id/cycles", "Create crop cycle"),
    ("GET", "/farms/:farm_id/plots/:plot_id/cycles", "List crop cycles"),
    ("GET", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id", "Cycle detail"),
    ("PATCH", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id", "Update cycle"),
    ("POST", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/start", "Start cycle"),
    ("POST", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/complete", "Complete cycle"),
    ("POST", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/cancel", "Cancel cycle"),
    ("PUT", "/farms/:farm_id/plots/:plot_id/soil-profile", "Upsert soil profile"),
    ("GET", "/farms/:farm_id/plots/:plot_id/soil-profile", "Get soil profile"),
    ("PUT", "/farms/:farm_id/plots/:plot_id/irrigation-profile", "Upsert irrigation"),
    ("GET", "/farms/:farm_id/plots/:plot_id/irrigation-profile", "Get irrigation"),
    ("POST", "/farms/:farm_id/water-sources", "Create water source"),
    ("GET", "/farms/:farm_id/water-sources", "List water sources"),
    ("POST", "/farms/:farm_id/water-sources/:source_id/archive", "Archive water source"),
    ("POST", "/farms/:farm_id/lab-observations", "Create lab observation"),
    ("GET", "/farms/:farm_id/lab-observations/:subject_type/:subject_id", "List lab observations"),
    ("POST", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/operations", "Create operation"),
    ("GET", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/operations", "List operations"),
    ("POST", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/operations/:operation_id/inputs", "Add operation input"),
    ("POST", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/harvests", "Create harvest"),
    ("GET", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/harvests", "List harvests"),
    ("POST", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/media", "Attach farm media"),
    ("GET", "/farms/:farm_id/plots/:plot_id/cycles/:cycle_id/media", "List farm media"),
    ("GET", "/farms/:farm_id/plots/:plot_id/weather", "Plot weather"),
    ("POST", "/farms/:farm_id/plots/:plot_id/weather/refresh", "Refresh plot weather"),
    ("GET", "/farms/:farm_id/plots/:plot_id/weather/alerts", "Plot weather alerts"),
    ("GET", "/farm-references/measurement-units?is_active=true", "Measurement units"),
    ("GET", "/admin/farms", "Admin farm support list"),
    ("GET", "/admin/farms/:farm_id", "Admin farm support detail"),
    ("GET", "/admin/farms/:farm_id/audit", "Admin farm audit"),
)


def request(method: str, path: str, name: str) -> dict:
    headers = [{"key": "Authorization", "value": "Bearer {{access_token}}"}]
    result = {
        "name": name,
        "request": {
            "method": method,
            "header": headers,
            "url": f"{{{{base_url}}}}{path}",
            "description": "Contract is defined by the live Farm Net OpenAPI schema.",
        },
    }
    if method in {"POST", "PUT", "PATCH"}:
        headers.append({"key": "Content-Type", "value": "application/json"})
        result["request"]["body"] = {"mode": "raw", "raw": "{}"}
    return result


def main() -> None:
    collection = {
        "info": {
            "name": "Farm Net - Farm Management",
            "description": (
                "Phase 24 private Farm contracts. Owner and Admin tokens are separate; "
                "replace empty mutation bodies using the linked OpenAPI schema."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000/api/v1"},
            {"key": "access_token", "value": ""},
            {"key": "farm_id", "value": "1"},
            {"key": "plot_id", "value": "1"},
            {"key": "cycle_id", "value": "1"},
            {"key": "operation_id", "value": "1"},
            {"key": "source_id", "value": "1"},
            {"key": "subject_type", "value": "soil"},
            {"key": "subject_id", "value": "1"},
        ],
        "item": [request(*operation) for operation in OPERATIONS],
    }
    OUTPUT.write_text(
        json.dumps(collection, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{OUTPUT}: {len(OPERATIONS)} requests")


if __name__ == "__main__":
    main()
