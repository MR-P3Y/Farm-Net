# 05 — Definition of Done
# معیار اتمام کار در پروژه فارم نت

## 1. هدف سند

این سند مشخص می‌کند در پروژه «فارم نت» چه زمانی یک کار واقعاً تمام‌شده است.

در این پروژه، عبارت‌های زیر قابل قبول نیستند:

```text
تقریباً آماده است
فقط تستش مانده
بعداً مستند می‌کنیم
فعلاً permission ندارد
فعلاً notification ندارد
فعلاً خطاها را بعداً درست می‌کنیم
UI بعداً ریسپانسیو می‌شود
```

هر کاری فقط زمانی Done است که معیارهای این سند را پاس کرده باشد.

---

# 2. قانون اصلی

قانون اصلی پروژه:

```text
کاری که تست نشده، مستند نشده، review نشده و merge استاندارد نشده باشد، تمام‌شده نیست.
```

برای ماژول‌های مهم:

```text
Database
API
Permission
Notification
Audit Log
Flutter UI
Admin UI
Tests
Docs
```

همه باید بررسی شوند.

---

# 3. Definition of Done عمومی برای هر Task

هر task فقط زمانی Done است که:

```text
1. کد پیاده‌سازی شده باشد.
2. کد با معماری پروژه سازگار باشد.
3. validation لازم انجام شده باشد.
4. error handling استاندارد داشته باشد.
5. اگر API دارد، response/error استاندارد داشته باشد.
6. اگر دیتابیس دارد، migration داشته باشد.
7. اگر endpoint حساس است، permission check داشته باشد.
8. اگر به اشتراک مربوط است، subscription check داشته باشد.
9. اگر رویداد مهم ایجاد می‌کند، notification event داشته باشد.
10. اگر عملیات ادمین یا مالی است، audit log داشته باشد.
11. تست لازم انجام شده باشد.
12. مستندات مرتبط آپدیت شده باشد.
13. کد review شده باشد.
14. branch به‌درستی merge شده باشد.
15. issue مربوطه بسته شده باشد.
```

---

# 4. Definition of Done برای Backend Feature

یک feature در Backend فقط زمانی تمام است که:

```text
1. مدل SQLAlchemy در صورت نیاز ساخته شده باشد.
2. schemaهای Pydantic ساخته شده باشند.
3. repository نوشته شده باشد.
4. service نوشته شده باشد.
5. router نوشته شده باشد.
6. business logic داخل service باشد، نه router.
7. validation ورودی‌ها انجام شود.
8. permission check انجام شود.
9. subscription/feature limit check اگر لازم است انجام شود.
10. transaction در عملیات حساس استفاده شود.
11. response استاندارد برگردد.
12. error code استاندارد داشته باشد.
13. trace_id در response و log وجود داشته باشد.
14. notification eventهای لازم ایجاد شود.
15. audit log برای عملیات مهم ثبت شود.
16. تست unit یا integration نوشته شود.
17. Swagger/OpenAPI درست نمایش داده شود.
18. docs/api در صورت نیاز آپدیت شود.
```

---

# 5. Definition of Done برای Database Change

هر تغییر دیتابیس فقط زمانی Done است که:

```text
1. migration Alembic داشته باشد.
2. مدل SQLAlchemy با migration هماهنگ باشد.
3. نام جدول‌ها طبق prefix ماژولار باشد.
4. فیلدهای پایه مثل id, created_at, updated_at وجود داشته باشند.
5. status برای موجودیت‌های دارای وضعیت وجود داشته باشد.
6. deleted_at برای soft delete در صورت نیاز وجود داشته باشد.
7. indexهای لازم تعریف شده باشند.
8. foreign keyهای لازم تعریف شده باشند.
9. migration در local اجرا شده باشد.
10. migration در staging تست شده باشد.
11. rollback یا روش برگشت بررسی شده باشد.
12. docs/database اگر لازم است آپدیت شده باشد.
```

## قوانین نام‌گذاری جدول‌ها

```text
auth_users
store_products
finance_invoices
notify_events
geo_cities
```

## قوانین فیلدهای مشترک

برای جدول‌های اصلی:

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

