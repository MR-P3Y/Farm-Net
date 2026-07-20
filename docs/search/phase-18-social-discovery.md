# Phase 18.7 — Social Discovery Hardening

## Outcome

Public Social posts are connected to the shared search engine while the
existing feed endpoint and newest-first default remain backward compatible.

## Contracts

- Visibility requires `status=published`, `visibility=public`, and no deletion.
- Persian-normalized matching covers title, body, province/city/village names,
  and category code, title, and description.
- Filters cover category, allow-listed post type, province, and city.
- Sort values are allow-listed: `relevance` and `newest`.
- Unified results contain only public post summary, Mobile route, geo, and
  relevance; comments and expert answers remain detail-only contracts.

## Client and verification

The typed Mobile API and Repository forward geo and sort parameters. The Social
Postman collection contains a representative normalized discovery request.
Verification evidence is recorded in `docs/PROJECT_PROGRESS.md`.
