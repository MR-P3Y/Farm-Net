# Phase 24.12 — Docs, Postman + Runtime Regression

Status: completed on 2026-07-25.

## Delivered

- Added the authoritative Farm API overview and linked it from the API index.
- Added a deterministic generator and a parseable Postman collection containing
  42 requests: all 41 Farm/Admin Farm operations plus measurement units.
- Added a read-only Runtime regression for health, OpenAPI coverage, and six
  representative unauthenticated privacy boundaries.

## Final verification

| Area | Result |
| --- | --- |
| Alembic | `3af106b82c79 (head)` |
| Auth seed | idempotent twice; 12 roles / 263 permissions |
| Runtime | app/database/Redis `ok` |
| Farm OpenAPI | 41 operations |
| Private reads | six representative routes returned 401 |
| Backend | Ruff/compileall OK; 278 tests passed |
| Mobile | 63 tests and Web/Wasm build passed |
| Admin | clean analyze; 24 tests and Web/Wasm build passed |
| Farm Postman | 42 requests; JSON parse and OpenAPI coverage passed |
| All Postman | 16 collections / 398 requests parsed |

Mobile analyze passed with `--no-fatal-infos`; seven pre-existing
`withOpacity` deprecation infos remain in user-owned concurrent UI changes.
The existing container image rebuild exceeded the command time budget, so the
fresh Runtime regression was executed from the current source on port 8001
against the same MySQL and Redis services. No authenticated mutation was
performed.

Next: Step 24.13 Release Gate + Tag.