برای موجودیت‌های حساس یا مدیریتی:

```text
created_by
updated_by
```

---

# 6. Definition of Done برای API Endpoint

هر endpoint فقط زمانی Done است که:

```text
1. URL و method مشخص باشد.
2. request schema مشخص باشد.
3. response schema مشخص باشد.
4. error response استاندارد باشد.
5. auth requirement مشخص باشد.
6. permission requirement مشخص باشد.
7. rate limit اگر لازم است اعمال شود.
8. pagination برای لیست‌ها وجود داشته باشد.
9. sorting/filtering در صورت نیاز وجود داشته باشد.
10. status flow رعایت شود.
11. notification event در صورت نیاز ایجاد شود.
12. audit log در صورت نیاز ثبت شود.
13. Swagger درست باشد.
14. Postman/Swagger تست دستی شده باشد.
15. docs/api آپدیت شده باشد.
```

## فرمت استاندارد Success

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

## فرمت استاندارد Error

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

---

# 7. Definition of Done برای Permission

هر قابلیت حساس فقط زمانی Done است که:

```text
1. permission مربوط تعریف شده باشد.
2. role مناسب به permission وصل شده باشد.
3. endpoint permission check داشته باشد.
4. تست دسترسی مجاز انجام شده باشد.
5. تست دسترسی غیرمجاز انجام شده باشد.
6. error code مناسب برای دسترسی غیرمجاز وجود داشته باشد.
7. مستندات permission آپدیت شده باشد.
```

## مثال permissionها

```text
users.read
users.update_status
shops.approve
shops.reject
products.approve
products.reject
commission.update
invoices.read
notifications.manage
contracts.manage
```

---

# 8. Definition of Done برای Notification Event

هر feature مهم فقط زمانی Done است که notification آن مشخص شده باشد.

## یک Notification Event فقط زمانی Done است که:

```text
1. event name مشخص باشد.
2. trigger مشخص باشد.
3. recipient مشخص باشد.
4. channels مشخص باشند.
5. template فارسی داشته باشد.
6. template انگلیسی داشته باشد.
7. payload لازم مشخص باشد.
8. delivery log ثبت شود.
9. خطای ارسال لاگ شود.
10. retry policy در صورت نیاز مشخص باشد.
11. docs/notifications آپدیت شده باشد.
```

## مثال

```text
Event:
SHOP_APPROVED

Trigger:
وقتی ادمین فروشگاه را تأیید می‌کند.

Recipient:
صاحب فروشگاه

Channels:
In-App + Push + Email

fa template:
فروشگاه شما با موفقیت تأیید شد.

en template:
Your shop has been approved.
```

---

# 9. Definition of Done برای Audit Log

هر عملیات مهم ادمین یا مالی فقط زمانی Done است که audit log داشته باشد.

## عملیات‌هایی که Audit Log اجباری دارند

```text
تغییر نقش کاربر
تغییر وضعیت کاربر
تأیید/رد فروشگاه
تأیید/رد محصول
تأیید/رد مدرک
تغییر کمیسیون
تغییر پلن اشتراک
تغییر وضعیت فاکتور
تغییر وضعیت پرداخت
تعلیق کاربر
تعلیق فروشگاه
حذف محتوای اجتماعی
```

## فیلدهای لازم Audit Log

```text
admin_user_id
action
target_type
target_id
old_value
new_value
ip_address
user_agent
trace_id
created_at
```

---

# 10. Definition of Done برای Payment / Finance

هر قابلیت پرداخت یا مالی فقط زمانی Done است که:

```text
1. invoice ساخته شود.
2. invoice itemها مشخص باشند.
3. مبلغ کل درست محاسبه شود.
4. کمیسیون درست محاسبه شود.
5. commission snapshot ذخیره شود.
6. payment_attempt ساخته شود.
7. اتصال به درگاه انجام شود.
8. callback دریافت شود.
9. verify پرداخت انجام شود.
10. transaction ثبت شود.
11. وضعیت invoice درست تغییر کند.
12. notification پرداخت ارسال شود.
13. audit log ثبت شود.
14. خطاهای پرداخت مدیریت شوند.
15. تست پرداخت موفق انجام شود.
16. تست پرداخت ناموفق انجام شود.
17. تست callback تکراری انجام شود.
18. تست verify نامعتبر انجام شود.
```

