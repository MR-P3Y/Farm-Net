# Phase 18.11 — Docs/Postman + Runtime Search Regression

Date: 2026-07-21

Branch: `develop`

Baseline commit: `3e79f60`

## Scope

This step adds no Search feature, database migration, permission, Mobile
behavior, or Admin behavior. It consolidates documentation, expands Postman,
adds a reusable read-only Runtime regression command, and records the full gate.

## Verified results

| Area | Result |
| --- | --- |
| Backend Ruff / compileall | OK |
| Backend pytest | OK — 164 passed; 18 known warnings |
| Alembic | OK — `fdcb2ab80c12 (head)` |
| Auth seed idempotency | OK — two runs; 12 roles / 249 permissions |
| Health | OK — app, database, Redis |
| OpenAPI | OK — 254 paths; `POST /api/v1/search` |
| Runtime Search | OK — 7 positive, 4 negative, six provider types |
| Privacy | OK — no-store/noindex, safe routes, forbidden keys absent |
| Mobile | OK — analyze, 40 tests, Web/Wasm build |
| Admin | OK — analyze, 17 tests, Web/Wasm build |
| Search Postman | OK — 12 requests / 12 raw JSON bodies |
| All Postman | OK — 13 collections / 284 requests parse |

## Runtime data boundary

All-domain and every individual provider returned total zero in the current
Runtime. The regression therefore proves live query execution, grouping,
normalization, privacy headers, empty responses, and validation errors. It does
not claim a populated real-row click-through. Populated results are covered by
typed provider and Mobile model tests.

## Release conclusion

Step 18.11 passes. Phase 18 may proceed to Step 18.12 only after a fresh clean
tree/upstream audit and complete release gate. The process-local limiter and
scan-based substring matching remain explicit production scaling boundaries.
