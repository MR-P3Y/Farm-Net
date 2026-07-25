# 01 - MVP Scope
# محدوده نسخه اول فارم نت

## 1. هدف MVP

MVP نسخه اول «فارم نت» باید یک نسخه قابل اجرا، قابل تست، قابل توسعه و قابل ارائه از ستون فقرات پلتفرم باشد.

هدف MVP این نیست که کل سوپراپ کامل شود.
هدف MVP این است که پایه‌های اصلی سیستم درست، پایدار و قابل توسعه ساخته شوند.

MVP باید ثابت کند که سیستم می‌تواند:

```text
کاربر ثبت کند
نقش و دسترسی مدیریت کند
پروفایل رایگان بسازد
جغرافیا و آدرس را مدیریت کند
نوتیفیکیشن تولید و ارسال کند
فایل و مدرک بگیرد
قرارداد را ثبت کند
درخواست فعالیت حرفه‌ای را بررسی کند
پنل ادمین داشته باشد
اشتراک و کمیسیون را مدیریت کند
پرداخت آنلاین پایه داشته باشد
فروشگاه ثبت کند
محصول ثبت کند
فاکتور صادر کند
کمیسیون محاسبه کند
پنل فروشگاه داشته باشد
```

---

## 2. MVP v1 شامل چه چیزهایی هست؟

MVP v1 شامل بخش‌های زیر است:

```text
1. Project Governance
2. Repository Structure
3. Documentation Foundation
4. Backend Foundation
5. Flutter Foundation
6. Flutter Web Admin Foundation
7. Auth
8. Users / Roles / Permissions
9. Free User Profile
10. Geo Core
11. Store Foundation
12. Product / Catalog Foundation
13. Cart / Orders / Payments / Commission Foundation
14. Media / File Upload / Storage Foundation
15. Notifications Foundation
16. Admin Management Core
```

---

## 3. MVP v1 شامل چه چیزهایی نیست؟

موارد زیر عمداً در MVP v1 کامل پیاده‌سازی نمی‌شوند:

```text
1. AI / RAG کامل
2. Social کامل
3. Services کامل
4. Rental کامل
5. Consultants کامل
6. Weather کامل
7. Data Access کامل
8. Wallet کامل
9. Settlement کامل
10. Reports سنگین
11. Chat
12. Live
13. Video
14. Advanced Recommendation
15. Advanced Reservation
16. Advanced Logistics
17. Return / Refund System پیشرفته
```

این موارد در roadmap بعد از MVP اضافه می‌شوند.

---

## 4. تصمیم‌های قطعی MVP

### 4.1 احراز هویت

MVP باید از دو روش پشتیبانی کند:

```text
1. شماره موبایل + OTP
2. ایمیل + رمز عبور
```

روش اصلی پیشنهادی:

```text
شماره موبایل + OTP
```

روش مکمل:

```text
ایمیل + رمز عبور
```

---

### 4.2 فروشگاه

قوانین فروشگاه در MVP:

```text
هر کاربر فقط می‌تواند یک فروشگاه داشته باشد.
فروشگاه می‌تواند چند مدیر یا کارمند داشته باشد.
فعال شدن فروشگاه نیازمند مدارک، قرارداد و تأیید ادمین است.
فروشگاه می‌تواند محصول ثبت کند.
محصول باید توسط ادمین تأیید شود.
```

نقش‌های داخلی فروشگاه:

```text
owner
manager
staff
viewer
```

---

### 4.3 موجر و خدمات

در MVP v1 ماژول کامل موجر و خدمات ساخته نمی‌شود.

اما طراحی سیستم باید از اول این نیاز را ببیند:

```text
موجر یعنی کاربری که ادوات کشاورزی خود را با راننده یا بدون راننده کرایه می‌دهد.
خدمات شامل همه خدمات مرتبط با کشاورزی است.
دسته‌بندی خدمات باید از پنل ادمین قابل مدیریت باشد.
```

