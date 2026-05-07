# 10 — Notification Events
# رویدادها و نوتیفیکیشن‌های پروژه فارم نت

## 1. هدف سند

این سند استاندارد نوتیفیکیشن پروژه «فارم نت» را مشخص می‌کند.

نوتیفیکیشن در این پروژه یک قابلیت جانبی نیست؛ یکی از هسته‌های اصلی سیستم است.  
تمام بخش‌های مهم باید بتوانند رویداد تولید کنند و کاربر، فروشگاه، مشاور، موجر، ادمین یا شرکت طرف قرارداد را در زمان درست مطلع کنند.

هدف نوتیفیکیشن:

```text
برگرداندن کاربر به اپ
اطلاع‌رسانی وضعیت‌ها
کاهش نیاز به پیگیری دستی
افزایش اعتماد کاربر
کاهش کار پشتیبانی
اطلاع‌رسانی مالی و قراردادی
ارسال هشدارهای مهم
```

---

# 2. اصل بنیادین

در سیستم باید بین Event و Delivery تفاوت وجود داشته باشد.

## Event

یعنی اتفاقی که در سیستم رخ داده است.

مثال:

```text
SHOP_APPROVED
PRODUCT_REJECTED
INVOICE_ISSUED
PAYMENT_SUCCESS
WEATHER_ALERT
AI_ANSWER_READY
```

## Delivery

یعنی رساندن پیام از طریق یک کانال.

کانال‌ها:

```text
In-App
Push
SMS
Email
```

قانون:

```text
هر Event الزاماً از همه کانال‌ها ارسال نمی‌شود.
کانال ارسال براساس نوع، اهمیت، هزینه و تنظیمات کاربر انتخاب می‌شود.
```

---

# 3. کانال‌های نوتیفیکیشن

## 3.1 In-App Notification

اعلان داخل اپ.

موارد استفاده:

```text
تقریباً همه رویدادهای مهم
وضعیت مدارک
وضعیت فروشگاه
وضعیت محصول
فاکتور
پرداخت
کامنت
لایک
درخواست مشاوره
درخواست خدمات
```

قانون:

```text
In-App باید از MVP فعال باشد.
```

---

## 3.2 Push Notification

اعلان روی موبایل برای بازگرداندن کاربر به اپ.

موارد استفاده:

```text
تأیید/رد فروشگاه
تأیید/رد محصول
درخواست جدید برای فروشگاه
پرداخت موفق یا ناموفق
هشدار آب‌وهوا
درخواست مشاوره
کامنت مهم
پاسخ AI آماده شد
```

قانون:

```text
Push باید از ابتدا در معماری دیده شود.
در MVP ساختار device token و ارسال پایه آماده باشد.
```

---

## 3.3 SMS

پیامک فقط برای موارد مهم و حساس استفاده می‌شود.

موارد استفاده:

```text
OTP
هشدار امنیتی
پرداخت مهم
قرارداد مهم
تسویه مالی
هشدار آب‌وهوایی خیلی مهم
```

قانون:

```text
SMS برای رویدادهای ساده مثل لایک، کامنت، تأیید محصول عادی یا تبلیغات معمولی استفاده نمی‌شود.
SMS هزینه دارد و نباید بی‌رویه مصرف شود.
```

---

## 3.4 Email

ایمیل برای موارد رسمی، قراردادی و قابل بایگانی استفاده می‌شود.

موارد استفاده:

```text
قرارداد
فاکتور
رسید پرداخت
گزارش
دسترسی داده
اطلاعیه رسمی حساب
```

قانون:

```text
Email برای نسخه انگلیسی، کاربران سازمانی و شرکت‌های طرف قرارداد مهم است.
```

---

# 4. معماری فنی نوتیفیکیشن

جریان استاندارد:

```text
Business Action
→ Create notify_event
→ Create notify_notification
→ Decide delivery channels
→ Queue delivery jobs
→ Worker sends messages
→ Save delivery_attempt
```

هیچ API نباید منتظر ارسال SMS، Push یا Email بماند.

قانون:

```text
ساخت Event و Notification می‌تواند در transaction اصلی انجام شود.
ارسال واقعی باید از طریق worker انجام شود.
```

---

# 5. جدول‌های اصلی