## قانون مهم

```text
فاکتور پرداخت‌شده نباید با تغییر commission rule بعدی تغییر کند.
```

---

# 11. Definition of Done برای Commission

Commission فقط زمانی Done است که:

```text
1. rule قابل تعریف باشد.
2. rule از پنل ادمین قابل مدیریت باشد.
3. rule وضعیت active/inactive داشته باشد.
4. module scope مشخص باشد.
5. rate type مشخص باشد: percent/fixed
6. effective_from مشخص باشد.
7. در زمان invoice مقدار commission snapshot شود.
8. platform_amount محاسبه شود.
9. provider_amount محاسبه شود.
10. تغییر rule قبلی فاکتورهای قبلی را تغییر ندهد.
11. audit log برای تغییر commission ثبت شود.
12. تست محاسبه commission نوشته شود.
```

---

# 12. Definition of Done برای Media / File Upload

آپلود فایل فقط زمانی Done است که:

```text
1. محدودیت حجم وجود داشته باشد.
2. محدودیت پسوند وجود داشته باشد.
3. MIME type بررسی شود.
4. نام فایل random شود.
5. مسیر ذخیره امن باشد.
6. فایل metadata ذخیره شود.
7. owner فایل مشخص باشد.
8. visibility مشخص باشد: public/private
9. دسترسی به فایل private کنترل شود.
10. حذف یا غیرفعال‌سازی فایل مشخص باشد.
11. فایل executable اجرا نشود.
12. تست آپلود معتبر انجام شود.
13. تست آپلود نامعتبر انجام شود.
```

---

# 13. Definition of Done برای Verification / Contract

جریان تأیید یا قرارداد فقط زمانی Done است که:

```text
1. verification request ساخته شود.
2. target_type و target_id مشخص باشد.
3. مدارک لازم مشخص باشند.
4. قرارداد مرتبط مشخص باشد.
5. version قرارداد ذخیره شود.
6. تیک پذیرش قرارداد ذخیره شود.
7. PDF قرارداد در صورت نیاز آپلود شود.
8. status flow رعایت شود.
9. ادمین بتواند approve/reject/needs_revision کند.
10. دلیل رد یا اصلاح ذخیره شود.
11. notification وضعیت ارسال شود.
12. audit log تصمیم ادمین ثبت شود.
13. کاربر بتواند وضعیت درخواست را ببیند.
```

---

# 14. Definition of Done برای Flutter UI

هر صفحه Flutter فقط زمانی Done است که:

```text
1. طبق finalui طراحی شده باشد.
2. LSM responsive رعایت شده باشد.
3. از r.dp استفاده نشده باشد.
4. اگر glass لازم است از CrystalGlass استفاده شده باشد.
5. Light/Dark theme را پشتیبانی کند.
6. fa/en را پشتیبانی کند.
7. RTL/LTR درست باشد.
8. اعداد در فارسی فارسی نمایش داده شوند.
9. تاریخ در فارسی شمسی باشد.
10. تومان درست نمایش داده شود.
11. loading state داشته باشد.
12. error state داشته باشد.
13. empty state داشته باشد.
14. validation فرم داشته باشد.
15. API error را درست نمایش دهد.
16. دکمه برگشت با Icons.arrow_back باشد.
17. برگشت با Navigator.pop(context) باشد.
18. روی موبایل و تبلت و وب/عرض بزرگ تست شده باشد.
```

---

# 15. Definition of Done برای Admin UI

هر صفحه Admin فقط زمانی Done است که:

```text
1. permission guard داشته باشد.
2. table/list pagination داشته باشد.
3. search/filter در صورت نیاز داشته باشد.
4. loading/error/empty state داشته باشد.
5. فرم‌ها validation داشته باشند.
6. عملیات مهم confirm dialog داشته باشد.
7. عملیات مهم audit log ایجاد کند.
8. statusها واضح نمایش داده شوند.
9. تاریخ و پول درست نمایش داده شود.
10. خطاهای API قابل فهم نمایش داده شوند.
11. responsive برای web/tablet باشد.
12. role-based access رعایت شود.
```

