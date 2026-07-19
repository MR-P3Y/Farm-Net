# Phase 20 Wallet, Settlement, and Accounting Real-State Audit

## Step 20.1 Result

This read-only audit inspected the real Backend models, migrations, services,
routes, permissions, tests, and financial documentation on `develop`. It did
not add a table, API, payment provider, or client behavior.

## Existing Financial Foundation

Phase 9 already provides an order-specific financial foundation:

- product orders snapshot subtotal, discount, shipping, total, commission, and
  seller amounts;
- one order invoice and its line items;
- one commission snapshot per order/invoice;
- idempotent checkout, payment attempts, payment verification, transactions,
  inventory reservations, and full refunds;
- typed Admin invoice, attempt, transaction, refund, and audit reads;
- database uniqueness and positive-amount constraints for important replay
  boundaries;
- only the `mock` payment provider and mock refund completion.

These contracts must remain compatible. They are not a wallet or an accounting
ledger and must not be renamed into one without a migration strategy.

## Domain Readiness

| Domain | Existing amount contract | Existing finance integration |
| --- | --- | --- |
| Product orders | immutable order/invoice/commission totals | Phase 9 mock payment and full refund |
| Services | offer price and request budget | none |
| Equipment rental | accepted price, rental, deposit, and total snapshots | none |
| Consultation | request budget | none |

Services and consultation budgets are not final payable prices. Rental totals
are commercial snapshots but do not prove deposit capture, payment, release,
damage, penalty, refund, commission, or settlement.

## Confirmed Gaps

- no wallet account or balance-bucket model;
- no immutable double-entry journal or balanced debit/credit entries;
- no pending, available, reserved, withdrawn, or refunded balance derivation;
- no provider payable/release policy;
- no settlement or payout request, approval, execution, or reconciliation;
- no universal billable-source contract across orders, services, rentals, and
  consultations;
- no finance integration for services, rentals, or consultations;
- no partial refund or accounting adjustment/reversal workflow;
- no real gateway callback/verification adapter or real money transfer;
- no user/provider wallet history and no settlement UI;
- no complete accounting reconciliation or operational close report.

The permissions `finance.settlements.read` and
`finance.settlements.manage` exist, but no settlement model or API implements
them. Permissions alone are not an implemented feature.

## Blocking Contract Decisions

1. `TOMAN` is used by products, services, and rentals, while consultation used
   `IRR`. Step 20.2 resolved this: canonical storage/API is Iranian toman with
   code `TOMAN`, Persian display is `تومان`, and legacy conversion is
   `10 IRR = 1 TOMAN`.
2. A service or consultation budget cannot create an invoice. A separately
   accepted final-price snapshot is required first.
3. Rental deposit principal must remain separate from rental revenue. Deposit
   capture, release, damage, and penalty require their own auditable events.
4. Wallet balances must be derived from immutable balanced entries, not changed
   directly as a single mutable balance.
5. Every financial command requires an idempotency key, source reference,
   actor, trace metadata, currency, and database transaction boundary.
6. Corrections use reversal/adjustment entries. Posted entries are never edited
   or deleted.

## Approved Architecture Boundary

Phase 20 will extend the existing foundation incrementally:

```text
billable domain event
  -> immutable commercial snapshot
  -> invoice and commission snapshot
  -> payment/refund event
  -> balanced journal transaction and entries
  -> provider pending/available balance
  -> settlement request
  -> payout execution and reconciliation
```

The ledger is the accounting source of truth. Cached balance rows, if added,
are projections protected by row locks and reconciliation checks. Existing
Phase 9 order APIs remain compatible while their successful payment/refund
events are bridged into the ledger exactly once.

## Phase 20 Delivery Plan

1. **20.1 — Real-State Audit + Contract Boundary** (this step)
2. **20.2 — Canonical Money + Billable Source Contracts**
3. **20.3 — Wallet Accounts + Double-Entry Ledger DB/Permissions**
4. **20.4 — Order Finance Ledger Bridge + Reconciliation**
5. **20.5 — Universal Invoice + Commission Foundation**
6. **20.6 — Services/Consultation Final-Price Contracts**
7. **20.7 — Rental Revenue + Deposit Accounting Boundaries**
8. **20.8 — Balance Release + Settlement/Payout Workflow**
9. **20.9 — Refund, Reversal, Adjustment + Concurrency Hardening**
10. **20.10 — Real Payment Gateway Adapter + Callback Verification**
11. **20.11 — Financial Notifications + Privacy/Audit Hardening**
12. **20.12 — Mobile Wallet, Invoices, and Provider Settlements**
13. **20.13 — Admin Accounting, Settlement, and Reconciliation**
14. **20.14 — Docs/Postman + Runtime Financial Regression**
15. **20.15 — Finance Release Gate + Tag**

Real gateway and payout activation require provider credentials, sandbox
contracts, callback URLs, secret management, and operational approval. Until
those exist, the project must label monetary movement as mock/simulated and must
not claim production payment or settlement.

## Step 20.2 Entry Criteria

Step 20.2 may change contracts only after it proves:

- the canonical storage/display unit for `IRR` and `TOMAN`;
- exact billable source types and immutable source identifiers;
- which domain state creates, pays, releases, cancels, or refunds an invoice;
- separation of customer funds, provider payable, platform revenue, deposits,
  refunds, and payout clearing;
- backward compatibility for all Phase 9 order/payment endpoints.