```text
notify_events
notify_notifications
notify_templates
notify_channels
notify_user_preferences
notify_delivery_attempts
notify_device_tokens
```

---

## 5.1 notify_events

برای ثبت اتفاق سیستم.

فیلدهای پیشنهادی:

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

مثال:

```text
event_type = PRODUCT_APPROVED
actor_user_id = admin_id
recipient_user_id = shop_owner_id
target_type = product
target_id = 101
```

---

## 5.2 notify_notifications

برای اعلان داخل اپ.

فیلدهای پیشنهادی:

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

---

## 5.3 notify_templates

برای متن‌های قابل مدیریت.

فیلدهای پیشنهادی:

```text
id
event_type
channel
language
title_template
body_template
is_active
created_at
updated_at
```

مثال:

```text
event_type = SHOP_APPROVED
channel = push
language = fa
title_template = فروشگاه شما تأیید شد
body_template = فروشگاه {{shop_name}} با موفقیت تأیید شد.
```

---

## 5.4 notify_channels

برای مدیریت فعال/غیرفعال بودن کانال‌ها.

فیلدهای پیشنهادی:

```text
id
channel
provider
is_active
config_key
created_at
updated_at
```

کانال‌ها:

```text
in_app
push
sms
email
```

---

## 5.5 notify_user_preferences

برای تنظیمات کاربر.

فیلدهای پیشنهادی:

```text
id
user_id
event_group
in_app_enabled
push_enabled
sms_enabled
email_enabled
created_at
updated_at
```

نکته:

```text
اعلان‌های امنیتی، مالی و قراردادی نباید کامل خاموش شوند.
```

---

## 5.6 notify_delivery_attempts

برای لاگ ارسال.

فیلدهای پیشنهادی:

```text
id
notification_id
event_id
user_id
channel
provider
status
attempt_count
provider_message_id
error_message
sent_at
created_at
updated_at
```

Status:

```text
pending
sent
failed
retrying
cancelled
```

---

## 5.7 notify_device_tokens

برای Push Notification.

فیلدهای پیشنهادی:

```text
id
user_id
device_id
platform
token
provider
is_active
last_seen_at
created_at
updated_at
```

platform:

```text
android
ios
web
```

---

# 6. Event Naming Standard

Eventها باید uppercase و snake_case باشند.

مثال درست:

```text
SHOP_APPROVED
PRODUCT_REJECTED
INVOICE_ISSUED
PAYMENT_SUCCESS
```

مثال غلط:

```text
shopApproved
product rejected
InvoiceIssued
```

قانون:

```text
Event name باید ثابت و قابل استفاده در template و code باشد.
```

---

# 7. Event Group

برای مدیریت preference و template، eventها باید گروه داشته باشند.

گروه‌های پیشنهادی:

```text
auth
account
verification
contract
store
product
finance
payment
billing
promotion
service
rental
consultant
weather
ai
social
data_access
admin
security
```

---

# 8. Channel Policy

هر Event باید policy داشته باشد:

```text
کدام کانال‌ها استفاده شوند؟
آیا کاربر می‌تواند خاموش کند؟
آیا SMS مجاز است؟
آیا Email لازم است؟
آیا Push لازم است؟
```

مثال:

```text
OTP_SENT:
SMS = required
In-App = no
Push = no
Email = optional

SHOP_APPROVED:
In-App = yes
Push = yes
Email = yes
SMS = no

PAYMENT_SUCCESS:
In-App = yes
Push = yes
Email = yes
SMS = optional

WEATHER_CRITICAL_ALERT:
In-App = yes
Push = yes
SMS = yes
Email = no
```

---

# 9. رویدادهای Auth

```text
OTP_SENT
USER_REGISTERED
USER_LOGIN
USER_LOGOUT
PASSWORD_CHANGED
EMAIL_VERIFIED
PHONE_VERIFIED
ACCOUNT_SUSPENDED
ACCOUNT_RESTORED
```

## OTP_SENT

Trigger:

```text
درخواست کد ورود یا ثبت‌نام
```

Recipient:

```text
کاربر
```

Channels:

```text
SMS
```

خاموش‌شدنی؟

```text
خیر
```

---

# 10. رویدادهای Profile / Account

```text
PROFILE_UPDATED
AVATAR_UPDATED
USER_PREFERENCE_UPDATED
```

