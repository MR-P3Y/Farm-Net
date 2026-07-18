# Phase 16.2 — Rental DB + Permission Foundation

## Implemented

- Added an independent `rentals` Backend domain with explicit lifecycle,
  operator-mode, pricing-unit, availability, and request-status enums.
- Added eight tables at Alembic revision `104ae669cc1a`:
  - `rental_categories`
  - `rental_lessor_profiles`
  - `rental_equipment`
  - `rental_equipment_media`
  - `rental_pricing_rules`
  - `rental_availability_blocks`
  - `rental_requests`
  - `rental_request_status_logs`
- Added ownership and moderation foreign keys, non-destructive category
  hierarchy, unique lessor/slug and equipment/media/pricing identities, valid
  date-range and positive-price/unit checks, overlap-query indexes, immutable
  commercial snapshot columns, and unique status-log event keys.
- Expanded the four Rental placeholders into 24 requester, lessor, and Admin
  permissions. The `user`, `lessor`, and `admin` default roles receive only
  their appropriate operations; Super Admin continues to receive all active
  permissions through the established seed behavior.
- Kept Rental tables independent from Product stock, Services offers, and
  order-only invoice/payment tables.

## Runtime verification

```text
Ruff: OK
compileall: OK
focused Rental tests: 3 passed
full Backend tests: 62 passed, 16 existing datetime.utcnow warnings
Alembic upgrade/current: 104ae669cc1a (head)
Rental tables: 8/8
Auth seed twice: 12 roles, 241 permissions
Rental permissions: 24
Health: app=ok, database=ok, redis=ok
```

## Existing migration drift

`alembic check` reports four pre-existing redundant MySQL indexes named
`user_id`/`code` on Consultant and Services tables. Autogeneration initially
attempted to remove them, but those unrelated operations were intentionally
removed from the Rental migration. No existing index or table was changed.
This baseline drift must be handled as an explicit compatibility cleanup before
the Phase 16 release gate rather than hidden inside this foundation migration.

## Deferred to Step 16.3+

No API, seed taxonomy, notification, Mobile screen, or Admin screen is added in
this step. Category and lessor-profile behavior begins in Step 16.3.
