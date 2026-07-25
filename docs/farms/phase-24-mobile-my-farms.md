# Phase 24.10 — Mobile My Farms, Plots, Cycles + Diary

Verified: 2026-07-26

## Outcome

Authenticated farmers now have a role-aware `مزرعه‌های من` entry from Home and
the Activity Center. The Mobile feature uses typed models, an authenticated
API adapter, repository boundary, protected routes, and explicit
loading/empty/error/refresh states.

The implemented flow covers:

- list and create Farm profiles;
- list and create Plots with canonical square-metre area and optional exact
  coordinate pair;
- list and create crop cycles using the real crop reference catalog;
- planned/active/completed/cancelled lifecycle actions;
- operation diary list/create;
- harvest list/create with friendly active mass/count unit selection;
- Plot-specific contextual Weather, alerts, and explicit refresh;
- Home and permission-aware Activity Center navigation.

The client never accepts an owner ID and does not receive private Weather
coordinates or internal Weather-location identity.

## Supporting API

The reference foundation now exposes:

`GET /api/v1/farm-references/measurement-units?dimension=mass|count`

It requires `farm_references.read`, returns only active typed reference rows,
and validates supported dimensions. This closes the discovered Mobile gap and
avoids asking farmers to enter raw database IDs.

## Verification

- Backend Ruff/compileall: passed.
- Full Backend suite: 276 passed with 27 existing warnings.
- Runtime app/database/Redis health: all `ok`.
- Alembic head: `3af106b82c79`; no new migration required.
- Measurement-unit OpenAPI path: present.
- Mobile tests: 63 passed, including 5 new Farm/Activity tests.
- Mobile Web build: passed.
- Mobile analyze: Farm code has no diagnostics. The repository still reports
  7 non-fatal `withOpacity` deprecation infos in an existing shared glass card
  and concurrently edited Auth screen; these files were not changed for this
  step.

## Deliberate boundaries

This step does not add polygon map editing, offline synchronization, Farm
media upload UI, soil/water/lab editing UI, or Admin support. These remain
separate product work rather than being hidden behind incomplete controls.

## Next step

Step 24.11 — Activity Center + Restricted Admin Support.
