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
11. Notification Event Core
12. Media Upload
13. Documents
14. Verification
15. Contracts
16. Billing / Subscription Core
17. Commission Core
18. Payment Gateway Core
19. Finance / Invoice Core
20. Store Core
21. Store Members
22. Product Categories
23. Product Management
24. Product Approval
25. Shop Panel Core
26. Public Store UI
27. Promotion / Ladder Core ساده
28. Admin Management Core
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

ماژول کامل Services / Rental بعد از Store Core می‌آید.

---

### 4.4 مشاوران

در MVP v1 ماژول کامل مشاوران ساخته نمی‌شود.

اما طراحی سیستم باید از اول این نیاز را ببیند:

```text
مشاوران براساس رشته و تخصص کشاورزی فعالیت می‌کنند.
تخصص‌ها باید از پنل ادمین قابل مدیریت باشند.
فعال شدن مشاور نیازمند مدارک، قرارداد و تأیید ادمین است.
```

ماژول کامل Consultants بعد از Services / Rental می‌آید.

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

### Phase 7 - Notification Core

خروجی‌ها:

```text
notify_events
notify_notifications
notify_templates
notify_channels
notify_user_preferences
notify_delivery_attempts
notify_device_tokens
In-App notification
Push base structure
SMS provider integration
Email provider integration
Queue worker
```

---

### Phase 8 - Media / Documents

خروجی‌ها:

```text
upload image
upload document
file validation
file metadata
public/private file
profile image
document upload
link file to module
```

---

### Phase 9 - Verification / Contracts

خروجی‌ها:

```text
verification requests
document review
contract templates
contract versions
contract acceptance
PDF contract upload
admin approval
status flow
notifications
audit logs
```

---

### Phase 10 - Billing / Subscription

خروجی‌ها:

```text
plans
plan features
subscriptions
feature usage
subscription limits
admin plan management
manual/online subscription payment base
notifications for expiration
```

---

### Phase 11 - Commission / Finance / Payment Core

خروجی‌ها:

```text
commission rules
commission snapshot
invoice
invoice items
payment gateway
payment attempt
payment callback
payment verify
transaction
platform amount
provider amount
notification
audit log
```

---

### Phase 12 - Store Core

خروجی‌ها:

```text
create shop request
shop documents
shop contract
admin approval
store_shops
store_shop_members
shop roles
product categories
products
product images
product features
product benefits
product status flow
admin product approval
notifications
```

---

### Phase 13 - Shop Panel UI

خروجی‌ها:

```text
shop dashboard
shop profile
shop members
create/edit product
upload product images
product status
invoice list
promotion requests
notifications
```

---

### Phase 14 - Public Store UI

خروجی‌ها:

```text
home store section
product list
product detail
category filter
location filter
price display
shop public profile
```

---

### Phase 15 - Admin Store Management

خروجی‌ها:

```text
shop requests
shop approval
shop suspension
product approval
category management
shop members view
commission view
invoice view
promotion management
```

---

### Phase 16 - Promotion / Ladder Core

خروجی‌ها:

```text
promotion packages
promotion slots
promotion target
duration
payment
activation
priority display
notification
```

---

## 6. معیار اتمام MVP v1

MVP v1 زمانی تمام‌شده حساب می‌شود که:

```text
1. Backend با Docker اجرا شود.
2. MySQL migrationها بدون خطا اجرا شوند.
3. Flutter App اجرا شود.
4. Flutter Web Admin اجرا شود.
5. کاربر بتواند ثبت‌نام و ورود کند.
6. نقش و دسترسی قابل مدیریت باشد.
7. کاربر پروفایل رایگان داشته باشد.
8. Geo Core قابل استفاده باشد.
9. نوتیفیکیشن داخلی کار کند.
10. SMS برای OTP کار کند.
11. Email برای قرارداد/فاکتور آماده باشد.
12. فایل و مدرک قابل آپلود باشد.
13. قرارداد قابل پذیرش و آپلود باشد.
14. ادمین بتواند مدارک را تأیید/رد کند.
15. ادمین بتواند کمیسیون را تنظیم کند.
16. فاکتور صادر شود.
17. پرداخت آنلاین Core کار کند.
18. کمیسیون در فاکتور snapshot شود.
19. کاربر بتواند فروشگاه ثبت کند.
20. ادمین بتواند فروشگاه را تأیید/رد کند.
21. فروشگاه بتواند محصول ثبت کند.
22. محصول توسط ادمین تأیید/رد شود.
23. محصولات در UI عمومی دیده شوند.
24. پنل فروشگاه پایه کار کند.
25. تبلیغ/نردبان ساده قابل تعریف باشد.
26. APIها مستند باشند.
27. Postman/Swagger تست شده باشد.
28. Git tag برای MVP زده شود.
```

---

## 7. ریسک‌های MVP

### ریسک 1: MVP بیش از حد سنگین شود

راه کنترل:

```text
پرداخت آنلاین فقط Core باشد.
نوتیفیکیشن همه کانال‌ها را داشته باشد، اما ارسال‌ها ساده و کنترل‌شده باشد.
Social، AI، Services، Consultants و Weather کامل وارد MVP نشوند.
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
1. Services / Rental Core
2. Consultants Core
3. Weather Core
4. AI / RAG Core
5. Social Core
6. Data Access / BI
7. Advanced Payment / Settlement
8. Reports / Analytics
```
