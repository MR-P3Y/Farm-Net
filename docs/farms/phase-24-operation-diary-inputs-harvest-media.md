# Phase 24.7 — Operation Diary, Inputs, Harvest + Farm Media

Verified: 2026-07-26

## Outcome

Farm owners can retain an immutable operational diary inside an active crop
cycle. The diary records dated field operations, the measured inputs used by
an operation, harvest observations, and private media attached to a cycle,
operation, or harvest.

Alembic revision `18dcf4e96057` adds:

- `farm_operations`;
- `farm_operation_inputs`;
- `farm_harvest_observations`;
- `farm_record_media`.

## Contracts

- New diary records can only be added while the owner-scoped crop cycle is
  active. Completed and cancelled history is not rewritten.
- Operation and harvest dates cannot precede the actual cycle start date.
- Input and harvest quantities must be positive and reference an active shared
  measurement unit.
- Harvest units are limited to the `mass` and `count` dimensions.
- A media link has exactly one subject: cycle, operation, or harvest.
- Linked media must be active, private, owned by the authenticated user, and
  uploaded with the `farm_record` purpose.
- Duplicate attachment to the same subject is rejected.
- There is no public Farm diary route and no cost/payment field in this step.

## API

- `POST/GET /api/v1/farms/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/operations`
- `POST /api/v1/farms/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/operations/{operation_id}/inputs`
- `POST/GET /api/v1/farms/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/harvests`
- `POST/GET /api/v1/farms/{farm_id}/plots/{plot_id}/cycles/{cycle_id}/media`

Read routes require `farms.read_own`; writes require `farms.manage_own`.
Ownership is derived from the authenticated user through the complete
Farm/Plot/Cycle chain.

## Verification

- Ruff and compileall: passed.
- Focused diary tests: 5 passed; all focused Farm tests: 33 passed.
- Full Backend suite: 259 passed with 27 existing deprecation warnings.
- MySQL migration and Alembic no-drift: passed at `18dcf4e96057`.
- Fresh Backend image and container: healthy.
- Runtime `/health`: app/database/Redis all `ok`.
- OpenAPI: all 4 private diary path templates present.

## Next step

Step 24.8 — Privacy, Concurrency, Audit + Retention Hardening.
