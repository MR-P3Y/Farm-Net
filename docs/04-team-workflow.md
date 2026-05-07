# 04 — Team Workflow
# روند همکاری تیمی پروژه فارم نت

## 1. هدف سند

این سند قوانین همکاری تیمی پروژه «فارم نت» را مشخص می‌کند.

چون پروژه توسط ۲ یا ۳ تیم انجام می‌شود، بدون روند کاری مشخص، پروژه به‌سرعت دچار این مشکلات می‌شود:

```text
کدهای ناهماهنگ
APIهای ناسازگار
UIهای متفاوت
تغییرات بدون مستندات
mergeهای خراب
دیتابیس‌های ناهماهنگ
باگ‌های سخت‌ردیابی
دوباره‌کاری
گم شدن وضعیت پروژه
```

هدف این سند این است که همه تیم‌ها با یک قانون مشترک کار کنند.

---

# 2. تیم‌های اصلی پروژه

## Team A — Backend / API

مسئولیت‌ها:

```text
FastAPI Backend
MySQL Database
SQLAlchemy Models
Alembic Migrations
Business Logic
Permissions
Subscriptions
Commission
Payment
Notifications Backend
API Tests
Swagger/OpenAPI
```

---

## Team B — Flutter App / UI

مسئولیت‌ها:

```text
Flutter Mobile App
User UI
Shop Panel UI
finalui
LSM Responsive
Localization fa/en
Light/Dark Theme
API Integration
State Management
Forms
Error/Loading/Empty States
```

---

## Team C — Admin / DevOps / QA / Data

اگر تیم سوم وجود داشته باشد، مسئولیت‌ها:

```text
Flutter Web Admin
Docker
Deployment
Nginx
SSL
Backup
Restore Test
Postman Collections
QA Testing
Geo Seed Data
Documentation Review
Release Management
```

اگر فقط دو تیم وجود داشته باشد:

```text
Team A:
Backend + DevOps + Database

Team B:
Flutter App + Flutter Web Admin + QA

Docs و QA نباید بدون مالک بمانند.
```

---

# 3. اصل مالکیت ماژول‌ها

هر ماژول باید یک مالک مشخص داشته باشد.

مثلاً:

```text
Auth Module Owner: Backend Team Lead
Flutter Auth UI Owner: Flutter Team Lead
Admin Auth Management Owner: Admin Team Lead
Geo Seed Owner: Data/QA Team
Notification Owner: Backend Team + Flutter Team
Payment Owner: Backend Team + Admin Team
```

قانون:

```text
هیچ ماژولی بدون مالک شروع نمی‌شود.
هیچ تغییری بدون اطلاع مالک ماژول merge نمی‌شود.
```

---

# 4. ساختار Repository

ساختار پروژه به‌صورت monorepo است:

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

قانون:

```text
تمام کد، مستندات، migrationها، postman collectionها و scripts باید داخل همین repository باشند.
```

موارد ممنوع داخل repository:

```text
.env واقعی
رمزها
توکن‌ها
کلیدهای خصوصی
فایل‌های SSL واقعی
بکاپ دیتابیس واقعی
فایل‌های آپلودی کاربران
```

---

# 5. Git Branch Strategy

Branchهای اصلی:

```text
main
develop
feature/*
fix/*
hotfix/*
release/*
```

## main

```text
فقط نسخه پایدار و قابل انتشار
هیچ‌کس مستقیم روی main کد نمی‌زند
فقط از release یا hotfix به main merge می‌شود
```

## develop

```text
شاخه اصلی توسعه
تمام featureها بعد از review به develop merge می‌شوند
```

## feature branches

برای هر قابلیت جدید:

```text
feature/auth-core
feature/geo-core
feature/notification-core
feature/store-core
feature/admin-users
feature/flutter-auth-ui
```

## fix branches

برای باگ‌های عادی:

```text
fix/product-status-bug
fix/payment-callback-error
fix/otp-rate-limit
```

## hotfix branches

برای خطاهای فوری production:

```text
hotfix/payment-verify-production
hotfix/login-token-expire
```

## release branches

برای آماده‌سازی نسخه:

