# 07 — API Standard
# استاندارد API پروژه فارم نت

## 1. هدف سند

این سند استاندارد طراحی APIهای پروژه «فارم نت» را مشخص می‌کند.

تمام APIهای Backend باید طبق این سند طراحی شوند تا تیم‌های Backend، Flutter، Admin Panel و QA با یک قرارداد ثابت کار کنند.

هیچ endpoint نباید خارج از این استاندارد ساخته شود.

---

## 2. API Versioning

تمام APIهای اصلی باید version داشته باشند.

فرمت پایه:

```text
/api/v1/...
```

مثال:

```text
/api/v1/auth/login/email
/api/v1/store/products
/api/v1/admin/users
```

قانون:

```text
اگر در آینده تغییر ناسازگار ایجاد شد، نسخه جدید مثل /api/v2 ساخته می‌شود.
```

---

## 3. ساختار کلی URLها

### Public / User API

```text
/api/v1/{module}/...
```

مثال:

```text
/api/v1/auth/otp/request
/api/v1/store/products
/api/v1/notifications
```

### Admin API

```text
/api/v1/admin/{module}/...
```

مثال:

```text
/api/v1/admin/users
/api/v1/admin/store/products
/api/v1/admin/commission/rules
```

### Me API

برای اطلاعات مربوط به کاربر فعلی:

```text
/api/v1/users/me
/api/v1/store/shops/me
/api/v1/billing/subscription/me
/api/v1/notifications/preferences
```

---

## 4. HTTP Methods

استفاده از methodها باید استاندارد باشد:

```text
GET     دریافت اطلاعات
POST    ساختن رکورد یا اجرای action
PATCH   ویرایش بخشی از رکورد
PUT     جایگزینی کامل، فقط در صورت نیاز
DELETE  حذف یا soft delete
```

مثال:

```text
GET    /api/v1/store/products
POST   /api/v1/store/products
PATCH  /api/v1/store/products/{id}
DELETE /api/v1/store/products/{id}
```

برای actionها:

```text
POST /api/v1/admin/store/products/{id}/approve
POST /api/v1/admin/store/products/{id}/reject
POST /api/v1/payments/verify
```

---

## 5. فرمت استاندارد Response موفق

تمام پاسخ‌های موفق باید این ساختار را داشته باشند:

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

### قانون

```text
data همیشه محل داده اصلی است.
message پیام عمومی است.
meta برای اطلاعات کمکی مثل trace_id، pagination و version استفاده می‌شود.
```

---

## 6. فرمت استاندارد Error Response

تمام خطاها باید این ساختار را داشته باشند:

```json
{
  "success": false,
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "Product not found",
    "details": {}
  },
  "meta": {
    "trace_id": "abc-123"
  }
}
```

### قانون

```text
error.code باید ثابت، انگلیسی و قابل ترجمه در Flutter باشد.
error.message پیام پیش‌فرض Backend است.
Flutter می‌تواند براساس error.code پیام فارسی/انگلیسی مناسب نمایش دهد.
```

---

## 7. Error Code Naming

Error codeها باید uppercase و ماژول‌محور باشند.

مثال:

```text
AUTH_INVALID_CREDENTIALS
AUTH_TOKEN_EXPIRED
AUTH_OTP_EXPIRED
AUTH_OTP_RATE_LIMITED

USER_NOT_FOUND
USER_SUSPENDED

SHOP_NOT_FOUND
SHOP_ALREADY_EXISTS
SHOP_NOT_APPROVED

PRODUCT_NOT_FOUND
PRODUCT_NOT_PUBLISHED
PRODUCT_REVIEW_REQUIRED

DOCUMENT_REQUIRED
DOCUMENT_REJECTED

CONTRACT_NOT_ACCEPTED

PAYMENT_VERIFY_FAILED
PAYMENT_ALREADY_PROCESSED
PAYMENT_ATTEMPT_NOT_FOUND

COMMISSION_RULE_NOT_FOUND

NOTIFICATION_TEMPLATE_NOT_FOUND
NOTIFICATION_SEND_FAILED

PERMISSION_DENIED
VALIDATION_ERROR
INTERNAL_SERVER_ERROR
```

---

## 8. HTTP Status Codes

استفاده از status codeها:

