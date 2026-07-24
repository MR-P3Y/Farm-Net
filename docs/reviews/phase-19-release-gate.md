# Phase 19 Reviews / Ratings / Reports Release Gate

## Release

- Step: 19.11
- Tag: `v0.25.0-reviews-foundation`
- Branch: `develop`
- Result: passed

## Verified scope

This release provides one shared marketplace Review engine for Product, Store,
Service Offer, Service Provider, Rental Equipment, Rental Lessor, and
Consultant subjects. Reviews require a real delivered Order or completed
Service, Rental, or Consultation Request owned by the reviewer.

The release includes owner CRUD, public privacy-safe Reviews, canonical atomic
rating aggregates, reports, Admin moderation and immutable audit logs,
exact-once notifications, Mobile creation/history/public rendering, Admin
moderation UI, and unified-search rating integration.

## Gate evidence

- Backend: Ruff and compileall passed; 186 tests passed with 18 known
  deprecation warnings.
- Database: Alembic upgraded/current at `a7c9e1f30d13 (head)`; Auth seed passed
  twice at stable 12 roles and 257 permissions.
- Runtime: application, database, and Redis are `ok`; OpenAPI exposes 264 paths
  including ten Review path groups.
- Review regression: ten required contracts, seven subject types, four source
  types, typed response references, public privacy, seven unauthenticated
  boundaries, and missing-subject 404 passed with zero mutations.
- Mobile: analyze passed; 54 tests passed; Web build and Wasm dry run passed.
- Admin: analyze passed; 20 tests passed; Web build and Wasm dry run passed.
- Postman: all 14 collections and 325 requests parse; all 130 templated raw JSON
  bodies parse after variable normalization.
- Git: the release candidate was clean, on `develop`, and synchronized with
  `origin/develop`; the release tag did not previously exist.

## Explicit operational boundary

The Runtime has no fabricated terminal source/Review/report fixture, so this
gate does not claim live authenticated Review or moderation mutations.
Eligibility, aggregate concurrency, exact-once notifications, ownership,
privacy, and moderation transitions are covered by focused tests and earlier
rollback-only smoke verification.

Broad device/browser E2E automation, fraud/abuse analytics, production external
notification providers, and production deployment hardening remain outside
this foundation release.