```text
release/v0.1.0
release/v0.2.0
release/v1.0.0
```

---

# 6. قوانین Git

```text
1. هیچ‌کس مستقیم روی main commit نمی‌زند.
2. هیچ‌کس مستقیم روی develop commit نمی‌زند مگر با اجازه Lead.
3. هر قابلیت باید branch جدا داشته باشد.
4. هر branch باید نام واضح داشته باشد.
5. هر merge باید از طریق Pull Request انجام شود.
6. هر Pull Request باید review شود.
7. هر Pull Request باید تست‌های مربوط را پاس کند.
8. هر migration باید داخل همان PR باشد.
9. هر تغییر API باید docs/API Contract را آپدیت کند.
10. هر تغییر UI باید screenshot یا توضیح تست داشته باشد.
```

---

# 7. Commit Message Standard

فرمت commit:

```text
type(scope): message
```

## typeهای مجاز

```text
feat
fix
docs
test
refactor
chore
style
perf
build
ci
```

## مثال‌ها

```text
feat(auth): add otp login endpoint
feat(store): add product approval flow
fix(payment): handle failed verify response
docs(api): update invoice contract
test(auth): add permission tests
refactor(media): simplify file validation
chore(docker): add redis service
```

## قوانین commit

```text
commit باید کوچک و قابل فهم باشد.
commit نباید شامل چند قابلیت نامربوط باشد.
پیام commit باید انگلیسی و واضح باشد.
commitهایی مثل "update", "fix", "changes" ممنوع هستند.
```

---

# 8. Pull Request Rules

هر Pull Request باید شامل این موارد باشد:

```text
1. خلاصه تغییرات
2. ماژول مرتبط
3. لیست فایل‌های مهم تغییرکرده
4. migrationها اگر وجود دارد
5. APIهای جدید یا تغییرکرده
6. Notification Eventهای اضافه‌شده
7. Permissionهای اضافه‌شده
8. تست‌هایی که انجام شده
9. Screenshot برای UI اگر لازم است
10. ریسک‌های احتمالی
```

## قالب پیشنهادی PR

```md
## Summary
توضیح کوتاه تغییرات

## Module
auth / store / notification / finance / ...

## Changes
- ...
- ...

## Database
- [ ] No migration
- [ ] Migration added: ...

## API Contract
- [ ] No API change
- [ ] API docs updated

## Notifications
- [ ] No notification event
- [ ] Events added: ...

## Permissions
- [ ] No permission change
- [ ] Permissions added: ...

## Tests
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual Swagger/Postman test
- [ ] Flutter test

## Screenshots
اگر UI دارد

## Risks
ریسک‌ها و نکات مهم
```

---

# 9. Code Review Rules

هیچ PR بدون review merge نمی‌شود.

## Backend Review باید بررسی کند:

```text
ساختار Router → Service → Repository رعایت شده؟
منطق سنگین داخل router نیست؟
Migration درست است؟
Permission check وجود دارد؟
Subscription check اگر لازم است وجود دارد؟
Notification event اگر لازم است ساخته شده؟
Audit log برای عملیات مهم ثبت شده؟
Error response استاندارد است؟
Test وجود دارد؟
```

## Flutter Review باید بررسی کند:

```text
finalui رعایت شده؟
LSM responsive رعایت شده؟
r.dp استفاده نشده؟
Light/Dark درست است؟
fa/en درست است؟
RTL/LTR درست است؟
اعداد فارسی در حالت فارسی درست است؟
تاریخ شمسی درست است؟
Loading/Error/Empty state وجود دارد؟
API error mapping درست است؟
```

## Admin Review باید بررسی کند:

```text
Permission guard وجود دارد؟
جدول‌ها pagination دارند؟
فیلتر و search درست است؟
عملیات مهم confirm dialog دارد؟
عملیات مهم audit log می‌سازد؟
وضعیت‌ها واضح نمایش داده می‌شوند؟
```

---

# 10. API Contract Workflow

هیچ UI جدی نباید قبل از مشخص شدن API Contract ساخته شود.

برای هر API باید مشخص باشد:

```text
URL
Method
Auth required یا نه
Permission required
Request body
Success response
Error response
Pagination
Status flow
Notification events
Audit logs
```

