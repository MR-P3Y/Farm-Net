# Phase 12.3 — Services Category Contract Hardening

## Completed

- Full ancestor traversal rejects direct and indirect hierarchy cycles.
- Explicit `parent_id: null` moves a category to the root.
- Default seed creates missing categories but never overwrites Admin title,
  description, order, hierarchy, or active state.
- Added an idempotent Windows/Docker-ready `seed_services.py` entry point.
- Admin category responses and typed UI expose direct children, provider links,
  offers, and requests usage counts.
- Admin category dialog now supports selecting or clearing the parent.
- Postman update request verifies the parent-clear contract.

No table or migration was required; the existing Services category schema was
already capable of representing the hardened contract.

## Verification

```text
Backend Ruff/compileall: OK
Backend tests: 55 passed
Admin analyze: OK
Admin tests: 9 passed
Admin Web build/Wasm dry run: OK
Service seed first/repeat run: 8/8, OK
Runtime active Services categories: 8
Health app/database/redis: OK
OpenAPI category list/create/update: OK
Postman JSON parse: OK
```
