# 09 — Permissions and Roles
# نقش‌ها و دسترسی‌های پروژه فارم نت

## 1. هدف سند

این سند مدل نقش‌ها و دسترسی‌های پروژه «فارم نت» را مشخص می‌کند.

چون پروژه چندبخشی است و شامل کاربران عادی، فروشگاه‌ها، موجران، خدمات‌دهندگان، مشاوران، ادمین‌ها، پشتیبان‌ها و شرکت‌های طرف قرارداد داده می‌شود، سیستم دسترسی باید از اول دقیق و قابل توسعه طراحی شود.

هدف این سند جلوگیری از مشکلات زیر است:

```text
دسترسی غیرمجاز کاربران
ادمین‌های بیش از حد قدرتمند
تغییرات حساس بدون کنترل
دسترسی اشتباه اعضای فروشگاه
مشکل در کنترل پنل‌های مختلف
ناامنی اطلاعات مالی، مدارک و داده‌ها
```

---

# 2. اصل بنیادین

در این پروژه فقط Role کافی نیست.

مدل دسترسی باید ترکیبی باشد:

```text
Role-Based Access Control + Permission-Based Access Control
```

یعنی:

```text
Role = عنوان یا جایگاه کاربر
Permission = اجازه دقیق برای انجام یک عمل
```

مثال:

```text
Role: admin
Permission: products.approve
```

ممکن است دو ادمین داشته باشیم، اما یکی اجازه تأیید محصول داشته باشد و دیگری نداشته باشد.

---

# 3. قانون اصلی User

در سیستم:

```text
User = حساب اصلی شخص
```

User به خودی خود فروشنده، مشاور یا موجر نیست.

کاربر بعد از ثبت‌نام یک پروفایل رایگان دارد.
سپس می‌تواند درخواست فعالیت حرفه‌ای بدهد:

```text
ثبت فروشگاه
موجر شدن
خدمات‌دهنده شدن
مشاور شدن
شرکت داده شدن
```

فعال شدن این نقش‌ها نیازمند:

```text
مدارک
قرارداد
بررسی ادمین
تأیید
```

---

# 4. جدول‌های اصلی دسترسی

```text
auth_users
auth_roles
auth_permissions
auth_user_roles
auth_role_permissions
```

برای نقش‌های داخلی فروشگاه:

```text
store_shop_members
```

در آینده برای نقش‌های داخلی سایر بخش‌ها هم می‌توان جدول مشابه داشت.

---

# 5. نقش‌های سراسری سیستم

## نقش‌های پایه

```text
user
shop_owner
shop_manager
service_provider
lessor
consultant
support
content_manager
finance_admin
verification_admin
admin
super_admin
data_client
```

---

# 6. توضیح نقش‌ها

## user

کاربر عادی سیستم.

دسترسی‌ها:

```text
مشاهده محصولات منتشرشده
مشاهده فروشگاه‌ها
ثبت پروفایل رایگان
ثبت آدرس
دریافت نوتیفیکیشن
ثبت درخواست فعالیت حرفه‌ای
استفاده محدود از امکانات رایگان
```

---

## shop_owner

صاحب فروشگاه تأییدشده.

قوانین:

```text
هر user فقط یک فروشگاه می‌تواند داشته باشد.
فعال شدن shop_owner نیازمند مدارک، قرارداد و تأیید ادمین است.
```

دسترسی‌ها:

```text
مدیریت فروشگاه خود
مدیریت محصولات فروشگاه خود
مدیریت اعضای فروشگاه
مشاهده فاکتورهای فروشگاه
درخواست تبلیغ/نردبان
مشاهده نوتیفیکیشن‌های فروشگاه
```

---

## shop_manager

مدیر فروشگاه.

این نقش داخل فروشگاه تعریف می‌شود، نه الزاماً role سراسری.

دسترسی‌ها:

```text
مدیریت محصولات فروشگاه
مشاهده برخی فاکتورها
مدیریت سفارش‌ها یا درخواست‌ها در آینده
```

محدودیت:

```text
نمی‌تواند مالک فروشگاه را تغییر دهد.
نمی‌تواند فروشگاه را حذف یا تعطیل کند.
نمی‌تواند حساب مالی اصلی را تغییر دهد.
```

---

## service_provider

ارائه‌دهنده خدمات کشاورزی.

فعال شدن نیازمند:

```text
مدارک
قرارداد
تأیید ادمین
```

