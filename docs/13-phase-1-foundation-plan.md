# 13 — Phase 1 Foundation Plan
# برنامه اجرایی فاز ۱ پروژه فارم نت

## 1. هدف فاز ۱

هدف فاز ۱ این است که قبل از شروع کدنویسی Backend، Flutter و Admin Panel، ساختار رسمی پروژه آماده شود.

در این فاز هنوز وارد پیاده‌سازی Auth، Store، Payment یا UI اصلی نمی‌شویم.

هدف فاز ۱:

```text
ساخت monorepo
ساخت پوشه‌های اصلی پروژه
ثبت اسناد پایه
ساخت README
ساخت .gitignore
ساخت .env.example
تعریف Git workflow
تعریف ساختار docs
تعریف ساختار infra
تعریف ساختار scripts
تعریف ساختار postman
آماده‌سازی پروژه برای چند تیم
```

قانون مهم:

```text
فاز ۱ یعنی آماده‌سازی زمین پروژه، نه ساخت فیچر.
```

---

# 2. خروجی نهایی فاز ۱

در پایان فاز ۱ باید این ساختار وجود داشته باشد:

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

---

# 3. ساختار نهایی Repository

ساختار پیشنهادی:

```text
farmnet/
  backend/
    README.md
    .gitkeep

  mobile/
    README.md
    .gitkeep

  admin-panel/
    README.md
    .gitkeep

  docs/
    00-product-vision.md
    01-mvp-scope.md
    02-architecture.md
    03-module-roadmap.md
    04-team-workflow.md
    05-definition-of-done.md
    06-risk-control.md
    07-api-standard.md
    08-database-design-rules.md
    09-permissions-and-roles.md
    10-notification-events.md
    11-payment-and-commission.md
    12-deployment-and-backup.md
    13-phase-1-foundation-plan.md

    api/
      README.md

    database/
      README.md

    notifications/
      README.md

    payments/
      README.md

    deployment/
      README.md

    backup-restore/
      README.md

  infra/
    README.md
    docker-compose.yml
    nginx/
      README.md
    mysql/
      README.md
    redis/
      README.md

  scripts/
    README.md
    backup/
      README.md
    seed/
      README.md
    migrate/
      README.md
    dev/
      README.md

  postman/
    README.md
    collections/
      README.md

  README.md
  .gitignore
  .env.example
```

---

# 4. وظیفه هر پوشه

## backend/

برای کد FastAPI.

در فاز ۱ فقط پوشه ساخته می‌شود.
Backend واقعی در فاز ۲ ساخته می‌شود.

```text
backend/
```

در آینده شامل:

```text
app/
alembic/
tests/
Dockerfile
pyproject.toml
.env.example
```

---

## mobile/

برای اپ Flutter کاربران.

در فاز ۱ فقط پوشه ساخته می‌شود.
Flutter واقعی در فاز ۳ ساخته می‌شود.

```text
mobile/
```

در آینده شامل:

```text
lib/
pubspec.yaml
android/
ios/
web/
```

---

## admin-panel/

برای پنل ادمین Flutter Web.

در فاز ۱ فقط پوشه ساخته می‌شود.
Admin Panel واقعی در فاز ۴ ساخته می‌شود.

```text
admin-panel/
```

در آینده شامل:

```text
lib/
pubspec.yaml
web/
```

---

## docs/

برای تمام مستندات رسمی پروژه.

قانون:

```text
هر تصمیم مهم باید داخل docs ثبت شود.
هر تغییر API باید docs/api را آپدیت کند.
هر تغییر دیتابیس مهم باید docs/database را آپدیت کند.
```

---

## infra/

برای فایل‌های استقرار و زیرساخت.

در آینده شامل:

```text
docker-compose.yml
nginx configs
mysql configs
redis configs
ssl notes
```

قانون:

```text
فایل‌های SSL واقعی وارد Git نمی‌شوند.
فقط config و README وارد Git می‌شود.
```

---

## scripts/

برای اسکریپت‌های کمکی.

زیرپوشه‌ها:

```text
backup/
seed/
migrate/
dev/
```

مثال‌های آینده:

```text
backup_mysql.sh
backup_storage.sh
seed_permissions.py
seed_geo.py
run_migrations.sh
```

---

## postman/

برای collectionهای تست API.

در آینده:

```text
auth.postman_collection.json
geo.postman_collection.json
notification.postman_collection.json
store.postman_collection.json
payment.postman_collection.json
```

قانون:

```text
هر ماژول Backend باید collection تست دستی داشته باشد.
```

---

# 5. README اصلی پروژه

فایل:

```text
README.md
```

باید شامل این بخش‌ها باشد:

