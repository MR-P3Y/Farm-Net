# 12 — Deployment and Backup
# استقرار، بکاپ و بازیابی پروژه فارم نت

## 1. هدف سند

این سند قوانین استقرار، بکاپ، ریستور و نگهداری پروژه «فارم نت» را مشخص می‌کند.

هدف اصلی این سند جلوگیری از اتفاقاتی مثل موارد زیر است:

```text
پاک شدن پروژه
نبود بکاپ سالم
خراب شدن دیتابیس بعد از migration
deploy نسخه خراب
گم شدن .env
از دست رفتن فایل‌های آپلودی
مشکل SSL
نداشتن rollback
ناهماهنگی محیط local/staging/production
```

قانون اصلی:

```text
هیچ deploy بدون backup، هیچ migration بدون تست، هیچ production بدون rollback plan.
```

---

# 2. محیط‌های پروژه

پروژه باید حداقل این محیط‌ها را داشته باشد:

```text
local
development
staging
production
```

## local

برای توسعه روی سیستم برنامه‌نویس‌ها.

ویژگی‌ها:

```text
دیتابیس local
Redis local
.env.local
داده تستی
بدون اتصال به سرویس‌های واقعی پرداخت/SMS مگر sandbox
```

---

## development

محیط مشترک تیمی برای تست اولیه.

ویژگی‌ها:

```text
روی سرور یا VM داخلی
داده تستی
برای تست ادغام Backend و Flutter
ممکن است ناپایدار باشد
```

---

## staging

محیط شبه-production.

ویژگی‌ها:

```text
نزدیک‌ترین حالت به production
برای تست release قبل از انتشار
migration ابتدا اینجا تست می‌شود
درگاه پرداخت sandbox
SMS محدود یا fake provider
Email تستی
Push تستی
```

---

## production

محیط واقعی کاربران.

قوانین:

```text
فقط نسخه tag شده deploy می‌شود
تست مستقیم روی production ممنوع است
migration بدون backup ممنوع است
.env واقعی فقط روی سرور امن باشد
```

---

# 3. معماری Deploy در MVP

برای MVP از Docker Compose استفاده می‌کنیم.

سرویس‌های اصلی:

```text
backend
worker
mysql
redis
nginx
admin-panel
storage
```

## توضیح سرویس‌ها

```text
backend:
FastAPI app

worker:
پردازش نوتیفیکیشن، ایمیل، SMS، jobهای سبک

mysql:
دیتابیس اصلی

redis:
cache، queue، rate limit

nginx:
reverse proxy، SSL termination، static/media serving در صورت نیاز

admin-panel:
Flutter Web build

storage:
فایل‌های آپلودی مثل عکس‌ها و مدارک
```

---

# 4. ساختار infra

ساختار پیشنهادی:

```text
infra/
  docker-compose.yml
  docker-compose.staging.yml
  docker-compose.production.yml

  nginx/
    nginx.conf
    sites/
      api.conf
      admin.conf
      media.conf

  mysql/
    init/
    backups/

  redis/

  ssl/
    README.md
```

قانون:

```text
فایل‌های SSL واقعی وارد Git نشوند.
فقط README و نمونه config داخل Git باشد.
```

---

# 5. Docker Compose پیشنهادی MVP

ساختار کلی:

```yaml
services:
  backend:
    build: ../backend
    env_file:
      - ../.env.production
    depends_on:
      - mysql
      - redis
    volumes:
      - ../storage:/app/storage
    restart: unless-stopped

  worker:
    build: ../backend
    command: ["python", "-m", "app.worker"]
    env_file:
      - ../.env.production
    depends_on:
      - mysql
      - redis
    volumes:
      - ../storage:/app/storage
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    env_file:
      - ../.env.production
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

  redis:
    image: redis:7
    restart: unless-stopped

  nginx:
    image: nginx:stable
    volumes:
      - ./nginx:/etc/nginx/conf.d
      - ../storage:/var/www/storage
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  mysql_data:
```

این فقط نمونه مفهومی است. فایل نهایی در زمان ساخت infra دقیق می‌شود.

---

# 6. فایل‌های env

فقط `.env.example` وارد Git می‌شود.

