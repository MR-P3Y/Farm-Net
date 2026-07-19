# Phase 20.2 Canonical Money and Billable Source Contracts

## Canonical Currency

Farm Net uses Iranian toman everywhere:

- API/database code: `TOMAN`
- Persian UI label: `تومان`
- amount semantics: one stored unit equals one Iranian toman
- `IRR` is not accepted for any new commercial input
- legacy conversion rule: `10 IRR = 1 TOMAN`

Amounts are never silently converted at an API boundary. The consultation
migration converts legacy `IRR` rows once, changes the code to `TOMAN`, and
divides the amount by 10 in the same statement. New consultation requests,
product inputs, service offers/requests, and rental equipment/pricing inputs
reject every currency except `TOMAN`.

## Typed Source Contract

`BillableSourceRef` defines the minimum identity for future accounting posts:

- `source_type`: `product_order`, `service_request`, `rental_request`, or
  `consultation_request`;
- immutable positive `source_id`;
- positive payer and provider user IDs;
- currency fixed to `TOMAN`.

The contract also names invoice, payment, release, cancellation, refund,
reversal, and settlement events. It does not post money yet.

## Source Eligibility

| Source | Current eligibility | Required commercial snapshot |
| --- | --- | --- |
| Product order | eligible through the existing Phase 9 flow | order/invoice totals and commission snapshot |
| Service request | not yet eligible | mutually accepted final price; budget is not enough |
| Rental request | commercially eligible after acceptance, not yet finance-enabled | rental revenue and deposit principal separated from accepted snapshots |
| Consultation request | not yet eligible | mutually accepted final price; budget is not enough |

No invoice may be created from a service or consultation budget. No rental
deposit may be posted as provider revenue.

## Event Boundaries

- invoice: created once from an eligible immutable commercial snapshot;
- payment: posted only after trusted Provider verification;
- release: moves provider payable from pending to available after the domain's
  completion/dispute window policy;
- cancellation: cancels only unpaid/unposted obligations;
- refund: returns a previously verified payment and reverses its economic
  effect exactly once;
- reversal/adjustment: corrects accounting without editing posted entries;
- settlement: reduces available provider payable only through an approved,
  traceable payout workflow.

Every future command must carry a stable idempotency key, source reference,
actor, trace metadata, amount, and `TOMAN` currency inside one database
transaction boundary.

## Compatibility

Existing Phase 9 order/payment endpoints and response shapes are unchanged.
Step 20.2 adds no Wallet balance, invoice endpoint, gateway, settlement, or
money movement. Step 20.3 will add Wallet Accounts and the Double-Entry Ledger
database/permission foundation.

## Verification

- Backend Ruff: passed
- Backend compileall: passed
- focused financial/domain tests: 53 passed
- full Backend tests: 84 passed with 16 existing UTC deprecation warnings
- Alembic: `4c9a2f20b102 (head)`
- consultation currency rows after migration: none (empty table)
- Mobile analyze: passed; 34 tests passed
- Admin analyze: passed; 14 tests passed
- health: app/database/Redis `ok`