ماژول کامل Services بعد از Social / Community Foundation می‌آید.
Equipment / Rental در فاز جداگانه بعد از Consultants اجرا می‌شود.

---

### 4.4 مشاوران

در MVP v1 ماژول کامل مشاوران ساخته نمی‌شود.

اما طراحی سیستم باید از اول این نیاز را ببیند:

```text
مشاوران براساس رشته و تخصص کشاورزی فعالیت می‌کنند.
تخصص‌ها باید از پنل ادمین قابل مدیریت باشند.
فعال شدن مشاور نیازمند مدارک، قرارداد و تأیید ادمین است.
```

ماژول کامل Consultants بعد از Services Module و قبل از Equipment / Rental می‌آید.

---

### 4.5 قراردادها

MVP باید از هر دو حالت پشتیبانی کند:

```text
1. تیک پذیرش قرارداد
2. آپلود فایل PDF قرارداد امضاشده
```

هر قرارداد باید version داشته باشد.

---

### 4.6 پرداخت

پرداخت آنلاین از MVP وجود دارد.

اما فقط در حد Core:

```text
ساخت فاکتور
محاسبه کمیسیون
ارسال به درگاه
callback پرداخت
verify پرداخت
ثبت تراکنش
تغییر وضعیت فاکتور
نوتیفیکیشن پرداخت
```

در MVP این موارد کامل نمی‌شوند:

```text
Wallet کامل
Settlement کامل
Refund پیشرفته
چند درگاه همزمان
سیستم حسابداری کامل
```

---

### 4.7 نوتیفیکیشن

MVP باید ساختار همه کانال‌ها را داشته باشد:

```text
In-App
Push
SMS
Email
```

حداقل فعال در MVP:

```text
In-App Notification
SMS برای OTP و موارد مهم
Email برای قرارداد و فاکتور
Push پایه، در صورت آماده بودن FCM
```

---

### 4.8 پنل ادمین

پنل ادمین با Flutter Web ساخته می‌شود.

MVP Admin باید این موارد را مدیریت کند:

```text
کاربران
نقش‌ها
دسترسی‌ها
مدارک
قراردادها
فروشگاه‌ها
اعضای فروشگاه
محصولات
دسته‌بندی محصولات
دسته‌بندی خدمات
تخصص مشاوران
کمیسیون‌ها
فاکتورها
پرداخت‌ها
تبلیغات
نوتیفیکیشن‌ها
تنظیمات
Audit Logs
```

---

## 5. فازهای اجرایی MVP

### Phase 1 - Repository + Documentation Foundation

خروجی‌ها:

```text
ساخت monorepo
ساخت docs
README
.gitignore
.env.example
branch strategy
ساختار backend/mobile/admin/infra/scripts
```

---

### Phase 2 - Backend Foundation

خروجی‌ها:

```text
FastAPI skeleton
MySQL connection
SQLAlchemy setup
Alembic setup
Redis setup
config/env
standard response
standard error
logging
trace_id
pagination
CORS
rate limit پایه
health check
Swagger/OpenAPI
Dockerfile
```

---

### Phase 3 - Flutter Foundation

خروجی‌ها:

```text
Flutter structure
finalui
LSM responsive
theme light/dark
localization fa/en
RTL/LTR
Persian digit helper
Jalali date helper
Toman formatter
routing
network client
token storage
base widgets
```

---

### Phase 4 - Admin Panel Foundation

خروجی‌ها:

```text
Flutter Web admin structure
admin login
admin routing
admin layout
sidebar
permission guard
table/list component
form component
status chip
audit view base
```

---

### Phase 5 - Auth / Users / Roles / Permissions

خروجی‌ها:

```text
mobile OTP login/register
email + password login/register
refresh token
sessions
users
roles
permissions
user_roles
admin role management
```

---

### Phase 6 - Geo Core

خروجی‌ها:

```text
provinces
counties
districts
cities
rural districts
villages
addresses
manual address
map coordinates
seed data structure
```

---

### Phase 7 - Store Foundation

