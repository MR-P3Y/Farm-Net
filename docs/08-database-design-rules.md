# 08 — Database Design Rules
# قوانین طراحی دیتابیس پروژه فارم نت

## 1. هدف سند

این سند قوانین طراحی دیتابیس پروژه «فارم نت» را مشخص می‌کند.

چون پروژه چندماژولی و چندتیمی است، اگر دیتابیس از ابتدا قانون نداشته باشد، بعداً با این مشکلات روبه‌رو می‌شویم:

```text
نام‌گذاری شلخته جدول‌ها
رابطه‌های نامشخص
migrationهای ناسازگار
statusهای متفاوت
فیلدهای تکراری
نبود index
نبود audit
حذف اشتباه داده‌ها
مشکل در گزارش‌گیری
سخت شدن توسعه ماژول‌های جدید
```

هدف این سند این است که تمام تیم‌ها دیتابیس را با یک استاندارد واحد طراحی کنند.

---

# 2. نوع دیتابیس

دیتابیس انتخاب‌شده:

```text
MySQL
```

معماری دیتابیس:

```text
یک دیتابیس واحد
ماژول‌بندی با prefix جدول‌ها
```

مثال:

```text
auth_users
store_products
finance_invoices
notify_events
geo_cities
```

---

# 3. چرا یک دیتابیس واحد؟

در MVP و شروع پروژه، یک دیتابیس واحد بهترین انتخاب است.

دلایل:

```text
سادگی توسعه
سادگی transaction
سادگی backup و restore
رابطه‌های واضح‌تر
هماهنگی بهتر تیم‌ها
کاهش پیچیدگی DevOps
```

در آینده اگر پروژه بسیار بزرگ شد، بعضی بخش‌ها مثل AI، Reports، Notifications یا Data Access قابل جداسازی هستند.

---

# 4. قانون prefix جدول‌ها

هر جدول باید prefix ماژول خودش را داشته باشد.

## Prefixهای اصلی

```text
auth_
profile_
geo_
media_
verification_
contract_
admin_
billing_
commission_
finance_
payment_
notify_
store_
promotion_
service_
consult_
weather_
ai_
social_
data_
report_
system_
```

## مثال درست

```text
auth_users
auth_roles
store_shops
store_products
finance_invoices
notify_notifications
geo_provinces
```

## مثال غلط

```text
users
products
orders
notifications
settings
```

چرا غلط است؟
چون وقتی پروژه بزرگ شود معلوم نیست هر جدول متعلق به کدام ماژول است.

---

# 5. قانون نام‌گذاری جدول‌ها

نام جدول‌ها باید:

```text
انگلیسی
lowercase
snake_case
جمع یا مفهومی واضح
دارای prefix ماژول
```

مثال:

```text
store_products
store_product_images
finance_invoice_items
auth_user_roles
consult_profile_specialties
```

نام‌هایی مثل این ممنوع هستند:

```text
tblUser
ProductTable
userData
new_products
test_table
```

---

# 6. قانون نام‌گذاری ستون‌ها

ستون‌ها باید:

```text
انگلیسی
lowercase
snake_case
واضح
بدون abbreviation مبهم
```

مثال درست:

```text
user_id
shop_id
created_at
updated_at
price_toman
commission_amount
verification_status
```

مثال غلط:

```text
uid
sid
crt
upd
p
comm
vstatus
```

اختصار فقط وقتی مجاز است که کاملاً رایج باشد؛ مثل:

```text
id
ip
url
otp
```

---

# 7. فیلدهای پایه مشترک

اکثر جدول‌های اصلی باید این فیلدها را داشته باشند:

```text
id
created_at
updated_at
```

برای جدول‌هایی که حذف نرم دارند:

```text
deleted_at
```

برای جدول‌هایی که وضعیت دارند:

```text
status
```

برای جدول‌هایی که توسط کاربر یا ادمین ساخته/ویرایش می‌شوند:

