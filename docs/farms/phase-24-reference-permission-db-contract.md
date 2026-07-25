# Phase 24.2 — Crop/Measurement References, Permissions + DB Contract

Verified: 2026-07-25
Branch: `develop`

## Outcome

The first executable Farm Management foundation is complete. It introduces
only shared agricultural references and access-control contracts; owner farms,
plots, crop cycles, APIs, Mobile, Admin, AI, and public discovery remain outside
this step.

## Database contract

Alembic revision `c3e7a9f41b02` adds:

- `farm_measurement_units`;
- `farm_crop_categories`;
- `farm_crops`;
- `farm_crop_varieties`.

The contract includes positive conversion factors, annual/perennial crop-cycle
types, unique crop codes and scientific names, category/crop foreign keys with
restricted deletion, per-crop variety-code uniqueness, active/sort fields, and
indexes for reference listing.

Area conversion is explicit: square metre is the canonical area base and one
hectare equals 10,000 square metres. These references contain no money fields;
the project-wide financial currency remains TOMAN.

## Seed contract

`python scripts/seed_farms.py` idempotently maintains:

- 8 measurement units across area, mass, volume, length, and count;
- 7 crop categories;
- 13 initial common crops.

No varieties were guessed or seeded. Varieties require later curated
management because cultivar names and applicability need authoritative
agronomic review.

## Permission contract

The Auth seed now defines:

- `farms.read_own` and `farms.manage_own` for owner-derived Farm access;
- `farms.admin_read` and `farms.admin_manage` for explicit administrative
  support;
- `farm_references.read` and `farm_references.manage` for the shared catalog.

The normal user role receives only own-farm and reference-read permissions.
The content manager may maintain references. The admin role receives explicit
farm administrative and reference-management permissions. These permissions
do not create an API and do not bypass future ownership checks.

## Verification evidence

- Ruff: passed for all Backend app, scripts, and Alembic sources.
- Compileall: passed for Backend app and scripts.
- Focused tests: 4 passed.
- Full Backend tests: 230 passed, with 27 existing deprecation warnings.
- Alembic: one head (`c3e7a9f41b02`), upgrade passed, no model drift detected.
- Auth seed: ran twice; 12 roles and 263 permissions both times.
- Farm reference seed: ran twice; 8 units, 7 categories, and 13 crops both
  times.
- Runtime health: app, MySQL database, and Redis all reported `ok`.
- Mobile/Admin: not run because this step contains no client changes.

The first local Backend container was stale and lacked the already-locked
Prometheus dependency. It was rebuilt from the current repository; this was an
environment repair, not a product-source change.

## Next step

Step 24.3 — Owner-Scoped Farm CRUD + Archive Lifecycle.

That step must derive `owner_user_id` from the authenticated session, prevent
cross-user reads and mutations, support multiple farms per user, validate
private farm fields, and archive rather than destructively delete records.
