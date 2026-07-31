import json
import re
from pathlib import Path

from app.main import app


ROOT = Path(__file__).resolve().parents[3]
COLLECTION_PATH = (
    ROOT / "postman" / "collections" / "ai-barzegar.postman_collection.json"
)
API_DOC_PATH = ROOT / "docs" / "api" / "ai-barzegar.md"


def _requests(items: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for item in items:
        if "request" in item:
            rows.append(item["request"])
        rows.extend(_requests(item.get("item", [])))
    return rows


def _normalized_path(url: str) -> str:
    value = url.replace("{{base_url}}", "/api/v1").split("?", 1)[0]
    return re.sub(r":([a-z_]+)", r"{\1}", value)


def test_ai_collection_is_complete_parseable_and_secret_free() -> None:
    raw = COLLECTION_PATH.read_text(encoding="utf-8")
    collection = json.loads(raw)
    requests = _requests(collection["item"])

    assert len(requests) == 30
    assert re.search(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}", raw) is None
    assert "OPENAI_API_KEY" not in raw
    assert "SUPER_ADMIN_PASSWORD" not in raw

    collection_operations = {
        (request["method"].lower(), _normalized_path(request["url"]))
        for request in requests
    }
    openapi_operations = {
        (method, path)
        for path, value in app.openapi()["paths"].items()
        if path.startswith("/api/v1/ai/")
        or path.startswith("/api/v1/admin/ai/")
        for method in value
        if method in {"get", "post", "patch", "put", "delete"}
    }
    assert len(openapi_operations) == 30
    assert collection_operations == openapi_operations

    for request in requests:
        body = request.get("body", {})
        if body.get("mode") != "raw":
            continue
        resolved = re.sub(r"\{\{[^}]+\}\}", "idempotency-value", body["raw"])
        json.loads(resolved)


def test_ai_api_doc_names_every_runtime_path_and_safety_boundary() -> None:
    document = API_DOC_PATH.read_text(encoding="utf-8")
    runtime_paths = {
        path.removeprefix("/api/v1")
        for path in app.openapi()["paths"]
        if path.startswith("/api/v1/ai/")
        or path.startswith("/api/v1/admin/ai/")
    }
    for path in runtime_paths:
        assert path in document

    assert "AI_PROVIDER_ENABLED=false" in document
    assert "ریال" in document
    assert "تومان" in document
    assert "جایگزین کارشناس" in document
