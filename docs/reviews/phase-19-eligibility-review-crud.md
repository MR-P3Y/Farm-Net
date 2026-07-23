# Phase 19.3 — Eligibility, Ownership, Lifecycle + Review CRUD

Date: 2026-07-23

Branch: `develop`

## Delivered

- Shared Review schemas, repository, domain eligibility service, exceptions,
  and authenticated Router.
- Create, paginated/filterable own list, own detail, active update, and
  idempotent soft delete.
- Row-lock eligibility checks across delivered Orders and completed Service,
  Rental, and Consultation Requests.
- Seven validated subjects: Product, Store, Service Offer, Service Provider,
  Rental Equipment, Rental Lessor, and Consultant.
- Self-review, cross-owner access, incomplete source, unrelated subject,
  duplicate, invalid lifecycle, empty update, null score, and body limits.

## Lifecycle

New Reviews start `active`. Owners may edit only `active` Reviews. Admin-hidden
Reviews remain visible in owner history and owner-deletable but are not
owner-editable. Delete sets `deleted` and `deleted_at`; repeated delete returns
the same deleted representation without another write. Source/subject/reviewer
identity is immutable, and the exact-once unique key prevents recreation.

## Explicit boundary

Aggregate rows are intentionally not mutated and no Review is publicly exposed
in Step 19.3. Consequently existing public rating/count values remain unchanged
until Step 19.4 implements atomic aggregates and public contracts. Review
reports, Admin moderation, and notifications also remain inactive.

## Verification

| Check | Result |
| --- | --- |
| Ruff / compileall | OK |
| Focused CRUD tests | 12 passed |
| Full Backend tests | 180 passed; 18 known warnings |
| Runtime health | app/database/Redis `ok` |
| OpenAPI | 257 paths; 3 Review paths / 5 operations |
| Unauthenticated own list | 401 |
| Postman | 5 owner CRUD requests; JSON parses |

Runtime currently has zero delivered Orders, zero completed Service/Rental/
Consultation Requests, and zero Reviews. No fake terminal source was inserted,
so no authenticated live Review mutation is claimed. All seven populated
eligibility branches and lifecycle/error rules are covered by focused tests.

## Next step

Step 19.4 adds public Review reads, atomic aggregate maintenance, and typed
discovery/detail integration.
