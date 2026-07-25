# Phase 24.9 — Farm Weather Linking + Contextual Alerts

Verified: 2026-07-26

## Outcome

An authenticated owner can obtain cached current weather, forecasts, and
contextual alerts for a Plot with an exact coordinate pair. The implementation
reuses the existing Weather providers, forecast cache, alert rules, duplicate
guards, and Notification domain.

Alembic revision `3af106b82c79`:

- adds private/public ownership scope to `weather_locations`;
- keeps all existing locations public by migration default;
- adds one-to-one `farm_plot_weather_links`;
- enforces private locations having an owner and public locations having none.

## Privacy

Private Farm weather locations are excluded from all normal public Weather
location lookups, search, current-weather, forecast, and alert routes. Farm
responses do not contain latitude, longitude, internal Weather location ID, or
owner ID.

The provider receives only the coordinates needed for the weather request and
a generic private label. Farmer-facing notifications contain alert type,
severity, title, and body, but no exact location or coordinate. Private alerts
notify only the Farm owner; the public/admin Weather-alert notification fanout
is not reused.

## API

- `GET /api/v1/farms/{farm_id}/plots/{plot_id}/weather`
- `POST /api/v1/farms/{farm_id}/plots/{plot_id}/weather/refresh`
- `GET /api/v1/farms/{farm_id}/plots/{plot_id}/weather/alerts`

Read routes require `farms.read_own`; explicit refresh requires
`farms.manage_own`. A Plot without both latitude and longitude returns the
stable `FARM_WEATHER_COORDINATES_REQUIRED` validation contract.

The existing Weather TTLs remain authoritative: current weather 30 minutes and
forecast 180 minutes. A moved Plot synchronizes its private location and
forces a new refresh. Existing Weather alert rules cover frost, heat, heavy
rain, strong wind, and unsuitable spraying conditions.

Weather values and alerts are observations/decision support, not guaranteed
agricultural instructions.

## Verification

- Ruff/compileall: passed.
- Farm Weather tests: 6 passed; all focused Farm tests: 49 passed.
- Full Backend suite: 275 passed with 27 existing warnings.
- MySQL migration/no-drift: passed at `3af106b82c79`.
- Fresh Backend image/container: passed.
- Runtime app/database/Redis health: all `ok`.
- OpenAPI: all 3 owner-private Farm Weather paths present.

## Next step

Step 24.10 — Mobile My Farms, Plots, Cycles + Diary.