دسترسی‌ها:

```text
ثبت خدمت
مدیریت خدمات خود
مشاهده درخواست‌های خدمات
مشاهده فاکتورهای خدمات
```

---

## lessor

موجر ادوات کشاورزی.

تعریف:

```text
کاربری که ادوات کشاورزی خود را با راننده یا بدون راننده اجاره می‌دهد.
```

فعال شدن نیازمند:

```text
مدارک
قرارداد
تأیید ادمین
```

دسترسی‌ها:

```text
ثبت ادوات
مدیریت ادوات خود
مشخص کردن با راننده / بدون راننده
مشاهده درخواست‌های اجاره
مشاهده فاکتورهای اجاره
```

---

## consultant

مشاور کشاورزی تأییدشده.

فعال شدن نیازمند:

```text
مدارک
قرارداد
تخصص
تأیید ادمین
```

دسترسی‌ها:

```text
مدیریت پروفایل مشاور
مدیریت تخصص‌ها
مشاهده درخواست‌های مشاوره
پاسخ به درخواست‌های مشاوره
مشاهده فاکتورهای مشاوره
```

---

## support

پشتیبان کاربران.

دسترسی‌ها:

```text
مشاهده کاربران
مشاهده وضعیت درخواست‌ها
مشاهده نوتیفیکیشن‌ها
کمک به کاربران
```

محدودیت:

```text
نباید به تغییر کمیسیون، پرداخت، نقش‌ها یا قراردادها دسترسی داشته باشد.
```

---

## content_manager

مدیر محتوا.

دسترسی‌ها:

```text
مدیریت دسته‌بندی‌ها
مدیریت محتوای آموزشی
مدیریت فضای اجتماعی
بررسی گزارش تخلف
حذف یا رد محتوای نامناسب
```

---

## finance_admin

ادمین مالی.

دسترسی‌ها:

```text
مشاهده فاکتورها
مشاهده پرداخت‌ها
مدیریت تراکنش‌ها
مشاهده کمیسیون‌ها
مدیریت تسویه در آینده
```

محدودیت:

```text
تغییر commission rule فقط اگر permission جدا داشته باشد.
```

---

## verification_admin

ادمین بررسی مدارک و قراردادها.

دسترسی‌ها:

```text
مشاهده مدارک
تأیید/رد مدارک
بررسی قراردادها
تأیید/رد درخواست فروشگاه
تأیید/رد درخواست مشاور
تأیید/رد درخواست موجر
```

---

## admin

ادمین عمومی با دسترسی‌های محدود شده توسط permission.

ادمین نباید به صورت پیش‌فرض همه دسترسی‌ها را داشته باشد.

---

## super_admin

مالک کامل سیستم.

دسترسی‌ها:

```text
مدیریت همه بخش‌ها
مدیریت ادمین‌ها
مدیریت permissionها
مدیریت تنظیمات حساس
مدیریت کمیسیون‌ها
مدیریت پرداخت‌ها
دسترسی به audit logs
```

قانون:

```text
تعداد super_admin باید بسیار محدود باشد.
```

---

## data_client

شرکت یا سازمان طرف قرارداد داده.

دسترسی‌ها:

```text
مشاهده داده‌های مجاز
دریافت exportهای مجاز
مشاهده گزارش‌های قراردادی
```

محدودیت:

```text
دسترسی به داده حساس فقط با قرارداد، permission و log مجاز است.
```

---

# 7. نقش‌های داخلی فروشگاه

فروشگاه می‌تواند چند عضو داشته باشد.

جدول:

```text
store_shop_members
```

نقش‌های داخلی:

```text
owner
manager
staff
viewer
```

## owner

```text
مالک فروشگاه
دسترسی کامل به فروشگاه
فقط یک owner اصلی وجود دارد
```

## manager

```text
مدیریت محصولات
مشاهده فاکتورها
مدیریت برخی اعضا در صورت مجوز
```

## staff

```text
ثبت یا ویرایش محدود محصول
مشاهده وضعیت محصول
```

## viewer

```text
فقط مشاهده اطلاعات فروشگاه و گزارش‌های مجاز
```

---

# 8. تفاوت role سراسری و role داخلی

## role سراسری

در جدول:

```text
auth_user_roles
```

مثال:

```text
shop_owner
consultant
admin
```

## role داخلی فروشگاه

در جدول:

```text
store_shop_members
```

مثال:

