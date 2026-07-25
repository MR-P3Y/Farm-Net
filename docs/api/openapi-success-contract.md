# OpenAPI Success Contract

Step 22.5 establishes a complete success-response schema boundary for every
Farm-Net OpenAPI operation without changing runtime serialization.

## Shared JSON envelope

All JSON endpoints return the established shape:

```json
{
  "success": true,
  "data": {},
  "message": "OK",
  "meta": {
    "trace_id": "..."
  }
}
```

`StandardSuccessEnvelope` documents the required `success`, `data`, `message`,
and `meta` members. `success` is constrained to `true`, `message` is a string,
and `meta.trace_id` is documented. The `data` member remains endpoint-specific
for legacy routes; newer routes with exact Pydantic response models retain
their more precise domain schema instead of being replaced by the shared
envelope.

This is intentionally an OpenAPI-only hardening layer. It does not validate,
filter, rename, or otherwise alter response bodies at runtime.

## Binary responses

These download routes are explicitly represented as
`application/octet-stream` with a binary string schema:

- `GET /api/v1/media/public/{file_key}`
- `GET /api/v1/media/private/{file_key}`
- `GET /api/v1/admin/media/private/{file_key}`

They are not described as JSON envelopes.

## Contract rules

- Every successful operation must expose at least one non-empty response
  schema.
- An exact endpoint response model always takes precedence over the shared
  envelope.
- Binary downloads must not advertise `application/json`.
- The shared envelope must match the actual `/health` runtime response.
- Mobile and Admin continue to consume the existing `data` member; this step
  changes documentation only.

## Verified baseline

On 2026-07-24:

- OpenAPI paths: 264
- OpenAPI operations: 303
- operations with a typed success schema: 303
- exact domain schemas: 22
- shared-envelope schemas: 278
- binary schemas: 3
- missing success schemas: 0
- total component schemas: 142

Backend Ruff and compileall passed. Backend tests reported 197 passed with 18
known warnings, and the independent backup-tool suite reported 8 passed.
Mobile analyze and all 54 tests passed. Admin analyze and all 20 tests passed.
Runtime application, database, and Redis health were all `ok`.
