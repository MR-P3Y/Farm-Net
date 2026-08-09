# Farm Plot Controlled Location Search

Implemented: 2026-08-10

Status: completed, runtime-verified, and accepted by the project owner on
2026-08-10

## Outcome

Farmers can now find a Province, city, village, or named place without typing
latitude or longitude. A result moves the existing Street/Satellite map to the
point; the normal centre-marker, GPS, and boundary editor remain the source of
the final geometry.

The Backend attempts to match the Provider address to active Farm-Net Geo
records. An unambiguous match supplies the existing `province_id`, `county_id`,
`district_id`, `rural_district_id`, `city_id`, and `village_id` fields. Plot
responses expose a stable `location_label` derived from those internal IDs.
No schema migration was required.

## Provider and abuse contract

- `GET /api/v1/geo/search` and `GET /api/v1/geo/reverse` are private and require
  `farms.manage_own`.
- Mobile never searches while the user types. The search button or keyboard
  submit is an explicit request.
- Search defaults to Iran and returns at most five results.
- The Backend identifies the application with a configurable User-Agent,
  enforces at least 1.1 seconds between upstream requests, applies the existing
  per-client search limiter, and caches bounded responses for seven days by
  default.
- Cache keys are SHA-256 digests. API responses are `no-store`.
- The public Nominatim endpoint is configurable and can be replaced by a
  managed/self-hosted compatible service before higher-volume production use.
- OpenStreetMap attribution remains visible in the result sheet.

## Privacy and fallback

The configured external provider receives the exact submitted search text or
the selected point used for reverse lookup. Farm-Net does not write the raw
Provider payload, free-form display name, or search history to Farm tables,
logs, or analytics as part of this feature. The bounded provider cache may hold
the response for its configured TTL.

Plot storage continues to contain owner-private coordinates/boundaries and the
existing internal Geo IDs. If search or reverse lookup is disabled, rate
limited, unavailable, or cannot resolve a name, Plot creation remains usable
with the selected coordinates. Phone, emulator, and Chrome keep the shared
`http://localhost:8000/api/v1` contract; no LAN address was introduced.

## Automated evidence

- Backend provider request, country/language boundary, cache, internal hierarchy
  mapping, private OpenAPI, rate-limit, Plot label, and configuration safety
  tests are included.
- Mobile model and result-sheet tests prove that typing alone causes no request,
  explicit submit causes one request, Persian and English remain localized, and
  attribution is visible.
- The existing Street/Satellite tests remain part of the focused regression.
- Backend Ruff/compileall passed and all 408 Backend tests passed against an
  isolated in-memory test database.
- One policy-compliant, identified live Provider search returned an Iran result;
  no autocomplete or repeated high-rate request was made.
- All 138 Mobile tests passed; focused Farm analysis passed without diagnostics.
  Full analysis reports one pre-existing owner-work warning in the unrelated
  Activity Center file.
- Web release/Wasm dry run and Android debug APK build passed. The Android
  build excluded `setupDebugApiReverse`, so the active mapping was unchanged.
- Read-only runtime inspection found Backend health HTTP 200, Chrome active,
  and the real phone connected with `tcp:8000` reverse intact. The emulator was
  not present in ADB and was not launched.
- After owner approval, only `farmnet_backend` was restarted. The first startup
  exposed that the existing runtime image did not contain the test-only `httpx`
  package. The geocoder transport was moved to Python's standard library, so
  the same bind-mounted container recovered without rebuild or replacement.
  MySQL, Redis, and Qdrant retained their exact container IDs and start times.
- Runtime health is `healthy`; both paths are present in OpenAPI and return
  authenticated-boundary `401` instead of stale-route `404`. A live Provider
  call from inside the Backend container returned one Iran result.

## Manual acceptance checklist

Run without restarting or replacing an existing runtime:

1. On the real phone, emulator, and Chrome, open a Farm and start `Add Plot`.
2. Tap the compact search icon, type `قلات شیراز`, and confirm no request is
   triggered until Search is submitted.
3. Select a result and confirm the satellite/street map moves to it.
4. Continue, draw an optional boundary, save, reopen the Farm, and confirm the
   location label is retained.
5. Pan manually to another point and confirm the prior searched location is
   cleared and the manually selected coordinate still saves.
6. Repeat once in English and confirm controls/errors are English.

## Acceptance

The project owner accepted the completed Farm Plot location-search flow on
2026-08-10 after Backend activation. No phone, emulator, Chrome, database,
Redis, or Qdrant runtime was restarted, replaced, or reconfigured. Only the
explicitly approved Backend container restart was performed.
