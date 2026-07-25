# Phase 24.6 — Soil, Water, Irrigation + Laboratory Observations

Verified: 2026-07-26

## Outcome

Owners can maintain one soil profile and one irrigation profile per Plot,
multiple retained water sources per Farm, and immutable dated laboratory
observations for soil or water.

Alembic revision `07cbe3d85f46` adds:

- `farm_soil_profiles`;
- `farm_water_sources`;
- `farm_irrigation_profiles`;
- `farm_lab_observations`.

Soil texture/depth, water-source type/lifecycle, irrigation method/efficiency,
and exact-one lab subject are database constrained. Water sources archive
without destructive deletion.

Laboratory metrics use canonical units: pH (`ph`), electrical conductivity
(`ds_m`), percentages (`percent`), soil nutrients (`mg_kg`), water TDS
(`mg_l`), and SAR (`ratio`). Metric/subject compatibility is validated.
Sampling/testing dates are ordered and values cannot be negative.

These records are owner-private observations. They do not produce automatic
fertilizer, pesticide, irrigation, medical, legal, or financial advice.

## Verification

- Ruff/compileall: passed.
- Focused Farm tests: 28 passed.
- Full Backend suite: 254 passed with 27 existing warnings.
- MySQL migration, rollback/upgrade replay, and Alembic no-drift: passed.
- OpenAPI private environment routes and no public Farm route: passed.
- App/database/Redis health: passed.

## Next step

Step 24.7 — Operation Diary, Inputs, Harvest + Farm Media.
