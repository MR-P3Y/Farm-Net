# Collections

فایل‌های Postman collection هر ماژول در این پوشه قرار می‌گیرند.

## Current Collections

- `auth.postman_collection.json`
- `consultants.postman_collection.json`
- `geo-profile-verification.postman_collection.json`
- `media.postman_collection.json`
- `notifications.postman_collection.json`
- `orders-payments-commission.postman_collection.json`
- `products.postman_collection.json`
- `social-expert.postman_collection.json`
- `services.postman_collection.json`
- `stores.postman_collection.json`
- `weather.postman_collection.json`

`social-expert.postman_collection.json` covers social post detail `expert_answers`, public/expert answer flows, admin expert answer moderation, and notification visibility checks for `expert_answer_created`.

`consultants.postman_collection.json` covers public consultant discovery, the public response privacy contract, user consultant profile management, consultation request creation/cancellation, approved-consultant assigned request workbench endpoints, and admin consultant profile/specialty/request moderation.

`services.postman_collection.json` covers public discovery, provider profile and
offer ownership, category/provider/offer admin moderation, request creation,
requester/provider/admin lists and details, controlled status transitions,
requester cancellation, and role ownership.

`orders-payments-commission.postman_collection.json` covers 34 Phase 9 requests,
including idempotent Checkout/payment, verify, full Refund, Admin Finance, and
Audit Log contracts.
