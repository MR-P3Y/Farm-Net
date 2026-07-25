from fastapi.testclient import TestClient

from app.core.openapi import SUCCESS_ENVELOPE_SCHEMA_NAME
from app.main import app


METHODS = {"get", "post", "put", "patch", "delete"}
BINARY_MEDIA_PATHS = {
    "/api/v1/media/public/{file_key}",
    "/api/v1/media/private/{file_key}",
    "/api/v1/admin/media/private/{file_key}",
}


def successful_operations(schema):
    for path, path_item in schema["paths"].items():
        for method, operation in path_item.items():
            if method not in METHODS:
                continue
            for status_code, response in operation["responses"].items():
                if str(status_code).startswith("2"):
                    yield path, method, response


def test_every_success_response_has_a_useful_schema():
    schema = app.openapi()
    missing = []
    for path, method, response in successful_operations(schema):
        content = response.get("content", {})
        response_schemas = [
            media["schema"]
            for media in content.values()
            if isinstance(media, dict) and media.get("schema")
        ]
        if not response_schemas:
            missing.append(f"{method.upper()} {path}")

    assert missing == []


def test_standard_envelope_matches_runtime_contract():
    schema = app.openapi()
    envelope = schema["components"]["schemas"][SUCCESS_ENVELOPE_SCHEMA_NAME]
    assert envelope["required"] == ["success", "data", "message", "meta"]
    assert envelope["properties"]["success"]["const"] is True

    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert set(response.json()) == {"success", "data", "message", "meta"}
    assert response.json()["success"] is True


def test_existing_domain_models_are_not_replaced_by_generic_envelope():
    schema = app.openapi()
    review_schema = schema["paths"]["/api/v1/admin/reviews"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]
    request_schema = schema["paths"]["/api/v1/services/requests"]["post"]["responses"][
        "200"
    ]["content"]["application/json"]["schema"]

    assert review_schema["$ref"].endswith("/ReviewAdminListResponse")
    assert request_schema["$ref"].endswith("/ServiceRequestDetailResponse")


def test_media_downloads_are_documented_as_binary_not_json_envelopes():
    schema = app.openapi()
    for path in BINARY_MEDIA_PATHS:
        content = schema["paths"][path]["get"]["responses"]["200"]["content"]
        assert "application/json" not in content
        assert content["application/octet-stream"]["schema"] == {
            "type": "string",
            "format": "binary",
        }
