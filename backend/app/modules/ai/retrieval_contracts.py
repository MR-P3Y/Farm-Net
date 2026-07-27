from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence


@dataclass(frozen=True)
class EmbeddingRequest:
    model_key: str
    model_version: str
    texts: Sequence[str]


@dataclass(frozen=True)
class EmbeddingResult:
    model_key: str
    model_version: str
    dimensions: int
    vectors: Sequence[tuple[float, ...]]

    def __post_init__(self) -> None:
        if self.dimensions <= 0:
            raise ValueError("dimensions must be positive")
        if any(len(vector) != self.dimensions for vector in self.vectors):
            raise ValueError("every vector must match the declared dimensions")


@dataclass(frozen=True)
class RetrievalPoint:
    point_id: str
    chunk_id: int
    vector: tuple[float, ...]
    metadata: Mapping[str, str | int | bool]


@dataclass(frozen=True)
class RetrievalQuery:
    vector: tuple[float, ...]
    limit: int
    source_version_ids: tuple[int, ...] = ()
    approved_only: bool = True

    def __post_init__(self) -> None:
        if not self.vector:
            raise ValueError("query vector cannot be empty")
        if self.limit < 1 or self.limit > 50:
            raise ValueError("limit must be between 1 and 50")
        if not self.approved_only:
            raise ValueError("Barzegar retrieval cannot include unapproved sources")


@dataclass(frozen=True)
class RetrievalHit:
    point_id: str
    chunk_id: int
    score: float
    metadata: Mapping[str, str | int | bool]

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 1:
            raise ValueError("retrieval score must be between 0 and 1")


class EmbeddingProvider(Protocol):
    @property
    def provider_key(self) -> str: ...

    def embed(self, request: EmbeddingRequest) -> EmbeddingResult: ...


class RetrievalStore(Protocol):
    """Vector-store boundary; vector payloads must not be persisted in MySQL."""

    @property
    def store_key(self) -> str: ...

    def upsert(self, *, collection_name: str, points: Sequence[RetrievalPoint]) -> None: ...

    def search(self, *, collection_name: str, query: RetrievalQuery) -> Sequence[RetrievalHit]: ...

    def remove(self, *, collection_name: str, point_ids: Sequence[str]) -> None: ...


@dataclass(frozen=True)
class CitationContract:
    chunk_id: int
    citation_order: int
    quoted_text: str
    source_title: str
    source_version: str
    page_number: int
    retrieval_score: float | None

    def __post_init__(self) -> None:
        if self.chunk_id <= 0 or self.citation_order <= 0 or self.page_number <= 0:
            raise ValueError("citation identifiers and ordering must be positive")
        if not self.quoted_text or not self.source_title or not self.source_version:
            raise ValueError("citation source and quote cannot be empty")
        if self.retrieval_score is not None and not 0 <= self.retrieval_score <= 1:
            raise ValueError("citation retrieval score must be between 0 and 1")


def build_citation(
    *,
    chunk_id: int,
    chunk_text: str,
    quoted_text: str,
    citation_order: int,
    source_title: str,
    source_version: str,
    page_number: int,
    retrieval_score: float | None,
) -> CitationContract:
    if quoted_text not in chunk_text:
        raise ValueError("citation quote must be an exact substring of its chunk")
    return CitationContract(
        chunk_id=chunk_id,
        citation_order=citation_order,
        quoted_text=quoted_text,
        source_title=source_title,
        source_version=source_version,
        page_number=page_number,
        retrieval_score=retrieval_score,
    )
