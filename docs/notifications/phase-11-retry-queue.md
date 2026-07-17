# Phase 11.4 Retry Queue and Delivery Attempt Logs

Completion date: 2026-07-18

## Implemented

- Durable `notification_delivery_attempts` history with one monotonic attempt
  number per delivery.
- Atomic queue claim using `FOR UPDATE SKIP LOCKED` for external channels.
- Processing leases and recovery of abandoned attempts.
- Capped exponential backoff for retryable failure.
- Terminal failure at `max_attempts` and controlled Admin requeue that preserves
  monotonic attempt numbering.
- Provider-neutral success/failure recording methods for later adapters.
- Permission-protected Admin delivery list, detail/attempt history, and retry.

## State Rules

- `pending -> processing` creates an attempt and worker lease.
- `processing -> sent` closes the attempt successfully.
- Retryable `processing` failure closes the attempt and schedules `pending`.
- Failure at the maximum attempt count becomes terminal `failed`.
- An expired processing lease closes its active attempt with `lease_expired`
  before reclaim, or becomes terminal if its attempt budget is exhausted.
- In-app, processing, sent, and delivered records cannot be manually requeued.

No provider adapter or network delivery is part of this step.

## Verification

- Alembic/MySQL head: `a16d7c4e52b9`.
- Attempt table, unique attempt number, and indexes inspected at runtime: OK.
- Backend Ruff and compileall: OK.
- Full Backend suite: 40 passed with 16 existing UTC deprecation warnings.
- Runtime health application/database/Redis: OK.
- Three Admin delivery operation paths present in OpenAPI.
- Notifications Postman JSON includes queue, detail, and retry requests.

## Deferred

- Email provider adapter: Step 11.5.
- SMS provider adapter: Step 11.6.
- Push device registry/provider: Step 11.7.
- Mobile/Admin UI hardening: Steps 11.8 and 11.9.
