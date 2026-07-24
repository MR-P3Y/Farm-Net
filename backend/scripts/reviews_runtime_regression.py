import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


REQUIRED_METHODS = {
    "/api/v1/reviews": {"post"},
    "/api/v1/reviews/me": {"get"},
    "/api/v1/reviews/me/{review_id}": {"get", "patch", "delete"},
    "/api/v1/reviews/subjects/{subject_type}/{subject_id}": {"get"},
    "/api/v1/reviews/{review_id}/reports": {"post"},
    "/api/v1/admin/reviews": {"get"},
    "/api/v1/admin/reviews/{review_id}/status": {"patch"},
    "/api/v1/admin/reviews/{review_id}/moderation-logs": {"get"},
    "/api/v1/admin/reviews/reports": {"get"},
    "/api/v1/admin/reviews/reports/{report_id}/status": {"patch"},
}

EXPECTED_RESPONSE_REFS = {
    ("/api/v1/reviews/me", "get"): "ReviewOwnerListResponse",
    (
        "/api/v1/reviews/subjects/{subject_type}/{subject_id}",
        "get",
    ): "ReviewPublicListResponse",
    ("/api/v1/admin/reviews", "get"): "ReviewAdminListResponse",
    (
        "/api/v1/admin/reviews/{review_id}/status",
        "patch",
    ): "ReviewAdminDetailResponse",
    (
        "/api/v1/admin/reviews/{review_id}/moderation-logs",
        "get",
    ): "ReviewModerationLogListResponse",
    (
        "/api/v1/admin/reviews/reports",
        "get",
    ): "ReviewReportAdminListResponse",
    (
        "/api/v1/admin/reviews/reports/{report_id}/status",
        "patch",
    ): "ReviewReportAdminDetailResponse",
}

PRIVATE_BOUNDARIES = [
    ("GET", "/api/v1/reviews/me", None),
    ("GET", "/api/v1/reviews/me/1", None),
    ("POST", "/api/v1/reviews", {}),
    ("POST", "/api/v1/reviews/1/reports", {}),
    ("GET", "/api/v1/admin/reviews", None),
    ("GET", "/api/v1/admin/reviews/reports", None),
    ("GET", "/api/v1/admin/reviews/1/moderation-logs", None),
]

EXPECTED_SUBJECT_TYPES = {
    "product",
    "store",
    "service_offer",
    "service_provider",
    "rental_equipment",
    "rental_lessor",
    "consultant",
}

FORBIDDEN_PUBLIC_REVIEW_FIELDS = {
    "reviewer_user_id",
    "source_type",
    "source_id",
    "subject_type",
    "subject_id",
    "status",
    "deleted_at",
    "reports",
    "moderation_logs",
}


def request_json(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    body: dict | None = None,
):
    payload = None if body is None else json.dumps(body).encode()
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310 - operator URL
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def response_ref(openapi: dict, path: str, method: str) -> str:
    schema = openapi["paths"][path][method]["responses"]["200"]["content"]["application/json"][
        "schema"
    ]
    return schema["$ref"].rsplit("/", 1)[-1]


def run(base_url: str) -> None:
    status, health = request_json(base_url, "/health")
    assert status == 200
    assert health["data"] == {"app": "ok", "database": "ok", "redis": "ok"}

    status, openapi = request_json(base_url, "/openapi.json")
    assert status == 200
    paths = openapi["paths"]
    schemas = openapi["components"]["schemas"]

    for path, methods in REQUIRED_METHODS.items():
        assert path in paths, path
        assert methods.issubset(paths[path]), (path, methods, set(paths[path]))

    verified_refs = {}
    for (path, method), expected in EXPECTED_RESPONSE_REFS.items():
        actual = response_ref(openapi, path, method)
        assert actual == expected, (path, method, expected, actual)
        verified_refs[f"{method.upper()} {path}"] = actual

    assert set(schemas["ReviewSubjectType"]["enum"]) == EXPECTED_SUBJECT_TYPES
    assert set(schemas["ReviewSourceType"]["enum"]) == {
        "order",
        "service_request",
        "rental_request",
        "consult_request",
    }
    public_fields = set(schemas["ReviewPublicOut"]["properties"])
    assert not (public_fields & FORBIDDEN_PUBLIC_REVIEW_FIELDS)
    assert set(schemas["ReviewPublicAuthorOut"]["properties"]) == {"display_name"}

    unauthorized = {}
    for method, path, body in PRIVATE_BOUNDARIES:
        status, response = request_json(base_url, path, method=method, body=body)
        assert status == 401, (method, path, status, response)
        assert response["success"] is False
        unauthorized[f"{method} {path}"] = status

    status, missing = request_json(
        base_url,
        "/api/v1/reviews/subjects/product/2147483647?page=1&page_size=20",
    )
    assert status == 404
    assert missing["error"]["code"] == "REVIEW_NOT_FOUND"

    print(
        json.dumps(
            {
                "health": health["data"],
                "openapi_paths": len(paths),
                "review_paths": len([path for path in paths if "review" in path.lower()]),
                "review_contracts": len(REQUIRED_METHODS),
                "typed_response_refs": verified_refs,
                "subject_types": sorted(EXPECTED_SUBJECT_TYPES),
                "unauthenticated_private_contracts": unauthorized,
                "public_missing_subject": status,
                "public_privacy_fields": sorted(public_fields),
                "mutations_performed": 0,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run read-only marketplace Reviews runtime regression"
    )
    parser.add_argument("--base-url", default="http://localhost:8000")
    run(parser.parse_args().base_url)
