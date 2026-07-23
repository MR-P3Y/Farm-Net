# Phase 19.4 — Public Reviews, Atomic Aggregates + Discovery Integration

## Delivered contract

- Added a public paginated Review endpoint for all seven Review subject types.
- Public reads require the target to be publicly approved/active.
- Only active Reviews are visible. Public author identity is limited to a safe
  display name and never includes user ID, source identity, contacts, reports,
  or moderation information.
- `marketplace_rating_aggregates` is the canonical rating source.
- Create, score update, and active delete update sum/count/average inside the
  same transaction as the Review mutation.
- Average uses deterministic two-decimal half-up rounding; an empty aggregate
  is exactly `0 / 0 / 0.00`.
- Existing Service Provider and Consultant rating fields remain compatibility
  projections and are synchronized in the same transaction.
- Product, Store, Service Offer, Rental Equipment, and Rental Lessor public
  outputs read the shared canonical aggregate.

## Discovery fields

| Public subject | Added/read fields |
| --- | --- |
| Product | `rating_average`, `reviews_count` |
| Store | `rating_average`, `reviews_count` |
| Service Offer | `rating_average`, `reviews_count` |
| Service Provider | existing synchronized fields |
| Rental Equipment | equipment and Lessor average/count |
| Consultant | existing synchronized fields |

No Review report, moderation, notification, Mobile UI, or Admin UI behavior is
part of Step 19.4.

## Verification

Focused tests cover all subject mappings, eligibility, duplicate/self-review
prevention, aggregate deltas, safe public author output, canonical summary, and
OpenAPI route presence.

| Check | Result |
| --- | --- |
| Ruff / compileall | OK |
| Focused Review tests | 17 passed |
| Full Backend tests | 181 passed; 18 known warnings |
| Alembic | `a7c9e1f30d13` head |
| Runtime health | app/database/Redis `ok` |
| OpenAPI | 258 paths; four Review paths |
| Public missing subject | 404 |
| Postman | 14 collections / 319 requests; JSON parse OK |