## قانون

```text
Backend و Flutter قبل از شروع هر feature باید API Contract را تأیید کنند.
اگر API تغییر کرد، docs باید همان PR آپدیت شود.
```

## مسیر پیشنهادی مستندات API

```text
docs/api/
  auth.md
  geo.md
  notification.md
  media.md
  verification.md
  billing.md
  finance.md
  store.md
```

---

# 11. Database Workflow

تمام تغییرات دیتابیس باید با Alembic انجام شود.

## قوانین

```text
هیچ تغییر دستی روی دیتابیس بدون migration مجاز نیست.
هر migration باید در local تست شود.
هر migration باید در staging تست شود.
هر migration باید rollback قابل بررسی داشته باشد.
نام migration باید واضح باشد.
```

## نام‌گذاری migration

```text
add_auth_users_table
add_store_products_table
add_commission_rules_table
add_notify_events_table
```

## هر PR دیتابیس باید شامل باشد:

```text
migration file
مدل SQLAlchemy
schemaهای لازم
توضیح تغییر در docs/database اگر لازم است
```

---

# 12. Documentation Workflow

مستندات بخشی از کار است، نه کار اضافه.

اگر کدی تغییر کند ولی مستندات لازم آپدیت نشود، PR ناقص است.

## docs اصلی

```text
docs/00-product-vision.md
docs/01-mvp-scope.md
docs/02-architecture.md
docs/03-module-roadmap.md
docs/04-team-workflow.md
docs/05-definition-of-done.md
docs/06-risk-control.md
```

## docs فنی

```text
docs/api/
docs/database/
docs/notifications/
docs/payments/
docs/deployment/
docs/backup-restore/
```

## قانون

```text
هر تغییر API → docs/api آپدیت شود.
هر تغییر دیتابیس مهم → docs/database آپدیت شود.
هر notification event جدید → docs/notifications آپدیت شود.
هر تغییر پرداخت → docs/payments آپدیت شود.
```

---

# 13. Testing Workflow

هیچ فاز بدون تست تمام‌شده نیست.

## Backend

حداقل تست‌های لازم:

```text
unit test برای serviceها
integration test برای APIها
permission test
auth test
payment verify test
commission calculation test
notification event test
file upload validation test
```

## Flutter

حداقل تست‌های لازم:

```text
widget test برای ویجت‌های مهم
provider/state test
localization test
API error mapping test
responsive sanity test
```

## Manual Test

برای هر ماژول باید Postman یا Swagger تست شود.

مسیر:

```text
postman/
  auth.postman_collection.json
  geo.postman_collection.json
  notification.postman_collection.json
  store.postman_collection.json
```

---

# 14. Release Workflow

هر فاز مهم باید نسخه داشته باشد.

## نسخه‌ها

```text
v0.1.0-foundation
v0.2.0-auth-core
v0.3.0-geo-core
v0.4.0-notification-core
v0.5.0-media-documents
v0.6.0-verification-contracts
v0.7.0-admin-core
v0.8.0-billing-finance
v0.9.0-store-core
v1.0.0-mvp-release
```

## مراحل Release

```text
1. featureها به develop merge شوند.
2. release branch ساخته شود.
3. تست کامل انجام شود.
4. migration روی staging تست شود.
5. Flutter build تست شود.
6. Admin build تست شود.
7. backup قبل از deploy گرفته شود.
8. merge به main انجام شود.
9. tag زده شود.
10. release notes نوشته شود.
```

---

# 15. Daily Workflow

هر روز تیم‌ها باید وضعیت را کوتاه گزارش کنند.

فرمت گزارش روزانه:

```text
دیروز:
- ...

امروز:
- ...

مانع:
- ...
```

قانون:

```text
اگر مانعی وجود دارد، همان روز اعلام شود.
هیچ‌کس نباید چند روز روی مشکل گیر کند و چیزی نگوید.
```

---

# 16. Weekly Review

هر هفته باید review فنی انجام شود.

موارد بررسی:

```text
پیشرفت فاز
PRهای merge شده
PRهای معطل
باگ‌های مهم
تغییرات API
تغییرات دیتابیس
ریسک‌ها
مستندات
تست‌ها
برنامه هفته بعد
```

خروجی جلسه هفتگی باید در docs یا issue tracker ثبت شود.

---

# 17. Phase Handoff

وقتی یک فاز تمام می‌شود، باید تحویل رسمی داشته باشد.

## چک‌لیست تحویل فاز

```text
کد merge شده؟
تست‌ها پاس شده؟
migration اجرا شده؟
Swagger/Postman تست شده؟
Flutter UI اگر دارد تست شده؟
Admin UI اگر دارد تست شده؟
docs آپدیت شده؟
release note نوشته شده؟
tag زده شده؟
backup گرفته شده؟
demo انجام شده؟
```

بدون این‌ها فاز تمام‌شده نیست.

---

# 18. Issue Tracking

هر کار باید issue داشته باشد.

## نوع issueها

```text
Feature
Bug
Task
Documentation
Refactor
Test
DevOps
Research
```

## هر issue باید داشته باشد:

```text
عنوان واضح
ماژول مرتبط
توضیح
Acceptance Criteria
اولویت
مسئول
وضعیت
```

## وضعیت‌ها

```text
Backlog
Ready
In Progress
In Review
Testing
Done
Blocked
```

---

# 19. Acceptance Criteria

هر task باید معیار پذیرش داشته باشد.

مثال بد:

```text
پیاده‌سازی فروشگاه
```

مثال خوب:

```text
کاربر تأییدشده بتواند فروشگاه خود را ثبت کند.
هر کاربر فقط یک فروشگاه داشته باشد.
فروشگاه بدون تأیید ادمین فعال نشود.
ادمین بتواند فروشگاه را تأیید/رد کند.
نوتیفیکیشن وضعیت برای کاربر ارسال شود.
Audit log تصمیم ادمین ثبت شود.
```

---

# 20. Communication Rules

برای جلوگیری از گم‌شدن پروژه:

```text
تصمیم‌های مهم فقط شفاهی نباشند.
هر تصمیم مهم باید در docs یا issue ثبت شود.
تغییر scope باید تأیید شود.
تغییر API باید به همه تیم‌ها اعلام شود.
تغییر دیتابیس باید با migration و توضیح باشد.
```

## تصمیم‌های مهم شامل:

```text
تغییر فازها
تغییر دیتابیس
تغییر API
تغییر مدل پرداخت
تغییر role/permission
تغییر notification events
تغییر UI pattern
```

---

# 21. Environment Rules

محیط‌ها:

```text
local
development
staging
production
```

## قوانین

```text
Production برای تست استفاده نمی‌شود.
Migration اول local، بعد staging، بعد production اجرا می‌شود.
.env هر محیط جداست.
Secrets داخل Git ممنوع است.
```

## فایل‌ها

```text
.env.example
.env.local
.env.development
.env.staging
.env.production
```

فقط `.env.example` وارد Git می‌شود.

---

# 22. Backup Rules

برای جلوگیری از فاجعه قبلی، backup اجباری است.

## موارد بکاپ

```text
Git remote repository
MySQL database
Uploaded files/storage
.env files به صورت امن
SSL certificates
Postman collections
Docs
```

## قانون

```text
بکاپ باید زمان‌بندی داشته باشد.
بکاپ باید خارج از سرور اصلی هم ذخیره شود.
Restore باید تست شود.
```

## زمان‌های ضروری بکاپ

```text
قبل از migration مهم
قبل از deploy
قبل از تغییر payment
قبل از تغییر auth
قبل از تغییر storage
```

---

# 23. Security Workflow

هر PR باید امنیت را در نظر بگیرد.

## چک‌های امنیتی

```text
آیا endpoint permission دارد؟
آیا ورودی‌ها validate می‌شوند؟
آیا فایل‌ها امن upload می‌شوند؟
آیا اطلاعات حساس در log نیست؟
آیا rate limit لازم است؟
آیا اطلاعات کاربر دیگر قابل دسترسی نیست؟
آیا role escalation ممکن نیست؟
```

---

# 24. UI Workflow

برای Flutter و Admin UI:

