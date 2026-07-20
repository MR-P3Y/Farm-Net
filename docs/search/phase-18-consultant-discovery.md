# Phase 18.6 — Consultant Discovery Hardening

## Outcome

Approved Consultant profiles are connected to the shared search engine while
the existing public endpoint and default ordering remain backward compatible.

## Contracts

- Visibility remains approved and non-deleted profiles only.
- Persian-normalized matching covers display name, title, bio, province/city
  names, and active specialty code, title, and description.
- Filters cover specialty, province, and city.
- Sort values are allow-listed: `relevance`, `newest`, and `rating`.
- Unified results contain only public identity, route, geo, rating, specialty
  context, and relevance. Contact and moderation fields are excluded.

## Client and verification

The typed Mobile API and Repository forward geo and sort parameters. The
Consultants Postman collection contains a representative normalized discovery
request. Verification evidence is recorded in `docs/PROJECT_PROGRESS.md`.
