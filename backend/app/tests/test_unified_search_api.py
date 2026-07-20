from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.common.search import SearchResultType, UnifiedSearchGroup
from app.db.session import get_db
from app.main import app
from app.modules.search import router as search_router


class EmptyEngine:
    def search(self, query):
        return Mock(
            model_dump=lambda **_: {
                "query": query.q,
                "groups": [
                    UnifiedSearchGroup(
                        type=result_type,
                        items=[],
                        total=0,
                        page=query.page,
                        page_size=query.page_size,
                    ).model_dump(mode="json")
                    for result_type in query.types
                ],
                "total": 0,
            }
        )


def test_unified_search_api_normalizes_query_and_preserves_type_order(monkeypatch) -> None:
    app.dependency_overrides[get_db] = lambda: None
    monkeypatch.setattr(search_router, "build_search_engine", lambda _db: EmptyEngine())
    try:
        response = TestClient(app).post(
            "/api/v1/search",
            json={
                "q": "  خدمات   كشاورزي ",
                "types": ["service", "product"],
                "filters": {"province_id": 1, "currency": "TOMAN"},
                "sort": "relevance",
                "page": 1,
                "page_size": 10,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    data = response.json()["data"]
    assert data["query"] == "خدمات کشاورزی"
    assert [group["type"] for group in data["groups"]] == ["service", "product"]


def test_unified_search_api_rejects_invalid_contract_before_provider_call() -> None:
    response = TestClient(app).post(
        "/api/v1/search",
        json={
            "q": "کود",
            "types": ["product", "product"],
            "filters": {"currency": "IRR"},
        },
    )
    assert response.status_code == 422

    over_budget = TestClient(app).post(
        "/api/v1/search",
        json={"q": "کود", "types": ["product", "store", "service"], "page_size": 50},
    )
    assert over_budget.status_code == 422


def test_unified_search_api_openapi_contract_and_provider_registration() -> None:
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/search"]["post"]
    body_ref = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    assert body_ref.endswith("/UnifiedSearchQuery")

    engine = search_router.build_search_engine(None)
    assert list(engine._providers) == list(SearchResultType)
