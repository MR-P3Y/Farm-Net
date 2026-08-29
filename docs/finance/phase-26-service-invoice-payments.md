# Phase 26.2: service invoice payments

## Scope

This phase makes the universal `BillingInvoice` payable for
`service_request` and `consultation_request` sources. It does not release the
provider balance. Verified provider proceeds remain in the pending wallet until
a later completion-confirmation and release phase.

## Contract

1. A provider proposes the final price.
2. The requester accepts it; the existing final-price service creates or
   reuses one payment-pending `BillingInvoice`.
3. The payer calls `POST /api/v1/finance/invoices/{invoice_id}/checkout` with
   `provider` and an idempotency key.
4. Mock checkout is available only outside production. Zarinpal checkout uses
   the server callback under `/api/v1/finance/payments/callback/zarinpal`.
5. `POST /api/v1/finance/payments/verify` verifies a payer-owned attempt.
6. Successful verification marks both attempt and Invoice paid and posts the
   exact-once ledger transaction keyed by `payment:billing_invoice:{id}`.
7. A service cannot enter `in_progress` until its final-price Invoice is paid.

## Accounting movement

| Entry | Debit | Credit |
|---|---:|---:|
| Platform cash | Invoice total | 0 |
| Provider pending balance | 0 | Provider net amount |
| Platform revenue | 0 | Commission amount |

The transaction must balance and all amounts use the canonical Iranian Toman
money contract.

## Deployment

Run `alembic upgrade head` before serving the new routes. The migration adds
`finance_billing_payment_attempts` and advances the Alembic head to
`p26d4e5f6a7b`. Existing Backend, database, phone, emulator, and Chrome sessions
must be left running until the owner chooses the deployment window.

## Verification targets

- Source OpenAPI contains checkout, verify, and Zarinpal callback paths.
- Payment attempt ownership, provider, expiry, and idempotency are enforced.
- Re-verifying a successful attempt does not duplicate the ledger transaction.
- Service provider and admin transitions reject `in_progress` while unpaid.
- Mobile requester/provider UI exposes proposal, decision, payment, and paid
  state in Persian/English and inherits light/dark theme colors.
