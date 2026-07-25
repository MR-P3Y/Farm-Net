# Phase 25.5 — Atomic Quota Reservation, Usage + Idempotency

Status: completed on 2026-07-26

## Delivered contract

- Added `POST /api/v1/billing/usage/estimate` for an authenticated owner to
  check a metered feature without changing quota state.
- Added an internal `QuotaService` contract for reserve, finalize, release,
  expiry, and bounded expiry sweeping. These mutation operations are
  deliberately not public client APIs.
- A reservation locks the active usage row, reclaims expired reservations,
  includes both used and reserved values in the limit check, and increments
  the reserved counter in the same transaction.
- The database-unique `idempotency_key` returns the original reservation for
  an identical retry and rejects a changed owner, feature, or amount with
  `BILLING_IDEMPOTENCY_CONFLICT`.
- Finalization transfers reserved quota to used quota exactly once. Release
  and expiry return reserved quota exactly once. A finalized reservation
  cannot be released.
- Reservation ownership is hidden with a not-found response, and only active,
  enabled, metered Entitlements can be consumed.

## Concurrency and safety

- Usage rows are selected with `FOR UPDATE` before quota arithmetic.
- Reservation rows have a database unique key and a race fallback after
  `IntegrityError`.
- Amounts are positive `Decimal(18,4)` values; reservation TTL is restricted
  to 30–3600 seconds.
- Usage, reservation state, terminal timestamps, release reason, and version
  changes commit as one database transaction.
- No TOMAN amount is mixed with quota units. Billing money remains TOMAN-only.

## Verification evidence

- Ruff: passed.
- `compileall backend/app backend/scripts`: passed.
- Focused Subscription tests: 14 passed.
- Full Backend suite: 292 passed, 27 pre-existing warnings.
- Alembic upgrade: head; Alembic check: no new upgrade operations.
- Real MySQL: estimate, reserve, identical replay, release, and reserved-value
  restoration passed.
- Runtime health: app/database/Redis all `ok`.

## Explicitly deferred

- Paid plan invoice, wallet, payment, refund, renewal, and grace transitions
  belong to Step 25.6.
- Client-callable reserve/finalize/release endpoints are intentionally absent;
  consuming Backend modules call the internal service around real operations.
- Mobile and Admin subscription experiences are later Phase 25 steps.
