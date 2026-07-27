import hashlib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


EXTRACTOR_VERSION = "pypdf-6-nfkc-v1"


@dataclass(frozen=True)
class ExtractedPDFPage:
    page_number: int
    text: str
    text_sha256: str
    character_count: int
    quality_score: float
    needs_review: bool


@dataclass(frozen=True)
class ExtractedPDF:
    sha256: str
    byte_size: int
    page_count: int
    is_encrypted: bool
    pages: tuple[ExtractedPDFPage, ...]
    quality_score: float
    needs_review: bool


class PDFExtractionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def normalize_persian_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.translate(str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک"}))
    normalized = normalized.replace("\u200f", "").replace("\u200e", "")
    lines = (" ".join(line.split()) for line in normalized.splitlines())
    return "\n".join(line for line in lines if line).strip()


def extract_pdf(path: Path, *, max_bytes: int = 100 * 1024 * 1024) -> ExtractedPDF:
    try:
        resolved = path.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise PDFExtractionError("DOCUMENT_UNAVAILABLE", "PDF document is not available") from exc
    if resolved.suffix.lower() != ".pdf":
        raise PDFExtractionError("UNSUPPORTED_MEDIA_TYPE", "Only PDF documents are accepted")
    byte_size = resolved.stat().st_size
    if byte_size <= 0 or byte_size > max_bytes:
        raise PDFExtractionError("INVALID_FILE_SIZE", "PDF size is outside the allowed range")

    try:
        payload = resolved.read_bytes()
        reader = PdfReader(resolved)
    except (OSError, PdfReadError) as exc:
        raise PDFExtractionError("MALFORMED_PDF", "PDF cannot be parsed safely") from exc
    if reader.is_encrypted:
        raise PDFExtractionError("ENCRYPTED_PDF", "Encrypted PDFs require manual review")

    pages: list[ExtractedPDFPage] = []
    for number, page in enumerate(reader.pages, start=1):
        text = normalize_persian_text(page.extract_text() or "")
        count = len(text)
        quality = min(1.0, count / 800.0)
        needs_review = count < 120
        pages.append(
            ExtractedPDFPage(
                page_number=number,
                text=text,
                text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                character_count=count,
                quality_score=quality,
                needs_review=needs_review,
            )
        )
    if not pages:
        raise PDFExtractionError("EMPTY_PDF", "PDF contains no pages")
    score = sum(page.quality_score for page in pages) / len(pages)
    return ExtractedPDF(
        sha256=hashlib.sha256(payload).hexdigest(),
        byte_size=byte_size,
        page_count=len(pages),
        is_encrypted=False,
        pages=tuple(pages),
        quality_score=score,
        needs_review=any(page.needs_review for page in pages),
    )
