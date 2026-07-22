# Phase 23 Role-Based My Activity Center Release Gate

## Release

- Step: 23.11
- Tag: `v0.24.0-activity-center-foundation`
- Branch: `develop`
- Result: passed

## Verified scope

This release provides one authenticated, permission-aware Mobile Activity
Center for personal activity and four professional roles: Shop Owner, Service
Provider, Lessor, and Consultant. It includes the Seller Order workbench,
role setup and Verification journeys, deterministic multi-role composition,
Home simplification, and shared private-route session recovery.

## Gate evidence

- Backend: Ruff and compileall passed; 164 tests passed with 18 known
  deprecation warnings.
- Database: Alembic upgraded/current at `fdcb2ab80c12 (head)`; Auth seed passed
  twice at stable 12 roles and 249 permissions.
- Runtime: application, database, and Redis are `ok`; OpenAPI exposes 254 paths.
- Activity runtime: 16 required contract groups passed; nine representative
  private reads returned 401 without authentication; zero mutations performed.
- Mobile: analyze passed; 52 tests passed; Web build and Wasm dry-run passed.
- Admin: analyze passed; 17 tests passed; Web build and Wasm dry-run passed.
- Postman: all 13 collections and 313 requests parse; all 125 templated raw JSON
  bodies parse after variable normalization.
- Git: the release candidate was clean and `develop` synchronized with
  `origin/develop` before release documentation.

## Explicit operational boundary

The Runtime environment has no authenticated fixture matrix covering all four
professional roles, so this gate does not claim live Seller/Provider/Lessor/
Consultant mutations. Destination APIs remain the final authorization boundary.
External payment and notification providers, broad device/browser E2E coverage,
and production deployment hardening remain outside this foundation release.
