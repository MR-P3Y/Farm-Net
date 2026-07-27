# Phase 21.5 — Conversation, Request and Async Run Workflow

Verified: 2026-07-27

## Outcome

Barzegar now has owner-scoped conversation and request APIs plus a database
queue/worker contract with exact replay, leases, retries, attempt history,
stale-worker recovery, terminal exhaustion, cancellation, and exact-once
input/output messages.

No model Provider is enabled and no worker process is started automatically.
Farm context is Step 21.6, Provider/prompt routing is Step 21.7, and commercial
quota consumption is Step 21.8.

## Owner APIs

| Method | Path | Permission |
|---|---|---|
| POST | `/api/v1/ai/conversations` | `ai.conversations.create` |
| GET | `/api/v1/ai/conversations` | `ai.conversations.read_own` |
| GET | `/api/v1/ai/conversations/{id}` | `ai.conversations.read_own` |
| POST | `/api/v1/ai/conversations/{id}/requests` | `ai.requests.create` |
| GET | `/api/v1/ai/requests/{id}` | `ai.requests.read_own` |
| POST | `/api/v1/ai/requests/{id}/cancel` | `ai.requests.cancel_own` |

Every lookup includes owner scope. Owner responses exclude idempotency keys,
fingerprints, worker identities, leases, attempt counters, Provider fields, and
internal queue details.

## Idempotency

`user_id + idempotency_key` remains unique. A canonical SHA-256 fingerprint
binds the key to conversation, feature, request kind, normalized content, and
prompt-policy version. Exact replay returns the existing request; a changed
payload returns `AI_IDEMPOTENCY_CONFLICT`.

One input and one output message per request are enforced by
`request_message_kind`. Tool messages remain outside that uniqueness scope.

## Queue and worker contract

- queue order respects priority, availability time, and stable request ID;
- `SELECT ... FOR UPDATE SKIP LOCKED` prevents concurrent worker claims;
- every claim creates a monotonic execution attempt;
- running work has a worker identity and expiring lease;
- stale attempts close as `timed_out` before reclaim;
- retry uses bounded exponential backoff;
- max-attempt exhaustion becomes a terminal request failure;
- success creates the assistant output exactly once;
- only queued requests may be cancelled by their owner.

Migration: `d21f7e15d9b3`.

## Verification

- all 344 Backend tests, Ruff, and compileall passed;
- MySQL upgrade and Alembic no-drift passed;
- runtime create, exact replay, queued cancellation, and cleanup passed;
- five OpenAPI paths expose six typed operations;
- application, database, and Redis health remained `ok`.

## Next

Step 21.6 — Selected Farm Context, Consent, Freshness + Privacy Hardening.
