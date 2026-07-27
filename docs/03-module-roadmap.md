# 03 — Module Roadmap
# نقشه راه ماژول‌های پروژه فارم نت

## 1. هدف سند

این سند مسیر پیاده‌سازی ماژول‌های پروژه «فارم نت» را مشخص می‌کند.

هدف این است که تیم‌ها بدانند:

- هر ماژول چه کاری انجام می‌دهد.
- ترتیب اجرای ماژول‌ها چیست.
- هر ماژول به چه ماژول‌های دیگری وابسته است.
- خروجی قابل تحویل هر ماژول چیست.
- چه زمانی یک ماژول تمام‌شده حساب می‌شود.

این سند باید قبل از شروع هر فاز توسط تیم Backend، Flutter، Admin و QA خوانده شود.

---

# 2. قانون اصلی توسعه ماژول‌ها

هر ماژول باید ابتدا در حد Core پیاده‌سازی شود.

```text
Core کامل ≠ نسخه نهایی کامل
```

یعنی هر ماژول باید اول نسخه قابل استفاده، قابل تست و قابل توسعه داشته باشد.
امکانات پیشرفته بعداً اضافه می‌شوند.

مثال:

Store Core یعنی:

```text
ثبت فروشگاه
مدارک فروشگاه
قرارداد
تأیید ادمین
ثبت محصول
عکس محصول
تأیید محصول
لیست عمومی محصول
پنل پایه فروشگاه
فاکتور پایه
کمیسیون
نوتیفیکیشن
```

اما Store Core یعنی این‌ها نیست:

```text
انبارداری پیشرفته
لجستیک کامل
مرجوعی
کد تخفیف
داشبورد مالی پیشرفته
سیستم ارسال کامل
```

---

# 3. ترتیب اجرای کل ماژول‌ها

ترتیب اجرای رسمی پروژه:

```text
Phase 0: Product Scope & Governance
Phase 1: Repository + Documentation Foundation
Phase 2: Backend Foundation
Phase 3: Flutter Foundation
Phase 4: Admin Panel Foundation
Phase 5: Auth / Users / Roles / Permissions
Phase 6: Geo Core
Phase 7: Store Foundation
Phase 8: Product / Catalog Foundation
Phase 9: Cart / Orders / Payments / Commission
Phase 10: Media / File Upload / Storage
Phase 11: Notifications Foundation
Phase 12: Weather Foundation
Phase 13: Social / Community Foundation
Phase 14: Services Module
Phase 15: Consultants Module
Phase 16: Equipment / Rental
Phase 17: Category Management
Phase 18: Search / Filters / Discovery
Phase 19: Reviews / Ratings / Reports
Phase 20: Wallet / Settlement / Accounting
Phase 21: AI / RAG Assistant Integration
Phase 22: Production Hardening / Deployment
Phase 23: Role-Based My Activity Center
Phase 24: Farm Management / Digital Farm Profiles
```

Phase 18 implementation began on 2026-07-20. Step 18.1 completed a read-only
real-state audit; the approved incremental plan is recorded in
`docs/search/phase-18-real-state-audit.md`. Existing domain discovery contracts
remain active while shared contracts are added incrementally.

Phase 19 implementation began on 2026-07-23. Step 19.1 confirmed that no
marketplace Review/Rating engine exists; Social reports and Verification review
logs are separate domains. The approved shared-engine sequence and completed-
source eligibility boundary are recorded in
`docs/reviews/phase-19-real-state-audit.md`.

Phase 19 is complete and released as `v0.25.0-reviews-foundation`. Phase 22
Production Hardening reached Step 22.10 and is blocked on external credentials.
By owner decision, Phase 24 Farm Management is now the active product track
and is the required farmer-data foundation before Phase 21 AI/RAG resumes.
The approved Phase 24 sequence is recorded in
`docs/farms/phase-24-real-state-audit.md`.

---

## 3.1 Current Roadmap Note

This roadmap was revised after Phase 8 on 2026-05-20.

The phase order above is authoritative for Phase 9 and later. Older detailed
module notes later in this document remain backlog notes until they are
rewritten during their implementation phase.

## 3.2 New Phase Scope Notes

### Phase 12 - Weather Foundation

Status: Foundation completed in Phase 12

Implemented:

- Weather database foundation
- Weather permissions
- Provider abstraction
- Mock provider
- OpenWeather-ready config using `api_key_ref`
- Public weather APIs
- Admin weather APIs
- DB cache-aware refresh
- Automatic alert rules engine
- Weather alert notifications for admin/super_admin
- Flutter mobile weather foundation
- Admin panel weather foundation
- Docs and Postman collection

Deferred:

- User weather subscriptions
- User-targeted weather notifications
- Real external provider production hardening
- Push/SMS/email delivery

### Phase 13 - Social / Community Foundation

Status: Completed on develop.

Implemented:

- Social DB models and migration
- Social permissions seed
- Social service/repository foundation
- Public/user social APIs
- Comments and one-level replies
- Reactions, bookmarks, reports
- Admin moderation APIs
- Media image integration for social posts
- Social notification integration
- Flutter mobile social foundation
- Admin panel moderation foundation
- Social API docs and Postman collection

Known limitations:

- Mobile/admin manual UI QA not completed yet
- Mobile create post image upload is not implemented yet
- Advanced moderation filters/details are not implemented yet
- Feed ranking/search is not implemented yet
- Anti-abuse/rate-limit rules should be hardened before high-traffic production use

---

# 4. Phase 1 — Repository + Documentation Foundation

## هدف

ساخت پایه مدیریت پروژه، ساختار مخزن، مستندات و قوانین همکاری تیم‌ها.

## وابستگی‌ها

ندارد.

## خروجی‌ها

