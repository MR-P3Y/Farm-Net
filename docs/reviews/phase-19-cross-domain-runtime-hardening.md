# Phase 19 — Step 19.9 Cross-Domain Contract and Runtime Hardening

## Outcome

Step 19.9 closes two cross-domain contract gaps without adding routes or
changing Review lifecycle behavior:

1. all five Admin Review route groups now publish explicit typed OpenAPI
   response schemas;
2. unified Product, Store, and Rental Equipment search results now read rating
   average/count from the canonical shared Review aggregate, matching the
   existing Service and Consultant integration.

The Search providers keep their existing visibility, filtering, pagination,
route, and privacy behavior. A missing aggregate is represented as
`0.00 / 0`; no synthetic Review or rating is created.

## Typed Admin contracts

The following response envelopes are explicit OpenAPI components:

- `ReviewAdminListResponse`
- `ReviewAdminDetailResponse`
- `ReviewReportAdminListResponse`
- `ReviewReportAdminDetailResponse`
- `ReviewModerationLogListResponse`

They cover Review/report lists, Review/report status changes, and moderation
log reads. The Admin Flutter client continues to use typed models; no raw JSON
is introduced into the UI.

## Unified Search rating parity

The Product, Store, and Rental Equipment Search providers now use
`ReviewsRepository.rating_values` with the authoritative subject keys:

- `product`
- `store`
- `rental_equipment`

This makes the shared Search result `rating_average` and `reviews_count`
consistent with public Review aggregates. Service and Consultant providers
already exposed their synchronized canonical projections.

## Verification

- Ruff: passed.
- Python compileall: passed.
- Backend tests: `186 passed` with 18 known deprecation warnings.
- Mobile analyze: passed.
- Mobile tests: `54 passed`.
- Mobile Web build and Wasm dry run: passed.
- Admin analyze: passed.
- Admin tests: `20 passed`.
- Admin Web build and Wasm dry run: passed.
- Runtime health: app/database/Redis all `ok`.
- Alembic: `a7c9e1f30d13 (head)`.
- OpenAPI: 264 paths / ten Review paths.
- Admin Review response schemas: verified from live OpenAPI.
- Postman: 14 JSON collections / 325 requests parsed successfully.

No Postman request was added because this step hardens the response contracts
of existing routes and corrects existing Search result fields.
