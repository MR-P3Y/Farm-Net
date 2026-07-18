# Phase 12.5 — Consultant Specialty Usage + Admin Search Hardening

## Completed

- Added profile-link and consultation-request usage counts to typed contracts.
- Wired Backend `q` search into Admin API/repository/controller/UI.
- Added usage columns to the existing specialty management table.
- Preserved flat, non-destructive specialty lifecycle and existing permissions.
- Updated Postman to exercise `q` and `active_only` query contracts.

No migration or new permission was required. No default specialty rows were
invented: the current runtime has zero specialties and an authoritative product
taxonomy has not yet been approved.

## Verification

```text
Backend Ruff/compileall: OK
Backend tests: 59 passed
Admin analyze: OK
Admin tests: 11 passed
Admin Web build/Wasm dry run: OK
OpenAPI specialty q/active_only: OK
Health app/database/redis: OK
Runtime specialties: 0 (intentional documented data gap)
Postman JSON parse: OK
```