```md
# فارم نت

## معرفی پروژه

فارم نت یک سوپراپلیکیشن کشاورزی چندبخشی است که شامل فروشگاه، خدمات، اجاره ادوات، مشاوران، آب‌وهوا، هوش مصنوعی، فضای اجتماعی، تبلیغات، اشتراک، کمیسیون و پنل ادمین مرکزی است.

## تکنولوژی‌ها

- Backend: FastAPI
- Database: MySQL
- ORM: SQLAlchemy
- Migration: Alembic
- Cache/Queue: Redis
- Mobile: Flutter
- Admin Panel: Flutter Web
- Deployment: Docker Compose

## ساختار پروژه

backend/
mobile/
admin-panel/
docs/
infra/
scripts/
postman/

## قوانین مهم

- هیچ secret واقعی داخل Git قرار نمی‌گیرد.
- هیچ تغییر دیتابیس بدون migration انجام نمی‌شود.
- هیچ API بدون مستندات و contract ساخته نمی‌شود.
- هیچ فازی بدون تست، review و tag تمام نمی‌شود.
- main فقط نسخه پایدار است.
- develop شاخه اصلی توسعه است.

## اسناد مهم

- docs/00-product-vision.md
- docs/01-mvp-scope.md
- docs/02-architecture.md
- docs/03-module-roadmap.md
- docs/04-team-workflow.md
- docs/05-definition-of-done.md
- docs/06-risk-control.md
- docs/07-api-standard.md
- docs/08-database-design-rules.md
- docs/09-permissions-and-roles.md
- docs/10-notification-events.md
- docs/11-payment-and-commission.md
- docs/12-deployment-and-backup.md
- docs/13-phase-1-foundation-plan.md
```

---

# 6. .gitignore

فایل:

```text
.gitignore
```

باید حداقل این موارد را داشته باشد:

```gitignore
# Environment
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
venv/
.venv/
env/
ENV/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# FastAPI / logs
logs/
*.log

# Alembic temp
*.sqlite3

# Flutter / Dart
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.pub/
build/
coverage/

# Android / iOS generated
android/.gradle/
ios/Pods/
ios/.symlinks/

# IDE
.idea/
.vscode/
*.iml

# OS
.DS_Store
Thumbs.db

# Storage / Uploads
storage/
uploads/
media/
documents/

# Backups
backups/
*.sql
*.sql.gz
*.tar.gz
*.bak

# SSL / Secrets
*.pem
*.key
*.crt
ssl/
certs/

# Node / Web if needed
node_modules/
dist/
```

نکته مهم:

```text
.env.example باید وارد Git شود.
.env واقعی نباید وارد Git شود.
```

---

# 7. .env.example

فایل:

```text
.env.example
```

نمونه پیشنهادی:

```env
# App
APP_NAME=FarmNet
APP_ENV=development
APP_DEBUG=false
APP_VERSION=0.1.0

# URLs
PUBLIC_BASE_URL=http://localhost:8000
ADMIN_BASE_URL=http://localhost:8080
MEDIA_BASE_URL=http://localhost:8000/media

# Backend
API_V1_PREFIX=/api/v1

# Database
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=farmnet_db
MYSQL_USER=farmnet_user
MYSQL_PASSWORD=change-me
DATABASE_URL=mysql+pymysql://farmnet_user:change-me@mysql:3306/farmnet_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Super Admin Bootstrap
SUPER_ADMIN_EMAIL=admin@example.com
SUPER_ADMIN_PHONE=09120000000
SUPER_ADMIN_PASSWORD=change-me

# OTP
OTP_EXPIRE_MINUTES=2
OTP_MAX_ATTEMPTS=5
OTP_RATE_LIMIT_SECONDS=60

# SMS
SMS_PROVIDER=
SMS_API_KEY=
SMS_SENDER=

# Email
EMAIL_PROVIDER=smtp
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USER=
EMAIL_PASSWORD=
EMAIL_FROM=

# Push
PUSH_PROVIDER=fcm
FCM_SERVER_KEY=

# Payment
PAYMENT_GATEWAY=zarinpal
PAYMENT_MERCHANT_ID=
PAYMENT_CALLBACK_BASE_URL=http://localhost:8000/api/v1/payments/callback

# Storage
STORAGE_DRIVER=local
STORAGE_PATH=/app/storage
MAX_UPLOAD_SIZE_MB=10

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
RATE_LIMIT_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

---

# 8. docs/ ساختار اولیه

در فاز ۱ باید تمام سندهای زیر داخل `docs/` قرار بگیرند:

```text
00-product-vision.md
01-mvp-scope.md
02-architecture.md
03-module-roadmap.md
04-team-workflow.md
05-definition-of-done.md
06-risk-control.md
07-api-standard.md
08-database-design-rules.md
09-permissions-and-roles.md
10-notification-events.md
11-payment-and-commission.md
12-deployment-and-backup.md
13-phase-1-foundation-plan.md
```

همچنین پوشه‌های زیر باید ساخته شوند:

```text
docs/api/
docs/database/
docs/notifications/
docs/payments/
docs/deployment/
docs/backup-restore/
```

داخل هرکدام فعلاً یک `README.md` ساده قرار می‌گیرد.

---

# 9. infra/docker-compose.yml اولیه

در فاز ۱ می‌توانیم یک docker-compose اولیه placeholder داشته باشیم.

نسخه واقعی در Phase 2 کامل می‌شود.

نمونه اولیه:

```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: farmnet_mysql
    environment:
      MYSQL_DATABASE: farmnet_db
      MYSQL_USER: farmnet_user
      MYSQL_PASSWORD: change-me
      MYSQL_ROOT_PASSWORD: change-root-me
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7
    container_name: farmnet_redis
    ports:
      - "6379:6379"

