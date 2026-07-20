# Phase 20.14 — Docs/Postman + Runtime Financial Regression

Date: 2026-07-20

Branch: `develop`

Baseline commit: `99d3d88`

## Scope

This step adds no feature and changes no API, Mobile, or Admin behavior. It
consolidates the implemented Phase 20 contract and records release evidence for
canonical Iranian toman accounting, Wallet/Ledger, Invoice/Commission,
Settlement, Refund/Reversal/Adjustment, Zarinpal adapter boundaries, Mobile,
and Admin Finance.

## Verified results

| Area | Result |
| --- | --- |
| Backend Ruff | OK |
| Backend compileall | OK |
| Backend pytest | OK — 129 passed; 17 existing UTC deprecation warnings |
| Alembic | OK — upgraded/current at `fdcb2ab80c12 (head)` |
| Auth seed idempotency | OK — two runs, 12 roles / 249 permissions each |
| Health | OK — application, database, and Redis |
| Runtime reconciliation | OK — all mismatch arrays empty |
| OpenAPI | OK — 253 total paths; 27 financial/payment/admin-refund paths |
| Mobile | OK — analyze, 38 tests, Web build, Wasm dry-run |
| Admin | OK — analyze, 17 tests, Web build, Wasm dry-run |
| Postman | OK — 48 requests; 18 raw JSON templates parse after variable resolution |

Runtime reconciliation observed zero successful Payment transactions, zero
successful Refund transactions, zero posted Payment journals, and zero posted
Refund journals. This is a valid clean-state consistency check, not evidence of
real money movement.

## Postman contract

The authoritative collection is
`postman/collections/orders-payments-commission.postman_collection.json`. It
covers Product Order checkout/payment/refund, Invoice/Commission, own Wallet and
Settlement operations, Admin Ledger/Wallet/Settlement/Reconciliation and
Adjustment operations, and the Zarinpal callback contract. Placeholder values
such as `{{order_id}}` are resolved before validating raw request bodies as
JSON.

## Explicitly skipped or unavailable

- Credentialed Zarinpal sandbox request/redirect/callback: skipped because no
  Merchant ID and no public HTTPS callback endpoint are configured. The adapter
  remains disabled by default.
- Production payment: not attempted and not claimed.
- Real bank payout: not implemented; the current terminal payout operation is
  explicitly simulated clearing.
- Real-row financial reconciliation: unavailable because this runtime contains
  no successful Payment or Refund rows.

## Release conclusion

Step 20.14 passes. Phase 20 can proceed to its release gate and tag only after a
fresh clean-tree/upstream check. Operational activation of Zarinpal and real
bank payout remain separate future work and are not implied by this result.
