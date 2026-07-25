# Phase 25.4 — Subscription Lifecycle, Periods + Cancellation

Date: 2026-07-26

Status: completed.

## Delivered

- Idempotent activation of the active default Free plan.
- User-row locking before current-subscription checks to serialize lifecycle
  writes for one owner.
- A 30-day Free period with plan code/version/price/currency snapshots.
- Snapshot of all active Plan Features into immutable period Entitlements.
- Zeroed usage rows only for enabled metered features.
- End-of-period cancellation with reason.
- Resume of pending end-of-period cancellation.
- Immediate cancellation only for Free subscriptions.
- Optimistic `expected_version` conflict protection.
- Explicit reactivation after a terminated Free subscription.

## APIs

```text
POST /api/v1/billing/subscription/free
POST /api/v1/billing/subscription/cancel
POST /api/v1/billing/subscription/resume
```

All require `billing.subscription.manage_own`. Paid activation remains
impossible in this step; it must follow verified payment in Step 25.6.

## Rules

- Repeated Free activation returns the same current Free subscription.
- Free activation is rejected when a paid active/grace subscription exists.
- End-of-period cancellation keeps access until the current period ends.
- Resume requires a current subscription pending cancellation.
- Immediate paid cancellation is rejected until refund/financial policy exists.
- Immediate Free cancellation closes the active period and entitlement
  validity without deleting history.
- A stale version returns HTTP 409 and the current version.
- Owner reads and lifecycle writes never target a user ID supplied by clients.

## Verification

- Runtime MySQL lifecycle: idempotent activation, cancel, resume, immediate
  Free cancel, and reactivation passed.
- Reactivated Free subscription: 1 period / 15 entitlements / 5 metered usage
  records.
- Eight focused Subscription tests passed.
- Complete Backend suite: 286 passed; 27 pre-existing warnings after removing
  new UTC deprecation warnings.
- Ruff, compileall, Alembic no-drift, and app/database/Redis health passed.

Next: Step 25.5 Atomic Quota Reservation, Usage + Idempotency.