```text
created_by
updated_by
```

نمونه:

```sql
id BIGINT PRIMARY KEY AUTO_INCREMENT,
created_at DATETIME NOT NULL,
updated_at DATETIME NOT NULL,
deleted_at DATETIME NULL,
status VARCHAR(50) NOT NULL
```

---

# 8. نوع داده ID

برای MVP:

```text
BIGINT UNSIGNED AUTO_INCREMENT
```

پیشنهاد:

```text
id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT
```

چرا؟

```text
ساده است
با MySQL راحت است
برای MVP کافی است
برای تیم‌ها قابل فهم است
```

در آینده اگر نیاز به public id جدا داشتیم، می‌توانیم اضافه کنیم:

```text
public_id CHAR(36)
```

یا:

```text
uuid CHAR(36)
```

اما از اول همه‌چیز را با UUID پیچیده نمی‌کنیم مگر نیاز واقعی داشته باشیم.

---

# 9. تاریخ و زمان

تمام تاریخ‌ها در دیتابیس باید میلادی و UTC ذخیره شوند.

فرمت پیشنهادی:

```text
DATETIME
```

یا اگر تنظیمات timezone دقیق‌تر لازم شد:

```text
TIMESTAMP
```

قانون:

```text
Backend تاریخ را UTC ذخیره می‌کند.
Frontend آن را به شمسی نمایش می‌دهد.
```

مثال:

```text
created_at = 2026-05-06 12:30:00
```

نمایش در UI فارسی:

```text
۱۶ اردیبهشت ۱۴۰۵
```

---

# 10. پول و تومان

مبالغ باید عددی ذخیره شوند، نه string نمایشی.

مثال درست:

```text
price_toman BIGINT UNSIGNED
amount_toman BIGINT UNSIGNED
commission_amount_toman BIGINT UNSIGNED
platform_amount_toman BIGINT UNSIGNED
provider_amount_toman BIGINT UNSIGNED
```

مثال غلط:

```text
price = "۲۵۰٬۰۰۰ تومان"
```

قانون:

```text
Backend عدد خام ذخیره می‌کند.
Frontend نمایش تومان و اعداد فارسی را انجام می‌دهد.
```

---

# 11. وضعیت‌ها / Status

statusها باید string، lowercase و snake_case باشند.

مثال محصول:

```text
draft
pending_review
published
rejected
inactive
deleted
```

مثال فروشگاه:

```text
draft
pending_review
approved
rejected
suspended
closed
```

مثال فاکتور:

```text
draft
issued
paid
cancelled
refunded
settled
```

قانون:

```text
statusها باید در enumهای Backend تعریف شوند.
statusهای هر ماژول باید در docs/database یا docs/module-roadmap ثبت شوند.
```

---

# 12. Soft Delete

برای موجودیت‌های مهم حذف فیزیکی نکنیم.

به جای حذف:

```text
deleted_at = timestamp
status = deleted
```

موجودیت‌هایی که باید soft delete داشته باشند:

```text
users
profiles
shops
products
services
consultants
documents
posts
comments
promotions
```

جدول‌های لاگ و تراکنش معمولاً delete نمی‌شوند.

---

# 13. Audit و History

برای عملیات مهم باید history یا audit داشته باشیم.

## Audit کلی ادمین

```text
admin_audit_logs
```

## Status log برای موجودیت‌های مهم

مثلاً:

```text
store_product_status_logs
service_request_status_logs
consult_request_status_logs
```

این جدول‌ها باید ثبت کنند:

```text
از چه وضعیتی
به چه وضعیتی
توسط چه کسی
در چه زمانی
با چه دلیل
```

---

# 14. Foreign Key

تا جای ممکن باید رابطه‌ها با foreign key مشخص شوند.

مثال:

```text
store_products.shop_id → store_shops.id
store_shops.owner_user_id → auth_users.id
finance_invoices.user_id → auth_users.id
```

