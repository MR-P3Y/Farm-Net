from __future__ import annotations

from copy import deepcopy
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


SUCCESS_ENVELOPE_SCHEMA_NAME = "StandardSuccessEnvelope"
SUCCESS_ENVELOPE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "title": SUCCESS_ENVELOPE_SCHEMA_NAME,
    "description": (
        "Shared Farm-Net success envelope. Domain endpoints may provide a more "
        "specific schema for data."
    ),
    "required": ["success", "data", "message", "meta"],
    "properties": {
        "success": {"type": "boolean", "const": True},
        "data": {
            "description": "Endpoint-specific JSON payload.",
        },
        "message": {"type": "string"},
        "meta": {
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "trace_id": {"type": "string"},
            },
        },
    },
    "additionalProperties": False,
}


def install_typed_openapi(app: FastAPI) -> None:
    """Document the shared success envelope without changing runtime serialization."""

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            summary=app.summary,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        components = schema.setdefault("components", {}).setdefault("schemas", {})
        components[SUCCESS_ENVELOPE_SCHEMA_NAME] = deepcopy(SUCCESS_ENVELOPE_SCHEMA)

        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if not isinstance(operation, dict) or "responses" not in operation:
                    continue
                for status_code, response in operation["responses"].items():
                    if not str(status_code).startswith("2"):
                        continue
                    json_content = response.get("content", {}).get("application/json")
                    if json_content is None or json_content.get("schema") not in ({}, None):
                        continue
                    json_content["schema"] = {
                        "$ref": f"#/components/schemas/{SUCCESS_ENVELOPE_SCHEMA_NAME}"
                    }

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
