# Phase 16.1 — Equipment Rental Real-State Audit

## Result

Equipment Rental is not implemented yet. The repository only contains several
cross-domain prerequisites and placeholders:

- the `lessor` Auth role;
- four moderation-only `rental_equipment.*` permission placeholders;
- the `equipment` store type and Product equipment categories;
- the `equipment_ownership` verification document type;
- reusable Auth, Geo, Media, Notifications, Admin, and financial foundations.

There is no Rental module, database table, Alembic migration, router, API
contract, Mobile feature, Admin feature, focused test, API documentation, or
Postman collection. Existing Product equipment rows describe goods for sale and
must not be treated as rentable assets. Existing Services offers describe work
performed and must not be treated as equipment rental.

## Domain boundary

Phase 16 implements a separate agricultural equipment rental marketplace:

- an approved lessor profile owns rental listings;
- equipment can be offered with operator, without operator, or either;
- listings have moderation, media, location, delivery/collection terms,
  deposits, pricing rules, and explicit availability blocks;
- renters submit date-bound requests against an approved available listing;
- the accepted request snapshots commercial terms and prevents overlapping
  accepted/in-progress bookings;
- requester, lessor, and Admin see role-specific contracts;
- every state change has an exact-once status log and notification event.

Rental remains independent from Products and Services while reusing Auth, Geo,
Media, Notifications, verification evidence, and Admin conventions.

## Lifecycle contracts

### Lessor profile and equipment moderation

```text
draft -> pending_review -> approved
                         -> rejected
approved -> suspended
rejected/suspended -> pending_review
```

### Rental request

```text
pending -> accepted -> in_progress -> completed
        -> rejected
pending/accepted -> cancelled
```

Requester cancellation is allowed only before `in_progress`. A lessor may
accept or reject a pending request and start/complete its accepted booking.
Admin may inspect and control the workflow using explicit permissions.

## Financial boundary

Phase 16 stores immutable rental price, deposit, duration, and total snapshots
when a request is accepted. It does not pretend that the existing order-only
invoice/payment flow supports Rental. Connecting Rental invoices, real payment,
deposit capture/release, commission, refunds, settlement, penalties, and damage
claims requires explicit cross-domain financial contracts and remains outside
the Rental foundation release unless implemented and verified in a dedicated
step.

## Authorized implementation sequence

```text
16.1 Real-State Audit + Contract Boundary
16.2 Rental DB + Permission Foundation
16.3 Categories + Lessor Profile APIs
16.4 Equipment Listing + Media APIs
16.5 Availability + Pricing Rules
16.6 Rental Request/Booking Workflow
16.7 Notifications + Privacy/Concurrency Hardening
16.8 Mobile Rental Discovery + Request Flow
16.9 Mobile Lessor Management + Workbench
16.10 Admin Panel Equipment Rental
16.11 Docs/Postman + Runtime Regression
16.12 Equipment Rental Release Gate + Tag
```

## Completion gate

Phase 16 is complete only when Backend, Mobile, Admin, OpenAPI, Postman,
migration/seed, database/Redis health, overlap protection, ownership/privacy,
status-log exact-once behavior, notifications, clean Git, pushed `develop`, and
an annotated release tag all pass. Any deferred finance integration must be
reported exactly and may not be represented as completed payment behavior.