```text
Monorepo structure
README.md
.gitignore
.env.example
docs/
infra/
scripts/
postman/
branch strategy
commit rules
initial documentation
```

## ساختار پیشنهادی

```text
farmnet/
  backend/
  mobile/
  admin-panel/
  docs/
  infra/
  scripts/
  postman/
  README.md
  .gitignore
  .env.example
```

## Definition of Done

```text
ساختار repo آماده باشد.
پوشه docs ساخته شده باشد.
سه سند اول وجود داشته باشند:
- 00-product-vision.md
- 01-mvp-scope.md
- 02-architecture.md
Git strategy مشخص شده باشد.
.env.example وجود داشته باشد.
هیچ secret واقعی داخل repo نباشد.
```

---

# 5. Phase 2 — Backend Foundation

## هدف

ساخت اسکلت اصلی Backend برای تمام ماژول‌ها.

## وابستگی‌ها

```text
Repository Foundation
```

## خروجی‌ها

```text
FastAPI skeleton
MySQL connection
SQLAlchemy setup
Alembic migration
Redis connection
Config/env
Standard response
Standard error
Trace ID
Logging
Pagination
CORS
Rate limit پایه
Health check
Swagger/OpenAPI
Dockerfile
```

## ساختار Backend

```text
backend/
  app/
    main.py
    core/
    common/
    modules/
    db/
    tests/
  alembic/
  Dockerfile
  pyproject.toml
  .env.example
```

## APIهای پایه

```text
GET /health
GET /api/v1/health
```

## Definition of Done

```text
Backend اجرا شود.
Swagger باز شود.
MySQL متصل باشد.
Redis متصل باشد.
Migration اولیه اجرا شود.
Response format استاندارد کار کند.
Error format استاندارد کار کند.
Trace ID در response و log وجود داشته باشد.
Docker build شود.
```

---

# 6. Phase 3 — Flutter Foundation

## هدف

ساخت پایه اپ Flutter برای کاربران.

## وابستگی‌ها

```text
Repository Foundation
```

## خروجی‌ها

```text
Flutter project structure
Routing
Theme light/dark
Localization fa/en
RTL/LTR
finalui
LSM responsive
Network client
Token storage
Base widgets
Persian digit helper
Jalali date helper
Toman formatter
Error mapper
```

## قوانین UI

```text
finalui
LSM Pattern
ResponsiveBuilder + ScreenUtil + MediaQuery
بدون r.dp
CrystalGlass به جای CustomGlassBox
KmAppBar
Icons.arrow_back
Navigator.pop(context)
Light/Dark
fa/en
RTL/LTR
اعداد فارسی در حالت فارسی
تاریخ شمسی در UI فارسی
واحد تومان
```

## UIهای پایه

```text
KmAppBar
KmButton
KmTextField
KmLoadingView
KmErrorView
KmEmptyView
KmStatusChip
KmPriceText
KmJalaliDateText
KmNotificationBadge
```

## Definition of Done

```text
اپ Flutter اجرا شود.
تم روشن/تاریک کار کند.
زبان فارسی/انگلیسی قابل تغییر باشد.
RTL/LTR درست باشد.
اعداد فارسی در حالت فارسی نمایش داده شود.
تاریخ شمسی helper داشته باشد.
فرمت تومان helper داشته باشد.
Network client آماده باشد.
Base widgets آماده باشند.
```

---

# 7. Phase 4 — Admin Panel Foundation

## هدف

ساخت پایه پنل ادمین با Flutter Web.

## وابستگی‌ها

```text
Flutter Foundation
Backend Foundation
```

## خروجی‌ها

```text
Flutter Web admin project
Admin login layout
Admin dashboard shell
Sidebar
Topbar
Routing
Permission guard
Table component
Filter/search component
Form component
Status chip
Audit view base
```

## UIهای اصلی

```text
AdminLoginPage
AdminDashboardShell
AdminSidebar
AdminDataTable
AdminFormPage
AdminStatusChip
AdminPermissionGuard
```

## Definition of Done

```text
پنل ادمین با Flutter Web اجرا شود.
Layout اصلی ادمین آماده باشد.
Routing کار کند.
ساختار permission guard آماده باشد.
Componentهای پایه جدول و فرم وجود داشته باشند.
```

---

# 8. Phase 5 — Auth / Users / Roles / Permissions

## هدف

ساخت هویت اصلی کاربران، ورود، ثبت‌نام، نقش‌ها و دسترسی‌ها.

## وابستگی‌ها

```text
Backend Foundation
Flutter Foundation
Admin Panel Foundation
Notification Core برای OTP بهتر است، اما می‌توان OTP اولیه را موقت ساده پیاده کرد.
```

## قوانین اصلی

```text
User فروشنده نیست.
User فقط حساب اصلی شخص است.
هر User می‌تواند چند Role داشته باشد.
Endpointهای حساس باید Permission Check داشته باشند.
```

## جدول‌های اصلی

```text
auth_users
auth_roles
auth_permissions
auth_user_roles
auth_role_permissions
auth_sessions
auth_refresh_tokens
auth_otp_codes
```

## APIهای اصلی

```text
POST /api/v1/auth/register/email
POST /api/v1/auth/login/email
POST /api/v1/auth/otp/request
POST /api/v1/auth/otp/verify
POST /api/v1/auth/refresh
POST /api/v1/auth/logout

GET /api/v1/users/me
PATCH /api/v1/users/me

GET /api/v1/admin/users
GET /api/v1/admin/users/{id}
PATCH /api/v1/admin/users/{id}/status

GET /api/v1/admin/roles
POST /api/v1/admin/roles
PATCH /api/v1/admin/roles/{id}

GET /api/v1/admin/permissions
POST /api/v1/admin/users/{id}/roles
DELETE /api/v1/admin/users/{id}/roles/{role_id}
```

