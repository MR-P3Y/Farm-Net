from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ai.chunking import CHUNKER_VERSION, chunk_persian_page
from app.modules.ai.models import (
    AIKnowledgeChunk,
    AIKnowledgeDocument,
    AIKnowledgeExtractedPage,
    AIKnowledgeSource,
    AIKnowledgeSourceVersion,
)


class KnowledgeRetrievalError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def create_approved_page_chunks(
    db: Session,
    *,
    source: AIKnowledgeSource,
    source_version: AIKnowledgeSourceVersion,
    document: AIKnowledgeDocument,
    page: AIKnowledgeExtractedPage,
    max_characters: int = 1200,
    overlap_characters: int = 160,
) -> tuple[AIKnowledgeChunk, ...]:
    """Create page chunks exactly once after all governance gates pass."""
    if source.status != "approved" or source_version.status != "approved":
        raise KnowledgeRetrievalError(
            "KNOWLEDGE_NOT_APPROVED",
            "Source and source version must both be approved",
        )
    if document.extraction_status != "succeeded" or page.needs_review:
        raise KnowledgeRetrievalError(
            "EXTRACTION_NOT_APPROVED",
            "Only successful pages that need no review can be chunked",
        )
    if (
        source_version.source_id != source.id
        or document.source_version_id != source_version.id
        or page.document_id != document.id
    ):
        raise KnowledgeRetrievalError(
            "KNOWLEDGE_LINEAGE_MISMATCH",
            "Source, version, document, and page lineage does not match",
        )

    existing = tuple(
        db.scalars(
            select(AIKnowledgeChunk)
            .where(
                AIKnowledgeChunk.extracted_page_id == page.id,
                AIKnowledgeChunk.chunker_version == CHUNKER_VERSION,
            )
            .order_by(AIKnowledgeChunk.chunk_index)
        )
    )
    if existing:
        return existing

    chunks = tuple(
        AIKnowledgeChunk(
            source_version_id=source_version.id,
            document_id=document.id,
            extracted_page_id=page.id,
            page_number=page.page_number,
            chunk_index=chunk.chunk_index,
            character_start=chunk.character_start,
            character_end=chunk.character_end,
            chunk_text=chunk.text,
            text_sha256=chunk.text_sha256,
            chunker_version=CHUNKER_VERSION,
            token_estimate=chunk.token_estimate,
            is_active=True,
        )
        for chunk in chunk_persian_page(
            page.extracted_text,
            max_characters=max_characters,
            overlap_characters=overlap_characters,
        )
    )
    db.add_all(chunks)
    db.flush()
    return chunks
