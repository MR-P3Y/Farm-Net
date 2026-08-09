# Mobile localized date selection and Farm map layers

Implemented: 2026-08-02

Status: completed and regression-verified on 2026-08-02; manually accepted on
2026-08-09

## Date-selection audit

A repository-wide Flutter audit found ten direct Material Date Picker calls
and no direct Date Picker in the Admin client:

- Farm Toolbox: two;
- Farm crop-cycle creation: two;
- Service request scheduling: one;
- Rental request scheduling: one;
- Rental availability create/edit: four.

All ten Mobile call sites now use `showLocalizedDatePicker` from
`mobile/lib/core/utils/dates.dart`. No feature is allowed to invoke the
Gregorian-only Material picker directly.

For Persian locale, the common entry point uses a `JalaliCalendarDelegate` for
real Solar Hijri month lengths, leap years, Saturday-first weeks, year/month
navigation, Persian digits, accessibility labels, and typed date input. It
returns a normal Gregorian `DateTime`, preserving every existing API and
database ISO-date contract. English locale keeps Flutter's standard Gregorian
calendar.

Existing user-facing Mobile date formatting already routes through
`formatDate`/`formatLocalizedDate` and remains Jalali in Persian and Gregorian
in English. The audit also found two Admin read-only raw `DateTime.toString`
renderings; they are not date selectors and remain a separate Admin display
localization follow-up.

## Farm map layers

Both Farm map surfaces now share `FarmMapStyle`, `FarmMapTiles`,
`FarmMapAttribution`, and `FarmMapLayerToggle`:

- Street: OpenStreetMap raster tiles;
- Satellite: ArcGIS World Imagery raster tiles;
- Plot creation defaults to Satellite;
- Farm Plot overview defaults to Street;
- Persian and English controls are localized;
- the active Provider credit is permanently visible.

Build-time overrides:

```text
MAP_TILE_URL
MAP_USER_AGENT
MAP_SATELLITE_TILE_URL
MAP_SATELLITE_ATTRIBUTION
```

The satellite URL is Provider-replaceable without source edits. If a future
Provider uses a client token, it must be a public, domain/application-restricted
token; unrestricted secrets must not be compiled into Flutter.

Remote map Providers inherently receive requests for tiles in the visible
viewport. Saved Plot coordinates and boundary geometry continue to use only
the authenticated owner-scoped Farm API. Neither layer is offered for offline
bulk download or represented as legal/cadastral imagery.

## Verification

- `flutter analyze`: passed with no diagnostics.
- Full Mobile suite: all 133 tests passed.
- Focused Jalali conversion, parsing, picker-widget, and locale tests: passed.
- Focused Street/Satellite source, attribution, toggle, and locale tests:
  passed.
- Flutter Web release build and automatic Wasm dry run: passed.
- Android debug APK build: passed with `setupDebugApiReverse` explicitly
  excluded so no running device mapping was changed.
- Live OpenStreetMap and ArcGIS World Imagery tile probes returned HTTP 200.
- No phone, emulator, Chrome, Backend, or database process was stopped,
  restarted, replaced, or reconfigured.
- On 2026-08-09, the owner confirmed the listed real-phone, emulator, and
  Chrome manual checks for localized date selection and Farm map layers.
