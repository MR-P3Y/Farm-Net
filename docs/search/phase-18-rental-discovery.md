# Phase 18.5 — Equipment Rental Discovery Hardening

## Outcome

Rental Equipment is connected to the shared search engine while the existing
public Rental endpoint remains backward compatible.

## Contracts

- Visibility remains approved, active, non-deleted equipment owned by an
  approved, non-deleted lessor.
- Persian-normalized matching covers equipment title, slug, description,
  manufacturer, model, lessor display name, and category title.
- Category filtering includes active descendants.
- Price filtering uses the minimum active `TOMAN` pricing rule. No price is
  invented when an active rule is absent.
- Availability requires a complete valid interval and excludes overlap with
  explicit availability blocks or accepted/in-progress Rental requests.
- Sort values are allow-listed: `relevance`, `newest`, `price_asc`, and
  `price_desc`. Null prices sort last.

## Client and verification

The typed Mobile API and Repository forward price, availability, and sort
parameters. The Rental Postman collection includes a representative hardened
public discovery request. Verification evidence is recorded in the Step 18.5
entry of `docs/PROJECT_PROGRESS.md`.
