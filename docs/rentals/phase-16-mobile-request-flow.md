# Phase 16.9 — Mobile Rental Request Flow

## Completed

- Added typed availability, request create/list/detail, commercial snapshot,
  and exact status-log models.
- Added availability preflight, active pricing selection, date/time range,
  requested units, operator derivation, delivery address, and requester note.
- Added request create, requester list/detail, refresh, Timeline, status labels,
  and cancellation for `pending`/`accepted` with a required reason.
- Added detail-to-request navigation, requester routes, and a Home entry.
- Preserved Backend as the authority for ownership, minimum units, operator
  compatibility, overlap prevention, and transition validity.

## Verification

```text
dart format: OK
flutter analyze --no-pub: OK
flutter test --no-pub: 32 passed
flutter build web --no-pub: OK
Wasm dry run: OK
```
