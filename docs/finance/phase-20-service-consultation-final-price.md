# Phase 20.6 Services and Consultation Final-Price Contracts

## Contract Boundary

`budget_amount` remains an optional planning value and can never create an
Invoice. A provider or consultant must first accept the operational request,
then create a positive `TOMAN` final-price proposal with a scope description.
Only the owning requester can accept or reject it.

Proposals are versioned and retained. A new proposal supersedes the previous
active proposal. Database constraints allow at most one active and one accepted
proposal per source, and an accepted proposal cannot be changed or deleted.

## Billing Gate

Acceptance creates exactly one universal Invoice, one immutable line-item
snapshot, and one immutable commission snapshot. The commission percent comes
only from the active default policy for the exact source domain. The operation
fails closed if that policy is absent; no percent is inferred from product
orders, budgets, offer prices, or planning documentation.

Work cannot enter `in_progress` until the final price is accepted. Cancelling
an unpaid request cancels its payment-pending Invoice and supersedes any active
proposal. A paid contract cannot be cancelled through these operational
endpoints; future payment/refund orchestration must handle it.

## Ownership APIs

Services and Consultations each expose provider/consultant `POST` and `GET`
under `/requests/assigned/{request_id}/final-price`, plus requester `GET` and
`PATCH` under `/requests/{request_id}/final-price`. Existing permissions and
real request ownership are enforced. No Admin, Mobile, or payment-provider
behavior was added in this step.

## Runtime Evidence

- Ruff and compileall: passed
- focused final-price/domain tests: 26 passed
- full Backend: 98 passed with 16 existing UTC warnings
- Alembic: `b9c8d6e40808 (head)`
- Runtime: proposal table and all unique/check constraints present
- OpenAPI: four path templates and eight operations
- health: app/database/Redis `ok`
- Postman: Services and Consultants collections parse successfully
- Runtime data: zero proposals, zero domain invoices, and zero Service/
  Consultation policies; therefore no real-row acceptance smoke was possible

Before a real acceptance can succeed, an administrator must configure active
default `service_request` and/or `consultation_request` commission policies in
a later Commission Policy management step.
