# Phase 24.4 — Plot, Geo Point/Boundary + Area Consistency

Verified: 2026-07-26

## Outcome

Owners can manage private plots inside each of their farms. Plot area is stored
canonically in square metres, Geo references are validated as one hierarchy,
and exact point/boundary data exists only in authenticated owner responses.

## Database contract

Alembic revision `e5a9c1b63d24`:

- adds optional positive `declared_area_sqm` to `farms`;
- adds `farm_plots` with positive `area_sqm`;
- links a plot to Province, County, District, Rural District, City, and Village
  references using restricted deletion;
- stores an optional latitude/longitude pair at seven-decimal precision;
- stores an optional closed boundary ring as JSON;
- adds active/archive consistency, coordinate range/pair, area, lifecycle,
  owner traversal, and Geo lookup contracts.

The application locks the owner Farm row before changing area allocation.
The total area of every plot, including archived plots, cannot exceed the
Farm's declared area. Archived plots still represent retained land/history and
therefore cannot be used to bypass the area limit.

## Geo and boundary validation

- lower Geo levels require explicit Province and County parents;
- Rural District also requires District;
- every selected active Geo row must belong to the selected parents;
- latitude and longitude must be supplied together and remain in valid ranges;
- a boundary has 3–499 distinct vertices plus its repeated closing vertex;
- exact coordinates and boundary data are not exposed through public routes.

Boundary capture is a user-declared management boundary, not cadastral proof.
Self-intersection/geodesic area comparison requires a dedicated geospatial
engine and is not falsely claimed in this step.

## Owner API

- `POST/GET /api/v1/farms/{farm_id}/plots`;
- `GET/PATCH /api/v1/farms/{farm_id}/plots/{plot_id}`;
- `POST /api/v1/farms/{farm_id}/plots/{plot_id}/archive`;
- `POST /api/v1/farms/{farm_id}/plots/{plot_id}/restore`.

Every Farm and Plot lookup includes authenticated ownership. Archived Farms
block Plot mutations; archived Plots are immutable until restored.

## Verification

- Ruff and compileall: passed.
- Focused Farm tests: 18 passed.
- Full Backend suite: 244 passed with 27 existing deprecation warnings.
- MySQL migration and Alembic no-drift: passed.
- OpenAPI owner Plot routes and absence of public Farm routes: passed.
- App/database/Redis health: passed.
- Mobile/Admin: unchanged in this Backend step.

## Next step

Step 24.5 — Crop Catalog, Varieties + Crop-Cycle Lifecycle.
