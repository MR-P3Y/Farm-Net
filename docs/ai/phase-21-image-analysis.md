# Phase 21.10 — Image Analysis Boundary + Evidence-Gated Diagnosis

Verified: 2026-07-28  
Alembic head: `j21f7d4b0918`

## Implemented

- `image_analysis` requires one real `MediaFile.file_key`; other request kinds
  reject image attachment.
- Image lookup is owner-scoped and non-enumerating and requires active Media.
- Allowed evidence: JPEG, PNG, or WebP; 1–10MB; minimum 256×256.
- `ai_request_media` stores an immutable exact-once snapshot of Media id,
  checksum, MIME, size, and dimensions with `RESTRICT` foreign keys.
- Request idempotency includes the image checksum, so changed evidence cannot
  replay under the same logical request.
- Provider-neutral contracts accept in-memory image data and the OpenAI adapter
  sends it as `input_image`; private storage paths and file keys are not sent.
- Image output must describe visible evidence, express uncertainty, and
  recommend human review. It cannot claim a certain diagnosis from one image.
- Failed evidence validation blocks the answer and Step 21.9/21.8 rules release
  quota and prevent technical billable success.

## Verification

- Ruff and compileall: passed.
- Backend tests: `363 passed`.
- Alembic head: `j21f7d4b0918`.
- App/database/Redis health: OK.
- Real owner-image runtime: skipped because the development database contains
  no active owner image meeting the 256×256 evidence threshold. No artificial
  user Media was created. Owner, MIME, size, dimensions, checksum snapshot and
  Provider payload are covered by deterministic tests.
- Live OpenAI vision remains disabled because Provider Billing credit is
  unavailable.

Step 21.11 Smart Diary Suggestions + Farmer Reports is next.
