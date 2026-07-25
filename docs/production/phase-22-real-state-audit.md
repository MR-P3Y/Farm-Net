# Phase 22.1 — Production Readiness Real-State Audit

Date: 2026-07-24

Branch: `develop`

Baseline: `756e7ea` (`v0.25.0-reviews-foundation`)

## Decision

Phase 21 AI/RAG is intentionally deferred by the project owner. The next
authorized engineering track is Phase 22 Production Hardening. This audit is
read-only: it changes no API, database, Mobile, Admin, provider, or deployment
behavior.

## Healthy baseline

- `develop` is clean and synchronized with `origin/develop`.
- Backend, MySQL, and Redis containers are running; app/database/Redis health
  is `ok`.
- Alembic is at the single head `a7c9e1f30d13`.
- The database contains 98 tables.
- OpenAPI exposes 264 paths, 303 operations, and 141 schemas.
- The latest release gate passed Ruff/compileall, 186 Backend tests, 54 Mobile
  tests, 20 Admin tests, both Web builds, and 14 Postman collections / 325
  requests.

This is a strong development foundation, not a production-readiness claim.

## Blocking findings

### Deployment and operations

- The current Compose file runs only Backend, MySQL, and Redis in development
  mode with host ports and a source bind mount.
- There is no production/staging Compose, Nginx configuration, TLS termination,
  Admin/Mobile Web serving, notification worker service, scheduler, readiness
  policy, rolling/blue-green deployment, or rollback automation.
- `infra/nginx` and `scripts/backup` contain README placeholders only.
- No verified MySQL/media backup, restore drill, retention policy, or disaster
  recovery evidence exists.
- There is no GitHub Actions quality/deployment workflow.

### Release governance

- `develop` is 122 commits ahead of `main`; `main` and `origin/main` remain at
  the Phase 13 merge despite releases through `v0.25.0`.
- Backend reports version `0.1.0`, while both Flutter clients report
  `1.0.0+1`; none matches the current release tag.
- Roadmap numbering and current-position summaries contain historical drift
  (notably Services/Category phase numbering and an outdated progress header).

### Database and contracts

- `alembic upgrade head` passes, but `alembic check` reports four index
  differences on Consultant/Services code and user identity columns.
- 281 of 303 OpenAPI operations have no useful typed success schema. Newer
  Review endpoints demonstrate the desired typed-envelope pattern, but most
  earlier APIs still return manually assembled envelopes without
  `response_model`.
- Backend dependency ranges are open-ended and there is no reproducible lock,
  SBOM, dependency update policy, or automated vulnerability scan.

### Authentication and configuration

- Production configuration does not fail fast when JWT/Super Admin defaults or
  development OTP settings are unsafe.
- Disabling Dev OTP does not connect a real OTP sender; the service still
  derives the configured development code.
- Refresh-token rotation is explicitly deferred.
- Mobile/Admin do not perform centralized automatic 401 refresh/retry.
- Mobile tokens are stored in `SharedPreferences`, not operating-system secure
  storage.

### External integrations

- Zarinpal is disabled by default and has no credentialed staging evidence.
- Real bank payout and real provider refund movement are not implemented.
- Email, SMS, and Push delivery providers are disabled/uncredentialed.
- Weather production-provider operation is not verified.
- No secrets are required or introduced by this audit.

### Test depth and observability

- Existing focused tests are valuable, but most Backend domain tests use
  mocks; only a small subset exercises live HTTP through `TestClient`.
- There are no Flutter integration/device, browser E2E, golden regression,
  production-like load, DAST, or recovery tests.
- There is no coverage threshold, metrics endpoint/collector, trace backend,
  centralized log pipeline, error tracker, SLO, or alert policy.

## Deferred product backlog outside Phase 22

Production Hardening must not silently implement new business modules. The
following remain separate future product work:

- AI/RAG;
- contracts and digital-signature management;
- subscriptions/plans;
- promotions, coupons, and ladder packages;
- complete shipping/fulfilment;
- Data Access/BI and governed exports;
- analytics/report jobs;
- advanced fraud/abuse intelligence.

Permissions already seeded for some future modules do not mean those modules
are implemented.

## Approved Phase 22 sequence

1. **22.1** Production Readiness Real-State Audit.
2. **22.2** Release, Branch, Version + Documentation Governance.
3. **22.3** Production Configuration, Secret + Dev-Switch Safety.
4. **22.4** Database Drift, Migration + Backup/Restore Hardening.
5. **22.5** Typed OpenAPI + Cross-Client Contract Completion.
6. **22.6** Auth Session, Token Storage + Client Recovery Hardening.
7. **22.7** CI Quality, Security + Supply-Chain Gates.
8. **22.8** Production Containers, Nginx/TLS + Worker Topology.
9. **22.9** Observability, Readiness, Metrics + Alerting.
10. **22.10** Credentialed Staging Provider Verification.
11. **22.11** Cross-Surface E2E, Load, Security + Recovery Drills.
12. **22.12** Production Runbooks + Staging Release Regression.
13. **22.13** Production Hardening Release Gate + Tag.

Every step must preserve current API and business behavior unless its scope
explicitly authorizes a compatible contract/security change.

## Phase 22 completion gate

Phase 22 cannot close until:

- a reproducible CI gate protects `develop` and release promotion;
- `main` promotion policy and versioning are explicit and exercised;
- production configuration rejects unsafe defaults;
- Alembic head/check and clean-database/upgrade paths pass;
- encrypted backup and tested restore cover database and media;
- OpenAPI success contracts are typed and client contract regressions pass;
- session recovery and secure Mobile token storage pass;
- production images are immutable/non-root and dependency-scanned;
- Nginx/TLS, workers, persistent storage, readiness and graceful shutdown pass;
- logs, metrics, alerts and operational ownership are documented;
- credentialed staging checks succeed without exposing secrets;
- E2E, load/security baselines and disaster-recovery drills pass;
- staging deployment, rollback, runbooks, Git safety and final tag pass.

## Step 22.1 conclusion

The repository is ready to begin hardening, but not ready for public production
traffic. Step 22.2 is the next bounded action. AI/RAG remains deferred.