فایل‌های واقعی ممنوع در Git:

```text
.env
.env.local
.env.development
.env.staging
.env.production
```

## .env.example باید شامل کلیدها باشد، نه مقدار واقعی

مثال:

```env
APP_ENV=development
APP_DEBUG=false

DATABASE_URL=mysql+pymysql://user:password@mysql:3306/farmnet
REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=change-me
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

SMS_PROVIDER=
SMS_API_KEY=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_USER=
EMAIL_PASSWORD=

PAYMENT_GATEWAY=
PAYMENT_MERCHANT_ID=

FCM_SERVER_KEY=

STORAGE_PATH=/app/storage
PUBLIC_BASE_URL=https://api.example.com
```

---

# 7. مدیریت Secrets

Secrets شامل موارد زیر است:

```text
JWT secret
Database password
SMS API key
Email password
Payment merchant id/secret
FCM key
SSL private key
Admin bootstrap password
```

قوانین:

```text
Secrets داخل Git ممنوع است.
Secrets داخل پیام‌های عمومی تیم ممنوع است.
Secrets باید در password manager یا محل امن ذخیره شوند.
در logها نباید چاپ شوند.
اگر secret لو رفت، باید rotate شود.
```

---

# 8. Storage Strategy

در MVP فایل‌ها روی سرور ذخیره می‌شوند.

مسیر پیشنهادی:

```text
storage/
  media/
    public/
    private/
  documents/
    private/
  contracts/
    private/
  temp/
```

## قوانین

```text
عکس عمومی محصول می‌تواند public باشد.
مدارک و قراردادها باید private باشند.
فایل private باید با permission کنترل شود.
فایل‌های storage وارد Git نمی‌شوند.
storage باید جداگانه backup شود.
```

در آینده می‌توان storage را به MinIO/S3 منتقل کرد.

---

# 9. Nginx

Nginx وظایف زیر را دارد:

```text
reverse proxy برای backend
serving admin-panel build
serving فایل‌های public
SSL termination
redirect HTTP به HTTPS
rate limit اولیه در صورت نیاز
```

## مسیرهای پیشنهادی

```text
api.farmnet.com       → backend
admin.farmnet.com     → admin-panel
media.farmnet.com     → public media
```

یا در شروع:

```text
domain.com/api
domain.com/admin
domain.com/media
```

---

# 10. SSL

برای production باید HTTPS اجباری باشد.

گزینه‌ها:

```text
Let's Encrypt
Cloudflare SSL
SSL دستی
```

قوانین:

```text
private key وارد Git نشود.
تاریخ انقضای SSL مانیتور شود.
قبل از انقضا تمدید شود.
HTTP به HTTPS redirect شود.
```

---

# 11. Migration در Deploy

قانون مهم:

```text
Migration مستقیم روی production بدون backup ممنوع است.
```

جریان صحیح:

```text
1. migration در local تست شود.
2. migration روی staging اجرا شود.
3. تست smoke روی staging انجام شود.
4. قبل از production backup گرفته شود.
5. migration روی production اجرا شود.
6. health check و smoke test انجام شود.
```

---

# 12. Backup Strategy

بکاپ باید شامل این موارد باشد:

```text
1. Source Code
2. MySQL Database
3. Uploaded Files / Storage
4. .env files
5. SSL certificates
6. Postman collections
7. Docs
```

## 12.1 Source Code Backup

منبع اصلی:

```text
Git remote private repository
```

قانون:

```text
هر فاز باید tag داشته باشد.
main باید همیشه نسخه پایدار باشد.
```

---

## 12.2 MySQL Backup

بکاپ دیتابیس باید زمان‌بندی شود.

نمونه دستور:

```bash
mysqldump -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" > backups/db_$(date +%F_%H-%M).sql
```

نسخه فشرده:

```bash
mysqldump -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" | gzip > backups/db_$(date +%F_%H-%M).sql.gz
```

## زمان‌بندی پیشنهادی

```text
روزانه: بکاپ کامل
قبل از هر deploy: بکاپ فوری
قبل از هر migration: بکاپ فوری
قبل از تغییر payment/auth/storage: بکاپ فوری
```

---

## 12.3 Storage Backup

