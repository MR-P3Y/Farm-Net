# Phase 20.7 Rental Revenue and Deposit Accounting Boundary

## Canonical Terms

Rental acceptance already produces authoritative commercial snapshots. Step
20.7 mirrors those snapshots exactly once into `finance_rental_terms`:

- `rental_revenue_amount`: lessor revenue base before future commission;
- `deposit_principal_amount`: refundable principal, never provider revenue;
- `funding_total_amount`: revenue plus deposit principal;
- pricing rule, units, unit price, payer, provider, currency, and acceptance
  time snapshots.

All values are `TOMAN`. Database checks enforce positive revenue, nonnegative
deposit, and exact component equality. Accepted amounts and identity cannot be
updated, and financial-term history cannot be deleted.

## Truthful Lifecycle

The only statuses are `unfunded`, `cancelled_unfunded`, and
`operationally_completed_unfunded`. These names deliberately do not claim
payment capture, deposit custody/release, provider balance availability,
commission, damage, penalty, refund, or settlement.

Rental acceptance creates the terms in the same transaction. Starting work
requires the terms. Pre-start cancellation marks them cancelled; operational
completion records completion but still states that funding did not occur.
Existing accepted/in-progress/completed requests with complete valid snapshots
are safely backfilled by the Migration.

No universal Invoice or ledger journal is created in this step. A future
funding workflow must debit the full funding total while crediting rental
economics and deposit liability separately. Commission may use rental revenue
only, never deposit principal.

## Verification

- Ruff/compileall: passed
- focused Rental/Finance tests: 29 passed
- full Backend: 105 passed with 16 existing UTC warnings
- Alembic: `ecba19a70b11 (head)`
- Runtime table/constraints: verified
- eligible Runtime Rental requests: 0; backfilled terms: 0
- health: app/database/Redis `ok`
- Alembic metadata: no Step 20.7 drift; four pre-existing index naming
  differences remain outside Finance/Rental
- OpenAPI/Postman: no API operation changed; canonical Rental collection parses