---

# 16. Definition of Done برای Store Core

Store Core فقط زمانی Done است که:

```text
1. هر کاربر فقط یک فروشگاه بتواند ثبت کند.
2. فروشگاه مدارک داشته باشد.
3. فروشگاه قرارداد داشته باشد.
4. فروشگاه تأیید ادمین لازم داشته باشد.
5. فروشگاه چند عضو داشته باشد.
6. نقش داخلی فروشگاه مشخص باشد: owner/manager/staff/viewer
7. دسته‌بندی محصول از ادمین قابل مدیریت باشد.
8. فروشگاه بتواند محصول ثبت کند.
9. محصول عکس داشته باشد.
10. محصول ویژگی و مزایا داشته باشد.
11. محصول قبل از انتشار تأیید ادمین لازم داشته باشد.
12. وضعیت محصول درست مدیریت شود.
13. محصول منتشرشده در UI عمومی دیده شود.
14. notificationهای فروشگاه و محصول کار کنند.
15. audit logهای ادمین ثبت شوند.
16. تست‌های Store API انجام شده باشند.
17. Shop Panel UI پایه آماده باشد.
```

---

# 17. Definition of Done برای Geo Core

Geo Core فقط زمانی Done است که:

```text
1. استان‌ها قابل seed باشند.
2. شهرستان‌ها قابل seed باشند.
3. شهرها قابل seed باشند.
4. روستاها قابل seed باشند.
5. آدرس کاربر قابل ثبت باشد.
6. آدرس target_type/target_id داشته باشد.
7. مختصات latitude/longitude ذخیره شود.
8. انتخاب دستی پشتیبانی شود.
9. ساختار انتخاب از نقشه آماده باشد.
10. API فیلتر استان/شهر/روستا کار کند.
11. Admin در صورت نیاز بتواند داده geo را مدیریت کند.
```

---

# 18. Definition of Done برای Billing / Subscription

Billing فقط زمانی Done است که:

```text
1. پلن قابل تعریف باشد.
2. ویژگی‌های پلن قابل تعریف باشند.
3. اشتراک کاربر قابل ثبت باشد.
4. شروع و پایان اشتراک ذخیره شود.
5. وضعیت اشتراک مشخص باشد.
6. مصرف ویژگی‌ها ثبت شود.
7. محدودیت امکانات قابل بررسی باشد.
8. ادمین بتواند پلن را مدیریت کند.
9. ادمین بتواند اشتراک را دستی فعال یا لغو کند.
10. notification پایان اشتراک ارسال شود.
```

---

# 19. Definition of Done برای Promotion / Ladder

Promotion فقط زمانی Done است که:

```text
1. پکیج تبلیغ قابل تعریف باشد.
2. جایگاه تبلیغ مشخص باشد.
3. target_type مشخص باشد: shop/product/service/consultant
4. مدت زمان تبلیغ مشخص باشد.
5. قیمت تبلیغ مشخص باشد.
6. پرداخت تبلیغ به invoice وصل شود.
7. تبلیغ فعال روی رتبه نمایش اثر بگذارد.
8. تبلیغ منقضی شود.
9. notification شروع/پایان تبلیغ ارسال شود.
10. ادمین بتواند تبلیغ را مدیریت کند.
```

---

# 20. Definition of Done برای Localization

Localization فقط زمانی Done است که:

```text
1. متن‌ها hard-code نشده باشند.
2. فارسی و انگلیسی پشتیبانی شوند.
3. RTL برای فارسی درست باشد.
4. LTR برای انگلیسی درست باشد.
5. اعداد فارسی در حالت فارسی نمایش داده شوند.
6. تاریخ شمسی در حالت فارسی نمایش داده شود.
7. تومان در حالت فارسی نمایش داده شود.
8. خطاهای API به پیام قابل فهم ترجمه شوند.
9. notification templates فارسی و انگلیسی داشته باشند.
```

---

# 21. Definition of Done برای Tests

تست‌ها فقط زمانی قابل قبول هستند که:

