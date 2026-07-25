# Unified Subscription and Entitlement API

Base path: `/api/v1`

Currency: `TOMAN`

This API is the single product-wide plan, Entitlement, quota, and subscription
contract. Roles and permissions remain independent from commercial access:

```text
permission allowed
AND entitlement enabled
AND quota available
```

Safety, consent withdrawal, personal-data deletion, severe weather warnings,
source visibility, and human escalation must not be paywalled.

## Response Envelope

Successful responses use:

```json
{
  "success": true,
  "data": {},
  "message": "OK",
  "meta": {
    "trace_id": "..."
  }
}
```

Errors use the project error envelope and never expose payment authority,
idempotency keys, password data, or another user's Entitlements/Usage.

## Public Plan Catalog

### `GET /billing/plans`

Returns active and currently effective plan versions ordered by TOMAN price.

### `GET /billing/plans/{plan_code}`

Returns the latest active/effective version for a stable plan code.

Public plan fields include the typed feature values but no subscriber data.

## Owner Reads

Required permissions:

- `billing.subscription.read_own`;
- `billing.entitlements.read`;
- `billing.usage.read_own`.

### `GET /billing/subscription/me`

Returns the current active/grace subscription or `null`. The read is
non-mutating.

### `GET /billing/entitlements/me`

Returns the current period's resolved Entitlement snapshots. It does not read
mutable plan values after activation.

### `GET /billing/usage/me`

Returns used, reserved, limit, remaining, unlimited, and period-end values for
the authenticated owner only.

### `POST /billing/usage/estimate`

Read-only quota estimate:

```json
{
  "feature_code": "ai.text_chat",
  "amount": 1
}
```

Estimate does not reserve or consume quota. Internal consumers use the atomic
reserve/finalize/release service boundary with their own idempotency key.

## Owner Lifecycle

Required permission: `billing.subscription.manage_own`.

### `POST /billing/subscription/free`

Idempotently provisions the active default Free plan. Repeated calls return
the same current Free subscription. It is rejected when paid active/grace
access exists.

### `POST /billing/subscription/cancel`

```json
{
  "expected_version": 3,
  "cancel_at_period_end": true,
  "reason": "No longer needed"
}
```

Paid subscriptions can be cancelled only at period end through the owner API.
Immediate owner cancellation is Free-only. `expected_version` prevents lost
updates.

### `POST /billing/subscription/resume`

```json
{
  "expected_version": 4
}
```

Only a current subscription marked for period-end cancellation can resume.

## Paid Checkout and Renewal

### `POST /billing/checkout`

```json
{
  "plan_code": "farmer_plus",
  "provider": "mock",
  "idempotency_key": "checkout-user-42-farmer-plus-001"
}
```

`mock` is forbidden in production. Zarinpal authority stays server-side and is
not returned; only the redirect URL is exposed. Checkout creates pending
Subscription, Period, platform-owned Invoice, and Payment Attempt state.
Entitlements are not activated before verified payment.

### `POST /billing/subscription/renew/checkout`

Available only during a paid subscription's three-day Grace window:

```json
{
  "provider": "mock",
  "idempotency_key": "renew-user-42-period-2-001"
}
```

### `POST /billing/payments/verify`

```json
{
  "payment_attempt_id": 10,
  "provider_token": "mock-approved"
}
```

Verification is idempotent and row-locked. Success activates exactly one
Period and Entitlement snapshot, marks the Invoice paid, and posts one balanced
TOMAN platform cash/revenue Ledger journal.

### `GET /billing/payments/callback/zarinpal`

Gateway callback accepts `Authority` and `Status`. It is server-to-server
oriented and never accepts a client-supplied Merchant ID.

## Admin Plans

Admin base path: `/admin/billing`.

### `GET /admin/billing/plans`

Permission: `billing.plans.read`. Supports `q`, `status`, `page`, and
`page_size`.

### `POST /admin/billing/plans`

Permission: `billing.plans.create`. Creates a new Draft version. Currency is
implicit and fixed to TOMAN. Feature values are typed:

