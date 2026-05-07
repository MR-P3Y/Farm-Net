# Farm Net | فارم نت

Farm Net یک سوپراپلیکیشن کشاورزی چندبخشی است که شامل فروشگاه، خدمات، اجاره ادوات، مشاوران، آب‌وهوا، هوش مصنوعی، فضای اجتماعی، تبلیغات، اشتراک، کمیسیون و پنل ادمین مرکزی است.

## تکنولوژی‌ها

- Backend: FastAPI
- Database: MySQL
- ORM: SQLAlchemy
- Migration: Alembic
- Cache/Queue: Redis
- Mobile App: Flutter
- Admin Panel: Flutter Web
- Deployment: Docker Compose
- Architecture: Modular Monolith

## ساختار پروژه

```text
backend/
mobile/
admin-panel/
docs/
infra/
scripts/
postman/
```

## قوانین مهم

- هیچ secret واقعی داخل Git قرار نمی‌گیرد.
- فقط `.env.example` وارد Git می‌شود.
- هیچ تغییر دیتابیس بدون migration انجام نمی‌شود.
- هیچ API بدون contract و مستندات ساخته نمی‌شود.
- هیچ فازی بدون تست، review، docs و tag تمام نمی‌شود.
- `main` فقط نسخه پایدار است.
- `develop` شاخه اصلی توسعه است.

## اسناد پایه

- [docs/00-product-vision.md](docs/00-product-vision.md)
- [docs/01-mvp-scope.md](docs/01-mvp-scope.md)
- [docs/02-architecture.md](docs/02-architecture.md)
- [docs/03-module-roadmap.md](docs/03-module-roadmap.md)
- [docs/04-team-workflow.md](docs/04-team-workflow.md)
- [docs/05-definition-of-done.md](docs/05-definition-of-done.md)
- [docs/06-risk-control.md](docs/06-risk-control.md)
- [docs/07-api-standard.md](docs/07-api-standard.md)
- [docs/08-database-design-rules.md](docs/08-database-design-rules.md)
- [docs/09-permissions-and-roles.md](docs/09-permissions-and-roles.md)
- [docs/10-notification-events.md](docs/10-notification-events.md)
- [docs/11-payment-and-commission.md](docs/11-payment-and-commission.md)
- [docs/12-deployment-and-backup.md](docs/12-deployment-and-backup.md)
- [docs/13-phase-1-foundation-plan.md](docs/13-phase-1-foundation-plan.md)
