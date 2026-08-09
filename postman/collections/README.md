# Collections

فایل‌های Postman collection هر ماژول در این پوشه قرار می‌گیرند.

## Current Collections

- `auth.postman_collection.json`
- `consultants.postman_collection.json`
- `geo-profile-verification.postman_collection.json`
- `favorites.postman_collection.json`
- `media.postman_collection.json`
- `notifications.postman_collection.json`
- `orders-payments-commission.postman_collection.json`
- `products.postman_collection.json`
- `rentals.postman_collection.json`
- `reviews.postman_collection.json`
- `search.postman_collection.json`
- `social-expert.postman_collection.json`
- `services.postman_collection.json`
- `stores.postman_collection.json`
- `weather.postman_collection.json`
- `ai-barzegar.postman_collection.json`

`social-expert.postman_collection.json` covers social post detail `expert_answers`, public/expert answer flows, admin expert answer moderation, and notification visibility checks for `expert_answer_created`.

`consultants.postman_collection.json` covers public consultant discovery, the public response privacy contract, user consultant profile management, consultation request creation/cancellation, approved-consultant assigned request workbench endpoints, and admin consultant profile/specialty/request moderation.

`services.postman_collection.json` covers public discovery, provider profile and
offer ownership, category/provider/offer admin moderation, request creation,
requester/provider/admin lists and details, controlled status transitions,
requester cancellation, and role ownership.

`favorites.postman_collection.json` covers owner-private cross-domain list,
batch status, idempotent add, and idempotent remove contracts.

`orders-payments-commission.postman_collection.json` covers 34 Phase 9 requests,
including idempotent Checkout/payment, verify, full Refund, Admin Finance, and
Audit Log contracts.

`search.postman_collection.json` covers all-domain and per-domain Unified Search,
geo/price and Rental availability filters, Persian normalization, privacy
headers, duplicate types, non-TOMAN rejection, response-budget rejection, and
incomplete availability rejection.

`reviews.postman_collection.json` covers all Phase 19 Review route groups:
authenticated owner CRUD, public active-only Reviews and rating summaries,
governed reporting, typed Admin Review/report moderation, and immutable
moderation-log reads.

`ai-barzegar.postman_collection.json` covers all 30 Barzegar OpenAPI
operations: owner-private selected-Farm context, conversations, async requests,
exact-once feedback, retention-aware deletion, safety escalation, diary/report
tools, Admin governance, knowledge lifecycle, and deterministic evaluation
release gates. It contains no Provider key.
## Unified Subscriptions

`subscriptions.postman_collection.json` is the Phase 25 contract collection.
It contains 30 requests covering all 23 OpenAPI Billing operations and seven
negative/replay scenarios. Use only an isolated non-production environment.
