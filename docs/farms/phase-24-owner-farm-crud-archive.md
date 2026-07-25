# Phase 24.3 — Owner-Scoped Farm CRUD + Archive Lifecycle

Verified: 2026-07-25

## Outcome

Authenticated users can create and manage multiple private farm profiles.
Farm ownership is always derived from the authenticated user and is never
accepted from request data. No public Farm endpoint was introduced.

## Data contract

Alembic revision `d4f8b0a52c13` adds `farms` with:

- immutable owner reference to `auth_users`;
- normalized name and optional private description;
- `active` or `archived` lifecycle status;
- archive timestamp and optional reason;
- creation and update timestamps;
- database checks that keep archive state internally consistent;
- owner/status/update indexing for private paginated lists.

There is no destructive-delete operation. Archived farms retain their identity
for future plots, crop cycles, operations, tests, media, and AI audit history.

Geo hierarchy, area, coordinates, and boundaries intentionally remain in Step
24.4 so their consistency rules are implemented together rather than as
partially validated fields.

## API contract

All paths require the established Farm permissions:

- `POST /api/v1/farms`;
- `GET /api/v1/farms`;
- `GET /api/v1/farms/{farm_id}`;
- `PATCH /api/v1/farms/{farm_id}`;
- `POST /api/v1/farms/{farm_id}/archive`;
- `POST /api/v1/farms/{farm_id}/restore`.

The list is paginated, excludes archived farms by default, and accepts
`include_archived=true` for the owner. Archived farms cannot be edited until
restored. Repeated invalid transitions return conflict responses.

A repository lookup always includes both farm ID and authenticated owner ID.
A cross-user request is deliberately indistinguishable from a missing farm and
returns `FARM_NOT_FOUND` with HTTP 404.

Owner responses do not expose `owner_user_id`; ownership is already established
by the authenticated route. Capability flags tell clients whether edit,
archive, or restore is currently valid.

## Verification

- Ruff: passed.
- Compileall: passed.
- Farm-focused tests: 10 passed.
- Full Backend suite: 236 passed with 27 pre-existing deprecation warnings.
- Alembic head: `d4f8b0a52c13`.
- MySQL upgrade and Alembic no-drift check: passed.
- OpenAPI contains the four owner-only Farm path shapes and no public Farm
  route.
- Health: app, database, and Redis are `ok`.
- Mobile/Admin were not changed in this Backend step.

## Next step

Step 24.4 — Plot, Geo Point/Boundary + Area Consistency.