```text
هر صفحه باید با finalui باشد.
هر صفحه باید responsive باشد.
هر صفحه باید dark/light را پشتیبانی کند.
هر صفحه باید fa/en را پشتیبانی کند.
هر صفحه فارسی باید RTL باشد.
اعداد در فارسی باید فارسی باشند.
تاریخ در فارسی باید شمسی باشد.
پول باید تومان نمایش داده شود.
```

## ممنوعیت‌ها

```text
استفاده از r.dp ممنوع است.
CustomGlassBox ممنوع است.
باید از CrystalGlass استفاده شود.
آیکن برگشت باید Icons.arrow_back باشد.
برگشت باید Navigator.pop(context) باشد.
```

---

# 25. API Change Announcement

اگر API تغییر کند، مسئول Backend باید این‌ها را به تیم Flutter اعلام کند:

```text
Endpoint تغییر کرده
Request تغییر کرده
Response تغییر کرده
Error code جدید اضافه شده
Permission جدید اضافه شده
Status جدید اضافه شده
Notification event جدید اضافه شده
```

تغییر API بدون اطلاع تیم Flutter ممنوع است.

---

# 26. Blocker Rules

اگر کاری block شد:

```text
مسئول باید همان روز اعلام کند.
علت blocker باید ثبت شود.
اگر بیشتر از یک روز طول کشید، Lead باید تصمیم بگیرد.
```

نمونه blocker:

```text
API آماده نیست
Migration خطا دارد
طراحی UI نامشخص است
دسترسی سرور نیست
درگاه پرداخت sandbox مشکل دارد
```

---

# 27. Code Ownership

هر بخش باید owner داشته باشد.

نمونه:

```text
backend/app/core → Backend Lead
backend/app/modules/auth → Backend Auth Owner
backend/app/modules/store → Backend Store Owner
mobile/lib/core → Flutter Lead
mobile/lib/features/store → Flutter Store Owner
admin-panel/lib/features/users → Admin Owner
infra/docker → DevOps Owner
docs/api → API Owner
```

قانون:

```text
تغییر در کد یک ماژول بدون review مالک آن ماژول ممنوع است.
```

---

# 28. Merge Freeze

قبل از release، merge freeze داریم.

یعنی:

```text
فقط bug fixهای ضروری merge می‌شوند.
feature جدید وارد release نمی‌شود.
docs و تست‌ها نهایی می‌شوند.
```

---

# 29. Hotfix Workflow

اگر production مشکل مهم داشت:

```text
1. از main یک hotfix branch ساخته شود.
2. فقط همان مشکل fix شود.
3. تست سریع انجام شود.
4. merge به main شود.
5. tag جدید زده شود.
6. همان تغییر به develop هم merge شود.
```

مثال:

```text
hotfix/payment-verify-error
```

---

# 30. قوانین جلوگیری از گم شدن پروژه

این قوانین غیرقابل مذاکره هستند:

```text
1. هیچ کاری بدون issue شروع نمی‌شود.
2. هیچ feature بدون branch جدا شروع نمی‌شود.
3. هیچ PR بدون review merge نمی‌شود.
4. هیچ تغییر دیتابیس بدون migration انجام نمی‌شود.
5. هیچ API بدون contract به Flutter داده نمی‌شود.
6. هیچ فازی بدون تست و docs تمام نمی‌شود.
7. هیچ deploy بدون backup انجام نمی‌شود.
8. هیچ secret داخل Git قرار نمی‌گیرد.
9. هیچ تصمیم مهمی فقط شفاهی باقی نمی‌ماند.
10. هیچ تیمی بدون اطلاع تیم‌های دیگر API یا schema را عوض نمی‌کند.
```

---

# 31. نتیجه

این workflow برای این طراحی شده که پروژه «فارم نت» با چند تیم، قابل کنترل، قابل توسعه و قابل تحویل باشد.

اگر این قوانین رعایت نشوند، حتی بهترین معماری هم پروژه را نجات نمی‌دهد.

قانون نهایی:

```text
هر چیزی که مستند، تست‌شده، review‌شده و version شده نباشد، در پروژه رسمی حساب نمی‌شود.
```
