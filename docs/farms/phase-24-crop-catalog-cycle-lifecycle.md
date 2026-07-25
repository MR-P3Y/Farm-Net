# Phase 24.5 — Crop Catalog, Varieties + Crop-Cycle Lifecycle

Verified: 2026-07-26

## Outcome

Authenticated farmers can read the curated crop catalog and attach dated crop
cycles to their own plots. Crop/variety references are validated and lifecycle
history is retained.

## Reference API

- `GET /api/v1/farm-references/crop-categories`;
- `GET /api/v1/farm-references/crops`;
- `GET /api/v1/farm-references/crops/{crop_id}/varieties`.

These routes require `farm_references.read`. Only active references are
returned. A selected variety must belong to the selected crop. The initial
seed intentionally contains no guessed varieties; future curated varieties can
be added through the restricted management boundary.

## Crop-cycle contract

Alembic revision `f6bad2c74e35` adds `farm_crop_cycles` with:

- owner traversal through Plot and Farm;
- crop and optional variety references;
- planned and actual start/end dates;
- `planned`, `active`, `completed`, and `cancelled` states;
- `single` or explicit `intercrop` cultivation mode;
- database checks for ordered dates and lifecycle/date consistency.

Only planned cycles are editable. Valid transitions are planned to active,
active to completed, and planned/active to cancelled.

Overlapping planned/active cycles are rejected unless the new cycle and every
conflicting cycle explicitly use `intercrop`. Plot/Farm rows are locked during
mutation to prevent owner or lifecycle races.

## Owner API

- create/list cycles under an owned Plot;
- read/update one owned cycle;
- start, complete, or cancel through explicit transition endpoints.

Cross-owner access is indistinguishable from missing data. No public Farm,
Plot, or cycle endpoint exists.

## Verification

- Ruff and compileall: passed.
- Farm-focused tests: 24 passed.
- Full Backend suite: 250 passed with 27 existing warnings.
- MySQL migration and Alembic no-drift: passed.
- OpenAPI privacy/reference/lifecycle routes: passed.
- App/database/Redis health: passed.
- Mobile/Admin: unchanged.

## Next step

Step 24.6 — Soil, Water, Irrigation + Laboratory Observations.