```text
1. سناریوی موفق را تست کنند.
2. سناریوی خطا را تست کنند.
3. permission denied را تست کنند.
4. validation error را تست کنند.
5. edge case مهم را تست کنند.
6. برای payment، callback تکراری و verify نامعتبر تست شود.
7. برای commission، تغییر rule قبلی روی invoice قبلی اثر نگذارد.
8. برای notification، event و delivery attempt تست شود.
```

---

# 22. Definition of Done برای Documentation

مستندات فقط زمانی Done است که:

```text
1. فایل مربوط در docs آپدیت شده باشد.
2. API contract اگر تغییر کرده آپدیت شده باشد.
3. database design اگر تغییر کرده آپدیت شده باشد.
4. notification events اگر تغییر کرده آپدیت شده باشد.
5. payment flow اگر تغییر کرده آپدیت شده باشد.
6. README اگر اجرای پروژه تغییر کرده آپدیت شده باشد.
7. توضیح برای تیم‌های دیگر قابل فهم باشد.
```

---

# 23. Definition of Done برای Release

یک release فقط زمانی Done است که:

```text
1. release branch ساخته شده باشد.
2. تمام featureهای لازم merge شده باشند.
3. تست backend پاس شده باشد.
4. تست Flutter پاس شده باشد.
5. migration در staging اجرا شده باشد.
6. Postman/Swagger تست شده باشد.
7. Flutter build ساخته شده باشد.
8. Admin build ساخته شده باشد.
9. Docker build موفق باشد.
10. backup قبل از deploy گرفته شده باشد.
11. release notes نوشته شده باشد.
12. tag زده شده باشد.
13. نسخه روی staging یا production اجرا شده باشد.
14. smoke test بعد از deploy انجام شده باشد.
```

---

# 24. Definition of Done برای MVP v1

MVP v1 فقط زمانی Done است که:

```text
1. Backend Foundation آماده باشد.
2. Flutter Foundation آماده باشد.
3. Admin Panel Foundation آماده باشد.
4. Auth با موبایل OTP کار کند.
5. Auth با ایمیل/رمز کار کند.
6. Roles و Permissions کار کنند.
7. پروفایل رایگان کاربر ساخته شود.
8. Geo Core کار کند.
9. Notification Core کار کند.
10. SMS OTP کار کند.
11. Email رسمی پایه کار کند.
12. Push ساختار آماده داشته باشد.
13. Media Upload کار کند.
14. Documents کار کند.
15. Verification کار کند.
16. Contracts با تیک و PDF کار کند.
17. Billing Core کار کند.
18. Commission Core کار کند.
19. Payment Gateway Core کار کند.
20. Invoice Core کار کند.
21. Store Core کار کند.
22. Shop Members کار کند.
23. Product Management کار کند.
24. Product Approval کار کند.
25. Shop Panel Core آماده باشد.
26. Public Store UI آماده باشد.
27. Admin Store Management آماده باشد.
28. Promotion Core ساده کار کند.
29. APIها مستند باشند.
30. Postman/Swagger تست شده باشد.
31. Docs آپدیت باشند.
32. Git tag برای MVP زده شده باشد.
```

---

# 25. خط قرمزها

موارد زیر در پروژه قابل قبول نیستند:

```text
1. کد بدون review
2. migration دستی بدون Alembic
3. endpoint بدون permission برای بخش حساس
4. UI غیرریسپانسیو
5. متن hard-code برای فارسی/انگلیسی
6. فایل آپلود بدون validation
7. پرداخت بدون verify
8. کمیسیون بدون snapshot
9. عملیات ادمین بدون audit log
10. feature مهم بدون notification event
11. API تغییرکرده بدون docs
12. secret داخل Git
13. deploy بدون backup
14. release بدون tag
```

---

# 26. نتیجه

این سند معیار رسمی اتمام کار در پروژه «فارم نت» است.

هیچ تیمی نباید کاری را Done اعلام کند مگر اینکه معیارهای مربوط به آن را پاس کرده باشد.

قانون نهایی:

```text
Done یعنی قابل اجرا، قابل تست، قابل استفاده، قابل مستند، قابل review و قابل نگهداری.
```
