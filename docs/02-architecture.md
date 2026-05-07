# 02 — Architecture
# معماری فنی پروژه فارم نت

## 1. هدف سند

این سند معماری فنی پروژه «فارم نت» را مشخص می‌کند.

هدف این سند این است که تمام تیم‌ها طبق یک ساختار واحد کار کنند:

- تیم Backend
- تیم Flutter App
- تیم Flutter Web Admin
- تیم DevOps
- تیم QA
- تیم مستندات

هیچ تیمی نباید خارج از این معماری، ساختار جداگانه یا تصمیم فنی مستقل ایجاد کند مگر اینکه ابتدا در جلسه فنی بررسی و در این سند ثبت شود.

---

## 2. معماری کلان پروژه

معماری انتخاب‌شده برای شروع پروژه:

```text
Modular Monolith
```

یعنی:

```text
یک Backend واحد
یک دیتابیس MySQL واحد
ماژول‌بندی داخلی تمیز
یک API استاندارد
امکان جداسازی ماژول‌ها در آینده
```

در این مرحله از Microservices استفاده نمی‌کنیم.

### دلیل عدم استفاده از Microservices در شروع

Microservices در این مرحله باعث پیچیدگی غیرضروری می‌شود:

```text
چند دیتابیس
چند deploy
ارتباط بین سرویس‌ها
دیباگ سخت‌تر
تراکنش‌های پیچیده
نیاز به DevOps سنگین‌تر
هماهنگی سخت‌تر بین تیم‌ها
```

برای MVP، Modular Monolith بهترین انتخاب است.

---

## 3. تکنولوژی‌ها

### Backend

```text
Language: Python
Framework: FastAPI
ORM: SQLAlchemy
Migration: Alembic
Database: MySQL
Cache/Queue: Redis
API Docs: OpenAPI / Swagger
Auth: JWT + Refresh Token + OTP
```

### Frontend Mobile

```text
Framework: Flutter
State Management: Riverpod
UI System: finalui
Responsive Pattern: LSM
Localization: fa / en
Theme: Light / Dark
```

### Admin Panel

```text
Framework: Flutter Web
State Management: Riverpod
Access: Admin / Role-based
```

### Infrastructure

```text
Docker
Docker Compose
Nginx
SSL
MySQL
Redis
Storage
Backup scripts
```

---

## 4. ساختار Monorepo

ساختار اصلی پروژه:

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

توضیح پوشه‌ها:

```text
backend/
کد FastAPI، دیتابیس، ماژول‌ها، APIها، تست‌ها

mobile/
اپ Flutter برای کاربران

admin-panel/
پنل ادمین Flutter Web

docs/
مستندات رسمی پروژه

infra/
Docker، Nginx، MySQL، Redis، فایل‌های استقرار

scripts/
اسکریپت‌های بکاپ، seed، migration، deploy

postman/
collectionهای تست API

README.md
راهنمای اصلی پروژه

.env.example
نمونه متغیرهای محیطی بدون اطلاعات حساس
```

---

## 5. ساختار Backend

ساختار پیشنهادی Backend:

```text
backend/
  app/
    main.py

    core/
      config.py
      database.py
      security.py
      exceptions.py
      responses.py
      logging.py
      pagination.py
      permissions.py
      dependencies.py

    common/
      constants.py
      enums.py
      utils/
        dates.py
        money.py
        phone.py
        files.py
        slug.py
        text.py
        trace.py

    modules/
      auth/
      profile/
      geo/
      notification/
      media/
      verification/
      contracts/
      admin/
      billing/
      commission/
      finance/
      store/
      promotion/
      services/
      consultants/
      weather/
      ai/
      social/
      data_access/
      reports/

    db/
      base.py
      session.py

    tests/

  alembic/
  Dockerfile
  pyproject.toml
  .env.example
```

---

## 6. قانون ساختار هر ماژول Backend