اما برای بعضی ارتباط‌های عمومی با target_type/target_id، foreign key مستقیم نداریم.

مثلاً:

```text
geo_addresses
media_file_links
notify_events
```

در این موارد باید با کد و تست مراقبت شود.

---

# 15. Polymorphic Relation

برای اتصال عمومی به چند نوع موجودیت، از این الگو استفاده می‌کنیم:

```text
target_type
target_id
```

مثال:

```text
geo_addresses:
target_type = shop
target_id = 10
```

یا:

```text
media_file_links:
target_type = product
target_id = 55
```

قانون:

```text
target_type باید enum باشد.
target_id باید index داشته باشد.
هر استفاده از target_type/target_id باید در service validation شود.
```

---

# 16. Index Rules

هر فیلدی که زیاد برای جستجو، فیلتر یا join استفاده می‌شود باید index داشته باشد.

## indexهای رایج

```text
user_id
shop_id
product_id
status
created_at
city_id
province_id
target_type + target_id
phone
email
```

## مثال‌ها

برای محصولات:

```text
shop_id
category_id
status
city_id
created_at
```

برای نوتیفیکیشن‌ها:

```text
user_id
is_read
created_at
```

برای فاکتورها:

```text
user_id
status
created_at
```

برای پرداخت:

```text
invoice_id
gateway
authority
status
```

---

# 17. Unique Constraints

قوانین یکتا باید در دیتابیس enforce شوند، نه فقط در کد.

مثال:

```text
auth_users.phone UNIQUE
auth_users.email UNIQUE
store_shops.owner_user_id UNIQUE
```

چون تصمیم گرفته شد:

```text
هر کاربر فقط یک فروشگاه دارد.
```

پس باید در جدول فروشگاه:

```text
owner_user_id UNIQUE
```

برای کدهای تراکنش:

```text
payment_attempts.gateway_reference UNIQUE
```

برای idempotency:

```text
idempotency_key UNIQUE
```

یا ترکیبی با scope.

---

# 18. Idempotency در دیتابیس

برای عملیات حساس مالی باید idempotency ذخیره شود.

موارد:

```text
payment callbacks
payment verify
invoice creation
subscription checkout
promotion checkout
```

جدول پیشنهادی عمومی:

```text
system_idempotency_keys
```

یا در هر جدول حساس:

```text
idempotency_key
```

قانون:

```text
درخواست تکراری با همان idempotency_key نباید عملیات را دوباره انجام دهد.
```

---

# 19. جدول‌های Auth

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

## auth_users

فیلدهای پیشنهادی:

```text
id
phone
email
password_hash
status
is_phone_verified
is_email_verified
last_login_at
created_at
updated_at
deleted_at
```

قوانین:

```text
phone nullable اما unique
email nullable اما unique
حداقل یکی از phone یا email باید وجود داشته باشد
password_hash برای ورود ایمیلی لازم است
```

---

# 20. جدول‌های Profile

```text
profile_user_profiles
profile_user_preferences
```

## profile_user_profiles

```text
id
user_id
first_name
last_name
display_name
avatar_file_id
bio
province_id
city_id
created_at
updated_at
```

## profile_user_preferences

```text
id
user_id
language
theme_mode
notification_preferences
created_at
updated_at
```

---

# 21. جدول‌های Geo

```text
geo_provinces
geo_counties
geo_districts
geo_cities
geo_rural_districts
geo_villages
geo_addresses
```

## geo_addresses

```text
id
user_id
target_type
target_id
province_id
county_id
district_id
city_id
rural_district_id
village_id
address_line
postal_code
latitude
longitude
source
is_default
created_at
updated_at
deleted_at
```

source:

```text
manual
map
```

---

# 22. جدول‌های Notification

```text
notify_events
notify_notifications
notify_templates
notify_channels
notify_user_preferences
notify_delivery_attempts
notify_device_tokens
```

