# Phase 11.2 Delivery Contracts and Database Hardening

Completion date: 2026-07-17

## Implemented

- Database exact-once identity for one notification per
  `(event_id, recipient_user_id, channel)`.
- One durable delivery state per `(notification_id, channel)`.
- Migration cleanup retains the earliest legacy duplicate before creating each
  unique constraint.
- Race-safe service writes use nested transactions/savepoints so a uniqueness
  conflict does not roll back unrelated domain work.
- Source-backed event keys are deterministic over event type, source identity,
  and canonical JSON payload. Source-less/manual events remain unique.
- Self-notification is suppressed by default. Explicit confirmation flows for
  orders, payments, verification submission, and consultation creation opt in.
- Delivery state now includes `processing`, attempt/max-attempt counters, next
  and last attempt timestamps, and a worker lease timestamp.

## Delivery State Contract

External-channel delivery begins as `pending`. A future worker may claim it as
`processing`, then finish as `sent`, `delivered`, `failed`, or `skipped`.
`attempt_count`, `max_attempts`, `next_attempt_at`, `last_attempt_at`, and
`locked_at` are durable coordination fields. Step 11.2 does not execute or
schedule delivery.

In-app notifications continue to be recorded immediately as `sent` by the
`in_app` provider contract.

## Verification

- Alembic head/current/upgrade: `e72b9f4c31a6`.
- MySQL inspection: both new unique constraints and five retry fields present.
- Ruff for Backend application and migrations: passed.
- Compileall for Backend application and scripts: passed.
- Full Backend suite: 33 passed; 16 existing `datetime.utcnow()` warnings.
- Runtime health: application, database, and Redis `ok`.
- Runtime OpenAPI: all 8 existing notification paths remain present.

The broader Ruff command including `backend/scripts` still reports eight
pre-existing E402 import-order findings in four seed scripts. Those unrelated
files were not modified in this step.

## Deferred

- User preferences and channel routing (11.3).
- Queue execution, backoff, recovery, and attempt history (11.4).
- Real email, SMS, and push providers (11.5 through 11.7).
- Mobile/Admin operational changes (later Phase 11 steps).
