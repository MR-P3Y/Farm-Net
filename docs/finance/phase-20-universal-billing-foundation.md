# Phase 20.5 Universal Invoice and Commission Foundation

## Universal Contracts

Four `TOMAN`-only tables now provide domain-neutral billing:

- `finance_billing_invoices`: immutable source identity, payer/provider,
  lifecycle, totals, platform/provider split, and optional unique Phase 9 link;
- `finance_billing_invoice_items`: ordered immutable commercial snapshots;
- `finance_commission_policies`: source-specific percentage policy with a
  database-enforced single default per source;
- `finance_billing_commission_snapshots`: immutable policy/result snapshot for
  one invoice with an optional unique Phase 9 commission link.

Invoice constraints require positive total, nonnegative components, `TOMAN`,
and `platform_amount + provider_amount = total_amount`. Item quantities are
positive. Snapshot and item updates/deletes are blocked through the ORM.

## Product Order Compatibility

Phase 9 remains the public order/payment contract. During the existing atomic
Checkout, each legacy order Invoice, Invoice Item, and Commission Snapshot now
creates exactly one universal Invoice, Item set, Commission Policy, and
Commission Snapshot before Commit. Replay remains protected by the existing
Checkout idempotency plus unique legacy/source links.

Payment, refund-pending, refund, and unpaid cancellation synchronize the
universal invoice lifecycle. Historical Phase 9 invoices are lazily bridged
when one of these transitions occurs.

## Domain Eligibility Boundary

- product order: enabled;
- service request: blocked until a mutually accepted final-price snapshot;
- consultation request: blocked until a mutually accepted final-price snapshot;
- rental request: deferred to Step 20.7 so rental revenue and deposit principal
  remain separate.

No budget field can create an invoice. This step adds no public billing API,
payment provider, wallet balance, release, settlement, or payout.

## Verification

- Ruff/compileall: passed
- final focused billing/order/ledger tests: 19 passed
- full Backend: 92 passed with 16 existing UTC warnings
- Alembic: `f7a6d4b20606 (head)`
- Alembic metadata check: no Finance drift; it reports only four pre-existing
  Consultant/Services unique-index naming differences
- Runtime: all four billing tables present
- Runtime data: zero legacy invoices, zero universal invoices, zero policies;
  therefore no existing-row billing smoke candidate
- health: app/database/Redis `ok`
- no API path added; Postman remains unchanged