## notify_events

```text
id
event_type
actor_user_id
recipient_user_id
target_type
target_id
payload_json
trace_id
created_at
```

## notify_notifications

```text
id
user_id
event_id
title
body
data_json
is_read
read_at
created_at
```

## notify_delivery_attempts

```text
id
notification_id
channel
status
provider
provider_message_id
error_message
attempt_count
sent_at
created_at
```

channel:

```text
in_app
push
sms
email
```

---

# 23. جدول‌های Media و Documents

```text
media_files
media_documents
media_file_links
```

## media_files

```text
id
owner_user_id
file_name
original_name
mime_type
extension
size_bytes
storage_path
public_url
visibility
status
created_at
updated_at
deleted_at
```

visibility:

```text
public
private
```

## media_documents

```text
id
owner_user_id
document_type
file_id
target_type
target_id
status
reviewed_by
reviewed_at
rejection_reason
created_at
updated_at
```

---

# 24. جدول‌های Verification و Contracts

```text
verification_requests
verification_review_logs
contract_templates
contract_acceptances
```

## verification_requests

```text
id
user_id
target_type
target_id
status
submitted_at
reviewed_by
reviewed_at
rejection_reason
created_at
updated_at
```

target_type:

```text
shop
service_provider
lessor
consultant
data_client
```

## contract_templates

```text
id
title
type
version
language
content
is_active
created_at
updated_at
```

## contract_acceptances

```text
id
user_id
contract_template_id
target_type
target_id
accepted_at
ip_address
user_agent
signed_pdf_document_id
created_at
```

---

# 25. جدول‌های Billing

```text
billing_plans
billing_plan_features
billing_subscriptions
billing_feature_usage
```

## billing_plans

```text
id
name
code
module_scope
price_toman
duration_days
status
created_at
updated_at
```

## billing_subscriptions

```text
id
user_id
plan_id
status
starts_at
ends_at
created_at
updated_at
```

## billing_feature_usage

```text
id
user_id
feature_code
used_count
period_start
period_end
created_at
updated_at
```

---

# 26. جدول‌های Commission / Finance / Payment

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

## commission_rules

```text
id
module_scope
target_type
target_id
rate_type
rate_value
effective_from
effective_to
status
created_by
updated_by
created_at
updated_at
```

rate_type:

```text
percent
fixed
```

## finance_invoices

```text
id
user_id
target_type
target_id
invoice_number
status
total_amount_toman
currency
issued_at
paid_at
created_at
updated_at
```

## finance_commissions

```text
id
invoice_id
commission_rule_id
rate_type
rate_value_snapshot
commission_amount_toman
platform_amount_toman
provider_amount_toman
created_at
```

## payment_attempts

```text
id
invoice_id
gateway
amount_toman
status
authority
gateway_reference
idempotency_key
request_payload_json
callback_payload_json
verified_at
created_at
updated_at
```

---

# 27. جدول‌های Store

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

## store_shops

```text
id
owner_user_id
name
slug
description
logo_file_id
status
province_id
city_id
created_at
updated_at
deleted_at
```

قانون:

```text
owner_user_id UNIQUE
```

## store_shop_members

```text
id
shop_id
user_id
role
status
created_at
updated_at
```

role:

```text
owner
manager
staff
viewer
```

## store_products

```text
id
shop_id
category_id
title
slug
description
price_toman
currency
status
province_id
city_id
created_at
updated_at
deleted_at
```

---

# 28. جدول‌های Promotion

```text
promotion_packages
promotions
promotion_slots
promotion_payments
```

## promotion_packages

```text
id
title
target_type
placement
duration_days
price_toman
priority_weight
status
created_at
updated_at
```

## promotions

```text
id
user_id
target_type
target_id
package_id
starts_at
ends_at
status
created_at
updated_at
```

---

# 29. جدول‌های Services / Rental