```text
200 OK
برای دریافت یا عملیات موفق

201 Created
برای ساخت رکورد جدید

400 Bad Request
برای درخواست اشتباه

401 Unauthorized
برای نبودن یا نامعتبر بودن token

403 Forbidden
برای نداشتن permission

404 Not Found
برای پیدا نشدن resource

409 Conflict
برای تضاد منطقی مثل فروشگاه تکراری

422 Unprocessable Entity
برای validation error

429 Too Many Requests
برای rate limit

500 Internal Server Error
برای خطای غیرمنتظره
```

---

## 9. Validation Error

خطاهای validation باید قابل فهم و استاندارد باشند.

مثال:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "fields": [
        {
          "field": "phone",
          "message": "Invalid phone number"
        },
        {
          "field": "price_toman",
          "message": "Must be greater than zero"
        }
      ]
    }
  },
  "meta": {
    "trace_id": "abc-123"
  }
}
```

---

## 10. Pagination Standard

برای لیست‌ها باید pagination داشته باشیم.

### Query Params

```text
page
page_size
```

مثال:

```text
GET /api/v1/store/products?page=1&page_size=20
```

### Response

```json
{
  "success": true,
  "data": [],
  "message": "OK",
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 240,
    "total_pages": 12,
    "trace_id": "abc-123"
  }
}
```

### قانون

```text
page_size باید محدودیت حداکثری داشته باشد.
پیشنهاد: max page_size = 100
مقدار پیش‌فرض: 20
```

---

## 11. Filtering Standard

فیلترها باید از query params استفاده کنند.

مثال:

```text
GET /api/v1/store/products?category_id=5&city_id=12&status=published
```

برای admin:

```text
GET /api/v1/admin/store/products?status=pending_review&shop_id=10
```

قانون:

```text
فیلترهای مجاز هر endpoint باید در docs/api همان ماژول ثبت شوند.
```

---

## 12. Sorting Standard

فرمت sort:

```text
sort=created_at:desc
sort=price_toman:asc
```

مثال:

```text
GET /api/v1/store/products?sort=created_at:desc
```

اگر چند sort لازم شد:

```text
sort=promoted:desc,created_at:desc
```

---

## 13. Search Standard

برای جستجو از پارامتر `q` استفاده شود.

مثال:

```text
GET /api/v1/store/products?q=کود
GET /api/v1/admin/users?q=0912
```

قانون:

```text
search نباید بدون index روی جدول‌های بزرگ اجرا شود.
برای جستجوی پیشرفته بعداً موتور جدا مثل Meilisearch/Elasticsearch قابل بررسی است.
```

---

## 14. Authentication Header

تمام endpointهای protected باید از Bearer Token استفاده کنند.

```http
Authorization: Bearer <access_token>
```

Refresh token در endpoint جدا استفاده می‌شود:

```text
POST /api/v1/auth/refresh
```

---

## 15. Permission Standard

endpointهای حساس باید permission مشخص داشته باشند.

مثال:

```text
GET /api/v1/admin/users
Permission: users.read

POST /api/v1/admin/store/products/{id}/approve
Permission: products.approve

PATCH /api/v1/admin/commission/rules/{id}
Permission: commission.update
```

اگر permission کافی نبود:

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to perform this action"
  },
  "meta": {
    "trace_id": "abc-123"
  }
}
```

---

## 16. Idempotency Standard

برای عملیات حساس باید idempotency داشته باشیم.

موارد ضروری:

```text
payment verify
payment callback
invoice creation
subscription checkout
promotion checkout
order/payment operations
```

Header پیشنهادی:

```http
Idempotency-Key: unique-client-key
```

یا در body:

```json
{
  "idempotency_key": "unique-client-key"
}
```

قانون:

```text
اگر request تکراری با همان idempotency_key آمد، نباید عملیات مالی دوباره انجام شود.
```

---

## 17. Trace ID Standard

هر request باید trace_id داشته باشد.

اگر client فرستاد:

```http
X-Trace-Id: abc-123
```

Backend همان را استفاده می‌کند.

اگر client نفرستاد، Backend تولید می‌کند.

تمام responseها باید trace_id داشته باشند:

```json
{
  "meta": {
    "trace_id": "abc-123"
  }
}
```

---

