# Phase 25.7 — Renewal, Expiry, Grace Period + Notifications

Status: completed on 2026-07-26

## Lifecycle policy

- Free subscriptions renew automatically into a new 30-day Period with fresh
  Entitlement and metered-usage snapshots.
- A subscription marked `cancel_at_period_end` closes without entering Grace.
- A due paid subscription enters a three-day Grace window. Existing
  Entitlements are extended through that window so access does not disappear
  before the user can renew.
- Paid renewal Checkout is available only during Grace and creates a distinct
  pending Period, universal TOMAN Invoice, Invoice item, and Payment Attempt.
- Verified renewal payment activates that pending Period, clears Grace, and
  creates new Entitlement/usage snapshots exactly once.
- An unpaid subscription becomes `expired` at the Grace boundary and its
  Entitlements end at the same effective timestamp.

## APIs and processing

- Added `POST /api/v1/billing/subscription/renew/checkout`.
- Existing `POST /api/v1/billing/payments/verify` handles both initial
  activation and renewal.
- Added bounded, row-locked lifecycle processor:
  `backend/scripts/run_subscription_lifecycle.py --limit N`.
- Processor batches use `FOR UPDATE SKIP LOCKED`; repeated runs see no due
  transition after the first successful commit.

## Notifications

Registered lifecycle event types:

- `subscription.activated`
- `subscription.renewed`
- `subscription.grace_started`
- `subscription.cancelled`
- `subscription.expired`

Every event uses a deterministic key containing Subscription, Period sequence,
and transition. The existing Notification event/recipient uniqueness
therefore prevents duplicate lifecycle notifications on retries or competing
workers.

## Finance and database

- Added `platform_subscription_renewal` as an explicit platform-owned Invoice
  source with no provider and full platform share.
- Alembic revision `bc620ec4f128` extends the platform Invoice constraint
  without weakening marketplace Invoice ownership.
- Every renewal remains TOMAN-only and creates its own auditable Period and
  Invoice. Wallet money and feature quota remain separate.

## Verification evidence

- Ruff: passed for the complete Backend.
- `compileall backend/app backend/scripts`: passed.
- Focused Subscription tests: 27 passed.
- Full Backend suite: 305 passed, 27 pre-existing warnings.
- Alembic upgrade/check: head and no model drift.
- Real MySQL rolled-back lifecycle:
  paid due → Grace → idempotent renewal Checkout → exact-once Verify →
  Period 2 + 15 Entitlements → later Grace → Expired.
- Five lifecycle event records were created exactly once in the real
  regression.
- Empty production-like lifecycle worker run completed successfully.
- Runtime health: app/database/Redis all `ok`.

## Operational boundary

- The lifecycle script is ready for a scheduler/worker deployment, but
  production scheduling and alerting remain part of infrastructure rollout.
- Credentialed Zarinpal sandbox/production verification remains an external
  release gate.