```text
owner
manager
staff
viewer
```

یک کاربر ممکن است role سراسری `shop_owner` داشته باشد، اما داخل فروشگاه هم `owner` باشد.

---

# 9. Permission Naming Standard

فرمت permission:

```text
module.action
```

مثال:

```text
users.read
products.approve
commission.update
```

قانون:

```text
permissionها انگلیسی، lowercase و snake_case باشند.
```

---

# 10. Permissionهای Auth و Users

```text
users.read
users.read_detail
users.update_status
users.suspend
users.restore
users.manage_roles

roles.read
roles.create
roles.update
roles.delete
permissions.read
permissions.assign
```

---

# 11. Permissionهای Profile

```text
profiles.read
profiles.update
profiles.read_private
```

---

# 12. Permissionهای Geo

```text
geo.read
geo.manage
geo.seed
```

---

# 13. Permissionهای Notification

```text
notifications.read
notifications.manage_templates
notifications.send_test
notifications.view_delivery_logs
notifications.manage_channels
```

---

# 14. Permissionهای Media و Documents

```text
media.read
media.upload
media.delete
documents.read
documents.review
documents.approve
documents.reject
```

---

# 15. Permissionهای Verification و Contracts

```text
verification.read
verification.review
verification.approve
verification.reject
verification.needs_revision

contracts.read
contracts.create
contracts.update
contracts.activate
contracts.deactivate
contracts.review_signed_pdf
```

---

# 16. Permissionهای Billing و Subscription

```text
billing.plans.read
billing.plans.create
billing.plans.update
billing.plans.delete

billing.subscriptions.read
billing.subscriptions.activate
billing.subscriptions.cancel
billing.usage.read

billing.plans.public_read
billing.subscription.read_own
billing.subscription.manage_own
billing.usage.read_own
billing.entitlements.read
billing.audit.read
billing.reconciliation.read
```

---

# 17. Permissionهای Commission

```text
commission.read
commission.create
commission.update
commission.deactivate
```

قانون:

```text
تغییر commission rule همیشه audit log لازم دارد.
```

---

# 18. Permissionهای Finance و Payment

```text
finance.invoices.read
finance.invoices.read_detail
finance.transactions.read
finance.payments.read
finance.payments.verify_manual
finance.refunds.create
finance.settlements.read
finance.settlements.manage
```

---

# 19. Permissionهای Store

```text
shops.read
shops.read_detail
shops.approve
shops.reject
shops.suspend
shops.restore

shop_members.read
shop_members.manage

store_categories.read
store_categories.create
store_categories.update
store_categories.delete

products.read
products.read_detail
products.approve
products.reject
products.suspend
products.restore
```

---

# 20. Permissionهای Promotion

```text
promotions.read
promotions.create
promotions.update
promotions.activate
promotions.cancel

promotion_packages.read
promotion_packages.create
promotion_packages.update
promotion_packages.delete
```

---

# 21. Permissionهای Services / Rental

```text
services.read
services.approve
services.reject
services.suspend

service_categories.read
service_categories.create
service_categories.update
service_categories.delete

rental_equipment.read
rental_equipment.approve
rental_equipment.reject
rental_equipment.suspend
```

---

# 22. Permissionهای Consultants

```text
consultants.read
consultants.approve
consultants.reject
consultants.suspend

consult_specialties.read
consult_specialties.create
consult_specialties.update
consult_specialties.delete

consult_requests.read
consult_requests.manage
```

---

# 23. Permissionهای Weather

```text
weather.read
weather.manage_locations
weather.manage_alerts
```

---

# 24. Permissionهای AI

```text
ai.requests.read
ai.feedback.read
ai.knowledge_sources.read
ai.knowledge_sources.create
ai.knowledge_sources.update
ai.usage.read
```

---

# 25. Permissionهای Social

```text
social.posts.read
social.posts.remove
social.comments.read
social.comments.remove
social.reports.read
social.reports.resolve
social.users.block
```

---

# 26. Permissionهای Data Access

```text
data_clients.read
data_clients.create
data_clients.update
data_clients.suspend

data_access.contracts.read
data_access.contracts.manage
data_access.exports.read
data_access.exports.approve
data_access.logs.read
```

---

# 27. Permissionهای Dashboard و Reports

```text
dashboard.read
reports.read
reports.export
reports.finance
reports.users
reports.store
reports.ai
reports.social
```

---

# 28. Permissionهای Settings و Feature Flags