volumes:
  mysql_data:
```

نکته:

```text
این فایل برای شروع است.
Backend و worker در Phase 2 اضافه می‌شوند.
Nginx و admin deploy در فازهای بعد کامل می‌شوند.
```

---

# 10. scripts/README.md

محتوای پیشنهادی:

```md
# Scripts

این پوشه شامل اسکریپت‌های کمکی پروژه است.

## backup/
اسکریپت‌های بکاپ دیتابیس و storage

## seed/
اسکریپت‌های seed مثل roles، permissions، geo data و templates

## migrate/
اسکریپت‌های اجرای migration

## dev/
اسکریپت‌های توسعه محلی
```

---

# 11. postman/README.md

محتوای پیشنهادی:

```md
# Postman Collections

این پوشه شامل collectionهای تست API پروژه است.

هر ماژول Backend باید collection جدا داشته باشد:

- auth
- geo
- notification
- media
- verification
- billing
- finance
- store
- promotion

هر collection باید شامل سناریوهای موفق، خطا، permission denied و validation error باشد.
```

---

# 12. Git Initialization

در فاز ۱ باید Git آماده شود.

دستورات:

```bash
git init
git checkout -b main
git add .
git commit -m "chore(project): initialize repository structure"
```

بعد:

```bash
git checkout -b develop
```

قانون:

```text
main = نسخه پایدار
develop = توسعه
feature/* = قابلیت‌ها
```

---

# 13. Branch Protection

وقتی remote repository ساخته شد، باید این قوانین فعال شوند:

```text
main protected
develop protected
no direct push to main
pull request required
review required
status checks required در صورت وجود CI
```

---

# 14. اولین Tag

بعد از تکمیل فاز ۱:

```bash
git checkout main
git merge develop
git tag v0.1.0-foundation-docs
git push origin main --tags
```

یا اگر هنوز remote نداریم، tag local زده می‌شود.

---

# 15. Definition of Done فاز ۱

فاز ۱ فقط زمانی Done است که:

```text
1. ساختار monorepo ساخته شده باشد.
2. backend/ وجود داشته باشد.
3. mobile/ وجود داشته باشد.
4. admin-panel/ وجود داشته باشد.
5. docs/ وجود داشته باشد.
6. infra/ وجود داشته باشد.
7. scripts/ وجود داشته باشد.
8. postman/ وجود داشته باشد.
9. README.md اصلی نوشته شده باشد.
10. .gitignore نوشته شده باشد.
11. .env.example نوشته شده باشد.
12. تمام ۱۳ سند پایه در docs قرار گرفته باشند.
13. docker-compose اولیه برای MySQL و Redis وجود داشته باشد.
14. Git init شده باشد.
15. branchهای main و develop ساخته شده باشند.
16. اولین commit زده شده باشد.
17. tag فاز ۱ زده شده باشد.
18. هیچ secret واقعی داخل repo نباشد.
```

---

# 16. خروجی قابل تحویل فاز ۱

خروجی فاز ۱:

```text
یک repository تمیز و مستند که آماده شروع Backend Foundation، Flutter Foundation و Admin Foundation است.
```

بعد از این فاز، تیم‌ها می‌توانند وارد فازهای اجرایی شوند:

```text
Phase 2: Backend Foundation
Phase 3: Flutter Foundation
Phase 4: Admin Panel Foundation
```

اما پیشنهاد اجرایی:

```text
اول Phase 2 Backend Foundation
بعد Phase 3 Flutter Foundation
بعد Phase 4 Admin Foundation
```

چون Flutter و Admin برای اتصال واقعی به API نیاز دارند Backend Foundation آماده باشد.

---

# 17. خط قرمزهای فاز ۱

موارد ممنوع:

```text
شروع کدنویسی Auth قبل از تکمیل repo structure
ساخت Flutter UI قبل از API استاندارد
قرار دادن .env واقعی داخل Git
قرار دادن فایل‌های SSL داخل Git
نداشتن docs
نداشتن .gitignore
نداشتن .env.example
commit با پیام نامفهوم
شروع feature بدون branch
```

---

# 18. نتیجه فاز ۱

فاز ۱ پایه نظم پروژه است.

اگر این فاز درست انجام شود:

```text
تیم‌ها مسیر مشترک دارند.
مستندات پایه آماده است.
Git آماده است.
ساختار پروژه گم نمی‌شود.
secrets وارد Git نمی‌شوند.
پروژه آماده شروع فاز Backend Foundation است.
```

قانون نهایی:

```text
قبل از کد، ساختار. قبل از ساختار، سند. قبل از توسعه، نظم.
```