خروجی‌ها:

```text
store database models
store owner/member structure
store status lifecycle
seller store APIs
store member management APIs
admin store review APIs
public approved store lookup APIs
mobile store foundation
admin panel store foundation
```

---

### Phase 8 - Product / Catalog Foundation

خروجی‌ها:

```text
product category seed
seller product APIs
product image metadata APIs
admin product moderation APIs
public product lookup APIs
mobile product foundation
admin panel product foundation
```

---

### Phase 9 - Cart / Orders / Payments / Commission

خروجی‌ها:

```text
cart
checkout base
orders
order items
payment attempts
payment verify/callback
commission snapshot
seller/admin order views
```

---

### Phase 10 - Media / File Upload / Storage

خروجی‌ها:

```text
file upload
image upload
document upload
file validation
file metadata
public/private storage policy
module file linking
safe file serving base
```

---

### Phase 11 - Notifications Foundation

خروجی‌ها:

```text
notification events
notification templates
in-app notification foundation
push notification base
SMS provider base
email provider base
delivery attempts
user notification preferences
queue worker foundation
```

---

Post-MVP roadmap continues in docs/03-module-roadmap.md.

---

## 6. معیار اتمام MVP v1

MVP v1 زمانی تمام‌شده حساب می‌شود که:

```text
1. Backend با Docker اجرا شود.
2. MySQL migrationها بدون خطا اجرا شوند.
3. Flutter App اجرا شود.
4. Flutter Web Admin اجرا شود.
5. Auth کامل پایه داشته باشد.
6. Role/Permission پایه کار کند.
7. Geo داده پایه داشته باشد.
8. Store Foundation کامل باشد.
9. Product / Catalog Foundation کامل باشد.
10. Cart/Orders/Payments/Commission foundation کامل باشد.
11. Media/File Upload foundation کامل باشد.
12. Notifications foundation کامل باشد.
13. API docs و Postman هر فاز ثبت شده باشد.
14. Mobile و Admin build شوند.
15. Git tag برای MVP زده شود.
```

---

## 7. ریسک‌های MVP

### ریسک 1: MVP بیش از حد سنگین شود

راه کنترل:

```text
Weather، Social، AI، Services، Consultants و Equipment/Rental کامل وارد MVP نشوند.
برای هرکدام فقط جایگاه roadmap و dependencyها مشخص شود.
```

---

### ریسک 2: پنل ادمین بزرگ و کند شود

راه کنترل:

```text
Admin Panel ابتدا روی مدیریت‌های ضروری تمرکز کند.
داشبوردهای آماری پیشرفته بعداً اضافه شوند.
```

---

### ریسک 3: تیم‌ها ناهماهنگ شوند

راه کنترل:

```text
API Contract
Git Workflow
Definition of Done
Weekly Review
Documentation
Code Review
```

---

### ریسک 4: پرداخت و کمیسیون اشتباه محاسبه شود

راه کنترل:

```text
Commission Snapshot
Payment Verify
Transaction Logs
Audit Logs
Finance Tests
```

---

### ریسک 5: نوتیفیکیشن باعث هزینه زیاد شود

راه کنترل:

```text
SMS فقط برای موارد مهم
Push و In-App برای بیشتر رویدادها
Email برای موارد رسمی
قابلیت تنظیم channel policy در پنل ادمین
```

---

## 8. نتیجه MVP

MVP v1 باید یک نسخه قابل اجرا از ستون فقرات پلتفرم باشد.

بعد از MVP v1، مسیر توسعه به این ترتیب ادامه پیدا می‌کند:

```text
1. Weather Foundation
2. Social / Community Foundation
3. Services Module
4. Consultants Module
5. Equipment / Rental
6. Category Management
7. Search / Filters / Discovery
8. Reviews / Ratings / Reports
9. Wallet / Settlement / Accounting
10. AI / RAG Assistant Integration
11. Production Hardening / Deployment
12. Farm Management / Digital Farm Profiles
```
