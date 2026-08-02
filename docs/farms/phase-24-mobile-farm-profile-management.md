# Phase 24 — Mobile Farm Profile Management

Implemented: 2026-08-02

Status: completed and manually accepted on 2026-08-02

## Outcome

The `My Farms` journey now supports the complete existing owner lifecycle:

- create a Farm profile with a dedicated, mobile-friendly form;
- edit its name, optional description, and optional declared area;
- remove it from the active list through the Backend archive contract;
- show removed/archived Farms and restore them later.

Create and edit use one consistent full-screen form. Only the Farm name is
required. Area input accepts Persian, Arabic, and Latin digits and explains
that declared area cannot be reduced below the total retained Plot area.

## Safe removal contract

The visible action is labelled `Remove Farm` / `حذف مزرعه` for user clarity,
but it calls `POST /api/v1/farms/{farm_id}/archive`; it does not destructively
delete a retained Farm record.

Before removal, the owner sees an explicit confirmation that Plots, crop
cycles, operations, media, and history remain preserved. An optional reason
can be recorded. Removed Farms disappear from the default active list and can
be shown with the archived-Farms switch, then restored through the existing
owner-scoped restore endpoint.

The UI consumes the Backend `can_edit`, `can_archive`, and `can_restore`
capability flags instead of inferring unauthorized actions.

## API use

No Backend or database change was required. Mobile now consumes the already
released owner endpoints:

- `GET /api/v1/farms/{farm_id}`;
- `PATCH /api/v1/farms/{farm_id}`;
- `POST /api/v1/farms/{farm_id}/archive`;
- `POST /api/v1/farms/{farm_id}/restore`;
- `GET /api/v1/farms?include_archived=true`.

All requests remain authenticated and owner-scoped. No owner ID is accepted
from Mobile input.

## Verification

- `flutter analyze`: passed with no diagnostics.
- Full Mobile suite: 109 tests passed.
- Farm profile model/input tests: 9 passed.
- Farm profile widget tests: 3 passed.
- Flutter Web release build and Wasm dry run: passed.
- Android debug APK build: passed.
- No existing phone, emulator, Chrome, Backend, or database process was
  stopped, restarted, installed over, or reconfigured.

## Acceptance

The implementation, automated gates, and project-owner visual review are
complete. The project owner manually accepted the Farm create, edit, safe
remove/archive, archived-list, and restore journey on 2026-08-02.
