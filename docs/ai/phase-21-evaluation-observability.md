# Phase 21.14 — Evaluation, Observability, Abuse + Concurrency Hardening

Status: completed

## Delivered

- Versioned, database-backed evaluation suites and cases.
- Draft-first suite lifecycle with transactional activation; activating a new
  version retires the previous active version of the same suite.
- Deterministic offline scoring for required terms, forbidden terms,
  uncertainty, and human-review language.
- Exact-once evaluation runs and results, with a configurable release pass
  threshold.
- Privacy-safe result storage: candidate output content is not retained; only
  its SHA-256 digest and bounded failure codes are stored.
- Dedicated `ai.evaluation.manage` permission assigned only to the Admin role.
- Three Admin OpenAPI paths for suite creation, activation, and execution.
- Bounded Prometheus metrics for request outcomes, Provider attempts and
  latency, active work, safety blocks, and abuse rejection.
- Per-user transactional serialization and a maximum of five queued/running AI
  requests, preventing concurrent quota/rate-limit bypass.
- Existing `SKIP LOCKED`, lease recovery, idempotency, and exact-once terminal
  workflow behavior remain intact.

## Database

Alembic head: `l21h9f6d2130`

Tables:

- `ai_evaluation_suites`
- `ai_evaluation_cases`
- `ai_evaluation_runs`
- `ai_evaluation_results`

## Runtime Contracts

Admin paths:

- `POST /api/v1/admin/ai/evaluation/suites`
- `POST /api/v1/admin/ai/evaluation/suites/{suite_id}/activate`
- `POST /api/v1/admin/ai/evaluation/runs`

Metrics:

- `farmnet_ai_requests_total`
- `farmnet_ai_attempts_total`
- `farmnet_ai_provider_latency_seconds`
- `farmnet_ai_active_requests`
- `farmnet_ai_safety_blocks_total`
- `farmnet_ai_abuse_rejections_total`

Metric labels are intentionally bounded and contain no user ID, prompt,
conversation, Farm context, idempotency key, or Provider credential.

## Verification

- Ruff: passed.
- Compileall: passed.
- Focused evaluation/observability tests: 7 passed.
- Full Backend suite: 379 passed, 29 warnings.
- Alembic current/head: `l21h9f6d2130`.
- Alembic drift check: no new upgrade operations.
- Auth seed executed twice with stable 12 roles and 285 permissions.
- Runtime health: app/database/Redis all `ok`.
- OpenAPI evaluation paths: 3.
- All six expected Prometheus metric families were present.

Live OpenAI generation remains disabled until billing is activated. The
evaluation gate is deterministic and therefore does not require Provider
billing.

Next: Step 21.15 — AI Docs/Postman + Runtime Regression.
