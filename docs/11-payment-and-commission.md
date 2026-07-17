# 11 — Payment and Commission
# پرداخت، فاکتور و کمیسیون پروژه فارم نت

## وضعیت اجرای Phase 9

Step 9.2 قراردادهای مالی و سخت‌سازی دیتابیس را بدون تغییر رفتار API موجود
اضافه کرد. جدول‌های `finance_invoices`، `finance_invoice_items`،
`commission_snapshots`، `payment_attempts`، `finance_transactions`،
`finance_refunds` و `inventory_reservations` اکنون مبنای گام‌های اتمیک Checkout،
Verify و Refund هستند. در این مرحله هنوز درگاه واقعی متصل نشده و جریان فعلی
Mock به این جدول‌ها مهاجرت نکرده است.

قیدهای یکتای `idempotency_key` و شناسه‌های Provider، مبالغ مثبت، Snapshot
یک‌به‌یک سفارش/فاکتور و Reservation یک‌به‌یک هر Order Item در سطح دیتابیس ثبت
شده‌اند. Step 9.3 باید Checkout را با قفل موجودی و Reservation اتمیک به این
قراردادها متصل کند.

Step 9.3 این اتصال را انجام داد: Cart و Productها با ترتیب ثابت و `FOR UPDATE`
قفل می‌شوند، موجودی در همان Transaction کاهش می‌یابد و برای هر Order، Invoice،
Invoice Items، Commission Snapshot، Payment Attempt و Inventory Reservation
ساخته می‌شود. هر خطا کل عملیات را Rollback می‌کند. پرداخت موفق Mock رزرو را
`consumed` کرده و Transaction ثبت می‌کند؛ لغو Admin نیز موجودی را دقیقاً یک‌بار
برمی‌گرداند. اتصال درگاه واقعی و Idempotency خود Checkout مربوط به گام‌های بعدی است.

Step 9.4 نیز Idempotency خود Checkout را عملیاتی کرد. هر درخواست یک کلید اجباری
دارد و Fingerprint محتوای آن همراه شناسه سفارش‌های حاصل در `checkout_requests`
ثبت می‌شود. Replay دقیق همان نتیجه را بدون کاهش دوباره موجودی برمی‌گرداند و
استفاده همان کلید با Payload متفاوت رد می‌شود. Reservation منقضی با قفل ردیفی
دقیقاً یک‌بار آزاد می‌شود. خروجی‌های Buyer و Seller نیز از اطلاعات مالی/یادداشت‌های
داخلی نامرتبط پاک شده‌اند. درگاه پرداخت واقعی همچنان پیاده نشده است.

Step 9.5 قرارداد استاندارد شروع و Verify پرداخت را فعال کرد. مسیر
`POST /api/v1/payments/checkout` برای Invoice متعلق به Buyer یک Payment Attempt
idempotent می‌سازد و مسیر `POST /api/v1/payments/verify` نتیجه Provider را
exact-once روی Attempt، Payment، Invoice، Order، Transaction و Reservation اعمال
می‌کند. در این گام فقط Provider آزمایشی `mock` مجاز است؛ Callback و درگاه واقعی
هنوز پیاده نشده‌اند.

Step 9.6 جریان Refund را برای Admin فعال کرد. درخواست Refund با کلید idempotency
ثبت می‌شود و در این مرحله فقط بازپرداخت کامل مجاز است. تکمیل Mock، Refund،
Transaction، Invoice، Order و Payment را دقیقاً یک‌بار به وضعیت بازپرداخت‌شده
می‌برد. جابه‌جایی واقعی پول و Partial Refund هنوز پیاده نشده‌اند.

Step 9.7 Read Modelهای تایپ‌شده و صفحه‌بندی‌شده Admin را برای Invoice، Payment
Attempt، Transaction، Refund و Audit Log اضافه کرد. درخواست و تکمیل Refund اکنون
actor، action، target، old/new value، IP، user-agent و trace ID را در همان
Transaction مالی داخل `admin_audit_logs` ثبت می‌کنند.

Step 9.8 رابط Admin Finance را با پنج تب تایپ‌شده برای Invoice، Payment Attempt،
Transaction، Refund و Audit Log تکمیل کرد. مسیر با Permission Guard محافظت شده و
حالت‌های loading/empty/error، retry و pagination دارد.

## 1. هدف سند

این سند استاندارد مالی پروژه «فارم نت» را مشخص می‌کند.

چون پروژه از همان MVP پرداخت آنلاین دارد و درآمد آن از چند مسیر است، طراحی مالی باید از ابتدا دقیق، قابل تست، قابل audit و قابل توسعه باشد.

