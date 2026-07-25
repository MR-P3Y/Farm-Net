# Phase 25.10 — Security, Concurrency, Audit + Reconciliation Hardening

Status: completed

## Database Concurrency Guarantees

Migration `e17c4b82a6d9` adds two stored Generated columns and unique indexes:

- `billing_plans.active_code` allows only one active version per plan code;
- `billing_subscriptions.current_user_id` allows only one active/grace
  subscription per user.

The nullable Generated slots preserve unlimited historical Draft, retired,
pending, cancelled, and expired rows while moving the current-state invariant
into MySQL. Pre-migration checks confirmed zero duplicate active plan codes and
zero users with duplicate current subscriptions. Both Generated expressions
and unique indexes were verified from `information_schema`.

Admin plan/version and subscription writes retain row locks and optimistic
version checks. Unique-race failures are translated to stable 409 application
errors rather than leaking database errors.

## Immutable Billing Audit

The new `billing_audit_logs` table records:

- an exact-once `event_key`;
- action and typed target;
- subscription and plan references;
- actor type and actor user where applicable;
- required Admin reasons;
- old/new JSON snapshots;
- request trace ID when available;
- immutable creation time.

ORM update and delete hooks reject mutation. The audit service rejects
non-system events without a user actor and detects event-key payload conflicts.
Audit coverage includes:

- Admin plan create, Draft update, activation, and retirement;
- Free activation, user cancel, and resume;
- paid checkout creation, renewal checkout, and verified payment;
- Admin manual activation and cancellation;
- Worker-driven renewal, grace, cancellation, and expiry.

Historical events before migration `e17c4b82a6d9` are intentionally not
invented or backfilled. Audit history is authoritative from this migration
forward.

## Read-Only Reconciliation

`GET /api/v1/admin/billing/reconciliation` and
`scripts/check_subscription_reconciliation.py` inspect:

- current Subscription versus active Period cardinality and boundaries;
- paid Period versus Invoice state;
- Entitlement ownership;
- required metered Usage rows;
- Usage owner/period/feature scope;
- used plus reserved quota versus limit;
- Payment Attempt versus Invoice owner, TOMAN currency, and amount;
- succeeded Payment versus exact-once balanced Ledger journal.

The check never repairs or deletes data. It examines at most 1,000
subscriptions and returns at most 200 issues; `truncated=true` prevents a
partial result from being reported as clean.

The real runtime result at completion was:

```text
clean=true
subscriptions=2
periods=2
entitlements=30
usage=10
payment_attempts=0
issues=0
```

## Permissions and Admin UI

Two explicit permissions were added and assigned to `finance_admin`:

- `billing.audit.read`;
- `billing.reconciliation.read`.

The Admin Billing screen now includes a typed Audit/Reconciliation tab with
summary counts, issue details, audit actor/reason/trace fields, filters,
pagination, loading, empty, and error states. Raw JSON is not rendered.

## Verification

- Backend Ruff: passed.
- Backend compileall: passed.
- Backend tests: 314 passed.
- Focused Subscription hardening tests: passed.
- Admin tests: 27 passed.
- Admin analyze: passed.
- Admin web build and Wasm dry-run: passed.
- Alembic head/current: `e17c4b82a6d9`.
- Alembic no-drift: passed.
- Auth seed twice: 12 roles and 270 permissions on both runs.
- Runtime Admin Billing paths: 9.
- Authenticated Audit/Reconciliation runtime: passed.
- Reconciliation API and CLI: clean, zero issues.
- Health: app, database, and Redis OK.

Concurrent owner Mobile design changes remained untouched and outside this
step.

## Next

Phase 25.11 — Docs, Postman + Runtime Regression.