Channels پیشنهادی:

```text
In-App برای موارد مهم
```

این‌ها معمولاً SMS یا Email لازم ندارند.

---

# 11. رویدادهای Verification / Documents

```text
DOCUMENT_UPLOADED
DOCUMENT_APPROVED
DOCUMENT_REJECTED
VERIFICATION_SUBMITTED
VERIFICATION_APPROVED
VERIFICATION_REJECTED
VERIFICATION_NEEDS_REVISION
VERIFICATION_SUSPENDED
```

## DOCUMENT_REJECTED

Channels:

```text
In-App
Push
```

Email در صورت رسمی بودن مدرک:

```text
optional
```

SMS:

```text
نه، مگر مورد خیلی حساس
```

---

# 12. رویدادهای Contracts

```text
CONTRACT_REQUIRED
CONTRACT_ACCEPTED
CONTRACT_PDF_UPLOADED
CONTRACT_APPROVED
CONTRACT_REJECTED
CONTRACT_UPDATED
CONTRACT_EXPIRED
```

## CONTRACT_REQUIRED

Channels:

```text
In-App
Push
Email
```

## CONTRACT_UPDATED

Channels:

```text
In-App
Email
```

چون رسمی است.

---

# 13. رویدادهای Store

```text
SHOP_CREATED
SHOP_SUBMITTED
SHOP_APPROVED
SHOP_REJECTED
SHOP_NEEDS_REVISION
SHOP_SUSPENDED
SHOP_RESTORED
SHOP_MEMBER_ADDED
SHOP_MEMBER_REMOVED
SHOP_MEMBER_ROLE_CHANGED
```

## SHOP_APPROVED

Channels:

```text
In-App
Push
Email
```

SMS:

```text
خیر
```

## SHOP_SUSPENDED

Channels:

```text
In-App
Push
Email
SMS optional
```

---

# 14. رویدادهای Product

```text
PRODUCT_CREATED
PRODUCT_SUBMITTED
PRODUCT_APPROVED
PRODUCT_REJECTED
PRODUCT_NEEDS_REVISION
PRODUCT_PUBLISHED
PRODUCT_INACTIVE
PRODUCT_DELETED
```

## PRODUCT_APPROVED

Channels:

```text
In-App
Push
```

## PRODUCT_REJECTED

Channels:

```text
In-App
Push
```

Email:

```text
optional
```

---

# 15. رویدادهای Billing / Subscription

```text
SUBSCRIPTION_CREATED
SUBSCRIPTION_ACTIVATED
SUBSCRIPTION_RENEWED
SUBSCRIPTION_EXPIRING
SUBSCRIPTION_EXPIRED
SUBSCRIPTION_CANCELLED
FEATURE_LIMIT_REACHED
```

## SUBSCRIPTION_EXPIRING

Channels:

```text
In-App
Push
Email
```

SMS:

```text
فقط برای پلن‌های مهم یا B2B
```

---

# 16. رویدادهای Finance / Invoice / Payment

```text
INVOICE_ISSUED
INVOICE_PAID
INVOICE_CANCELLED
INVOICE_REFUNDED
PAYMENT_STARTED
PAYMENT_SUCCESS
PAYMENT_FAILED
PAYMENT_VERIFY_FAILED
COMMISSION_CALCULATED
SETTLEMENT_CREATED
SETTLEMENT_PAID
PAYOUT_REQUESTED
PAYOUT_APPROVED
PAYOUT_REJECTED
```

## INVOICE_ISSUED

Channels:

```text
In-App
Push
Email
```

## PAYMENT_SUCCESS

Channels:

```text
In-App
Push
Email
SMS optional
```

## PAYMENT_FAILED

Channels:

```text
In-App
Push
```

---

# 17. رویدادهای Promotion / Ladder

```text
PROMOTION_CREATED
PROMOTION_PAYMENT_REQUIRED
PROMOTION_ACTIVATED
PROMOTION_EXPIRING
PROMOTION_EXPIRED
PROMOTION_CANCELLED
```

## PROMOTION_ACTIVATED

Channels:

```text
In-App
Push
```

## PROMOTION_EXPIRING

Channels:

```text
In-App
Push
Email optional
```

---

# 18. رویدادهای Services / Rental