```text
settings.read
settings.update

feature_flags.read
feature_flags.update
```

---

# 29. Mapping پیشنهادی نقش‌ها به Permissionها

## user

```text
profiles.update
geo.read
notifications.read
media.upload
```

---

## shop_owner

```text
profiles.update
geo.read
notifications.read
media.upload

shop_members.read
shop_members.manage

products.read
products.read_detail
```

نکته:

```text
shop_owner برای محصول‌های فروشگاه خودش دسترسی عملیاتی دارد.
این دسترسی باید با owner check در service کنترل شود، نه فقط permission عمومی.
```

---

## shop_manager

```text
products.read
products.read_detail
```

دسترسی عملیاتی روی محصولات فروشگاه خودش با membership check کنترل می‌شود.

---

## support

```text
users.read
users.read_detail
shops.read
shops.read_detail
products.read
products.read_detail
verification.read
notifications.read
```

---

## verification_admin

```text
documents.read
documents.review
documents.approve
documents.reject

verification.read
verification.review
verification.approve
verification.reject
verification.needs_revision

contracts.read
contracts.review_signed_pdf

shops.read
shops.read_detail
consultants.read
services.read
```

---

## finance_admin

```text
finance.invoices.read
finance.invoices.read_detail
finance.transactions.read
finance.payments.read
billing.subscriptions.read
commission.read
```

اگر اجازه تغییر کمیسیون داشته باشد:

```text
commission.update
```

---

## content_manager

```text
store_categories.read
store_categories.create
store_categories.update

service_categories.read
service_categories.create
service_categories.update

consult_specialties.read
consult_specialties.create
consult_specialties.update

social.posts.read
social.posts.remove
social.comments.read
social.comments.remove
social.reports.read
social.reports.resolve
```

---

## admin

ادمین عمومی باید permissionهای محدود و قابل تنظیم داشته باشد.

پیشنهاد:

```text
dashboard.read
users.read
shops.read
products.read
verification.read
finance.invoices.read
notifications.read
```

اما دسترسی‌های حساس مثل تغییر کمیسیون، پرداخت و نقش‌ها باید جداگانه داده شوند.

---

## super_admin

```text
all permissions
```

قانون:

```text
super_admin فقط برای مالک سیستم و افراد بسیار محدود.
```

---

## data_client

```text
data_access.exports.read
reports.read
```

همه دسترسی‌های data_client باید contract-based و permission-based باشند.

---

# 30. Ownership Check

Permission عمومی کافی نیست.

برای داده‌هایی که مالک دارند، باید ownership check انجام شود.

مثال:

```text
یک shop_owner فقط می‌تواند محصول فروشگاه خودش را ویرایش کند.
یک consultant فقط می‌تواند درخواست‌های مشاوره خودش را ببیند.
یک user فقط می‌تواند نوتیفیکیشن‌های خودش را ببیند.
```

پس در service باید این چک‌ها وجود داشته باشد:

```text
check_shop_membership(user_id, shop_id)
check_product_belongs_to_shop(product_id, shop_id)
check_notification_owner(user_id, notification_id)
check_invoice_owner_or_admin(user_id, invoice_id)
```

---

# 31. Permission + Ownership

برای بعضی عملیات‌ها هر دو لازم است.

مثال:

```text
PATCH /api/v1/store/products/{id}
```

لازم دارد:

```text
user logged in
user is member of product shop
user has internal shop role: owner/manager/staff
product is not locked
```

برای ادمین:

```text
Permission: products.approve
```

---

# 32. Admin Permission Guard

تمام routeهای admin باید permission guard داشته باشند.

مثال:

```text
GET /api/v1/admin/users
Permission: users.read

POST /api/v1/admin/store/products/{id}/approve
Permission: products.approve

PATCH /api/v1/admin/commission/rules/{id}
Permission: commission.update
```

اگر permission نبود:

```text
403 Forbidden
PERMISSION_DENIED
```

---

# 33. Frontend Permission Guard

پنل ادمین و اپ باید UI را براساس permission کنترل کنند.

اما قانون مهم:

```text
مخفی کردن دکمه در فرانت کافی نیست.
Backend همیشه باید permission check داشته باشد.
```

Admin UI باید:

```text
اگر permission ندارد، منو را نمایش ندهد.
اگر URL مستقیم زد، صفحه forbidden نمایش دهد.
```

---

# 34. Forbidden UI