## Notification Events

```text
OTP_SENT
USER_REGISTERED
USER_LOGIN
PASSWORD_CHANGED
ACCOUNT_SUSPENDED
```

## Flutter UI

```text
Login with phone
OTP verify
Login with email
Register with email
Profile base screen
```

## Admin UI

```text
Users list
User detail
User status change
Roles list
Role permissions management
```

## Definition of Done

```text
کاربر با موبایل + OTP وارد شود.
کاربر با ایمیل + رمز وارد شود.
Access token و refresh token کار کند.
نقش‌ها قابل مدیریت باشند.
Permission check برای endpointهای حساس کار کند.
ادمین بتواند کاربر را ببیند و وضعیتش را تغییر دهد.
OTP rate limit داشته باشد.
تست‌های Auth نوشته شوند.
```

---

# 9. Phase 6 — Geo Core

## هدف

ساخت بانک جغرافیای ایران و سیستم آدرس‌دهی مشترک.

## وابستگی‌ها

```text
Backend Foundation
Admin Panel Foundation
```

## جدول‌های اصلی

```text
geo_provinces
geo_counties
geo_districts
geo_cities
geo_rural_districts
geo_villages
geo_addresses
```

## APIهای اصلی

```text
GET /api/v1/geo/provinces
GET /api/v1/geo/counties?province_id=
GET /api/v1/geo/districts?county_id=
GET /api/v1/geo/cities?province_id=&county_id=
GET /api/v1/geo/villages?district_id=
POST /api/v1/geo/addresses
GET /api/v1/geo/addresses/me
PATCH /api/v1/geo/addresses/{id}
DELETE /api/v1/geo/addresses/{id}
```

## Admin API

```text
GET /api/v1/admin/geo/provinces
POST /api/v1/admin/geo/provinces
PATCH /api/v1/admin/geo/provinces/{id}

GET /api/v1/admin/geo/cities
POST /api/v1/admin/geo/cities
PATCH /api/v1/admin/geo/cities/{id}
```

## Flutter UI

```text
Province selector
City selector
Village selector
Address form
Map coordinate picker base
```

## Admin UI

```text
Geo list management
Province/city/village management
```

## Definition of Done

```text
داده استان/شهر/روستا قابل seed باشد.
کاربر بتواند آدرس دستی ثبت کند.
مختصات latitude/longitude قابل ذخیره باشد.
آدرس generic باشد و به target_type/target_id وصل شود.
فیلترهای جغرافیایی برای آینده آماده باشند.
```

---

# 10. Legacy Module Note — Notification Core

## هدف

ساخت هسته نوتیفیکیشن برای کل پلتفرم.

## وابستگی‌ها

```text
Backend Foundation
Auth
Redis
```

## کانال‌ها

```text
In-App
Push
SMS
Email
```

## جدول‌های اصلی

```text
notify_events
notify_notifications
notify_templates
notify_channels
notify_user_preferences
notify_delivery_attempts
notify_device_tokens
```

## APIهای اصلی

```text
GET /api/v1/notifications
GET /api/v1/notifications/unread-count
PATCH /api/v1/notifications/{id}/read
PATCH /api/v1/notifications/read-all
POST /api/v1/notifications/device-token
GET /api/v1/notifications/preferences
PATCH /api/v1/notifications/preferences
```

## Admin API

```text
GET /api/v1/admin/notifications/events
GET /api/v1/admin/notifications/templates
POST /api/v1/admin/notifications/templates
PATCH /api/v1/admin/notifications/templates/{id}

GET /api/v1/admin/notifications/delivery-attempts
POST /api/v1/admin/notifications/send-test
```

## Worker

```text
notification delivery worker
SMS sender
Email sender
Push sender
retry failed deliveries
```

## Notification Events پایه

```text
OTP_SENT
SHOP_APPROVED
SHOP_REJECTED
PRODUCT_APPROVED
PRODUCT_REJECTED
INVOICE_ISSUED
PAYMENT_SUCCESS
PAYMENT_FAILED
CONTRACT_REQUIRED
DOCUMENT_REJECTED
SUBSCRIPTION_EXPIRING
PROMOTION_EXPIRED
```

## Flutter UI

```text
Notifications list
Unread badge
Notification detail
Notification preferences
```

## Admin UI

```text
Templates management
Delivery logs
Send test notification
```

## Definition of Done

```text
In-App notification کار کند.
SMS برای OTP کار کند.
Email ارسال تستی داشته باشد.
Push ساختار device token داشته باشد.
Delivery attempts لاگ شوند.
Templateها قابل مدیریت باشند.
Notification از API اصلی جدا و صفی ارسال شود.
```

---

# 11. Legacy Module Note — Media / Documents

## هدف

ساخت سیستم آپلود فایل، عکس و مدارک.

## وابستگی‌ها

```text
Auth
Backend Foundation
Notification Core
```

## تفاوت Media و Document

```text
Media:
عکس پروفایل، عکس محصول، عکس فروشگاه، تصاویر عمومی

Document:
مدارک رسمی، قرارداد PDF، مجوزها، مدارک احراز
```

## جدول‌های اصلی

```text
media_files
media_documents
media_file_links
```

## APIهای اصلی

```text
POST /api/v1/media/upload
GET /api/v1/media/{id}
DELETE /api/v1/media/{id}

POST /api/v1/documents/upload
GET /api/v1/documents/me
GET /api/v1/documents/{id}
DELETE /api/v1/documents/{id}
```

## Admin API

```text
GET /api/v1/admin/documents
GET /api/v1/admin/documents/{id}
PATCH /api/v1/admin/documents/{id}/status
```

## Flutter UI