مدل‌های درآمدی پروژه:

```text
1. کمیسیون از فاکتورهای نهایی
2. اشتراک Pro
3. تبلیغات / نردبان
4. دسترسی داده کنترل‌شده برای شرکت‌ها
```

این سند روی موارد زیر تمرکز دارد:

```text
فاکتور
پرداخت آنلاین
تراکنش
کمیسیون
Snapshot کمیسیون
اشتراک
تبلیغات
Audit مالی
Idempotency
ریسک‌های پرداخت
```

---

# 2. اصل بنیادین مالی

قانون اصلی:

```text
هیچ عملیات مالی نباید بدون فاکتور، تراکنش، وضعیت مشخص، trace_id و audit قابل ردیابی باشد.
```

هر پرداخت باید به یک فاکتور وصل باشد.

هر فاکتور باید مبلغ، آیتم‌ها، وضعیت و کمیسیون مشخص داشته باشد.

هر کمیسیون باید در زمان صدور یا نهایی شدن فاکتور snapshot شود.

---

# 3. واحد پول

واحد پول اصلی سیستم:

```text
TOMAN
```

در دیتابیس:

```text
amount_toman BIGINT UNSIGNED
```

در API:

```json
{
  "amount_toman": 250000,
  "currency": "TOMAN"
}
```

در Flutter فارسی:

```text
۲۵۰٬۰۰۰ تومان
```

قانون:

```text
Backend مبلغ را عدد خام ذخیره و ارسال می‌کند.
Frontend نمایش فارسی، جداکننده هزارگان و تومان را انجام می‌دهد.
```

---

# 4. ماژول‌های مالی اصلی

ماژول‌های مالی پروژه:

```text
finance
payment
commission
billing
promotion
settlement
```

در MVP تمرکز روی این‌هاست:

```text
finance invoices
payment core
commission core
billing/subscription core
promotion payment core
```

بعد از MVP:

```text
wallet
settlement
payout
refund advanced
multi-gateway
advanced financial reports
```

---

# 5. جدول‌های اصلی

```text
commission_rules
commission_snapshots

finance_invoices
finance_invoice_items
finance_commissions
finance_transactions

payment_gateways
payment_attempts

billing_plans
billing_subscriptions

promotion_packages
promotions
promotion_payments
```

بعداً:

```text
finance_wallets
finance_settlements
finance_payout_requests
finance_refunds
```

---

# 6. Invoice

فاکتور پایه تمام عملیات مالی است.

هر خرید، اشتراک، تبلیغ، خدمت، اجاره، مشاوره یا دسترسی داده باید در نهایت به فاکتور وصل شود.

## جدول پیشنهادی

```text
finance_invoices
```

فیلدها:

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
cancelled_at
created_at
updated_at
```

## target_type

```text
store_order
subscription
promotion
service_request
rental_request
consult_request
data_access
manual
```

در MVP:

```text
subscription
promotion
store_order یا store_invoice
manual
```

---

# 7. Invoice Items

هر فاکتور باید آیتم داشته باشد.

## جدول

```text
finance_invoice_items
```

فیلدها:

```text
id
invoice_id
item_type
item_id
title
quantity
unit_price_toman
total_price_toman
created_at
```

مثال:

```text
item_type = product
item_id = 101
title = کود NPK
quantity = 2
unit_price_toman = 250000
total_price_toman = 500000
```

---

# 8. Invoice Status

وضعیت‌های فاکتور:

```text
draft
issued
payment_pending
paid
payment_failed
cancelled
refunded
settled
```

## معنی وضعیت‌ها

```text
draft:
فاکتور ساخته شده ولی هنوز نهایی نیست.

issued:
فاکتور صادر شده و آماده پرداخت است.

payment_pending:
کاربر به درگاه هدایت شده یا پرداخت در حال بررسی است.

paid:
پرداخت تأیید شده است.

payment_failed:
پرداخت ناموفق بوده است.

cancelled:
فاکتور لغو شده است.

refunded:
بازگشت وجه ثبت شده است.

