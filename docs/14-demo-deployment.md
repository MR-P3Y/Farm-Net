# 14 — Small Server Demo Deployment

This deployment is for a small, invite-only product demo on the existing server.
It is intentionally smaller than the production topology.

## Public endpoints

- `https://farmnet.ir`: Flutter Web user application
- `https://admin.farmnet.ir`: Flutter Web admin panel
- `https://api.farmnet.ir`: FastAPI backend
- `https://media.farmnet.ir`: media/API host for the demo

## Services included

- FastAPI backend
- MySQL 8
- Redis 7
- one-shot Alembic migration service
- Flutter Web builds served by the host Nginx

The demo does not run container Nginx, notification workers, Prometheus, or
Alertmanager. The backend is only published on `127.0.0.1:18100`.

## Build the web applications

Run these commands on a trusted build machine with Flutter installed:

```bash
cd mobile
flutter pub get
flutter build web --release \
  --dart-define=API_BASE_URL=https://api.farmnet.ir/api/v1

cd ../admin-panel
flutter pub get
flutter build web --release \
  --dart-define=API_BASE_URL=https://api.farmnet.ir/api/v1
```

Copy `mobile/build/web/` to `/var/www/farmnet/app/` and
`admin-panel/build/web/` to `/var/www/farmnet/admin/` on the server.

## Server-only configuration

1. Copy `infra/demo.env.example` to `infra/demo.env` and replace the admin
   identity values.
2. Create `infra/secrets-demo/` with mode `0700`.
3. Create these files with mode `0600` and unique random values:

   - `mysql_password`
   - `mysql_root_password`
   - `redis_password`
   - `jwt_secret_key` (at least 32 random characters)
   - `super_admin_password` (at least 12 characters)
   - `database_url`
   - `redis_url`

`database_url` must use the same MySQL password:

```text
mysql+pymysql://farmnet_user:<mysql_password>@mysql:3306/farmnet_db
```

`redis_url` must use the same Redis password:

```text
redis://:<redis_password>@redis:6379/0
```

Do not commit `demo.env` or `secrets-demo/`.

## Validate before starting

```bash
docker compose \
  --env-file infra/demo.env \
  -f infra/docker-compose.demo.yml \
  config --quiet
```

## Start the data services and migrate

Take a backup before every later migration. For the first demo install:

```bash
docker compose \
  --env-file infra/demo.env \
  -f infra/docker-compose.demo.yml \
  up -d mysql redis

docker compose \
  --env-file infra/demo.env \
  -f infra/docker-compose.demo.yml \
  run --rm migration

docker compose \
  --env-file infra/demo.env \
  -f infra/docker-compose.demo.yml \
  up -d backend
```

Seed the roles and the configured super admin once:

```bash
docker compose \
  --env-file infra/demo.env \
  -f infra/docker-compose.demo.yml \
  exec backend python scripts/seed_auth.py
```

## Local health checks on the server

```bash
curl -fsS http://127.0.0.1:18100/live
curl -fsS http://127.0.0.1:18100/ready
docker compose \
  --env-file infra/demo.env \
  -f infra/docker-compose.demo.yml \
  ps
```

Install `infra/nginx/farmnet-demo-host.conf.example` in the host Nginx only
after the certificate paths and existing virtual hosts have been checked.
