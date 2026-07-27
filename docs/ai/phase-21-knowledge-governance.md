# Phase 21.3 — Barzegar Knowledge Governance and Persian PDF Ingestion

Verified: 2026-07-27
Branch: `develop`

## Outcome

Barzegar now has a governed foundation for registering, versioning, reviewing,
withdrawing, and extracting Persian PDF knowledge. Extraction does not approve
a source, publish it for retrieval, create chunks/embeddings, or call an AI
Provider.

## Candidate corpus audit

The recursive read-only audit of `docs/FARMER` found:

- 30 PDF files;
- 1,245 pages;
- one encrypted PDF;
- extractable text on the sampled first three pages of every readable PDF.

These files remain candidates. They are not trusted knowledge until publisher,
license evidence, version, checksum, and human approval are registered. The
encrypted file requires manual handling. A rendered Persian sample was visually
checked for readability, but visual readability is not proof of extraction
quality.

## Database contract

Migration `b21d5c93b7f1` adds:

- `ai_knowledge_sources` — provenance, publisher, license evidence, review;
- `ai_knowledge_source_versions` — editions and effective/withdrawal lifecycle;
- `ai_knowledge_documents` — immutable PDF checksum and extraction state;
- `ai_knowledge_ingestion_jobs` — exact-once extraction and lifecycle evidence;
- `ai_knowledge_extracted_pages` — page-level text, checksum, quality and review.

All ownership/history foreign keys use `RESTRICT`. Approval and extraction are
separate states. A successful extraction never changes source/version approval.

## Extraction contract

- PDF only, maximum 100 MiB by default;
- SHA-256 verification before persistence;
- NFKC normalization plus Persian `ی`/`ک` normalization;
- deterministic page text checksums;
- page-level quality score and `needs_review`;
- unavailable, malformed, encrypted, empty, oversized, unsupported, and
  checksum-mismatched inputs fail with stable machine codes;
- an idempotency key prevents duplicate ingestion jobs and extracted pages.

The current quality signal is intentionally conservative and heuristic. OCR,
layout reconstruction, tables/images, chunking, embeddings, retrieval, and
citations belong to later steps.

## Access boundary

The dedicated permissions are:

- `ai.knowledge_sources.read/create/update`;
- `ai.knowledge_sources.review`;
- `ai.knowledge_ingestion.manage`.

Admin and Content Manager receive the governed knowledge operations. Super
Admin receives them through the existing all-permission rule. Ordinary users
receive none of these permissions.

## Next

Step 21.4 — Retrieval Store, Chunking, Embeddings + Citation Contracts.