در Flutter/Admin برای دسترسی غیرمجاز:

```text
403 Forbidden Page
پیام فارسی/انگلیسی
دکمه برگشت
```

---

# 35. Permission Seed

Permissionها باید seed شوند.

مسیر پیشنهادی:

```text
scripts/seed/permissions.py
```

Seed اولیه باید شامل:

```text
roles
permissions
role_permissions
super_admin
```

---

# 36. Super Admin Bootstrap

در اولین اجرای پروژه باید یک super_admin ساخته شود.

روش پیشنهادی:

```text
از env
```

مثال:

```text
SUPER_ADMIN_EMAIL=
SUPER_ADMIN_PHONE=
SUPER_ADMIN_PASSWORD=
```

قانون:

```text
بعد از ساخت super_admin، password پیش‌فرض باید تغییر کند.
```

---

# 37. Role Assignment Rules

فقط کاربر دارای permission زیر می‌تواند role بدهد:

```text
users.manage_roles
```

تغییر نقش باید audit log داشته باشد.

Audit action:

```text
USER_ROLE_ASSIGNED
USER_ROLE_REMOVED
```

---

# 38. Sensitive Permissions

دسترسی‌های حساس:

```text
users.manage_roles
commission.update
finance.payments.verify_manual
finance.refunds.create
finance.settlements.manage
settings.update
feature_flags.update
data_access.exports.approve
```

قانون:

```text
این permissionها فقط به super_admin یا افراد بسیار محدود داده شوند.
```

---

# 39. Temporary Access

اگر لازم شد به ادمین دسترسی موقت داده شود، باید تاریخ انقضا داشته باشد.

در MVP می‌توانیم این را بعداً اضافه کنیم، اما در طراحی دیده شود.

جدول احتمالی آینده:

```text
auth_temporary_permissions
```

---

# 40. Audit Log برای Permission

تمام عملیات‌های زیر audit log لازم دارند:

```text
ایجاد role
ویرایش role
حذف role
اضافه کردن permission به role
حذف permission از role
دادن role به user
حذف role از user
تغییر status کاربر
```

---

# 41. خطاهای دسترسی

## بدون token

```text
401 Unauthorized
AUTH_TOKEN_REQUIRED
```

## token منقضی

```text
401 Unauthorized
AUTH_TOKEN_EXPIRED
```

## token نامعتبر

```text
401 Unauthorized
AUTH_TOKEN_INVALID
```

## permission ناکافی

```text
403 Forbidden
PERMISSION_DENIED
```

## مالک نبودن resource

```text
403 Forbidden
RESOURCE_ACCESS_DENIED
```

---

# 42. تست‌های Permission

برای هر endpoint حساس باید این تست‌ها وجود داشته باشد:

```text
کاربر بدون token
کاربر با token نامعتبر
کاربر بدون permission
کاربر با permission
کاربر با permission اما بدون ownership
کاربر با permission و ownership
```

---

# 43. Permission در API Docs

هر endpoint در docs/api باید permission موردنیاز را مشخص کند.

مثال:

```text
POST /api/v1/admin/store/products/{id}/approve
Permission: products.approve
Audit: PRODUCT_APPROVED_BY_ADMIN
Notification: PRODUCT_APPROVED
```

---

# 44. خط قرمزهای نقش و دسترسی

موارد ممنوع:

```text
endpoint admin بدون permission
اتکا فقط به frontend برای کنترل دسترسی
دادن super_admin به افراد زیاد
تغییر role بدون audit log
دسترسی به resource دیگران بدون ownership check
permissionهای hard-code پراکنده
roleهای بدون مستندات
```

---

# 45. نتیجه

سیستم نقش‌ها و دسترسی‌ها باید از اول دقیق، قابل تست و قابل توسعه باشد.

قانون نهایی:

```text
هر کاربر فقط باید به همان چیزی دسترسی داشته باشد که نقش، permission، ownership و وضعیت تأییدش اجازه می‌دهد.
```
# Phase 20 Finance Permission Addendum

`wallet.read_own` is granted explicitly to user, shop owner, service provider,
lessor, and consultant roles. Finance operations separate
`finance.wallets.read`, `finance.ledger.read`, `finance.ledger.reconcile`, and
`finance.ledger.post_internal`. Internal posting is not assigned to ordinary or
Finance Admin roles; Super Admin receives it through the existing all-permission
rule until a dedicated machine identity is implemented.