```text
Image picker
File picker
Upload progress
Profile image upload
Document upload screen
```

## Admin UI

```text
Documents list
Document detail
Approve/reject document base
```

## Definition of Done

```text
فایل با محدودیت حجم و پسوند آپلود شود.
فایل metadata داشته باشد.
فایل public/private باشد.
مدرک رسمی قابل آپلود باشد.
ادمین بتواند مدارک را ببیند.
آپلود فایل امن باشد و نام فایل تصادفی شود.
```

---

# 12. Legacy Module Note — Verification / Contracts

## هدف

ساخت جریان تأیید فعالیت حرفه‌ای و قراردادها.

## وابستگی‌ها

```text
Auth
Media/Documents
Notification Core
Admin Panel
```

## جدول‌های اصلی

```text
verification_requests
verification_review_logs
contract_templates
contract_acceptances
```

## Status Flow

```text
draft
pending_documents
pending_contract
pending_review
needs_revision
approved
rejected
suspended
expired
```

## APIهای اصلی

```text
POST /api/v1/verification/requests
GET /api/v1/verification/requests/me
GET /api/v1/verification/requests/{id}
POST /api/v1/verification/requests/{id}/submit
POST /api/v1/contracts/{template_id}/accept
POST /api/v1/contracts/{template_id}/upload-signed-pdf
```

## Admin API

```text
GET /api/v1/admin/verification/requests
GET /api/v1/admin/verification/requests/{id}
POST /api/v1/admin/verification/requests/{id}/approve
POST /api/v1/admin/verification/requests/{id}/reject
POST /api/v1/admin/verification/requests/{id}/needs-revision

GET /api/v1/admin/contracts/templates
POST /api/v1/admin/contracts/templates
PATCH /api/v1/admin/contracts/templates/{id}
```

## Notification Events

```text
VERIFICATION_SUBMITTED
VERIFICATION_APPROVED
VERIFICATION_REJECTED
VERIFICATION_NEEDS_REVISION
CONTRACT_REQUIRED
CONTRACT_ACCEPTED
CONTRACT_UPDATED
```

## Flutter UI

```text
Professional request form
Document checklist
Contract accept screen
Signed PDF upload
Verification status screen
```

## Admin UI

```text
Verification requests list
Verification detail
Document review
Contract templates management
Approve/reject actions
```

## Definition of Done

```text
کاربر بتواند درخواست فعالیت حرفه‌ای ثبت کند.
مدارک به درخواست وصل شوند.
قرارداد با version پذیرفته شود.
PDF قرارداد قابل آپلود باشد.
ادمین بتواند تأیید/رد/نیاز به اصلاح ثبت کند.
نوتیفیکیشن وضعیت ارسال شود.
Audit log برای تصمیم ادمین ثبت شود.
```

---

# 13. Implemented Module — Billing / Subscription

Implementation status: Phase 25.1 through 25.10 complete. The canonical
contract is documented in `docs/api/billing.md`; the list below is a compact
roadmap summary.

## هدف

ساخت سیستم پلن‌ها، اشتراک‌ها و محدودیت امکانات.

## وابستگی‌ها

```text
Auth
Admin Panel
Notification Core
Payment Core برای پرداخت آنلاین اشتراک
```

## جدول‌های اصلی

```text
billing_plans
billing_features
billing_plan_features
billing_subscriptions
billing_subscription_periods
billing_entitlements
billing_feature_usage
billing_usage_reservations
billing_subscription_payment_attempts
billing_audit_logs
```

## APIهای اصلی

```text
GET /api/v1/billing/plans
GET /api/v1/billing/plans/{plan_code}
GET /api/v1/billing/subscription/me
GET /api/v1/billing/entitlements/me
GET /api/v1/billing/usage/me
POST /api/v1/billing/usage/estimate
POST /api/v1/billing/subscription/free
POST /api/v1/billing/subscription/cancel
POST /api/v1/billing/subscription/resume
POST /api/v1/billing/checkout
POST /api/v1/billing/subscription/renew/checkout
POST /api/v1/billing/payments/verify
GET /api/v1/billing/payments/callback/zarinpal
```

## Admin API

```text
GET /api/v1/admin/billing/plans
POST /api/v1/admin/billing/plans
PATCH /api/v1/admin/billing/plans/{id}
PATCH /api/v1/admin/billing/plans/{id}/status

GET /api/v1/admin/billing/subscriptions
GET /api/v1/admin/billing/subscriptions/{id}
POST /api/v1/admin/billing/subscriptions/manual-activate
PATCH /api/v1/admin/billing/subscriptions/{id}/cancel
GET /api/v1/admin/billing/audit
GET /api/v1/admin/billing/reconciliation
```

## Notification Events

```text
SUBSCRIPTION_CREATED
SUBSCRIPTION_ACTIVATED
SUBSCRIPTION_EXPIRING
SUBSCRIPTION_EXPIRED
FEATURE_LIMIT_REACHED
```

## Flutter UI

```text
Plans list
Current subscription
Usage limit view
Subscription checkout
```

## Admin UI

```text
Plans management
Subscriptions list
Manual activation
Feature limits management
Audit and reconciliation inspection
```

## Definition of Done

```text
پلن قابل تعریف باشد.
ویژگی‌های پلن قابل تعریف باشد.
اشتراک کاربر ثبت شود.
محدودیت امکانات قابل چک باشد.
مصرف امکانات ثبت شود.
ادمین بتواند اشتراک را مدیریت کند.
```

---

# 14. Legacy Module Note — Commission / Finance / Payment Core

## هدف

ساخت فاکتور، پرداخت آنلاین پایه، تراکنش و کمیسیون.

## وابستگی‌ها

```text
Auth
Notification Core
Admin Panel
Billing
```