بکاپ فایل‌ها:

```bash
tar -czf backups/storage_$(date +%F_%H-%M).tar.gz storage/
```

قانون:

```text
storage backup باید با database backup هماهنگ باشد.
```

چرا؟
چون دیتابیس ممکن است به فایل‌هایی اشاره کند که اگر storage backup قدیمی باشد، وجود ندارند.

---

## 12.4 Env Backup

`.env.production` باید به صورت امن و رمزدار backup شود.

قانون:

```text
.env backup عمومی یا داخل Git ممنوع است.
فقط افراد محدود به آن دسترسی داشته باشند.
```

---

## 12.5 Offsite Backup

بکاپ نباید فقط روی همان سرور باشد.

گزینه‌ها:

```text
سرور دیگر
S3/MinIO
Google Drive/Dropbox سازمانی
Telegram private channel برای نسخه رمزدار
NAS
```

قانون:

```text
اگر سرور اصلی پاک شد، بکاپ باید جای دیگری موجود باشد.
```

---

# 13. Retention Policy

پیشنهاد نگهداری بکاپ:

```text
Daily backups: 7 days
Weekly backups: 4 weeks
Monthly backups: 6 months
Before-deploy backups: حداقل 5 نسخه آخر
```

برای فایل‌های حجیم، می‌توان retention جدا تعیین کرد.

---

# 14. Restore Strategy

قانون بسیار مهم:

```text
بکاپی که restore آن تست نشده باشد، بکاپ واقعی نیست.
```

## Restore Test

حداقل ماهی یک بار باید روی staging تست شود:

```text
restore database
restore storage
run backend
run admin
run smoke tests
```

## مراحل Restore دیتابیس

```bash
gunzip db_backup.sql.gz
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" < db_backup.sql
```

## مراحل Restore Storage

```bash
tar -xzf storage_backup.tar.gz -C /path/to/project/
```

بعد از restore:

```text
health check
login test
media file test
invoice test
admin login test
```

---

# 15. Rollback Strategy

اگر deploy خراب شد:

```text
1. feature جدید متوقف شود.
2. آخرین tag سالم پیدا شود.
3. image قبلی اجرا شود.
4. اگر migration destructive نیست، rollback app کافی است.
5. اگر migration دیتابیس خراب کرده، restore backup بررسی شود.
6. incident ثبت شود.
```

قانون:

```text
Migration destructive بدون برنامه rollback ممنوع است.
```

---

# 16. Release Process

جریان release:

```text
1. featureها به develop merge شوند.
2. release branch ساخته شود.
3. تست کامل روی release branch انجام شود.
4. build backend و Flutter و admin انجام شود.
5. migration روی staging اجرا شود.
6. smoke test staging انجام شود.
7. backup production گرفته شود.
8. deploy production انجام شود.
9. migration production اجرا شود.
10. health check انجام شود.
11. smoke test production انجام شود.
12. tag زده شود.
13. release notes نوشته شود.
```

---

# 17. Health Check

Backend باید endpoint سلامت داشته باشد:

```text
GET /health
GET /api/v1/health
```

خروجی باید وضعیت‌ها را نشان دهد:

```json
{
  "success": true,
  "data": {
    "app": "ok",
    "database": "ok",
    "redis": "ok"
  },
  "message": "OK",
  "meta": {
    "trace_id": "..."
  }
}
```

---

# 18. Smoke Tests بعد از Deploy

بعد از هر deploy باید این موارد تست شوند:

```text
Backend health
Admin login
User login
OTP test در محیط مجاز
Database connection
Redis connection
Media public access
Private document permission
Invoice creation
Payment sandbox test
Notification in-app test
```

---

# 19. Monitoring و Logs

در MVP حداقل باید logهای زیر داشته باشیم:

```text
backend app logs
worker logs
nginx access/error logs
mysql logs
payment logs
notification delivery logs
admin audit logs
```

قانون:

```text
اطلاعات حساس در logها نباید ذخیره شود.
```

موارد ممنوع در log:

```text
password
OTP
JWT کامل
refresh token
payment secret
SMS API key
private document content
```

---

# 20. Worker Deployment

Worker باید جدا از backend اجرا شود.