هر ماژول باید ساختار یکسان داشته باشد.

مثال برای ماژول `store`:

```text
modules/store/
  models.py
  schemas.py
  repository.py
  service.py
  router.py
  permissions.py
  events.py
  enums.py
  tests/
```

توضیح فایل‌ها:

```text
models.py
مدل‌های SQLAlchemy

schemas.py
مدل‌های Pydantic برای request/response

repository.py
ارتباط مستقیم با دیتابیس

service.py
منطق اصلی کسب‌وکار

router.py
endpointهای FastAPI

permissions.py
دسترسی‌های مربوط به ماژول

events.py
Notification Eventهای ماژول

enums.py
statusها و enumهای داخلی ماژول

tests/
تست‌های مربوط به ماژول
```

---

## 7. قانون لایه‌بندی Backend

قانون اصلی:

```text
Router → Service → Repository → Database
```

### Router

وظیفه Router:

```text
دریافت request
اعتبارسنجی schema
گرفتن current_user
صدا زدن service
برگرداندن response استاندارد
```

Router نباید منطق سنگین داشته باشد.

### Service

وظیفه Service:

```text
اجرای business logic
بررسی permission
بررسی subscription
تغییر status
محاسبه commission
ساخت notification event
ثبت audit log
```

### Repository

وظیفه Repository:

```text
query به دیتابیس
create/update/delete
فیلتر
pagination
```

Repository نباید تصمیم کسب‌وکاری بگیرد.

---

## 8. استاندارد Response API

تمام APIها باید یک فرمت ثابت داشته باشند.

### Success Response

```json
{
  "success": true,
  "data": {},
  "message": "OK",
  "meta": {
    "trace_id": "abc-123"
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product not found"
  },
  "meta": {
    "trace_id": "abc-123"
  }
}
```

### Pagination Response

```json
{
  "success": true,
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 240,
    "trace_id": "abc-123"
  }
}
```

---

## 9. استاندارد Error Code

Error codeها باید ثابت، قابل فهم و انگلیسی باشند.

نمونه:

```text
AUTH_INVALID_CREDENTIALS
AUTH_TOKEN_EXPIRED
USER_NOT_FOUND
SHOP_NOT_APPROVED
SHOP_ALREADY_EXISTS
PRODUCT_NOT_FOUND
PRODUCT_NOT_APPROVED
DOCUMENT_REQUIRED
VERIFICATION_PENDING
CONTRACT_NOT_ACCEPTED
PAYMENT_VERIFY_FAILED
COMMISSION_RULE_NOT_FOUND
NOTIFICATION_SEND_FAILED
```

قانون:

```text
پیام نمایشی به کاربر در Flutter ترجمه می‌شود.
Backend error code استاندارد می‌دهد.
```

---

## 10. احراز هویت و امنیت

### روش‌های ورود

MVP از دو روش پشتیبانی می‌کند:

```text
شماره موبایل + OTP
ایمیل + رمز عبور
```

### Token

```text
Access Token
Refresh Token
```

### قوانین امنیتی

```text
رمز عبور باید hash شود.
OTP زمان انقضا داشته باشد.
Refresh token باید قابل revoke باشد.
هر session باید قابل مدیریت باشد.
Rate limit برای OTP اجباری است.
لاگ‌های حساس نباید رمز، OTP یا token کامل را ذخیره کنند.
```

---

## 11. نقش‌ها و دسترسی‌ها

سیستم باید Role-Based و Permission-Based باشد.

یعنی فقط role کافی نیست؛ permission هم لازم است.

### جدول‌ها

```text
auth_roles
auth_permissions
auth_user_roles
auth_role_permissions
```

### مثال Role

```text
super_admin
admin
support
shop_owner
shop_manager
staff
consultant
service_provider
user
```

### مثال Permission

```text
users.read
users.update_status
shops.approve
shops.reject
products.approve
products.reject
commission.update
invoices.read
notifications.send
contracts.manage
```

