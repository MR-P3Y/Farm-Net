# Phase 18 Search/Filters/Discovery Release Gate

## Release

- Step: 18.12
- Tag: `v0.23.0-search-discovery-foundation`
- Branch: `develop`
- Result: passed

## Verified scope

This release provides one shared public discovery engine across Product, Store,
Service, Rental Equipment, Consultant, and Social Post domains. It includes
shared Persian/Arabic normalization, typed domain providers, governed filters
and sorts, grouped cross-domain results, safe internal routes, the Mobile
Discovery Hub, privacy headers, a bounded response budget, and rate limiting.

## Gate evidence

- Backend: Ruff and compileall passed; 164 tests passed with 18 known
  deprecation warnings.
- Database: Alembic upgraded/current at `fdcb2ab80c12 (head)`; Auth seed passed
  twice at stable 12 roles and 249 permissions.
- Runtime: application, database, and Redis are `ok`; OpenAPI exposes 254 paths.
- Search runtime: all six providers executed; seven positive searches, four
  negative contracts, result ordering/totals, safe routes, privacy exclusion,
  `TOMAN`, `no-store`, and `noindex` checks passed.
- Mobile: analyze passed; 40 tests passed; Web build and Wasm dry-run passed.
- Admin: analyze passed; 17 tests passed; Web build and Wasm dry-run passed.
- Postman: all 13 collections and 313 current requests parse; Search contains
  12 requests and every raw Search body parses as JSON.
- Git: the release candidate was clean and `develop` synchronized with
  `origin/develop` before release documentation.

## Explicit operational boundary

The Runtime database currently has zero matching public rows across all six
Search domains. The gate therefore proves real provider SQL execution, response
shape, privacy, validation, and empty-state behavior, while populated-result
contracts remain covered by typed Backend and Mobile tests. Ranking is grouped
per domain and is not a global relevance comparison. Text matching remains
database scan based, and the in-memory limiter is per Backend process; an
external Search engine and distributed limiter remain evidence-driven future
production work.
