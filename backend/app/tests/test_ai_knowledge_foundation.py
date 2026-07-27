import hashlib

import pytest
from pypdf import PdfWriter
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.modules.ai.models import (
    AIKnowledgeDocument,
    AIKnowledgeExtractedPage,
    AIKnowledgeIngestionJob,
    AIKnowledgeSource,
    AIKnowledgeSourceVersion,
)
from app.modules.ai.pdf_extractor import (
    PDFExtractionError,
    extract_pdf,
    normalize_persian_text,
)
from app.modules.auth.seed import BASE_PERMISSIONS


KNOWLEDGE_TABLES = {
    "ai_knowledge_sources",
    "ai_knowledge_source_versions",
    "ai_knowledge_documents",
    "ai_knowledge_ingestion_jobs",
    "ai_knowledge_extracted_pages",
}


def _constraint_names(model, kind) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def test_barzegar_knowledge_governance_registers_five_separate_tables() -> None:
    models = {
        AIKnowledgeSource,
        AIKnowledgeSourceVersion,
        AIKnowledgeDocument,
        AIKnowledgeIngestionJob,
        AIKnowledgeExtractedPage,
    }
    assert {model.__tablename__ for model in models} == KNOWLEDGE_TABLES


def test_governance_and_exact_once_constraints_are_explicit() -> None:
    assert "ck_ai_knowledge_sources_review_state" in _constraint_names(
        AIKnowledgeSource, CheckConstraint
    )
    assert "uq_ai_source_version_no" in _constraint_names(
        AIKnowledgeSourceVersion, UniqueConstraint
    )
    assert AIKnowledgeDocument.__table__.c.sha256.unique is True
    assert AIKnowledgeIngestionJob.__table__.c.idempotency_key.unique is True
    assert "ck_ai_ingestion_jobs_lifecycle" in _constraint_names(
        AIKnowledgeIngestionJob, CheckConstraint
    )
    assert "ck_ai_ingestion_jobs_failure" in _constraint_names(
        AIKnowledgeIngestionJob, CheckConstraint
    )
    assert "uq_ai_extracted_page_job_number" in _constraint_names(
        AIKnowledgeExtractedPage, UniqueConstraint
    )


def test_knowledge_permissions_separate_edit_review_and_ingestion() -> None:
    codes = {permission.code for permission in BASE_PERMISSIONS}
    assert {
        "ai.knowledge_sources.read",
        "ai.knowledge_sources.create",
        "ai.knowledge_sources.update",
        "ai.knowledge_sources.review",
        "ai.knowledge_ingestion.manage",
    } <= codes


def test_persian_normalization_unifies_arabic_codepoints_and_spacing() -> None:
    assert normalize_persian_text("  كشتِ  گندم \u200f\n مزرعه ي من ") == ("کشتِ گندم\nمزرعه ی من")


def test_pdf_extraction_is_deterministic_and_flags_empty_text(tmp_path) -> None:
    path = tmp_path / "source.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with path.open("wb") as stream:
        writer.write(stream)

    result = extract_pdf(path)

    assert result.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert result.page_count == 1
    assert result.pages[0].page_number == 1
    assert result.pages[0].character_count == 0
    assert result.needs_review is True


def test_encrypted_pdf_is_rejected_for_manual_review(tmp_path) -> None:
    path = tmp_path / "encrypted.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.encrypt("secret")
    with path.open("wb") as stream:
        writer.write(stream)

    with pytest.raises(PDFExtractionError) as error:
        extract_pdf(path)

    assert error.value.code == "ENCRYPTED_PDF"


def test_malformed_pdf_has_stable_failure_code(tmp_path) -> None:
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"not-a-pdf")

    with pytest.raises(PDFExtractionError) as error:
        extract_pdf(path)

    assert error.value.code == "MALFORMED_PDF"