### قانون

```text
Endpointهای حساس باید permission check داشته باشند.
```

---

## 12. دیتابیس

Database:

```text
MySQL
```

ساختار:

```text
یک دیتابیس واحد
Prefix-based modular tables
```

مثال:

```text
auth_users
store_products
finance_invoices
notify_events
geo_cities
```

### قوانین دیتابیس

تمام جدول‌های مهم باید این فیلدها را داشته باشند:

```text
id
created_at
updated_at
```

برای موجودیت‌های قابل حذف نرم:

```text
deleted_at
```

برای موجودیت‌های دارای وضعیت:

```text
status
```

برای موجودیت‌های قابل audit:

```text
created_by
updated_by
```

---

## 13. Migration

تمام تغییرات دیتابیس باید با Alembic انجام شود.

قانون:

```text
هیچ تغییری مستقیم روی دیتابیس بدون migration مجاز نیست.
```

هر migration باید:

```text
نام واضح داشته باشد
در local تست شود
در staging تست شود
rollback آن بررسی شود
```

---

## 14. Geo Architecture

Geo یک هسته مشترک است.

جدول‌های اصلی:

```text
geo_provinces
geo_counties
geo_districts
geo_cities
geo_rural_districts
geo_villages
geo_addresses
```

آدرس‌ها باید generic باشند.

یعنی بتوانند به موجودیت‌های مختلف وصل شوند:

```text
user
shop
service
rental
consultant
invoice
order
```

مدل اتصال:

```text
target_type
target_id
```

فیلدهای آدرس:

```text
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
source: manual / map
is_default
```

---

## 15. Notification Architecture

نوتیفیکیشن یکی از هسته‌های اصلی سیستم است.

### کانال‌ها

```text
In-App
Push
SMS
Email
```

### Event با Delivery فرق دارد

Event یعنی اتفاق سیستم:

```text
SHOP_APPROVED
PRODUCT_REJECTED
INVOICE_ISSUED
PAYMENT_SUCCESS
WEATHER_ALERT
```

Delivery یعنی ارسال از کانال:

```text
In-App
Push
SMS
Email
```

### جریان ارسال

```text
Business Action
→ Create notify_event
→ Create notify_notification
→ Queue delivery job
→ Worker sends via channel
→ Save delivery_attempt
```

### جدول‌ها

```text
notify_events
notify_notifications
notify_templates
notify_channels
notify_user_preferences
notify_delivery_attempts
notify_device_tokens
```

### قانون کانال‌ها

همه eventها نباید SMS شوند.

```text
OTP: SMS
فاکتور: In-App + Push + Email
قرارداد: In-App + Email
پرداخت موفق: In-App + Push + SMS/Email
هشدار آب‌وهوایی مهم: Push + In-App + SMS در صورت ضرورت
```

---

## 16. Media و Document Architecture

Media و Documents باید جدا دیده شوند.

### Media

برای فایل‌های عمومی یا نمایشی:

```text
عکس پروفایل
عکس محصول
عکس فروشگاه
عکس پست اجتماعی
```

### Documents

برای مدارک رسمی:

```text
مدرک فروشگاه
مدرک مشاور
مدرک موجر
قرارداد PDF
مجوز فعالیت
```

### جدول‌ها

```text
media_files
media_documents
media_file_links
```

### قوانین فایل

```text
محدودیت حجم
محدودیت پسوند
تغییر نام فایل
ذخیره metadata
مالکیت فایل
visibility: public/private
عدم اجرای فایل آپلودی
```

### Storage در MVP

در MVP فایل‌ها روی سرور ذخیره می‌شوند.

در آینده قابل انتقال به:

```text
MinIO
S3-compatible storage
Cloud storage
```

---

## 17. Verification و Contracts Architecture

فعالیت حرفه‌ای نیازمند تأیید است:

```text
فروشگاه
موجر
خدمات‌دهنده
مشاور
شرکت داده
```

### Verification Flow

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

### جدول‌ها

```text
verification_requests
verification_review_logs
contract_templates
contract_acceptances
```

### قرارداد

قرارداد باید version داشته باشد.

پشتیبانی MVP:

```text
تیک پذیرش قرارداد
آپلود PDF امضاشده
ثبت IP
ثبت user_agent
ثبت accepted_at
```

---

## 18. Finance / Payment / Commission Architecture

پرداخت آنلاین از MVP وجود دارد.

### بخش‌های اصلی

```text
Invoice
Payment Attempt
Payment Verify
Transaction
Commission
```

### جدول‌ها

```text
finance_invoices
finance_invoice_items
finance_commissions
finance_transactions
payment_gateways
payment_attempts
commission_rules
commission_snapshots
```

### کمیسیون

کمیسیون باید هنگام صدور فاکتور snapshot شود.

```text
commission_rule_id
commission_percent_snapshot
commission_amount
platform_amount
provider_amount
```

### جریان پرداخت

```text
Create invoice
→ Calculate commission
→ Create payment_attempt
→ Redirect to gateway
→ Gateway callback
→ Verify payment
→ Mark invoice paid
→ Create transaction
→ Create notification
→ Audit log
```

### قانون مهم

```text
هیچ فاکتوری نباید بعد از پرداخت، کمیسیونش بر اساس rule جدید تغییر کند.
```

---

## 19. Store Architecture

هر کاربر فقط یک فروشگاه می‌تواند داشته باشد.

اما فروشگاه می‌تواند چند عضو داشته باشد.

### جدول‌ها

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

### وضعیت فروشگاه

```text
draft
pending_review
approved
rejected
suspended
closed
```

### وضعیت محصول

```text
draft
pending_review
published
rejected
inactive
deleted
```

### جریان ثبت فروشگاه

```text
User creates shop request
→ Upload documents
→ Accept contract
→ Admin review
→ Approved / Rejected / Needs revision
→ Notification
```

### جریان محصول

```text
Shop creates product
→ Upload images
→ Submit for review
→ Admin approves/rejects
→ Product visible publicly if approved
→ Notification
```

---

## 20. Promotion / Ladder Architecture

تبلیغات و نردبان یک ماژول درآمدی مستقل است.

### جدول‌ها

```text
promotion_packages
promotions
promotion_slots
promotion_payments
```

### موارد قابل تبلیغ

```text
shop
product
service
equipment
consultant
article
```

### جایگاه‌ها

```text
home_top
category_top
city_top
search_top
recommended
```

### قانون

تبلیغ فقط روی رتبه نمایش اثر می‌گذارد، نه روی داده اصلی.

---

## 21. Services / Rental Architecture

این ماژول بعد از Store Core کامل می‌شود.

موجر یعنی کاربری که ادوات کشاورزی را کرایه می‌دهد:

```text
با راننده
بدون راننده
```

خدمات شامل تمام خدمات مرتبط با کشاورزی است.

دسته‌بندی خدمات باید از پنل ادمین مدیریت شود.

### جدول‌های احتمالی

```text
service_provider_profiles
service_categories
service_items
service_item_images
service_requests
service_request_status_logs
```

در صورت نیاز برای اجاره ادوات جداگانه:

```text
rental_equipment
rental_requests
rental_pricing_rules
```

---

## 22. Consultants Architecture

مشاوران بر اساس تخصص فعالیت می‌کنند.

تخصص‌ها باید از پنل ادمین مدیریت شوند.

### جدول‌ها

```text
consult_profiles
consult_specialties
consult_profile_specialties
consult_requests
consult_request_status_logs
```

فعال شدن مشاور نیازمند:

```text
مدارک
قرارداد
تأیید ادمین
```

---

## 23. Weather Architecture