```text
service_provider_profiles
service_categories
service_items
service_item_images
service_requests
service_request_status_logs
```

برای اجاره ادوات، اگر نیاز به تفکیک بیشتر شد:

```text
rental_equipment
rental_requests
rental_pricing_rules
```

نکته:

```text
در MVP v1 ماژول کامل Services/Rental ساخته نمی‌شود.
اما ساختار دیتابیس آن باید با Geo, Media, Verification, Contracts, Finance قابل اتصال باشد.
```

---

# 30. جدول‌های Consultants

```text
consult_profiles
consult_specialties
consult_profile_specialties
consult_requests
consult_request_status_logs
```

نکته:

```text
specialties باید از پنل ادمین قابل مدیریت باشد.
```

---

# 31. جدول‌های Weather

```text
weather_locations
weather_cache
weather_user_locations
weather_alerts
```

Weather بیشتر cache/API است و نباید دیتابیس سنگین غیرضروری ایجاد کند.

---

# 32. جدول‌های AI

```text
ai_requests
ai_feedback
ai_usage_logs
ai_knowledge_sources
```

قانون:

```text
هر request باید user_id، intent، usage و feedback قابل ردیابی داشته باشد.
```

---

# 33. جدول‌های Social

```text
social_posts
social_post_media
social_comments
social_likes
social_reports
social_moderation_logs
```

قانون:

```text
Social بدون report و moderation نباید منتشر شود.
```

---

# 34. جدول‌های Data Access

```text
data_clients
data_access_contracts
data_access_plans
data_access_permissions
data_exports
data_access_logs
```

قانون:

```text
هر export یا access باید log شود.
داده حساس نباید بدون permission و contract خارج شود.
```

---

# 35. JSON Columns

برای payloadهای انعطاف‌پذیر می‌توان از JSON استفاده کرد.

موارد مجاز:

```text
notify_events.payload_json
payment_attempts.request_payload_json
payment_attempts.callback_payload_json
admin_audit_logs.old_value
admin_audit_logs.new_value
data_exports.filters_json
```

قانون:

```text
JSON برای داده‌های اصلی و قابل query زیاد استفاده نشود.
اگر فیلدی زیاد فیلتر می‌شود، ستون جدا داشته باشد.
```

---

# 36. Enumها

Enumها در Backend تعریف شوند و در دیتابیس به صورت string ذخیره شوند.

مثال:

```text
status VARCHAR(50)
```

مزیت:

```text
خوانایی بهتر
توسعه راحت‌تر
هماهنگی با API
```

---

# 37. Seed Data

برای داده‌های پایه باید seed script داشته باشیم.

موارد seed:

```text
roles
permissions
super_admin
geo data
notification templates
default commission rules
default billing plans
feature flags
system settings
```

مسیر پیشنهادی:

```text
scripts/seed/
```

---

# 38. Backup و Restore دیتابیس

قوانین:

```text
قبل از هر migration مهم backup گرفته شود.
قبل از deploy backup گرفته شود.
backup باید خارج از سرور اصلی ذخیره شود.
restore باید روی staging تست شود.
```

---

# 39. خط قرمزهای دیتابیس

موارد ممنوع:

```text
تغییر دستی production بدون migration
نام‌گذاری فارسی جدول یا ستون
جدول بدون prefix
حذف فیزیکی داده‌های مهم
مبلغ به صورت string
تاریخ شمسی در دیتابیس اصلی
statusهای بدون enum
نبود index روی فیلدهای پرتکرار
نبود unique constraint برای قوانین مهم
ذخیره secret یا token خام
ذخیره OTP خام بدون سیاست امنیتی
```

---

# 40. نتیجه

این سند استاندارد رسمی طراحی دیتابیس پروژه «فارم نت» است.

قانون نهایی:

```text
دیتابیس خوب یعنی قابل فهم، قابل migration، قابل تست، قابل گزارش‌گیری، قابل backup و قابل توسعه.
```
