import json
import re
from pathlib import Path
from app.main import app


ROOT = Path(__file__).resolve().parents[3]
COLLECTION_PATH = (
    ROOT / "postman" / "collections" / "subscriptions.postman_collection.json"
)
API_DOC_PATH = ROOT / "docs" / "api" / "billing.md"


def _requests(items: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for item in items:
        if "request" in item:
            rows.append(item["request"])
        rows.extend(_requests(item.get("item", [])))
    return rows


def _normalized_path(url: str) -> str:
    value = url.replace("{{base_url}}", "/api/v1")
    value = value.split("?", 1)[0]
    replacements = {
        "{{plan_code}}": "{plan_code}",
        "{{plan_id}}": "{plan_id}",
        "{{subscription_id}}": "{subscription_id}",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value


def test_subscription_collection_is_valid_complete_and_secret_free() -> None:
    raw = COLLECTION_PATH.read_text(encoding="utf-8")
    collection = json.loads(raw)
    requests = _requests(collection["item"])

    assert len(requests) == 30
    assert "sk-" not in raw
    assert "merchant_id" not in raw.lower()
    assert "SUPER_ADMIN_PASSWORD" not in raw

    collection_operations = {
        (request["method"].lower(), _normalized_path(request["url"]))
        for request in requests
    }
    openapi_operations = {
        (method, path)
        for path, value in app.openapi()["paths"].items()
        if path.startswith("/api/v1/billing")
        or path.startswith("/api/v1/admin/billing")
        for method in value
        if method in {"get", "post", "patch", "put", "delete"}
    }
    assert openapi_operations.issubset(collection_operations)
    assert len(openapi_operations) == 23

    for request in requests:
        body = request.get("body", {})
        if body.get("mode") != "raw":
            continue
        resolved = re.sub(r"\{\{[^}]+\}\}", "1", body["raw"])
        json.loads(resolved)


def test_billing_api_doc_names_every_runtime_operation() -> None:
    document = API_DOC_PATH.read_text(encoding="utf-8")
    runtime_paths = {
        path.removeprefix("/api/v1")
        for path in app.openapi()["paths"]
        if path.startswith("/api/v1/billing")
        or path.startswith("/api/v1/admin/billing")
    }

    for path in runtime_paths:
        assert path in document