Weather وابسته به Geo است.

### وظایف

```text
دریافت آب‌وهوا بر اساس شهر یا مختصات
کش کردن نتیجه در Redis
نمایش پیش‌بینی کوتاه
هشدارهای مهم
نوتیفیکیشن هشدار آب‌وهوا
```

### جدول‌ها

```text
weather_locations
weather_cache
weather_user_locations
weather_alerts
```

---

## 24. AI / RAG Architecture

AI بعد از هسته‌های اصلی اضافه می‌شود.

### وظایف

```text
ثبت سؤال کاربر
تشخیص intent
اتصال به RAG
برگشت پاسخ با منبع
ثبت مصرف
محدودیت بر اساس اشتراک
ثبت feedback
نوتیفیکیشن آماده شدن پاسخ
```

### جدول‌ها

```text
ai_requests
ai_feedback
ai_usage_logs
ai_knowledge_sources
```

---

## 25. Social Architecture

Social بعد از هسته‌های اصلی اضافه می‌شود.

باید از اول moderation داشته باشد.

### جدول‌ها

```text
social_posts
social_post_media
social_comments
social_likes
social_reports
social_moderation_logs
```

### قوانین

```text
گزارش تخلف
حذف توسط ادمین
تعلیق کاربر
وضعیت انتشار
نوتیفیکیشن کامنت/لایک
```

---

## 26. Data Access Architecture

دسترسی داده باید قراردادی، سطح‌بندی‌شده و لاگ‌شده باشد.

### جدول‌ها

```text
data_clients
data_access_contracts
data_access_plans
data_access_permissions
data_exports
data_access_logs
```

### قانون

داده حساس کاربران نباید بدون کنترل، قرارداد، سطح دسترسی و لاگ قابل دسترسی باشد.

---

## 27. Flutter Mobile Architecture

ساختار Flutter App:

```text
mobile/
  lib/
    main.dart
    app.dart

    core/
      config/
      routing/
      theme/
      localization/
      network/
      storage/
      responsive/
      errors/
      utils/
      widgets/

    features/
      auth/
      profile/
      geo/
      notification/
      store/
      shop_panel/
      payment/
      promotion/
      services/
      consultants/
      weather/
      ai/
      social/
```

### قوانین UI

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
اعداد فارسی در فارسی
تاریخ شمسی
تومان
```

### Feature Structure

هر feature:

```text
features/store/
  data/
  domain/
  presentation/
```

یا برای ساده‌سازی MVP:

```text
features/store/
  models/
  services/
  providers/
  screens/
  widgets/
```

تصمیم نهایی باید در شروع Flutter Foundation گرفته شود.
پیشنهاد فعلی: ساختار ساده و feature-first، نه Clean Architecture سنگین.

---

## 28. Flutter Web Admin Architecture

ساختار Admin:

```text
admin-panel/
  lib/
    main.dart
    app.dart

    core/
      routing/
      theme/
      localization/
      network/
      auth/
      permissions/
      widgets/

    features/
      dashboard/
      users/
      roles/
      shops/
      products/
      categories/
      documents/
      contracts/
      billing/
      commission/
      finance/
      notifications/
      promotions/
      settings/
      audit_logs/
