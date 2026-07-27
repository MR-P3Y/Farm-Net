import json
from dataclasses import FrozenInstanceError

import pytest
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.modules.ai.chunking import CHUNKER_VERSION, chunk_persian_page
from app.modules.ai.models import (
    AIEmbeddingIndexRecord,
    AIEmbeddingModel,
    AIKnowledgeChunk,
    AIResponseCitation,
)
from app.modules.ai.knowledge_retrieval import (
    KnowledgeRetrievalError,
    create_approved_page_chunks,
)
from app.modules.ai.retrieval_contracts import (
    EmbeddingResult,
    RetrievalQuery,
    build_citation,
)
from app.modules.ai.qdrant_store import QdrantRetrievalStore
from app.modules.auth.seed import BASE_PERMISSIONS


RETRIEVAL_TABLES = {
    "ai_knowledge_chunks",
    "ai_embedding_models",
    "ai_embedding_index_records",
    "ai_response_citations",
}


def _constraint_names(model, kind) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def test_retrieval_foundation_uses_four_normalized_tables() -> None:
    models = {
        AIKnowledgeChunk,
        AIEmbeddingModel,
        AIEmbeddingIndexRecord,
        AIResponseCitation,
    }
    assert {model.__tablename__ for model in models} == RETRIEVAL_TABLES
    assert all("vector" not in model.__table__.c for model in models)


def test_chunks_indexes_and_citations_are_exact_once() -> None:
    assert "uq_ai_chunk_page_version_index" in _constraint_names(AIKnowledgeChunk, UniqueConstraint)
    assert "uq_ai_embedding_chunk_model" in _constraint_names(
        AIEmbeddingIndexRecord, UniqueConstraint
    )
    assert "uq_ai_embedding_store_point" in _constraint_names(
        AIEmbeddingIndexRecord, UniqueConstraint
    )
    assert "uq_ai_citation_message_order" in _constraint_names(AIResponseCitation, UniqueConstraint)
    assert "uq_ai_citation_message_chunk" in _constraint_names(AIResponseCitation, UniqueConstraint)


def test_only_one_embedding_model_can_be_active() -> None:
    assert AIEmbeddingModel.__table__.c.active_scope.unique is True
    assert "ck_ai_embedding_active_scope" in _constraint_names(AIEmbeddingModel, CheckConstraint)


def test_persian_chunking_is_deterministic_bounded_and_lossless_by_offset() -> None:
    text = ("مدیریت آبیاری برای حفظ رطوبت خاک ضروری است. " * 80).strip()
    first = chunk_persian_page(text, max_characters=300, overlap_characters=40)
    second = chunk_persian_page(text, max_characters=300, overlap_characters=40)

    assert first == second
    assert len(first) > 1
    assert CHUNKER_VERSION == "barzegar-fa-page-v1"
    assert all(chunk.text == text[chunk.character_start : chunk.character_end] for chunk in first)
    assert all(0 < len(chunk.text) <= 300 for chunk in first)
    assert all(
        current.character_start < previous.character_end
        for previous, current in zip(first, first[1:], strict=False)
    )


def test_retrieval_management_permission_is_dedicated() -> None:
    assert "ai.retrieval.manage" in {permission.code for permission in BASE_PERMISSIONS}


def test_embedding_and_retrieval_contracts_validate_dimensions_and_approval() -> None:
    result = EmbeddingResult(
        model_key="provider-neutral",
        model_version="v1",
        dimensions=3,
        vectors=((0.1, 0.2, 0.3),),
    )
    assert result.dimensions == 3
    with pytest.raises(FrozenInstanceError):
        result.dimensions = 4  # type: ignore[misc]
    with pytest.raises(ValueError, match="dimensions"):
        EmbeddingResult(
            model_key="provider-neutral",
            model_version="v1",
            dimensions=3,
            vectors=((0.1, 0.2),),
        )
    with pytest.raises(ValueError, match="unapproved"):
        RetrievalQuery(vector=(0.1, 0.2), limit=5, approved_only=False)


def test_citation_quote_must_be_verbatim_from_immutable_chunk() -> None:
    citation = build_citation(
        chunk_id=10,
        chunk_text="تناوب زراعی به حفظ کیفیت خاک کمک می‌کند.",
        quoted_text="حفظ کیفیت خاک",
        citation_order=1,
        source_title="راهنمای کشاورز",
        source_version="نسخه ۱",
        page_number=12,
        retrieval_score=0.91,
    )
    assert citation.page_number == 12
    with pytest.raises(ValueError, match="exact substring"):
        build_citation(
            chunk_id=10,
            chunk_text="متن واقعی",
            quoted_text="متن تغییر یافته",
            citation_order=1,
            source_title="منبع",
            source_version="۱",
            page_number=1,
            retrieval_score=0.5,
        )


def test_unapproved_source_cannot_be_chunked() -> None:
    source = type("Source", (), {"id": 1, "status": "draft"})()
    version = type("Version", (), {"id": 2, "source_id": 1, "status": "approved"})()
    document = type(
        "Document",
        (),
        {"id": 3, "source_version_id": 2, "extraction_status": "succeeded"},
    )()
    page = type(
        "Page",
        (),
        {
            "id": 4,
            "document_id": 3,
            "page_number": 1,
            "needs_review": False,
            "extracted_text": "متن معتبر",
        },
    )()

    with pytest.raises(KnowledgeRetrievalError) as error:
        create_approved_page_chunks(
            object(),  # type: ignore[arg-type]
            source=source,  # type: ignore[arg-type]
            source_version=version,  # type: ignore[arg-type]
            document=document,  # type: ignore[arg-type]
            page=page,  # type: ignore[arg-type]
        )

    assert error.value.code == "KNOWLEDGE_NOT_APPROVED"


def test_qdrant_query_always_filters_approved_and_active(monkeypatch) -> None:
    captured: dict = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return b'{"result":{"points":[]}}'

    def fake_urlopen(request, *, timeout):
        captured["url"] = request.full_url
        captured["payload"] = json.loads(request.data)
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(
        "app.modules.ai.qdrant_store.urlopen",
        fake_urlopen,
    )
    store = QdrantRetrievalStore(base_url="http://qdrant:6333")
    result = store.search(
        collection_name="barzegar_knowledge",
        query=RetrievalQuery(
            vector=(0.1, 0.2),
            limit=5,
            source_version_ids=(10, 11),
        ),
    )

    assert result == ()
    assert captured["url"].endswith("/points/query")
    conditions = captured["payload"]["filter"]["must"]
    assert {"key": "approved", "match": {"value": True}} in conditions
    assert {"key": "active", "match": {"value": True}} in conditions
    assert {
        "key": "source_version_id",
        "match": {"any": [10, 11]},
    } in conditions