## جدول‌های اصلی

```text
commission_rules
commission_snapshots
finance_invoices
finance_invoice_items
finance_commissions
finance_transactions
payment_gateways
payment_attempts
```

## APIهای اصلی

```text
POST /api/v1/finance/invoices
GET /api/v1/finance/invoices/{id}
POST /api/v1/payments/checkout
GET /api/v1/payments/callback/{gateway}
POST /api/v1/payments/verify
```

## Admin API

```text
GET /api/v1/admin/commission/rules
POST /api/v1/admin/commission/rules
PATCH /api/v1/admin/commission/rules/{id}

GET /api/v1/admin/finance/invoices
GET /api/v1/admin/finance/invoices/{id}
GET /api/v1/admin/payments/attempts
GET /api/v1/admin/finance/transactions
```

## Commission Rule Scope

```text
store
service
rental
consultation
promotion
subscription
data_access
```

## Payment Flow

```text
Create invoice
→ Calculate commission
→ Save commission snapshot
→ Create payment_attempt
→ Redirect to gateway
→ Callback
→ Verify
→ Mark invoice paid
→ Create transaction
→ Notification
→ Audit log
```

## Notification Events

```text
INVOICE_ISSUED
PAYMENT_STARTED
PAYMENT_SUCCESS
PAYMENT_FAILED
COMMISSION_CALCULATED
```

## Flutter UI

```text
Invoice detail
Payment checkout
Payment success
Payment failed
```

## Admin UI

```text
Commission rules management
Invoices list/detail
Payment attempts
Transactions list
```

## Definition of Done

```text
فاکتور صادر شود.
آیتم‌های فاکتور ثبت شوند.
کمیسیون snapshot شود.
درگاه پرداخت Core کار کند.
callback و verify کار کند.
وضعیت فاکتور تغییر کند.
پرداخت موفق/ناموفق notification بدهد.
محاسبه کمیسیون تست داشته باشد.
```

---

# 15. Legacy Module Note — Store Core

## هدف

ساخت هسته فروشگاه و محصول.

## وابستگی‌ها

```text
Auth
Geo
Media/Documents
Verification/Contracts
Notification
Finance/Payment
Admin Panel
```

## قوانین

```text
هر کاربر فقط یک فروشگاه دارد.
فروشگاه می‌تواند چند عضو داشته باشد.
فعال شدن فروشگاه نیازمند مدارک، قرارداد و تأیید ادمین است.
محصول باید قبل از انتشار تأیید شود.
```

## جدول‌های اصلی

```text
store_shops
store_shop_members
store_categories
store_products
store_product_images
store_product_features
store_product_benefits
store_product_status_logs
```

## وضعیت فروشگاه

```text
draft
pending_review
approved
rejected
suspended
closed
```

## وضعیت محصول

```text
draft
pending_review
published
rejected
inactive
deleted
```

## APIهای اصلی

```text
POST /api/v1/store/shops
GET /api/v1/store/shops/me
PATCH /api/v1/store/shops/me
POST /api/v1/store/shops/me/submit

GET /api/v1/store/categories
GET /api/v1/store/products
GET /api/v1/store/products/{id}
POST /api/v1/store/products
PATCH /api/v1/store/products/{id}
POST /api/v1/store/products/{id}/submit
DELETE /api/v1/store/products/{id}

GET /api/v1/store/shops/me/members
POST /api/v1/store/shops/me/members
PATCH /api/v1/store/shops/me/members/{member_id}
DELETE /api/v1/store/shops/me/members/{member_id}
```

## Admin API

```text
GET /api/v1/admin/store/shops
GET /api/v1/admin/store/shops/{id}
POST /api/v1/admin/store/shops/{id}/approve
POST /api/v1/admin/store/shops/{id}/reject
POST /api/v1/admin/store/shops/{id}/suspend

GET /api/v1/admin/store/categories
POST /api/v1/admin/store/categories
PATCH /api/v1/admin/store/categories/{id}

GET /api/v1/admin/store/products
GET /api/v1/admin/store/products/{id}
POST /api/v1/admin/store/products/{id}/approve
POST /api/v1/admin/store/products/{id}/reject
```

## Notification Events

```text
SHOP_CREATED
SHOP_SUBMITTED
SHOP_APPROVED
SHOP_REJECTED
SHOP_SUSPENDED
SHOP_MEMBER_ADDED
PRODUCT_CREATED
PRODUCT_SUBMITTED
PRODUCT_APPROVED
PRODUCT_REJECTED
PRODUCT_PUBLISHED
```

## Flutter UI

```text
Create shop
Shop status
Shop profile
Product list
Create product
Edit product
Upload product images
Product detail
```

## Admin UI

```text
Shop requests
Shop detail
Approve/reject shop
Categories management
Products review
Approve/reject product
```

## Definition of Done

```text
کاربر بتواند فروشگاه ثبت کند.
فروشگاه مدارک و قرارداد داشته باشد.
ادمین فروشگاه را تأیید/رد کند.
فروشگاه عضو داشته باشد.
فروشگاه محصول ثبت کند.
محصول عکس و ویژگی داشته باشد.
محصول به تأیید ادمین برسد.
محصول منتشرشده در لیست عمومی دیده شود.
نوتیفیکیشن‌ها ارسال شوند.
Audit log برای تصمیمات ادمین ثبت شود.
```

---

# 16. Legacy Module Note — Shop Panel UI

## هدف

ساخت پنل فروشگاه برای صاحب فروشگاه و اعضای فروشگاه.

## وابستگی‌ها

```text
Store Core
Flutter Foundation
Notification Core
Finance Core
Promotion Core پایه
```

## صفحات اصلی

```text
Shop dashboard
Shop profile
Shop members
Products list
Create product
Edit product
Product status
Invoices list
Promotion requests
Notifications
```