```json
{
  "code": "farmer_plus",
  "name": "Farmer Plus",
  "billing_period": "monthly",
  "price_toman": 250000,
  "features": [
    {
      "feature_code": "ai.text_chat",
      "enabled": true,
      "unlimited": false,
      "numeric_value": 100
    }
  ]
}
```

### `PATCH /admin/billing/plans/{plan_id}`

Permission: `billing.plans.update`. Draft-only. Requires
`expected_version`. Active and retired commercial snapshots are immutable.

### `PATCH /admin/billing/plans/{plan_id}/status`

Permission: `billing.plans.update`.

```json
{
  "expected_version": 2,
  "status": "active"
}
```

Activating a Draft retires the previous active version of the same code.
MySQL guarantees at most one active version. The default Free plan cannot be
retired.

## Admin Subscriptions

### `GET /admin/billing/subscriptions`

Permission: `billing.subscriptions.read`. Supports owner search, status,
plan/user filters, and pagination.

### `GET /admin/billing/subscriptions/{subscription_id}`

Returns lifecycle provenance and typed Usage. This contract is Admin-only.

### `POST /admin/billing/subscriptions/manual-activate`

Permission: `billing.subscriptions.activate`.

```json
{
  "user_id": 42,
  "plan_id": 3,
  "reason": "Customer support grant"
}
```

Manual activation requires an active plan and a user without active/grace
access. It records Admin actor/reason and Admin-sourced Entitlements. It never
creates a fake payment or Invoice.

### `PATCH /admin/billing/subscriptions/{subscription_id}/cancel`

Permission: `billing.subscriptions.cancel`.

```json
{
  "expected_version": 3,
  "cancel_at_period_end": false,
  "reason": "Confirmed fraud response"
}
```

Admin cancellation may be immediate or period-end and is fully audited.

## Audit and Reconciliation

### `GET /admin/billing/audit`

Permission: `billing.audit.read`. Filters: `action`, `target_type`,
`target_id`, `actor_user_id`, and pagination.

Audit rows are immutable and exact-once by `event_key`. Audit is authoritative
from migration `e17c4b82a6d9` forward; historical events were not fabricated.

### `GET /admin/billing/reconciliation`

Permission: `billing.reconciliation.read`. Read-only comparison across
Subscription, Period, Entitlement, Usage, Invoice, Payment, and Ledger.
It does not repair data.

Operational CLI:

```powershell
docker exec farmnet_backend python scripts/check_subscription_reconciliation.py
```

Exit code is zero only for a complete clean result.

## Lifecycle States

```text
pending -> active -> grace -> active
                   \-> expired
active --period-end cancellation--> cancelled
active Free --immediate owner/admin cancellation--> cancelled
```

Free periods renew automatically. Due paid periods enter three-day Grace.
Lifecycle workers use row locks with `SKIP LOCKED`.

## Stable Error Families

- `BILLING_PLAN_NOT_FOUND`
- `BILLING_PLAN_IMMUTABLE`
- `BILLING_PLAN_VERSION_CONFLICT`
- `BILLING_PLAN_ACTIVE_CONFLICT`
- `BILLING_ACTIVE_SUBSCRIPTION_EXISTS`
- `BILLING_ACTIVE_SUBSCRIPTION_NOT_FOUND`
- `BILLING_SUBSCRIPTION_VERSION_CONFLICT`
- `BILLING_IDEMPOTENCY_CONFLICT`
- `BILLING_QUOTA_EXCEEDED`
- `BILLING_PAYMENT_PROVIDER_UNAVAILABLE`
- `BILLING_PAYMENT_TOKEN_INVALID`
- `BILLING_AUDIT_IDEMPOTENCY_CONFLICT`

Authentication failures return 401. Missing permissions return 403.
Validation returns 422. Version/idempotency/concurrency conflicts return 409.

## Production Boundaries

- Zarinpal remains disabled until credentialed staging verification succeeds.
- Mock payment is non-production only.
- Wallet TOMAN money and feature quota are separate accounting domains.
- Reconciliation is detection-only; repair requires a separately reviewed
  operation.
- Never store tokens, credentials, gateway authority, or real personal data in
  Postman collections.
