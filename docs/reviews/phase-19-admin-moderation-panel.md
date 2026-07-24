# Phase 19.8 — Admin Review/Report Moderation Panel

## Delivered

- Added typed Admin Review, report, moderation-log, and pagination models.
- Added authenticated API/repository/state pipeline without raw JSON in UI.
- Added a permission-guarded `/reviews` Admin route and permission-aware
  sidebar entry.
- Reviews tab supports status filter, pagination, body/score/subject display,
  hide, restore, terminal delete, and moderation timeline.
- Reports tab supports status filter, pagination, governed reason/description,
  reviewed, resolved, and dismissed actions.
- Every mutation requires a non-empty moderation/resolution note.
- Terminal actions are disabled in the UI and Backend remains authoritative.
- Loading, saving, empty, API-error, refresh, and disabled-action states are
  explicit.

Permissions remain separated:

- `reviews.admin_read` guards the page and Review/log reads.
- `reviews.admin_moderate` is enforced by the Backend for Review mutations.
- `review_reports.admin_read` and `review_reports.admin_resolve` remain enforced
  for report data and resolution.

## Verification

| Check | Result |
| --- | --- |
| Admin Flutter analyze | OK |
| Admin Flutter tests | 20 passed |
| Focused Review model tests | 4 passed |
| Admin Flutter Web build | OK |
| Wasm dry run | OK |
| Runtime health | app/database/Redis `ok` |
| OpenAPI | 264 paths; five Admin Review route groups |

Generated Web output is ignored and not committed. Cross-domain runtime
hardening remains Step 19.9.