## Definition of Done

```text
صاحب فروشگاه بتواند وضعیت فروشگاه را ببیند.
محصول ثبت و ویرایش کند.
عکس محصول آپلود کند.
وضعیت محصول را ببیند.
اعضای فروشگاه را مدیریت کند.
فاکتورها را ببیند.
نوتیفیکیشن‌ها را ببیند.
همه صفحات ریسپانسیو و fa/en باشند.
```

---

# 17. Legacy Module Note — Public Store UI

## هدف

نمایش فروشگاه و محصولات برای کاربران عمومی.

## وابستگی‌ها

```text
Store Core
Flutter Foundation
Geo
Promotion
```

## صفحات اصلی

```text
Store home section
Products list
Product detail
Category filter
Location filter
Search
Shop public profile
Promoted products/shops
```

## Definition of Done

```text
کاربر بتواند محصولات منتشرشده را ببیند.
فیلتر دسته‌بندی کار کند.
فیلتر مکان آماده باشد.
جزئیات محصول نمایش داده شود.
محصولات تبلیغ‌شده در جایگاه بالاتر نمایش داده شوند.
قیمت با تومان و عدد فارسی نمایش داده شود.
تاریخ‌ها شمسی باشند.
```

---

# 18. Legacy Module Note — Admin Store Management

## هدف

تکمیل مدیریت فروشگاه در پنل ادمین.

## وابستگی‌ها

```text
Store Core
Admin Panel Foundation
Finance Core
Promotion Core
```

## صفحات اصلی

```text
Shops list
Shop detail
Shop approval queue
Products review queue
Categories management
Shop members view
Invoices related to shop
Promotion management
Audit logs related to store
```

## Definition of Done

```text
ادمین بتواند فروشگاه‌ها را مدیریت کند.
محصولات را تأیید/رد کند.
دسته‌بندی محصولات را مدیریت کند.
فاکتورهای فروشگاه را ببیند.
تبلیغات فروشگاه را مدیریت کند.
Audit logs قابل مشاهده باشند.
```

---

# 19. Legacy Module Note — Promotion / Ladder Core

## هدف

ساخت سیستم تبلیغات و نردبان.

## وابستگی‌ها

```text
Store Core
Finance/Payment
Notification
Admin Panel
```

## جدول‌های اصلی

```text
promotion_packages
promotions
promotion_slots
promotion_payments
```

## APIهای اصلی

```text
GET /api/v1/promotions/packages
POST /api/v1/promotions/checkout
GET /api/v1/promotions/me
```

## Admin API

```text
GET /api/v1/admin/promotions/packages
POST /api/v1/admin/promotions/packages
PATCH /api/v1/admin/promotions/packages/{id}

GET /api/v1/admin/promotions
POST /api/v1/admin/promotions/{id}/activate
POST /api/v1/admin/promotions/{id}/cancel
```

## Notification Events

```text
PROMOTION_CREATED
PROMOTION_ACTIVATED
PROMOTION_EXPIRING
PROMOTION_EXPIRED
PROMOTION_CANCELLED
```

## Definition of Done

```text
ادمین بتواند پکیج تبلیغ تعریف کند.
فروشگاه بتواند تبلیغ/نردبان درخواست کند.
پرداخت تبلیغ به فاکتور وصل شود.
تبلیغ فعال در رتبه نمایش اثر بگذارد.
نوتیفیکیشن شروع/پایان تبلیغ ارسال شود.
```

---

# 20. Legacy Module Note — Services / Rental Core

## هدف

ساخت هسته خدمات و اجاره ادوات کشاورزی.

## وابستگی‌ها

```text
Auth
Geo
Media/Documents
Verification/Contracts
Finance/Payment
Notification
Admin Panel
```

## تعریف موجر

موجر یعنی کاربری که ادوات کشاورزی خود را اجاره می‌دهد:

```text
با راننده
بدون راننده
```

## جدول‌های اصلی پیشنهادی

```text
service_provider_profiles
service_categories
service_items
service_item_images
service_requests
service_request_status_logs
```

در صورت نیاز به تفکیک دقیق اجاره ادوات:

```text
rental_equipment
rental_requests
rental_pricing_rules
```

## APIهای اصلی

```text
GET /api/v1/services/categories
GET /api/v1/services/items
GET /api/v1/services/items/{id}
POST /api/v1/services/items
PATCH /api/v1/services/items/{id}
POST /api/v1/services/requests
GET /api/v1/services/requests/me
```

## Admin API

```text
GET /api/v1/admin/services/categories
POST /api/v1/admin/services/categories
PATCH /api/v1/admin/services/categories/{id}

GET /api/v1/admin/services/items
POST /api/v1/admin/services/items/{id}/approve
POST /api/v1/admin/services/items/{id}/reject
```

## Notification Events

```text
SERVICE_PROVIDER_APPROVED
SERVICE_ITEM_CREATED
SERVICE_ITEM_APPROVED
SERVICE_ITEM_REJECTED
SERVICE_REQUEST_CREATED
SERVICE_REQUEST_ACCEPTED
SERVICE_REQUEST_COMPLETED
SERVICE_REQUEST_CANCELLED
```

## Definition of Done

```text
ادمین بتواند دسته خدمات اضافه کند.
کاربر بتواند درخواست خدمات‌دهنده/موجر شدن بدهد.
مدارک و قرارداد بررسی شوند.
خدمت یا تجهیز ثبت شود.
درخواست خدمت ثبت شود.
فاکتور و کمیسیون برای خدمت آماده باشد.
نوتیفیکیشن‌ها کار کنند.
```

---

# 21. Legacy Module Note — Consultants Core

## هدف