## 18. Request ID / Correlation

برای عملیات زنجیره‌ای مثل پرداخت، نوتیفیکیشن و audit log باید trace_id حفظ شود.

مثال:

```text
Create invoice
→ Payment attempt
→ Callback
→ Verify
→ Notification
→ Audit log
```

همه باید trace_id قابل ردیابی داشته باشند.

---

## 19. Date and Time Standard

Backend تاریخ‌ها را به صورت ISO 8601 و UTC برمی‌گرداند.

مثال:

```json
{
  "created_at": "2026-05-06T12:30:00Z"
}
```

قانون:

```text
Backend تاریخ شمسی برای API عمومی برنمی‌گرداند.
Flutter تاریخ شمسی را برای UI فارسی نمایش می‌دهد.
```

استثنا:

```text
SMS، Email، Push، PDF و پیام‌های آماده می‌توانند تاریخ شمسی تولیدشده توسط Backend داشته باشند.
```

---

## 20. Money Standard

مبلغ‌ها به تومان و عدد خام ذخیره و ارسال می‌شوند.

مثال:

```json
{
  "price_toman": 250000,
  "currency": "TOMAN"
}
```

قانون:

```text
Backend عدد خام می‌دهد.
Flutter نمایش می‌دهد: ۲۵۰٬۰۰۰ تومان
```

---

## 21. Status Standard

statusها باید string و lowercase باشند.

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

---

## 22. Soft Delete Standard

برای موجودیت‌های مهم، حذف فیزیکی انجام نشود.

به جای آن:

```text
deleted_at
status = deleted
```

مواردی که باید soft delete شوند:

```text
users
shops
products
services
consultants
posts
documents
```

---

## 23. Admin Action Standard

هر action مهم ادمین باید:

```text
permission check داشته باشد
audit log ایجاد کند
notification event ایجاد کند اگر لازم است
reason بگیرد اگر reject/suspend است
```

مثال reject:

```json
{
  "reason": "مدرک ارسالی واضح نیست."
}
```

---

## 24. Notification Event Standard

هر endpoint که رویداد مهم ایجاد می‌کند باید event ثبت کند.

مثال:

```text
POST /api/v1/admin/store/shops/{id}/approve
Event: SHOP_APPROVED

POST /api/v1/admin/store/products/{id}/reject
Event: PRODUCT_REJECTED

POST /api/v1/payments/verify
Event: PAYMENT_SUCCESS یا PAYMENT_FAILED
```

---

## 25. Audit Log Standard

هر عملیات حساس باید audit log داشته باشد.

موارد اجباری:

```text
تغییر role
تأیید/رد فروشگاه
تأیید/رد محصول
تأیید/رد مدرک
تغییر commission
تغییر plan
تغییر وضعیت payment/invoice
تعلیق کاربر
```

فیلدهای اصلی:

```text
admin_user_id
action
target_type
target_id
old_value
new_value
reason
ip_address
user_agent
trace_id
created_at
```

---

## 26. File Upload API Standard

آپلود فایل باید multipart باشد.

مثال:

```text
POST /api/v1/media/upload
POST /api/v1/documents/upload
```

قوانین:

```text
max file size
allowed extensions
MIME type check
random file name
public/private visibility
owner_id
module
target_type
target_id
```

Response:

```json
{
  "success": true,
  "data": {
    "id": 10,
    "url": "/media/files/10",
    "file_type": "image",
    "visibility": "public"
  },
  "message": "File uploaded",
  "meta": {
    "trace_id": "abc-123"
  }
}
```

---

## 27. API Naming Rules

قانون نام‌گذاری:

```text
plural nouns برای resourceها
actionها با verb در انتها
admin جدا از public
me برای user فعلی
```

درست:

```text
/api/v1/store/products
/api/v1/admin/store/products/{id}/approve
/api/v1/users/me
```

غلط:

```text
/api/v1/getProducts
/api/v1/productApprove
/api/v1/myUserData
```

---

## 28. Module API Documentation

هر ماژول باید docs/api جدا داشته باشد.

ساختار:

```text
docs/api/auth.md
docs/api/geo.md
docs/api/notification.md
docs/api/media.md
docs/api/verification.md
docs/api/billing.md
docs/api/finance.md
docs/api/store.md
docs/api/promotion.md
```

