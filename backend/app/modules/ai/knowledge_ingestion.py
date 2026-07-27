from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ai.models import (
    AIKnowledgeDocument,
    AIKnowledgeExtractedPage,
    AIKnowledgeIngestionJob,
)
from app.modules.ai.pdf_extractor import (
    EXTRACTOR_VERSION,
    PDFExtractionError,
    extract_pdf,
)


class KnowledgeIngestionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def ingest_pdf_document(
    db: Session,
    *,
    document: AIKnowledgeDocument,
    path: Path,
    idempotency_key: str,
) -> AIKnowledgeIngestionJob:
    """Extract one registered PDF exactly once without approving its source."""
    existing = db.scalar(
        select(AIKnowledgeIngestionJob).where(
            AIKnowledgeIngestionJob.idempotency_key == idempotency_key
        )
    )
    if existing is not None:
        return existing

    now = datetime.utcnow()
    job = AIKnowledgeIngestionJob(
        document_id=document.id,
        idempotency_key=idempotency_key,
        extractor_version=EXTRACTOR_VERSION,
        status="running",
        pages_processed=0,
        extracted_characters=0,
        started_at=now,
    )
    db.add(job)
    db.flush()

    try:
        extracted = extract_pdf(path)
        if extracted.sha256 != document.sha256:
            raise KnowledgeIngestionError(
                "DOCUMENT_CHECKSUM_MISMATCH",
                "Stored document checksum does not match the extraction input",
            )
        for page in extracted.pages:
            db.add(
                AIKnowledgeExtractedPage(
                    ingestion_job_id=job.id,
                    document_id=document.id,
                    page_number=page.page_number,
                    extracted_text=page.text,
                    text_sha256=page.text_sha256,
                    character_count=page.character_count,
                    quality_score=Decimal(str(round(page.quality_score, 4))),
                    needs_review=page.needs_review,
                )
            )
        job.pages_processed = extracted.page_count
        job.extracted_characters = sum(page.character_count for page in extracted.pages)
        job.quality_score = Decimal(str(round(extracted.quality_score, 4)))
        job.status = "needs_review" if extracted.needs_review else "succeeded"
        document.page_count = extracted.page_count
        document.is_encrypted = False
        document.extraction_status = job.status
    except (PDFExtractionError, KnowledgeIngestionError) as exc:
        job.status = "failed"
        job.failure_code = exc.code
        if exc.code == "ENCRYPTED_PDF":
            document.is_encrypted = True
        document.extraction_status = "failed"
    finally:
        job.completed_at = datetime.utcnow()

    db.flush()
    return job
