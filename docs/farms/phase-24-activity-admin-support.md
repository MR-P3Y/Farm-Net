# Phase 24.11 — Activity Center + Restricted Admin Support

Status: completed on 2026-07-25.

## Delivered

- Reused the permission-aware Mobile Activity Center entry delivered in 24.10.
- Added read-only Admin APIs for paginated Farm lookup, restricted detail, and
  audit history.
- Added a typed Admin panel page with search, status filter, pagination,
  Farm/Plot/Cycle summaries, and audit history.
- Protected Backend and Admin navigation with `farms.admin_read`.
- Exposed no mutation action and no ownership-transfer workflow.

## Privacy boundary

The support contract deliberately excludes exact coordinates, Plot boundary,
soil/water laboratory values, diary notes, media/storage references, and other
private agronomic content. It exposes only the minimum identity, lifecycle,
count, administrative-area, crop-cycle, and audit fields needed for support.

## Verification

- Backend Ruff and compileall: passed.
- Backend focused tests: 2 passed.
- Backend full suite: 278 passed (27 pre-existing deprecation warnings).
- Admin `flutter analyze --no-pub`: passed.
- Admin tests: 24 passed.
- Admin Web build: passed, including the WebAssembly dry run.

Next: Step 24.12 Docs/Postman + Runtime Regression.