هر فایل باید شامل این موارد باشد:

```text
Endpoint list
Request samples
Response samples
Error codes
Permissions
Notification events
Status flow
```

---

## 29. API Backward Compatibility

بعد از اینکه Flutter یا Admin از API استفاده کرد، تغییر response بدون هماهنگی ممنوع است.

اگر تغییر لازم بود:

```text
docs/api آپدیت شود
Flutter team اعلام شود
Admin team اعلام شود
version یا deprecation مشخص شود
```

---

## 30. Rate Limit Standard

rate limit برای این موارد اجباری است:

```text
OTP request
login
password reset
payment verify
file upload
AI ask
social post/comment
```

خطای rate limit:

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests"
  },
  "meta": {
    "trace_id": "abc-123"
  }
}
```

---

## 31. Security Headers / CORS

CORS باید محدود باشد.

در development:

```text
localhostها مجاز
```

در production:

```text
فقط دامنه‌های رسمی اپ و ادمین
```

---

## 32. Public vs Private API

Public API:

```text
نیاز به login ندارد
مثلاً لیست محصولات منتشرشده
```

Private API:

```text
نیاز به login دارد
مثلاً پروفایل من، نوتیفیکیشن‌ها
```

Admin API:

```text
نیاز به login + permission دارد
```

---

## 33. Example: Product List API

Request:

```http
GET /api/v1/store/products?page=1&page_size=20&category_id=3&sort=created_at:desc
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "title": "کود NPK",
      "price_toman": 250000,
      "currency": "TOMAN",
      "status": "published",
      "main_image_url": "/media/files/55",
      "shop": {
        "id": 12,
        "name": "فروشگاه سبز"
      },
      "created_at": "2026-05-06T12:30:00Z"
    }
  ],
  "message": "OK",
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 240,
    "total_pages": 12,
    "trace_id": "abc-123"
  }
}
```

---

## 34. Example: Admin Product Approve API

Request:

```http
POST /api/v1/admin/store/products/101/approve
Authorization: Bearer <token>
```

Permission:

```text
products.approve
```

Response:

```json
{
  "success": true,
  "data": {
    "id": 101,
    "status": "published"
  },
  "message": "Product approved",
  "meta": {
    "trace_id": "abc-123"
  }
}
```

Side effects:

```text
Audit Log: PRODUCT_APPROVED_BY_ADMIN
Notification Event: PRODUCT_APPROVED
```

---

## 35. Example: Payment Verify API

Request:

```http
POST /api/v1/payments/verify
Idempotency-Key: pay-123
```

Body:

```json
{
  "gateway": "zarinpal",
  "authority": "A00000000000000000000000000000123456",
  "invoice_id": 5001
}
```

Response موفق:

```json
{
  "success": true,
  "data": {
    "invoice_id": 5001,
    "status": "paid",
    "transaction_id": 9001,
    "amount_toman": 250000
  },
  "message": "Payment verified",
  "meta": {
    "trace_id": "abc-123"
  }
}
```

Response خطا:

```json
{
  "success": false,
  "error": {
    "code": "PAYMENT_VERIFY_FAILED",
    "message": "Payment verification failed"
  },
  "meta": {
    "trace_id": "abc-123"
  }
}
```

Side effects:

```text
Invoice status update
Transaction create
Notification Event: PAYMENT_SUCCESS یا PAYMENT_FAILED
Audit/finance log
```

---

## 36. خط قرمزهای API

موارد زیر ممنوع هستند:

```text
API بدون version
Response غیر استاندارد
Error بدون code
Endpoint حساس بدون permission
لیست بدون pagination
پرداخت بدون idempotency
عملیات ادمین بدون audit log
رویداد مهم بدون notification event
تغییر API بدون آپدیت docs
تاریخ شمسی در داده خام عمومی API
مبلغ به صورت string نمایشی در API عمومی
```

---

## 37. نتیجه

این سند استاندارد رسمی API پروژه «فارم نت» است.

هر endpoint باید قبل از Done شدن با این سند بررسی شود.

قانون نهایی:

```text
API خوب یعنی قابل پیش‌بینی، قابل تست، قابل مستند، قابل مصرف توسط Flutter و قابل ردیابی.
```
