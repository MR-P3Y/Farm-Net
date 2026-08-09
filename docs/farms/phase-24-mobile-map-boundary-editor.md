# Phase 24 — Mobile Plot Map + Boundary Editor

Implemented: 2026-08-02

Status: completed and manually accepted on 2026-08-02; controlled place-search
follow-up completed and accepted on 2026-08-10

## Outcome

The Farm detail journey now lets an owner create a Plot without typing raw
latitude or longitude. The creation flow is split into three short steps:

1. choose the Plot location from the map or the device's current location;
2. mark the Plot corners on the map and review the calculated area;
3. enter the Plot name and optional description, then save.

The Farm detail surface can switch between a Plot list and a map. Existing
Plots with a declared point or boundary appear on the map and remain linked to
their detail journey.

## Interaction contract

- A fixed centre marker makes location selection usable with one-finger map
  panning and avoids asking non-technical users for coordinates.
- Device-location access is explicit and permission-aware on supported Mobile
  and browser platforms.
- Boundary points are numbered. Tapping a point removes it; undo and clear are
  available before saving.
- At least three distinct points are required for a boundary. A
  self-intersecting boundary is rejected by the client.
- The client closes the boundary ring before submission and keeps seven-decimal
  coordinate precision, matching the existing Backend contract.
- Boundary area is calculated locally and submitted in canonical square
  metres. A point-only Plot remains possible and asks for the known area rather
  than inventing it.
- The declared boundary is a farm-management sketch and is not presented as a
  cadastral or legal survey.

## Map and privacy contract

- The tile URL and application user agent are configurable with
  `MAP_TILE_URL` and `MAP_USER_AGENT` build-time values.
- Both map surfaces expose a shared Street/Satellite switch. Plot creation
  starts with satellite imagery because field boundaries are easier to
  recognize, while the Farm overview starts with the street layer.
- The street layer uses OpenStreetMap. The satellite layer uses ArcGIS World
  Imagery and can be replaced with `MAP_SATELLITE_TILE_URL`; its visible credit
  can be replaced with `MAP_SATELLITE_ATTRIBUTION`.
- Provider attribution stays visibly rendered over the map for both layers.
- Plot creation also exposes one compact search action. It searches only after
  explicit submit, shows OpenStreetMap attribution, moves the existing map to
  the selected result, and keeps manual pan/GPS selection available.
- Exact Plot points and boundaries continue through authenticated owner-scoped
  Farm APIs only; no public Farm route was introduced.
- Search and reverse geocoding go through authenticated Backend routes. The
  external provider receives only the submitted query or selected coordinate;
  the app performs no hidden autocomplete requests.
- As with every remote tile layer, the selected Provider receives ordinary
  tile requests for the visible viewport. Exact saved Plot geometry is still
  sent only to the authenticated Farm API.

## Deliberate boundaries

This map step does not include offline tile packs, boundary dragging, or
cadastral import. Satellite imagery is a visual positioning aid and is not
represented as current survey-grade or cadastral evidence. The public
Nominatim default is a replaceable development/low-volume provider boundary,
not a promise of unrestricted production capacity.

## Verification

- `flutter analyze`: passed with no diagnostics.
- Full Mobile tests: 133 passed after the shared Jalali picker and
  Street/Satellite layer addition.
- Focused Farm model/geometry tests: 8 passed.
- Focused Street/Satellite source, attribution, toggle, and locale tests:
  passed.
- OpenStreetMap and ArcGIS World Imagery live tile probes returned HTTP 200.
- Flutter Web release build and Wasm dry run: passed.
- Android debug APK build: passed.
- Existing real-phone connection and API reverse remained active.
- Runtime API health returned `ok`; the existing Chrome Web app returned HTTP
  200.
- No existing phone, emulator, Chrome, Backend, or database process was stopped,
  restarted, installed over, or reconfigured.

## Acceptance

The code, build gates, and project-owner manual review are complete. On
2026-08-02, the owner confirmed the manual map and Plot-creation checks passed.
No Codex-controlled restart, replacement, or reconfiguration of an existing
phone, emulator, Chrome, Backend, or database session was performed.