```text
SERVICE_PROVIDER_SUBMITTED
SERVICE_PROVIDER_APPROVED
SERVICE_PROVIDER_REJECTED
SERVICE_ITEM_CREATED
SERVICE_ITEM_APPROVED
SERVICE_ITEM_REJECTED
SERVICE_REQUEST_CREATED
SERVICE_REQUEST_ACCEPTED
SERVICE_REQUEST_REJECTED
SERVICE_REQUEST_COMPLETED
SERVICE_REQUEST_CANCELLED

RENTAL_EQUIPMENT_CREATED
RENTAL_EQUIPMENT_APPROVED
RENTAL_EQUIPMENT_REJECTED
RENTAL_REQUEST_CREATED
RENTAL_REQUEST_ACCEPTED
RENTAL_REQUEST_COMPLETED
RENTAL_REQUEST_CANCELLED
```

## RENTAL_REQUEST_CREATED

Recipient:

```text
موجر
```

Channels:

```text
In-App
Push
```

SMS:

```text
optional برای درخواست‌های فوری
```

---

# 19. رویدادهای Consultants

```text
CONSULTANT_SUBMITTED
CONSULTANT_APPROVED
CONSULTANT_REJECTED
CONSULTANT_SUSPENDED
CONSULT_REQUEST_CREATED
CONSULT_REQUEST_ACCEPTED
CONSULT_REQUEST_REJECTED
CONSULT_REQUEST_COMPLETED
CONSULT_REQUEST_CANCELLED
```

## CONSULT_REQUEST_CREATED

Recipient:

```text
مشاور
```

Channels:

```text
In-App
Push
```

---

# 20. رویدادهای Weather

```text
WEATHER_ALERT
FROST_WARNING
RAIN_WARNING
HEAT_WARNING
WIND_WARNING
DUST_WARNING
STORM_WARNING
```

## هشدارهای خیلی مهم

Channels:

```text
In-App
Push
SMS
```

## هشدارهای عادی

Channels:

```text
In-App
Push
```

قانون:

```text
SMS فقط برای هشدارهای واقعاً مهم و منطقه‌ای استفاده شود.
```

---

# 21. رویدادهای AI / RAG

```text
AI_REQUEST_CREATED
AI_ANSWER_READY
AI_LIMIT_REACHED
AI_FEEDBACK_RECEIVED
AI_REQUEST_FAILED
```

## AI_ANSWER_READY

Channels:

```text
In-App
Push
```

## AI_LIMIT_REACHED

Channels:

```text
In-App
Push
```

---

# 22. رویدادهای Social

```text
POST_CREATED
POST_APPROVED
POST_REMOVED
COMMENT_CREATED
COMMENT_REMOVED
POST_LIKED
POST_REPORTED
REPORT_RESOLVED
USER_BLOCKED
```

## COMMENT_CREATED

Recipient:

```text
صاحب پست
```

Channels:

```text
In-App
Push
```

SMS/Email:

```text
خیر
```

---

# 23. رویدادهای Data Access

```text
DATA_CLIENT_SUBMITTED
DATA_CLIENT_APPROVED
DATA_CLIENT_REJECTED
DATA_ACCESS_GRANTED
DATA_ACCESS_REVOKED
DATA_EXPORT_REQUESTED
DATA_EXPORT_APPROVED
DATA_EXPORT_READY
DATA_EXPORT_FAILED
```

## DATA_EXPORT_READY

Channels:

```text
In-App
Email
```

---

# 24. رویدادهای Admin / System

```text
ADMIN_CREATED
ROLE_ASSIGNED
ROLE_REMOVED
PERMISSION_CHANGED
FEATURE_FLAG_CHANGED
SYSTEM_SETTING_CHANGED
SECURITY_ALERT
```

این رویدادها معمولاً برای audit و ادمین‌ها هستند.

Channels:

```text
In-App
Email برای موارد حساس
```

---

# 25. Template Rules

Templateها نباید داخل کد hard-code شوند.

هر template باید:

```text
event_type
channel
language
title_template
body_template
```

داشته باشد.

زبان‌ها:

```text
fa
en
```

مثال فارسی:

```text
event_type: PRODUCT_APPROVED
channel: push
language: fa
title: محصول شما تأیید شد
body: محصول {{product_title}} با موفقیت منتشر شد.
```

مثال انگلیسی:

