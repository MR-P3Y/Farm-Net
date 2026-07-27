# Phase 21.8 — Subscription Quota, Technical Usage/Cost + Reconciliation

Verified: 2026-07-28  
Branch: `develop`  
Alembic head: `h21d5b29e7f6`

## Commercial boundary

Barzegar now consumes the existing Phase 25 Billing contracts. It does not
create a second Plan, Subscription, Entitlement, quota, or wallet system.

- `ai.text_chat`, `ai.farm_context`, `ai.deep_analysis`, and
  `ai.image_analysis` reserve one metered unit before queue insertion.
- `ai.smart_diary` and `ai.report_export` require an enabled boolean
  Entitlement and do not invent a numeric reservation.
- `ai.processing_priority` resolves the queue priority from the active
  Subscription snapshot; clients cannot choose priority.
- The Billing reservation key is derived from the AI idempotency key without
  exposing the original key in Billing context.

## Exact lifecycle

```text
validate feature / route / selected context
→ resolve active Entitlement and priority
→ reserve one metered unit exactly once
→ create queued request linked to the reservation
→ finalize only after a non-empty usable answer and technical usage write
→ release on cancellation, stale context, terminal Provider/internal failure,
  or exhausted attempts
```

Retryable attempts retain the same reservation. Request creation compensates a
reservation when insert/flush/commit fails. Replays return the existing request
and do not reserve twice.

## Technical usage and TOMAN cost

Successful attempts may write exactly one `ai_usage_records` row per request
and attempt with Provider/model, input/output/cached tokens and latency.
Failed, blocked, cancelled, partial, or empty results do not create billable
technical usage.

Model configuration now supports versioned:

- input cost per million tokens in TOMAN;
- cached-input cost per million tokens in TOMAN;
- output cost per million tokens in TOMAN.

All three rates must be set together. Until an Admin/product-approved TOMAN
rate exists, Provider cost remains `NULL`; no USD/IRR conversion is guessed.
When configured, technical cost is recorded only as `TOMAN`.

## Reconciliation

The read-only AI reconciliation checks:

- reservation existence, owner, and feature;
- queued/running → reserved;
- succeeded → finalized plus technical usage;
- failed/blocked/cancelled → released or expired;
- no technical usage on unusable results.

It reports stable issue codes and does not silently repair commercial ledgers.

## Verification

- Ruff: passed.
- compileall: passed.
- Backend tests: `357 passed`.
- Alembic upgrade/current/no-drift: passed at `h21d5b29e7f6`.
- real MySQL reserve → cancel → release → cleanup: passed.
- real MySQL reserve → worker success → finalize + exact-once technical usage
  → cleanup: passed.
- app/database/Redis health: OK.
- OpenAI Provider activation remains disabled because Billing credit is not
  available; deterministic Provider tests remain the Step 21.7 evidence.

Step 21.9 Agricultural Safety, Output Validation + Human Escalation is next.