```

### قوانین Admin

```text
ادمین باید role-based باشد.
هر صفحه باید permission guard داشته باشد.
هر عملیات مهم باید audit log ایجاد کند.
صفحات باید table، filter، search و pagination داشته باشند.
فرم‌ها باید validation داشته باشند.
```

---

## 29. Helperهای مشترک Backend

```text
standard_response()
standard_error()
paginate()
normalize_phone()
validate_email()
check_permission()
check_feature_access()
check_subscription_limit()
validate_upload_file()
create_audit_log()
create_notification_event()
calculate_commission()
format_money_for_message()
generate_slug()
sanitize_text()
get_client_ip()
generate_trace_id()
```

قانون:

```text
Helper فقط وقتی ساخته شود که واقعاً در چند ماژول استفاده می‌شود.
```

---

## 30. Helperهای مشترک Flutter

```text
formatToman()
formatJalaliDate()
toPersianDigits()
toEnglishDigits()
localizedText()
apiErrorToMessage()
showAppSnackbar()
showConfirmDialog()
validatePhone()
validateRequired()
validatePrice()
pickImage()
uploadFile()
responsiveValue()
themeModeHelper()
directionalityHelper()
```

---

## 31. Logging و Trace ID

هر request باید trace_id داشته باشد.

### هدف

```text
دیباگ راحت‌تر
ردیابی خطا
ارتباط بین API، notification، payment و audit
```

### قانون

```text
هر error response باید trace_id برگرداند.
هر log مهم باید trace_id داشته باشد.
```

---

## 32. Audit Log

هر عملیات مهم ادمین باید audit شود.

### موارد مهم

```text
تغییر نقش
تأیید/رد مدرک
تأیید/رد فروشگاه
تغییر کمیسیون
تغییر پلن
تغییر وضعیت فاکتور
تعلیق کاربر
حذف یا رد محصول
```

### جدول

```text
admin_audit_logs
```

### فیلدهای مهم

```text
admin_user_id
action
target_type
target_id
old_value
new_value
ip_address
user_agent
created_at
```

---

## 33. Testing Architecture

### Backend Tests

```text
unit tests
integration tests
permission tests
auth tests
payment verify tests
commission calculation tests
notification event tests
file upload tests
```

### Flutter Tests

```text
widget tests
provider tests
localization tests
error mapping tests
responsive sanity tests
```

### Manual Tests

Postman collection برای هر ماژول باید ساخته شود.

---

## 34. Deployment Architecture

MVP با Docker Compose اجرا می‌شود.

سرویس‌ها:

```text
backend
mysql
redis
nginx
admin-panel
mobile-web-build اگر نیاز باشد
worker
```

### Worker

برای کارهای صفی:

```text
notification delivery
email sending
sms sending
payment async checks
report jobs
```

---

## 35. Backup Architecture

بکاپ‌های لازم:

```text
MySQL database
uploaded files/storage
.env files به صورت امن
SSL certificates
docs
postman collections
```

قانون:

```text
بکاپی که ریستور آن تست نشده باشد، بکاپ واقعی نیست.
```

---

## 36. Security Architecture

قوانین پایه:

```text
.env داخل Git ممنوع
JWT امن
Refresh token قابل revoke
OTP rate limit
Password hashing
Permission check
File upload validation
CORS محدود
Admin audit log
Sensitive data masking in logs
SQL injection protection with ORM
Text sanitization for social/content
```

---

## 37. تصمیم‌های باز

مواردی که هنوز باید انتخاب شوند:

```text
Payment Gateway
SMS Provider
Email Provider
Push Provider
Geo Data Source
Storage Strategy: local server یا MinIO/S3
Admin panel repo strategy: جدا یا داخل monorepo
```

پیشنهاد پیش‌فرض:

```text
Payment: Zarinpal یا Zibal
SMS: Kavenegar یا Melipayamak
Email: SMTP
Push: Firebase Cloud Messaging
Storage MVP: local server
Storage later: MinIO/S3
Admin: داخل monorepo با پروژه جدا
```

---

## 38. نتیجه معماری

معماری پروژه باید این ویژگی‌ها را داشته باشد:

```text
قابل توسعه
قابل تست
قابل مدیریت توسط چند تیم
قابل مستندسازی
قابل backup و restore
قابل deploy
دارای API استاندارد
دارای دیتابیس منظم
دارای UI چندزبانه و ریسپانسیو
دارای notification core
دارای payment core
دارای admin control center
```

این سند باید قبل از شروع کدنویسی توسط تمام تیم‌ها خوانده و تأیید شود.