وظایف worker:

```text
ارسال SMS
ارسال Email
ارسال Push
پردازش retry نوتیفیکیشن
jobهای گزارش
پرداخت‌های async در صورت نیاز
```

قانون:

```text
اگر worker down شد، backend نباید کاملاً از کار بیفتد.
اما notification delivery عقب می‌افتد.
```

---

# 21. Database Access Rules

قوانین:

```text
دسترسی root دیتابیس برای app ممنوع است.
app باید user محدود داشته باشد.
backup user می‌تواند دسترسی read/lock مناسب داشته باشد.
production database فقط برای افراد محدود قابل دسترسی باشد.
```

---

# 22. Admin Panel Deploy

پنل ادمین Flutter Web باید build شود و توسط Nginx serve شود.

مراحل:

```bash
flutter build web --release
```

خروجی:

```text
admin-panel/build/web
```

Nginx باید این build را serve کند.

---

# 23. Mobile App Release

برای اپ موبایل:

```text
Android APK/AAB
iOS در آینده
```

قانون:

```text
API base URL برای هر محیط جدا باشد.
نسخه اپ باید با API version سازگار باشد.
```

---

# 24. Versioning

هر release باید tag داشته باشد.

مثال:

```text
v0.1.0-foundation
v0.2.0-auth-core
v0.3.0-geo-core
v0.4.0-notification-core
v1.0.0-mvp-release
```

---

# 25. Release Notes

هر release باید release note داشته باشد.

فرمت:

```md
# Release v0.2.0-auth-core

## Added
- OTP login
- Email/password login
- Refresh token

## Changed
- Standard API response updated

## Fixed
- ...

## Migration
- add auth_users table
- add auth_otp_codes table

## Risks
- OTP provider failure

## Rollback
- rollback to v0.1.0-foundation
```

---

# 26. Security Checklist قبل از Production

قبل از production:

```text
.env واقعی داخل Git نیست
JWT secret قوی است
debug خاموش است
CORS محدود است
admin فقط با HTTPS است
database public نیست
Redis public نیست
SSL فعال است
backup فعال است
restore تست شده است
rate limit OTP فعال است
file upload validation فعال است
payment verify فعال است
audit log فعال است
```

---

# 27. Incident Response

اگر اتفاق مهم افتاد:

```text
پرداخت خراب شد
دیتابیس خطا داد
فایل‌ها حذف شدند
secret لو رفت
deploy شکست خورد
```

باید incident ثبت شود.

فرمت:

```md
# Incident Report

## Time
زمان رخداد

## Impact
چه چیزی آسیب دید؟

## Cause
علت احتمالی

## Action Taken
چه کاری انجام شد؟

## Recovery
چطور برگشت؟

## Prevention
برای جلوگیری از تکرار چه کاری انجام می‌شود؟
```

---

# 28. Disaster Recovery

اگر سرور کامل از بین رفت، باید بتوانیم روی سرور جدید بالا بیاییم.

نیازها:

```text
Git repository
.env امن
database backup
storage backup
SSL یا امکان صدور SSL جدید
docker compose files
deployment docs
```

مراحل کلی:

```text
1. سرور جدید آماده شود.
2. Docker نصب شود.
3. repo clone شود.
4. env تنظیم شود.
5. database restore شود.
6. storage restore شود.
7. SSL تنظیم شود.
8. docker compose up اجرا شود.
9. smoke test انجام شود.
```

---

# 29. خط قرمزهای Deployment و Backup

موارد ممنوع:

```text
deploy بدون backup
migration مستقیم بدون تست staging
.env داخل Git
SSL private key داخل Git
دیتابیس production بدون backup روزانه
storage بدون backup
عدم تست restore
production با debug=true
دسترسی public به MySQL یا Redis
payment secret داخل log
اجرای app با database root user
```

---

# 30. نتیجه

استقرار و بکاپ در پروژه «فارم نت» فقط کار DevOps نیست؛ بخشی از امنیت و بقای پروژه است.

قانون نهایی:

```text
اگر امروز کل سرور پاک شود، باید بتوانیم پروژه را از Git + Backup + Env امن دوباره بالا بیاوریم.
```
