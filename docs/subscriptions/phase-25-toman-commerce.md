# Phase 25.6 — TOMAN Invoice, Wallet + Payment Integration

Status: completed on 2026-07-26

## Delivered contract

- Extended the universal Invoice contract with the explicit
  `platform_subscription` source. This source has no provider user, has zero
  provider share, and assigns the complete Invoice total to the platform.
- Preserved the existing marketplace rule: every non-subscription Invoice
  still requires a real provider.
- Added subscription Payment Attempts with unique checkout idempotency,
  unique gateway authority/reference, 30-minute expiry, and TOMAN-only money.
- Added authenticated owner operations:
  - `POST /api/v1/billing/checkout`
  - `POST /api/v1/billing/payments/verify`
  - `GET /api/v1/billing/payments/callback/zarinpal`
- Checkout creates a pending Subscription, pending Period, immutable
  plan/version/price snapshots, one universal Invoice item, and a Payment
  Attempt. It does not create Entitlements or activate access.
- Zarinpal uses a Subscription-specific callback and the existing
  server-to-server Verify adapter. Mock payment is restricted to
  non-production environments.
- A verified payment activates the pending Subscription, creates its resolved
  Entitlements and metered usage rows, marks the Invoice paid, and posts one
  balanced immutable ledger journal:
  platform cash debit / platform revenue credit.
- Identical Checkout and Verify retries return the original result without a
  second Invoice, activation, journal, or Entitlement snapshot.
- Upgrading from Free closes the Free period only after verified payment.
  A second active paid Subscription is rejected.

## Database

- Alembic revision: `7b98f2da6a10`.
- `finance_billing_invoices.provider_user_id` is nullable only under the new
  platform-owner check constraint.
- Added `billing_subscription_payment_attempts`.
- Currency remains `TOMAN`; quota remains a non-monetary allowance and is not
  stored in Wallet/Ledger amounts.

## Verification evidence

- Ruff: passed for the complete Backend.
- `compileall backend/app backend/scripts`: passed.
- Focused Subscription tests: 22 passed.
- Full Backend suite: 300 passed, 27 pre-existing warnings.
- Alembic upgrade/check: head and no model drift.
- Transaction-rolled-back real MySQL regression:
  checkout replay, verify exact-once, paid platform Invoice, one balanced
  journal, and 15 post-payment Entitlements passed.
- Runtime health: app/database/Redis all `ok`.

## Explicitly deferred

- No guessed commercial prices were seeded. Farmer Plus and Professional
  catalog values/prices require an explicit product decision.
- Automated renewal, failed-renewal grace, expiry, and lifecycle
  notifications belong to Step 25.7.
- Credentialed Zarinpal sandbox/production verification remains an
  operational release gate while the gateway is disabled locally.
