# Phase 18.8 — Unified Cross-Domain Search API + Ranking Boundary

## Outcome

`POST /api/v1/search` is the single public entry point for Product, Store,
Service, Rental Equipment, Consultant, and Social Post discovery.

## Boundary

- The request and response use the typed shared contracts introduced in 18.2.
- Providers execute in the caller's unique requested type order.
- Results remain grouped and independently paginated. The top-level total is a
  sum, not evidence of a comparable global relevance scale.
- Domain-inapplicable sorts fall back to that provider's safe relevance/default
  ordering; visibility and privacy stay inside each provider repository.
- No query history, personalization, suggestions, analytics, or external search
  engine is introduced.

## Verification

Focused tests cover normalization, type ordering, invalid money/duplicate types,
OpenAPI request schema, and exact registration of all six providers. Full gate
and Runtime evidence is recorded in `docs/PROJECT_PROGRESS.md`.
