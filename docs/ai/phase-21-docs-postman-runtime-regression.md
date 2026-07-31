# Phase 21.15 — Docs, Postman + Runtime Regression

Status: completed

## Delivered

- Added the authoritative Barzegar API contract:
  `docs/api/ai-barzegar.md`.
- Updated the module roadmap, database table register, Permission register,
  API index, and Postman collection index to match runtime state.
- Added a deterministic generator and a secret-free Barzegar Postman
  collection.
- Added contract tests that require exact Postman/OpenAPI operation parity,
  parse every JSON request body, reject credential patterns, and require every
  runtime path and core safety boundary in the API document.

## Contract inventory

- Farmer Barzegar operations: 16.
- Admin Barzegar operations: 14.
- Total OpenAPI/Postman operations: 30.
- Runtime AI tables: 28.
- Postman collections in repository: 17.
- Total Postman requests: 427.

The Postman collection uses separate owner and Admin token variables. It
contains no OpenAI key, Provider credential, Super Admin password, or live
mutation token.

## Runtime regression

| Area | Result |
| --- | --- |
| Health | app/database/Redis `ok` |
| Qdrant | `/healthz` returned 200 |
| Alembic | current/head `l21h9f6d2130`; no drift |
| AI database tables | 28 |
| OpenAPI | 30 Barzegar operations |
| Unauthenticated privacy boundary | 30/30 operations returned 401 |
| Prometheus | 6/6 expected AI metric families present |
| Provider flag | `false` |
| Postman | 17 collections / 427 requests; JSON parse OK |
| Backend | Ruff/compileall OK; 381 tests passed |
| Mobile | analyze OK; 72 tests; Web/Wasm build OK |
| Admin | analyze OK; 30 tests; Web/Wasm build OK |

No authenticated mutation was performed during Runtime regression. Live OpenAI
generation was intentionally not exercised because billing is not active and
`AI_PROVIDER_ENABLED=false`.

Next: Step 21.16 — Barzegar Release Gate + Tag.
