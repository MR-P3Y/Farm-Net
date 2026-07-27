import json
import re
from collections.abc import Sequence
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.modules.ai.retrieval_contracts import (
    RetrievalHit,
    RetrievalPoint,
    RetrievalQuery,
)


_COLLECTION_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,120}$")


class RetrievalStoreError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class QdrantRetrievalStore:
    """Minimal Qdrant REST adapter with mandatory approved-source filtering."""

    store_key = "qdrant"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str = "",
        timeout_seconds: int = 10,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("Qdrant URL must use HTTP or HTTPS")
        if timeout_seconds < 1 or timeout_seconds > 60:
            raise ValueError("Qdrant timeout must be between 1 and 60 seconds")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def ensure_collection(
        self,
        *,
        collection_name: str,
        dimensions: int,
        distance_metric: str,
    ) -> None:
        self._validate_collection(collection_name)
        distances = {"cosine": "Cosine", "dot": "Dot", "euclidean": "Euclid"}
        if distance_metric not in distances:
            raise ValueError("Unsupported distance metric")
        self._request(
            "PUT",
            f"/collections/{collection_name}",
            {"vectors": {"size": dimensions, "distance": distances[distance_metric]}},
        )

    def upsert(
        self,
        *,
        collection_name: str,
        points: Sequence[RetrievalPoint],
    ) -> None:
        self._validate_collection(collection_name)
        if any(point.metadata.get("approved") is not True for point in points):
            raise RetrievalStoreError(
                "UNAPPROVED_POINT_REJECTED",
                "Every retrieval point must carry approved=true",
            )
        self._request(
            "PUT",
            f"/collections/{collection_name}/points?wait=true",
            {
                "points": [
                    {
                        "id": point.point_id,
                        "vector": list(point.vector),
                        "payload": {**point.metadata, "chunk_id": point.chunk_id},
                    }
                    for point in points
                ]
            },
        )

    def search(
        self,
        *,
        collection_name: str,
        query: RetrievalQuery,
    ) -> Sequence[RetrievalHit]:
        self._validate_collection(collection_name)
        must: list[dict[str, Any]] = [
            {"key": "approved", "match": {"value": True}},
            {"key": "active", "match": {"value": True}},
        ]
        if query.source_version_ids:
            must.append(
                {
                    "key": "source_version_id",
                    "match": {"any": list(query.source_version_ids)},
                }
            )
        response = self._request(
            "POST",
            f"/collections/{collection_name}/points/query",
            {
                "query": list(query.vector),
                "limit": query.limit,
                "with_payload": True,
                "filter": {"must": must},
            },
        )
        points = response.get("result", {}).get("points", [])
        return tuple(
            RetrievalHit(
                point_id=str(point["id"]),
                chunk_id=int(point["payload"]["chunk_id"]),
                score=float(point["score"]),
                metadata=point["payload"],
            )
            for point in points
        )

    def remove(
        self,
        *,
        collection_name: str,
        point_ids: Sequence[str],
    ) -> None:
        self._validate_collection(collection_name)
        self._request(
            "POST",
            f"/collections/{collection_name}/points/delete?wait=true",
            {"points": list(point_ids)},
        )

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["api-key"] = self._api_key
        request = Request(
            f"{self._base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RetrievalStoreError(
                "RETRIEVAL_STORE_UNAVAILABLE",
                "Retrieval store request failed",
            ) from exc

    @staticmethod
    def _validate_collection(collection_name: str) -> None:
        if not _COLLECTION_PATTERN.fullmatch(collection_name):
            raise ValueError("Invalid retrieval collection name")
