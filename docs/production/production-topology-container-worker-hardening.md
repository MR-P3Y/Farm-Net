# Step 22.8 — Production Topology, Container + Worker Hardening

Verified: 2026-07-25
Branch: `develop`

## Delivered topology

`infra/docker-compose.production.yml` is the production topology contract. It
contains:

- MySQL and Redis on an internal-only data network with persistent named
  volumes, authentication, health checks, and no published host ports;
- a one-shot Alembic migration service that must complete successfully before
  the API or workers start;
- a non-root, read-only Backend container with a persistent Media volume;
- independent long-running Email, SMS, and Push workers with graceful
  SIGTERM/SIGINT shutdown, structured logs, per-batch database sessions, and
  heartbeat health checks;
- an Nginx TLS edge as the only public service, with the hardened proxy
  contract from Step 22.7;
- bounded CPU, memory, process, log-rotation, capability, and
  `no-new-privileges` settings.

The production Compose file consumes secrets from files rather than inline
environment values. `SECRETS_DIR` can point to an external secret mount;
`infra/secrets/` and `infra/production.env` are ignored. The non-secret
template is `infra/production.env.example`.

## Container contract

The Backend uses a multi-stage build from a digest-pinned Python base. Runtime
dependencies are version-locked in `backend/requirements.lock`. The final
image:

- runs as UID/GID `10001`;
- contains application, migration, and worker code but excludes tests, local
  environments, caches, generated metadata, uploads, and archives;
- owns only its required runtime paths;
- starts Uvicorn without trusting proxy headers directly, leaving trusted
  proxy resolution to the application contract;
- exposes a container health check.

MySQL, Redis, and Nginx images are digest-pinned. The application image is
locally version-tagged; immutable registry publication and vulnerability/SBOM
gates remain CI/CD work and are not claimed by this step.

## Secret-file contract

The runtime can load Database, Redis, JWT, Super Admin, Email, SMS, Push, and
Payment sensitive values from their corresponding `*_FILE` settings. Secret
files must exist, be regular non-symlink files, be non-empty, and be no larger
than 64 KiB. Startup errors identify only the setting name and never echo the
secret value. Existing production fail-closed validation runs after file
resolution.

## Real isolated topology drill

The complete topology was started under the isolated Compose project
`farmnet-step-22-8-drill` with temporary credentials, a one-day test
certificate, ports `18080/18443`, and fresh test-only volumes.

Observed results:

- MySQL: healthy
- Redis: healthy
- Alembic migration: exited `0`
- Backend: healthy
- Email worker: healthy
- SMS worker: healthy
- Push worker: healthy
- Nginx: healthy
- `HTTPS /health`: app/database/redis all `ok`
- Backend: UID/GID `10001`, read-only root filesystem, all capabilities
  dropped, `no-new-privileges`
- MySQL/Redis host port bindings: none

The drill exposed and led to correction of the Redis named-volume ownership
capability contract. After the successful run, all drill containers, networks,
and volumes were removed. No real credential, provider delivery, or production
host was used.

## Verification

- Docker production image build: passed
- Runtime image content/non-root checks: passed
- Docker Compose render/config validation: passed
- Full isolated production topology and HTTPS health drill: passed
- Backend Ruff: passed
- Backend compileall: passed
- Backend tests: `217 passed` with 27 known deprecation warnings

## Deliberate boundaries

- This is a deployable topology contract, not evidence of a live production
  deployment.
- Real TLS issuance/renewal, registry publication by immutable digest, CI
  supply-chain scanning, orchestrator rollout/rollback, external provider
  credentials, monitoring, and off-host recovery remain later Phase 22 work.
- Mobile, Admin, API behavior, database schema, and business features were not
  changed.
