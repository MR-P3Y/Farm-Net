# Phase 16.3 — Categories + Lessor Profile APIs

## Completed

- Added public active Rental category discovery and protected Admin
  list/create/update with search, ordering, hierarchy cycle prevention, parent
  clearing, activation, and equipment/child usage counts.
- Added an idempotent, non-destructive eight-category agricultural equipment
  seed. Existing Admin values are never overwritten.
- Added owner-scoped lessor profile get/save/submit contracts.
- Added Admin lessor list/filter/search/pagination and controlled moderation.
- Required an approved `lessor` Verification Request before Admin approval;
  rejection and suspension require an explanatory Admin note.
- Added API documentation and a parse-valid nine-request Postman collection.

## Verification

```text
Ruff: OK
compileall: OK
focused Rental tests: 5 passed
full Backend tests: 64 passed, 16 existing datetime.utcnow warnings
Rental seed twice: total=8
Runtime OpenAPI Rental paths: 7
Unauthenticated owner profile: 401
Health: app=ok, database=ok, redis=ok
Postman JSON: 9 requests, parse OK
```

Equipment listing, media, pricing, availability, requests, notifications, and
all client UI remain in later authorized steps.