ساخت هسته مشاوران کشاورزی.

## وابستگی‌ها

```text
Auth
Media/Documents
Verification/Contracts
Finance/Payment
Notification
Admin Panel
```

## جدول‌های اصلی

```text
consult_profiles
consult_specialties
consult_profile_specialties
consult_requests
consult_request_status_logs
```

## APIهای اصلی

```text
GET /api/v1/consultants/specialties
GET /api/v1/consultants
GET /api/v1/consultants/{id}
POST /api/v1/consultants/requests
GET /api/v1/consultants/requests/me
```

## Admin API

```text
GET /api/v1/admin/consultants/specialties
POST /api/v1/admin/consultants/specialties
PATCH /api/v1/admin/consultants/specialties/{id}

GET /api/v1/admin/consultants
POST /api/v1/admin/consultants/{id}/approve
POST /api/v1/admin/consultants/{id}/reject
```

## Notification Events

```text
CONSULTANT_REQUEST_SUBMITTED
CONSULTANT_APPROVED
CONSULTANT_REJECTED
CONSULT_REQUEST_CREATED
CONSULT_REQUEST_ACCEPTED
CONSULT_REQUEST_COMPLETED
CONSULT_REQUEST_CANCELLED
```

## Definition of Done

```text
ادمین بتواند تخصص مشاور اضافه کند.
کاربر بتواند درخواست مشاور شدن بدهد.
مدارک و قرارداد مشاور بررسی شوند.
مشاور تأییدشده در لیست نمایش داده شود.
کاربر بتواند درخواست مشاوره ثبت کند.
فاکتور و کمیسیون مشاوره آماده باشد.
نوتیفیکیشن‌ها کار کنند.
```

---

# 22. Legacy Module Note — Weather Core

## هدف

ساخت آب‌وهوا و هشدارهای کشاورزی.

## وابستگی‌ها

```text
Geo
Notification
Redis
```

## جدول‌های اصلی

```text
weather_locations
weather_cache
weather_user_locations
weather_alerts
```

## APIهای اصلی

```text
GET /api/v1/weather/current?city_id=
GET /api/v1/weather/forecast?city_id=
GET /api/v1/weather/alerts?city_id=
POST /api/v1/weather/user-location
```

## Notification Events

```text
WEATHER_ALERT
FROST_WARNING
RAIN_WARNING
HEAT_WARNING
WIND_WARNING
DUST_WARNING
```

## Definition of Done

```text
آب‌وهوا بر اساس شهر یا مختصات دریافت شود.
نتیجه در Redis کش شود.
هشدار آب‌وهوایی ثبت شود.
برای هشدار مهم Push/In-App/SMS ارسال شود.
```

---

# 23. Active Module — Barzegar AI / RAG Core

Official product name: **Barzegar (برزگر)**. Phase 21 is farmer-focused and
resumed after the Phase 24 Farm Management and Phase 25 Subscription releases.
The authoritative real-state boundary and 16-step implementation sequence are
in `docs/ai/phase-21-barzegar-real-state-audit.md`.

## هدف

ساخت هسته هوش مصنوعی و پاسخ‌گویی کشاورزی.

## وابستگی‌ها

```text
Auth
Billing/Subscription
Notification
Geo در بعضی intentها
```

## جدول‌های اصلی

```text
ai_requests
ai_feedback
ai_usage_logs
ai_knowledge_sources
```

## APIهای اصلی

```text
POST /api/v1/ai/ask
GET /api/v1/ai/requests/me
POST /api/v1/ai/feedback
```

## Admin API

```text
GET /api/v1/admin/ai/requests
GET /api/v1/admin/ai/feedback
GET /api/v1/admin/ai/knowledge-sources
POST /api/v1/admin/ai/knowledge-sources
```

## Notification Events

```text
AI_REQUEST_CREATED
AI_ANSWER_READY
AI_LIMIT_REACHED
AI_FEEDBACK_RECEIVED
```

## Definition of Done

```text
کاربر بتواند سؤال بپرسد.
مصرف AI ثبت شود.
محدودیت اشتراک اعمال شود.
پاسخ با منبع برگردد.
feedback ثبت شود.
نوتیفیکیشن آماده شدن پاسخ ارسال شود.
```

---

# 24. Legacy Module Note — Social Core

## هدف

ساخت فضای اجتماعی کشاورزی.

## وابستگی‌ها

```text
Auth
Media
Notification
Admin Panel
Moderation
```

## جدول‌های اصلی

```text
social_posts
social_post_media
social_comments
social_likes
social_reports
social_moderation_logs
```

## APIهای اصلی

```text
GET /api/v1/social/posts
POST /api/v1/social/posts
GET /api/v1/social/posts/{id}
POST /api/v1/social/posts/{id}/comments
POST /api/v1/social/posts/{id}/like
POST /api/v1/social/posts/{id}/report
```

## Admin API

```text
GET /api/v1/admin/social/posts
POST /api/v1/admin/social/posts/{id}/remove
GET /api/v1/admin/social/reports
POST /api/v1/admin/social/reports/{id}/resolve
```

## Notification Events

```text
POST_CREATED
COMMENT_CREATED
POST_LIKED
POST_REPORTED
POST_REMOVED
USER_BLOCKED
```

## Definition of Done

```text
کاربر بتواند پست ایجاد کند.
تصویر به پست وصل شود.
کامنت و لایک ثبت شود.
گزارش تخلف ثبت شود.
ادمین بتواند محتوا را حذف/بررسی کند.
نوتیفیکیشن کامنت و لایک ارسال شود.
```

---

# 25. Legacy Module Note — Data Access / BI

## هدف

ساخت دسترسی داده کنترل‌شده برای شرکت‌ها و سازمان‌ها.

## وابستگی‌ها

