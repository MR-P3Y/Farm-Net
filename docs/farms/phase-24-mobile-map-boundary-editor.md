# Phase 24 — Mobile Plot Map + Boundary Editor

Implemented: 2026-08-02

Status: completed and manually accepted on 2026-08-02

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
- The default map uses OpenStreetMap tiles and keeps visible contributor
  attribution.
- Exact Plot points and boundaries continue through authenticated owner-scoped
  Farm APIs only; no public Farm route was introduced.
- No public reverse-geocoding service or hidden location upload was added.

## Deliberate boundaries

This first map step does not yet include province/city/village text search,
satellite imagery, offline tile packs, boundary dragging, or cadastral import.
Search should be connected to a controlled Backend geocoder, and satellite
imagery requires an approved provider and key instead of a hard-coded public
endpoint.

## Verification

- `flutter analyze`: passed with no diagnostics.
- Full Mobile tests: 99 passed.
- Focused Farm model/geometry tests: 8 passed.
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
