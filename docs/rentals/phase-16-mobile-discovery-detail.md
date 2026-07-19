# Phase 16.8 — Mobile Equipment Discovery + Detail

## Completed

- Added typed Rental category, equipment, media, and pricing contracts.
- Added public API/Repository integration and Riverpod discovery/detail state.
- Added search and category, province/city, and operator-mode filters.
- Added list cards, media gallery, lessor summary, equipment facts, deposit,
  delivery terms, and active pricing presentation.
- Added loading, filtering, empty, error/retry, pull-to-refresh, Home navigation,
  and detail routing.
- Added model coverage for decimal strings, primary media, operator labels, and
  pricing units.

## Explicit boundaries

- Price-range filtering is absent because Backend does not support it.
- Request creation, date selection, availability submission, and requester
  history are Step 16.9, not incomplete behavior hidden inside this step.

## Verification

```text
dart format: OK
flutter analyze --no-pub: OK
flutter test --no-pub: 30 passed
flutter build web --no-pub: OK
Wasm dry run: OK
```