```text
Auth
Contracts
Admin
Reports
Audit
Notification
```

## جدول‌های اصلی

```text
data_clients
data_access_contracts
data_access_plans
data_access_permissions
data_exports
data_access_logs
```

## APIهای اصلی

```text
GET /api/v1/data-access/exports
POST /api/v1/data-access/exports/request
GET /api/v1/data-access/exports/{id}
```

## Admin API

```text
GET /api/v1/admin/data-clients
POST /api/v1/admin/data-clients
PATCH /api/v1/admin/data-clients/{id}/status

GET /api/v1/admin/data-access/contracts
GET /api/v1/admin/data-access/logs
POST /api/v1/admin/data-access/exports/{id}/approve
```

## Notification Events

```text
DATA_CLIENT_APPROVED
DATA_ACCESS_GRANTED
DATA_ACCESS_REVOKED
DATA_EXPORT_REQUESTED
DATA_EXPORT_READY
```

## Definition of Done

```text
شرکت طرف قرارداد قابل تعریف باشد.
قرارداد داده ثبت شود.
سطح دسترسی مشخص باشد.
export داده لاگ شود.
داده حساس بدون مجوز قابل دسترسی نباشد.
نوتیفیکیشن آماده شدن خروجی ارسال شود.
```

---

# 26. Legacy Module Note — Advanced Payment / Settlement

## هدف

تکمیل سیستم مالی پیشرفته.

## وابستگی‌ها

```text
Finance Core
Payment Core
Store
Services
Consultants
Admin
Notification
```

## امکانات

```text
Wallet
Settlement
Payout requests
Refund
Multi-gateway
Financial reports
```

## جدول‌های تکمیلی

```text
finance_wallets
finance_settlements
finance_payout_requests
finance_refunds
```

## Notification Events

```text
SETTLEMENT_CREATED
SETTLEMENT_PAID
PAYOUT_REQUESTED
PAYOUT_APPROVED
PAYOUT_REJECTED
REFUND_CREATED
REFUND_PAID
```

## Definition of Done

```text
کیف پول داخلی آماده باشد.
تسویه فروشگاه/مشاور/موجر قابل ثبت باشد.
درخواست برداشت قابل مدیریت باشد.
Refund پایه آماده باشد.
گزارش مالی پایه وجود داشته باشد.
```

---

# 27. Legacy Module Note — Reports / Analytics

## هدف

ساخت گزارش‌ها و تحلیل‌های مدیریتی.

## وابستگی‌ها

```text
Admin
Finance
Store
Services
Consultants
AI
Social
Data Access
```

## جدول‌های اصلی

```text
report_jobs
report_exports
```

## گزارش‌های مهم

```text
گزارش فروش
گزارش کمیسیون
گزارش پرداخت
گزارش تبلیغات
گزارش کاربران
گزارش فروشگاه‌ها
گزارش خدمات
گزارش مشاوران
گزارش AI
گزارش Social
گزارش Geo
```

## Definition of Done

```text
ادمین بتواند گزارش پایه ببیند.
گزارش قابل export باشد.
گزارش‌های سنگین به job صفی بروند.
دسترسی گزارش‌ها permission-based باشد.
```

---

# 28. وابستگی کلی ماژول‌ها

```text
Auth
  → Profile
  → Geo
  → Notification
  → Media/Documents
  → Verification/Contracts
  → Billing
  → Finance
  → Store
  → Services
  → Consultants
  → AI
  → Social

Geo
  → Store
  → Services/Rental
  → Weather
  → Social
  → Data Access

Notification
  → همه ماژول‌ها

Media/Documents
  → Profile
  → Store
  → Services
  → Consultants
  → Social
  → Contracts

Verification/Contracts
  → Store
  → Services/Rental
  → Consultants
  → Data Access

Finance/Payment/Commission
  → Store
  → Promotion
  → Services/Rental
  → Consultants
  → Subscription

Admin
  → همه ماژول‌ها
```

---

# 29. اولویت MVP v1

MVP v1 تا این فازها را شامل می‌شود:

```text
Phase 1: Repository + Documentation Foundation
Phase 2: Backend Foundation
Phase 3: Flutter Foundation
Phase 4: Admin Panel Foundation
Phase 5: Auth / Users / Roles / Permissions
Phase 6: Geo Core
Phase 7: Store Foundation
Phase 8: Product / Catalog Foundation
Phase 9: Cart / Orders / Payments / Commission
Phase 10: Media / File Upload / Storage
Phase 11: Notifications Foundation
```

بعد از MVP v1:

```text
Phase 12: Weather Foundation
Phase 13: Social / Community Foundation
Phase 14: Services Module
Phase 15: Consultants Module
Phase 16: Equipment / Rental
Phase 17: Category Management
Phase 18: Search / Filters / Discovery
Phase 19: Reviews / Ratings / Reports
Phase 20: Wallet / Settlement / Accounting
Phase 21: AI / RAG Assistant Integration
Phase 22: Production Hardening / Deployment
Phase 23: Role-Based My Activity Center
Phase 24: Farm Management / Digital Farm Profiles
```

---

# 30. قانون نهایی اجرای Roadmap

هیچ تیمی نباید وارد فاز بعدی شود مگر اینکه فاز قبلی:

```text
پیاده‌سازی شده باشد
تست شده باشد
مستند شده باشد
Review شده باشد
Tag خورده باشد
دمو شده باشد
```

اگر یک فاز ناقص باشد و تیم وارد فاز بعدی شود، پروژه دوباره شلوغ و شکننده می‌شود.

## Roadmap Maintenance Rule

Whenever a new phase, phase order change, or material scope change is defined,
the related roadmap and scope documents must be updated in the same change set.
The decision must not live only in chat or task notes.
