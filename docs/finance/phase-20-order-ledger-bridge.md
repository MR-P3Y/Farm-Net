# Phase 20.4 Order Finance Ledger Bridge and Reconciliation

## Atomic Order Bridge

The existing Phase 9 payment verification, legacy Mock Pay, and successful Mock
refund flows now post their ledger journal before the existing database commit.
If journal posting fails, the payment/refund state and legacy financial
transaction are rolled back with it.

Payment journal:

```text
Debit   platform_cash       invoice.total_amount
Credit  provider_pending    invoice.provider_amount
Credit  platform_revenue    invoice.platform_amount
```

Refund journal exactly reverses those economic sides. Zero-value commission or
provider lines are omitted; every stored entry remains positive and the journal
must still balance.

Each journal links one-to-one to the existing `finance_transactions` row using
`legacy_transaction_id`, plus a deterministic journal number and idempotency
key. Replaying the bridge returns the existing journal and cannot post twice.

## Reconciliation

```http
GET /api/v1/admin/finance/reconciliation
```

Permission: `finance.ledger.reconcile`.

The typed read-only report compares successful legacy payment/refund
transactions with linked ledger journals and reports:

- missing payment transaction IDs;
- missing refund transaction IDs;
- journal header debit/credit mismatches;
- entry-sum mismatches or journals with fewer than two entries;
- source and posted counts plus a derived `is_clean` flag.

The endpoint does not repair or post records. Automatic/manual repair requires
a separately authorized future command with audit and idempotency controls.

## Verification

- migration: `d9a4b2f20404 (head)`
- Ruff/compileall: passed
- focused bridge/order/ledger tests: 21 passed
- full Backend: 90 passed with 16 existing UTC warnings
- Runtime OpenAPI reconciliation path: present
- unauthenticated reconciliation: `401`
- Orders/Payments Postman collection JSON: valid; reconciliation request added
- Runtime reconciliation: clean, with zero existing successful payment/refund
  rows and therefore no production-like posting smoke candidate
- health: app/database/Redis `ok`
- Backend image rebuilt and container recreated; Database and Redis volumes were
  not removed or restarted

## Boundary

This step bridges only product orders. It does not release pending provider
funds, calculate a mutable balance, implement settlement/payout, connect a real
gateway, or finance Services, Consultation, or Rental.
