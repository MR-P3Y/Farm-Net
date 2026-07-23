# Phase 19.2 — Shared Review DB + Permission Foundation

Date: 2026-07-23

Branch: `develop`

Alembic head: `a7c9e1f30d13`

## Delivered foundation

Phase 19 now has four shared marketplace tables:

- `marketplace_reviews`
- `marketplace_rating_aggregates`
- `marketplace_review_reports`
- `marketplace_review_moderation_logs`

No Review API, repository/service behavior, notification, Mobile UI, Admin UI,
or public rating projection is activated in this step.

## Database guarantees

`marketplace_reviews` stores a typed source and subject, reviewer ownership,
one overall integer score from 1 through 5, optional text, lifecycle status,
and soft-delete time. A composite unique constraint prevents more than one
Review by the same reviewer for the same source and subject.

Database checks restrict:

- sources to Order, Service Request, Rental Request, and Consultation Request;
- subjects to Product, Store, Service Offer, Service Provider, Rental
  Equipment, Rental Lessor, and Consultant;
- each source to its allowed subject types;
- score to 1–5;
- lifecycle to `active`, `hidden`, or `deleted`;
- deleted status and timestamp to a consistent pair.

`marketplace_rating_aggregates` has one row per typed subject. It stores rating
sum, visible Review count, and decimal average with nonnegative/range and empty
state checks. Step 19.4 will define and implement its transactional mutation
rules.

`marketplace_review_reports` prevents duplicate reporting by the same user and
governs reason/status/review timestamps. `marketplace_review_moderation_logs`
has an exact-once `event_key`, actor/report links, lifecycle transition fields,
and immutable action time.

Cross-domain source/subject identifiers deliberately use typed identities
instead of impossible polymorphic foreign keys. Step 19.3 must resolve and lock
the real domain row and derive every identity server-side; clients never become
the authority for eligibility or ownership.

## Permissions

Eight dedicated permissions were added:

```text
reviews.create
reviews.read_own
reviews.manage_own
review_reports.create
reviews.admin_read
reviews.admin_moderate
review_reports.admin_read
review_reports.admin_resolve
```

The five customer/business roles receive the four owner permissions. Support
receives two read-only Admin permissions. Content Manager and Admin receive the
four moderation permissions. Super Admin receives all eight through the
existing all-permissions rule.

The permissions are separate from Social moderation and future management
`reports.*` permissions.

## Verification

| Check | Result |
| --- | --- |
| Ruff | OK |
| compileall | OK |
| Focused tests | 4 passed |
| Full Backend tests | 168 passed; 18 known warnings |
| Alembic chain | one head: `a7c9e1f30d13` |
| Offline MySQL SQL generation | OK |
| Real MySQL upgrade | OK |
| Real MySQL downgrade/re-upgrade | OK |
| Auth seed idempotency | two runs; 12 roles / 257 permissions |
| Runtime health | app/database/Redis `ok` |
| New constraints / rows | 20 checks; all four tables empty |

The first real MySQL attempt exposed that MySQL forbids a Check Constraint from
using a foreign-key column with `ON DELETE SET NULL`. The check was narrowed to
the authoritative review timestamp. The two partially created, verified-empty
new tables were removed and the same migration then ran successfully. No
pre-existing table or data was removed.

`alembic check` reports only the four previously documented unique-index
reflection differences on Consultant and Services tables. It reports no
Review-table drift; that unrelated baseline was not mixed into Phase 19.2.

## Next step

Step 19.3 implements server-authoritative eligibility, ownership, lifecycle,
and Review CRUD over this inactive foundation.