settled:
سهم طرف مقابل تسویه شده است.
```

---

# 9. Commission Rules

کمیسیون باید از پنل ادمین قابل مدیریت باشد.

## جدول

```text
commission_rules
```

فیلدها:

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

## module_scope

```text
store
service
rental
consultation
promotion
subscription
data_access
manual
```

## rate_type

```text
percent
fixed
```

## مثال‌ها

```text
store / percent / 10
consultation / percent / 20
promotion / fixed / 0
service / percent / 12
```

---

# 10. Commission Priority

در آینده ممکن است کمیسیون عمومی، دسته‌بندی‌محور یا اختصاصی داشته باشیم.

ترتیب اولویت پیشنهادی:

```text
1. rule اختصاصی برای target خاص
2. rule دسته‌بندی یا نوع خدمت
3. rule ماژول
4. rule پیش‌فرض سیستم
```

در MVP:

```text
فقط rule سطح module_scope کافی است.
```

مثلاً:

```text
store = 10%
promotion = 0% یا fixed
consultation = 20%
```

---

# 11. Commission Snapshot

قانون بسیار مهم:

```text
کمیسیون باید هنگام صدور یا نهایی شدن فاکتور snapshot شود.
```

چرا؟

اگر امروز کمیسیون ۱۰٪ باشد و فردا ادمین آن را ۱۲٪ کند، فاکتورهای قبلی نباید تغییر کنند.

## جدول

```text
commission_snapshots
```

یا در MVP می‌توانیم داده snapshot را در:

```text
finance_commissions
```

نگه داریم.

## finance_commissions

فیلدها:

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

مثال:

```text
invoice total = 1,000,000
rate_value_snapshot = 10
commission_amount_toman = 100,000
platform_amount_toman = 100,000
provider_amount_toman = 900,000
```

---

# 12. قانون کمیسیون

```text
کمیسیون بعد از پرداخت یا صدور فاکتور نباید بر اساس rule جدید دوباره محاسبه شود، مگر با عملیات اصلاح مالی و audit رسمی.
```

هر تغییر rule باید audit شود.

Audit action:

```text
COMMISSION_RULE_CREATED
COMMISSION_RULE_UPDATED
COMMISSION_RULE_DEACTIVATED
```

---

# 13. Payment Gateway

پرداخت آنلاین از MVP وجود دارد.

درگاه دقیق بعداً انتخاب می‌شود.

گزینه‌های احتمالی:

```text
Zarinpal
Zibal
IDPay
NextPay
درگاه بانکی مستقیم
```

## جدول

```text
payment_gateways
```

فیلدها:

```text
id
code
name
status
is_default
config_key
created_at
updated_at
```

مثال:

```text
code = zarinpal
name = Zarinpal
status = active
```

اطلاعات حساس درگاه داخل دیتابیس خام ذخیره نشود.
باید از env یا secret manager خوانده شود.

---

# 14. Payment Attempt

هر تلاش پرداخت باید ثبت شود.

## جدول

```text
payment_attempts
```

فیلدها:

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

## Status

```text
created
redirected
callback_received
verified
failed
expired
cancelled
```

---

# 15. Payment Flow

جریان استاندارد پرداخت:

```text
Create invoice
→ Calculate commission snapshot
→ Create payment_attempt
→ Request payment from gateway
→ Redirect user to gateway
→ Gateway callback
→ Save callback payload
→ Verify payment with gateway
→ Mark payment_attempt verified/failed
→ Mark invoice paid/payment_failed
→ Create finance_transaction
→ Create notification event
→ Create audit/finance log
```

---

# 16. Payment Verify

هیچ پرداختی فقط با callback موفق محسوب نمی‌شود.

قانون:

```text
پرداخت فقط پس از verify از درگاه، موفق است.
```

Callback فقط اطلاع می‌دهد که کاربر برگشته است.
Verify مشخص می‌کند پرداخت واقعاً موفق بوده یا نه.

---

# 17. Idempotency

برای پرداخت idempotency اجباری است.

چرا؟

چون callback ممکن است چند بار بیاید.
کاربر ممکن است چند بار دکمه پرداخت را بزند.
verify ممکن است تکرار شود.

## قانون

```text
پرداخت یک invoice فقط یک بار می‌تواند paid شود.
payment_attempt با authority/gateway_reference نباید دوبار transaction موفق بسازد.
```

## Header پیشنهادی

```http
Idempotency-Key: unique-key
```

یا body:

```json
{
  "idempotency_key": "unique-key"
}
```

## موارد idempotent

```text
payment checkout
payment callback
payment verify
invoice creation برای عملیات حساس
subscription checkout
promotion checkout
```

---

# 18. Finance Transactions

هر پرداخت موفق باید transaction داشته باشد.

## جدول

```text
finance_transactions
```

فیلدها:

```text
id
invoice_id
payment_attempt_id
user_id
type
status
amount_toman
currency
gateway
gateway_reference
trace_id
created_at
updated_at
```

## type

```text
payment
refund
settlement
payout
adjustment
```

## status

```text
pending
success
failed
cancelled
```

در MVP بیشتر از type `payment` استفاده می‌شود.

---

# 19. Subscription Payment

اشتراک Pro باید از سیستم invoice/payment استفاده کند.

جریان:

```text
User selects plan
→ Create subscription invoice
→ Payment
→ Verify
→ Activate subscription
→ Notification
```

اگر پرداخت ناموفق بود:

```text
subscription فعال نمی‌شود.
invoice payment_failed می‌شود.
notification ارسال می‌شود.
```

---

# 20. Promotion Payment

تبلیغات / نردبان نیز باید از invoice/payment استفاده کند.

جریان:

```text
User selects promotion package
→ Create promotion invoice
→ Payment
→ Verify
→ Activate promotion
→ Set starts_at / ends_at
→ Notification
```

در MVP می‌توان فعال‌سازی تبلیغ را بعد از پرداخت، با تأیید ادمین انجام داد.

---

# 21. Store Invoice

برای فروشگاه، فاکتور فروش محصول باید به کمیسیون وصل باشد.

در MVP می‌توانیم فروشگاه را ساده‌تر نگه داریم، اما ساختار باید آماده باشد.

جریان کلی آینده:

```text
User creates store order
→ Invoice issued
→ Payment
→ Commission snapshot
→ Shop/provider amount calculated
→ Notification
```

---

# 22. Refund

در MVP refund پیشرفته لازم نیست.

اما وضعیت `refunded` باید در invoice دیده شود.

بعداً:

```text
finance_refunds
```

اضافه می‌شود.

قانون آینده:

```text
refund باید transaction جدا، reason، audit و notification داشته باشد.
```

---

# 23. Settlement

تسویه با فروشگاه، مشاور یا موجر بعد از MVP کامل می‌شود.

اما از اول باید سهم طرف مقابل ذخیره شود:

```text
provider_amount_toman
platform_amount_toman
```

بعداً:

```text
finance_settlements
finance_payout_requests
```

---

# 24. Payment API

## Checkout

```text
POST /api/v1/payments/checkout
```

Request:

```json
{
  "invoice_id": 1001,
  "gateway": "zarinpal",
  "idempotency_key": "checkout-1001-user-10"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "payment_attempt_id": 501,
    "redirect_url": "https://gateway.example/pay/...",
    "status": "redirected"
  },
  "message": "Payment started",
  "meta": {
    "trace_id": "abc-123"
  }
}
```

---

## Callback

```text
GET /api/v1/payments/callback/{gateway}
```

یا بسته به درگاه:

```text
POST /api/v1/payments/callback/{gateway}
```

قانون:

```text
callback باید payload را ذخیره کند.
callback باید idempotent باشد.
callback نباید بدون verify پرداخت را paid کند.
```

---

## Verify

```text
POST /api/v1/payments/verify
```

Request:

```json
{
  "gateway": "zarinpal",
  "authority": "A00000000000000000000000000000123456",
  "invoice_id": 1001
}
```

Response موفق:

```json
{
  "success": true,
  "data": {
    "invoice_id": 1001,
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

---

# 25. Admin Finance API

```text
GET /api/v1/admin/finance/invoices
GET /api/v1/admin/finance/invoices/{id}

GET /api/v1/admin/finance/transactions
GET /api/v1/admin/payments/attempts

GET /api/v1/admin/commission/rules
POST /api/v1/admin/commission/rules
PATCH /api/v1/admin/commission/rules/{id}
POST /api/v1/admin/commission/rules/{id}/deactivate
```

Permissions:

```text
finance.invoices.read
finance.transactions.read
finance.payments.read
commission.read
commission.create
commission.update
commission.deactivate
```

---

# 26. Notification Events

## Payment / Finance

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
```

## Subscription

```text
SUBSCRIPTION_PAYMENT_REQUIRED
SUBSCRIPTION_ACTIVATED
SUBSCRIPTION_PAYMENT_FAILED
```

## Promotion

```text
PROMOTION_PAYMENT_REQUIRED
PROMOTION_ACTIVATED
PROMOTION_PAYMENT_FAILED
```

---

# 27. Audit Logs

Audit برای این موارد اجباری است:

```text
ساخت یا تغییر commission rule
غیرفعال کردن commission rule
تغییر وضعیت invoice توسط ادمین
verify دستی پرداخت
refund
settlement
تغییر تنظیمات درگاه
فعال‌سازی دستی اشتراک
```

Audit actions:

```text
COMMISSION_RULE_CREATED
COMMISSION_RULE_UPDATED
COMMISSION_RULE_DEACTIVATED

INVOICE_STATUS_CHANGED
PAYMENT_MANUAL_VERIFIED
PAYMENT_ATTEMPT_REVIEWED

SUBSCRIPTION_MANUALLY_ACTIVATED
PROMOTION_MANUALLY_ACTIVATED
```

---

# 28. Payment Errors

Error codeهای مالی:

```text
INVOICE_NOT_FOUND
INVOICE_ALREADY_PAID
INVOICE_NOT_PAYABLE
PAYMENT_GATEWAY_NOT_ACTIVE
PAYMENT_ATTEMPT_NOT_FOUND
PAYMENT_ALREADY_PROCESSED
PAYMENT_VERIFY_FAILED
PAYMENT_AMOUNT_MISMATCH
PAYMENT_CALLBACK_INVALID
COMMISSION_RULE_NOT_FOUND
COMMISSION_CALCULATION_FAILED
```

---

# 29. Payment Security

قوانین امنیتی پرداخت:

```text
verify اجباری
idempotency اجباری
amount check اجباری
invoice ownership check
gateway reference unique
callback payload ذخیره شود
توکن یا secret درگاه داخل log ذخیره نشود
trace_id برای همه عملیات مالی
```

## Amount Check

مبلغ verify شده توسط درگاه باید با invoice برابر باشد.

اگر نبود:

```text
PAYMENT_AMOUNT_MISMATCH
```

و invoice نباید paid شود.

---

# 30. Transaction Safety

عملیات مالی باید transaction دیتابیس داشته باشد.

مثال:

```text
mark invoice paid
create transaction
update payment_attempt
activate subscription/promotion
create notification event
```

باید یا همه انجام شوند، یا هیچ‌کدام.

---

# 31. Concurrency Risk

ممکن است دو callback همزمان برسند.

کنترل لازم:

```text
row lock روی invoice/payment_attempt
unique constraint روی gateway_reference
idempotency_key
check invoice status قبل از paid کردن
```

---

# 32. Admin Panel Finance UI

صفحات لازم:

```text
InvoicesListPage
InvoiceDetailPage
PaymentAttemptsPage
TransactionsPage
CommissionRulesPage
CreateCommissionRulePage
```

ادمین باید بتواند:

```text
فاکتورها را ببیند
جزئیات پرداخت را ببیند
تراکنش‌ها را ببیند
کمیسیون‌ها را مدیریت کند
درگاه فعال را ببیند
```

---

# 33. Flutter Payment UI

صفحات لازم:

```text
InvoiceDetailScreen
PaymentCheckoutScreen
PaymentResultScreen
SubscriptionPlansScreen
PromotionCheckoutScreen
```

UI باید:

```text
مبلغ را تومان نمایش دهد
اعداد فارسی در فارسی نمایش دهد
وضعیت پرداخت را واضح نمایش دهد
خطای پرداخت را قابل فهم نمایش دهد
بعد از پرداخت موفق کاربر را به صفحه درست برگرداند
```

---

# 34. Testing Payment

تست‌های اجباری:

```text
ساخت فاکتور
محاسبه کمیسیون
checkout موفق
callback موفق
verify موفق
verify ناموفق
callback تکراری
verify تکراری
مبلغ اشتباه
invoice already paid
gateway inactive
commission snapshot
تغییر commission rule بعد از invoice
```

---

# 35. Testing Commission

تست‌های کمیسیون:

```text
percent commission
fixed commission
inactive rule
missing rule
snapshot creation
platform amount
provider amount
rule update does not affect old invoice
admin update audit log
```

---

# 36. MVP Scope مالی

در MVP شامل باشد:

```text
invoice
invoice items
commission rules
commission snapshot
payment gateway core
payment attempts
verify
transactions
subscription payment base
promotion payment base
admin finance view
notifications
audit logs
```

در MVP شامل نباشد:

```text
wallet کامل
settlement کامل
refund پیشرفته
multi-gateway advanced routing
accounting system
financial dashboard advanced
```

---

# 37. خط قرمزهای مالی

موارد ممنوع:

```text
پرداخت بدون verify
پرداخت بدون idempotency
invoice بدون item
invoice paid بدون transaction
commission بدون snapshot
تغییر فاکتور paid شده بدون audit
ذخیره secret درگاه در log
callback که مستقیم invoice را paid کند
SMS/notification مالی بدون trace
تغییر commission rule بدون audit
```

---

# 38. نتیجه

سیستم مالی پروژه باید از اول قابل ردیابی، تست‌پذیر و قابل audit باشد.

قانون نهایی:

```text
پول شوخی نیست؛ هر عملیات مالی باید قابل اثبات، قابل پیگیری و قابل بازگشت منطقی باشد.
```
