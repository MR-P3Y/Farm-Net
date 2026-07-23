# Phase 19.1 — Reviews / Ratings / Reports Real-State Audit

Date: 2026-07-23

Branch: `develop`

Baseline: `v0.24.0-activity-center-foundation` (`1055319`)

## Audit result

Farm-Net has no marketplace Review/Rating engine, review API, review permission,
Mobile review flow, Admin review moderation surface, or Postman review
collection. Phase 19 must add one shared engine rather than four unrelated
implementations.

Two similarly named foundations must remain separate:

- `social_reports` moderates Social posts/comments and is already complete.
- `verification_reviews` is an identity-verification audit trail, not a user
  rating.

The existing generic `reports.*` permissions belong to future management
reports/analytics. They must not authorize marketplace review moderation.

## Existing rating-shaped fields

`service_provider_profiles` and `consult_profiles` already expose
`rating_average` and `reviews_count`, and Search can sort those domains by
rating. No persisted review source updates these fields, so they currently act
as zero-valued placeholders. Product, Store, Rental Equipment, and Lessor
models have no equivalent rating aggregate.

Phase 19 must make every exposed rating traceable to approved persisted reviews
and must update aggregate values atomically. It must not seed or fabricate
ratings.

## Authoritative eligibility sources

| Domain | Authoritative source | Required status | Reviewer | Review subjects |
| --- | --- | --- | --- | --- |
| Commerce | `orders` / `order_items` | `delivered` | `buyer_user_id` | purchased Product; Store |
| Services | `service_requests` | `completed` | `requester_user_id` | Service Offer; Provider |
| Rentals | `rental_requests` | `completed` | `requester_user_id` | Equipment; Lessor |
| Consultants | `consult_requests` | `completed` | `requester_user_id` | Consultant |

The source row supplies ownership and subject identity. Client-supplied user,
provider, store, lessor, consultant, product, offer, or equipment ownership is
never trusted. Cancelled, rejected, refunded-before-delivery, open, accepted,
or in-progress sources are ineligible.

## Shared contract boundary

The first foundation uses one overall integer score from 1 through 5 and an
optional bounded text body. A reviewer may create at most one active review per
eligible source and subject. Replays must return the existing result or a
deterministic conflict; concurrent submissions must not create duplicates.

Public listing exposes only active/moderation-approved review content, safe
author summary, score, and timestamps. It must not expose source IDs, private
request/order data, contact data, moderation notes, reporter identity, or
internal ownership IDs.

The review owner may read their own history and edit/delete according to the
explicit lifecycle defined in Step 19.3. A reviewed business user cannot edit,
hide, or delete customer feedback. Admin moderation requires dedicated Review
permissions and a durable status log.

## Reports boundary

Phase 19 Reports means reporting a marketplace Review for spam, abuse,
harassment, privacy exposure, fraud, or other governed reasons. A user cannot
report the same Review repeatedly. Self-report policy and Admin resolution must
be explicit and audited. Social reports remain in the Social module; financial,
user, sales, BI, and export reports remain future Analytics work.

## Aggregate and discovery rules

- Only active, publicly visible Reviews contribute to average/count.
- Create, score edit, deletion, hide, restore, and moderation must update the
  matching aggregate in the same transaction.
- Average uses a documented deterministic decimal rounding rule.
- Empty subjects return `0.00` and count `0`, never null or seeded values.
- Existing Service and Consultant discovery sorts must consume real aggregates.
- Product, Store, Rental, and Lessor discovery integration is added only after
  their public contracts receive typed aggregate fields.

## Explicitly deferred

- Review media/video, provider replies, helpful votes, badges, incentives, and
  multi-dimension scores.
- Anonymous reviews, reviews without a completed real source, imported ratings,
  and Admin-authored customer reviews.
- Bayesian/weighted ranking, fraud ML, sentiment analysis, and AI summaries.
- Social reports consolidation and management analytics/export reports.

## Approved implementation sequence

1. **19.1** Real-State Audit + Contract Boundary.
2. **19.2** Shared Review DB + Permission Foundation.
3. **19.3** Eligibility, Ownership, Lifecycle + Review CRUD.
4. **19.4** Public Reviews, Aggregates + Discovery Integration.
5. **19.5** Review Reports, Admin Moderation + Audit Logs.
6. **19.6** Notifications, Privacy, Exact-Once + Concurrency Hardening.
7. **19.7** Mobile Review Creation, History + Public Rendering.
8. **19.8** Admin Review/Report Moderation Panel.
9. **19.9** Cross-Domain Contract and Runtime Hardening.
10. **19.10** Docs, Postman + Runtime Regression.
11. **19.11** Release Gate + Tag.

## Step 19.1 verification

- Repository was clean and synchronized on `develop` at audit start.
- Static model/migration/router/client/Postman inspection found no marketplace
  review foundation.
- Existing Social report UI/API/Admin flow was confirmed and excluded.
- Four completed-source ownership contracts were confirmed from real models and
  state machines.
- Docker Desktop and local Runtime were unavailable during this read-only audit;
  no Runtime result is claimed. Runtime availability is mandatory before the
  implementation release gates.