```text
event_type: PRODUCT_APPROVED
channel: push
language: en
title: Your product was approved
body: Your product {{product_title}} has been published.
```

---

# 26. Template Variables

متغیرهای template باید از payload_json پر شوند.

مثال payload:

```json
{
  "product_title": "کود NPK",
  "shop_name": "فروشگاه سبز",
  "invoice_number": "INV-1001",
  "amount_toman": 250000
}
```

قانون:

```text
اگر template متغیری دارد که در payload نیست، ارسال نباید crash کند.
باید fallback یا error log داشته باشد.
```

---

# 27. Localization Rules

Backend می‌تواند متن نهایی نوتیفیکیشن را بر اساس زبان کاربر بسازد.

زبان کاربر از اینجا خوانده می‌شود:

```text
profile_user_preferences.language
```

اگر زبان مشخص نبود:

```text
fa
```

به عنوان default برای بازار اصلی.

---

# 28. User Preferences

کاربر باید بتواند بعضی گروه‌های اعلان را کنترل کند.

قابل خاموش:

```text
social
promotion
marketing
ai_updates
non_critical_weather
```

غیرقابل خاموش:

```text
security
auth
payment
contract
critical_weather
account_status
```

قانون:

```text
کاربر نباید بتواند اعلان‌های امنیتی و مالی حیاتی را کامل خاموش کند.
```

---

# 29. Admin Controls

پنل ادمین باید بتواند:

```text
templateها را ببیند
templateها را ویرایش کند
کانال‌ها را فعال/غیرفعال کند
ارسال تست انجام دهد
delivery attempts را ببیند
event logs را ببیند
```

اما:

```text
غیرفعال کردن SMS برای OTP فقط برای super_admin مجاز است.
```

---

# 30. Retry Policy

برای ارسال‌های شکست‌خورده باید retry داشته باشیم.

پیشنهاد MVP:

```text
max_attempts = 3
retry delays = 1m, 5m, 15m
```

بعد از شکست نهایی:

```text
status = failed
error_message ذخیره شود
```

---

# 31. Delivery Status

وضعیت ارسال:

```text
pending
sent
failed
retrying
cancelled
```

برای Push:

```text
invalid_token
provider_error
```

اگر device token نامعتبر بود:

```text
is_active = false
```

---

# 32. Priority

برای eventها priority داشته باشیم:

```text
low
normal
high
critical
```

مثال:

```text
OTP_SENT = critical
PAYMENT_SUCCESS = high
WEATHER_CRITICAL_ALERT = critical
COMMENT_CREATED = normal
POST_LIKED = low
```

Priority روی worker queue و کانال ارسال اثر دارد.

---

# 33. Deduplication

برای جلوگیری از ارسال تکراری:

```text
event_type + recipient_user_id + target_type + target_id + dedupe_window
```

مثال:

```text
اگر یک محصول چندبار پشت سر هم submit شد، نوتیفیکیشن تکراری ارسال نشود.
```

برای payment، idempotency مهم‌تر است و باید جدا کنترل شود.

---

# 34. Rate Limit Notification

برای جلوگیری از اسپم:

```text
تعداد Push برای social در هر ساعت محدود شود.
SMS فقط با policy مجاز باشد.
Email digest برای بعضی موارد قابل بررسی است.
```

مثال:

```text
لایک‌های متعدد می‌توانند digest شوند.
کامنت‌ها مستقیم‌تر ارسال شوند.
```

---

# 35. Worker

Worker باید این وظایف را انجام دهد:

```text
خواندن delivery jobs
render template
انتخاب provider
ارسال پیام
ثبت نتیجه
retry شکست‌ها
غیرفعال کردن device token خراب
```

در MVP می‌تواند worker ساده باشد، اما نباید ارسال داخل request اصلی انجام شود.

---

# 36. Providers

Providerها هنوز قطعی نیستند، اما پیشنهاد پیش‌فرض:

```text
Push: Firebase Cloud Messaging
SMS: Kavenegar یا Melipayamak
Email: SMTP
```

قانون:

```text
Provider نباید در business logic hard-code شود.
باید در notification service یا adapter باشد.
```

---

# 37. Security and Privacy

نوتیفیکیشن نباید اطلاعات حساس زیادی نمایش دهد.

مثال بد:

```text
کد ملی شما ۰۰۱۲۳۴۵۶۷۸ رد شد.
```

مثال بهتر:

```text
یکی از مدارک شما نیاز به اصلاح دارد.
```

برای lock screen، متن Push باید محتاطانه باشد.

---

# 38. Audit and Logs

نوتیفیکیشن خودش audit log نیست، اما برای عملیات مهم باید قابل ردیابی باشد.

هر delivery attempt باید log شود:

```text
چه eventی؟
برای چه کسی؟
از چه کانالی؟
با چه providerی؟
موفق یا ناموفق؟
خطا چه بود؟
```

---

# 39. APIهای نوتیفیکیشن

## User API

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

---

# 40. Flutter UI

## User App

صفحات لازم:

```text
NotificationsListScreen
NotificationDetailScreen
NotificationPreferencesScreen
NotificationBadgeWidget
```

باید پشتیبانی کند:

```text
read/unread
mark as read
read all
deep link based on data_json
```

---

# 41. Admin UI

صفحات لازم:

```text
NotificationEventsPage
NotificationTemplatesPage
NotificationDeliveryLogsPage
SendTestNotificationPage
NotificationChannelsPage
```

ادمین باید بتواند:

```text
template ببیند
template ویرایش کند
ارسال تست انجام دهد
delivery log ببیند
کانال‌ها را مدیریت کند
```

---

# 42. Deep Link

نوتیفیکیشن باید بتواند کاربر را به صفحه مربوط ببرد.

مثال data_json:

```json
{
  "route": "/shop/products/101",
  "target_type": "product",
  "target_id": 101
}
```

قانون:

```text
Flutter باید route را validate کند.
اگر کاربر permission ندارد، صفحه مناسب نمایش داده شود.
```

---

# 43. Error Handling

اگر ارسال شکست خورد:

```text
delivery_attempt ثبت شود.
error_message ذخیره شود.
retry طبق policy انجام شود.
در صورت شکست نهایی status failed شود.
```

API اصلی نباید به خاطر شکست Push/SMS/Email fail شود، مگر خود عملیات وابسته به ارسال باشد؛ مثل OTP.

برای OTP:

```text
اگر SMS ارسال نشود، request باید خطای مناسب بدهد.
```

---

# 44. OTP Special Rule

OTP یک مورد خاص است.

برای OTP:

```text
SMS باید همان لحظه ارسال شود یا حداقل وضعیت ارسال مشخص شود.
rate limit اجباری است.
OTP نباید در log ذخیره شود.
OTP باید expire شود.
تلاش ناموفق باید محدود شود.
```

Event:

```text
OTP_SENT
OTP_VERIFIED
OTP_FAILED
```

---

# 45. Notification Testing

برای هر event مهم باید تست داشته باشیم:

```text
event ایجاد می‌شود؟
recipient درست است؟
template درست انتخاب می‌شود؟
channel policy درست است؟
delivery_attempt ساخته می‌شود؟
failed delivery retry می‌شود؟
user preference رعایت می‌شود؟
```

---

# 46. Definition of Done برای Notification

Notification فقط زمانی Done است که:

```text
event name مشخص باشد.
trigger مشخص باشد.
recipient مشخص باشد.
payload مشخص باشد.
channels مشخص باشند.
template فارسی داشته باشد.
template انگلیسی داشته باشد.
delivery attempt ثبت شود.
retry policy مشخص باشد.
UI داخل اپ نمایش دهد.
Admin بتواند logs را ببیند.
docs آپدیت شده باشد.
```

---

# 47. خط قرمزهای نوتیفیکیشن

موارد ممنوع:

```text
ارسال SMS برای رویدادهای کم‌اهمیت
hard-code کردن templateها داخل کد
ارسال Push/SMS/Email داخل request اصلی بدون queue
نبود delivery log
نبود retry policy
نمایش اطلاعات حساس در Push
نداشتن user preferences
نداشتن template انگلیسی و فارسی
```

---

# 48. نتیجه

نوتیفیکیشن در پروژه «فارم نت» باید از ابتدا به‌عنوان یک زیرساخت مرکزی طراحی شود.

قانون نهایی:

```text
Notification یعنی سیستم به‌موقع، از کانال درست، با پیام درست، به شخص درست اطلاع بدهد.
```
