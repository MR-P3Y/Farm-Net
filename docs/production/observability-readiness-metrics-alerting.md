# Step 22.9 — Observability, Readiness, Metrics + Alerting

Verified: 2026-07-25

## Runtime signals

- `/live` proves only that the API process can serve requests.
- `/ready` checks required MySQL and Redis dependencies and returns HTTP 503
  when either is unavailable.
- The existing `/health` and `/api/v1/health` response contract remains
  unchanged for compatibility.
- Docker and Nginx use `/ready` and `/live` respectively.
- `/metrics` exposes Prometheus process, HTTP, application-build, and
  dependency-readiness signals on the internal Backend network.

Nginx deliberately returns 404 for `/metrics` and `/ready`; neither endpoint
is exposed at the public edge. `/live` remains a safe dependency-free edge
probe.

## Structured logging and privacy

API request completion logs are JSON and contain only timestamp, severity,
logger, event, sanitized trace ID, HTTP method, normalized route template,
status, and duration. Query strings, request/response bodies, authorization
headers, raw entity IDs, and credentials are not logged.

Client-provided trace IDs are accepted only when bounded to 100 characters and
made solely of alphanumeric characters plus `-_.`; invalid values are replaced.
Prometheus labels use normalized route templates such as
`/orders/{order_id}`, preventing raw identifiers and unbounded-cardinality
paths from entering metrics.

## Prometheus and Alertmanager

The production topology adds digest-pinned, non-public Prometheus and
Alertmanager services on the internal data network. Both run read-only,
non-root, without Linux capabilities, with resource limits and persistent
named storage. Prometheus retains data for 15 days by default; deployments can
override `PROMETHEUS_RETENTION`.

Prometheus scrapes:

- Farm-Net API;
- Prometheus itself;
- Alertmanager.

Five rules cover:

- API scrape unavailability;
- required dependency readiness failure;
- Alertmanager unavailability;
- sustained server-error ratio above 5 percent;
- sustained p95 API latency above 2 seconds.

Rules have explicit severity, duration, summary, and runbook annotations.
`alerts.test.yml` verifies real firing behavior for API-down and
dependency-not-ready inputs.

## Operational response

For a critical availability/readiness alert:

1. identify the failing target/dependency and correlation window;
2. check the API, MySQL, Redis, migration, and worker container health;
3. use structured logs and the response `X-Trace-Id` to correlate the request;
4. do not restart or restore data before identifying the failed dependency;
5. use the backup/restore runbook only when database integrity requires it;
6. record incident start, impact, mitigation, and recovery timestamps.

For error-ratio or latency warnings, compare affected route templates and
deployment time, check dependency saturation, and roll back only through the
approved release process.

## Verified drill

An isolated full production topology with fresh test volumes and temporary
credentials/certificate passed:

- migration exited `0`;
- Backend, MySQL, Redis, Nginx, all three notification workers, Prometheus,
  and Alertmanager were healthy;
- Prometheus reported `up=1` for API, Prometheus, and Alertmanager;
- `farmnet_app_info` reported environment `production` and version
  `0.26.0-dev.1`;
- public HTTPS returned `/live=200`, `/metrics=404`, `/ready=404`;
- Backend emitted correlated JSON request logs;
- Prometheus config and five rules passed `promtool`;
- Alertmanager config passed `amtool`;
- alert-rule firing tests passed.

The drill containers, networks, and test volumes were removed afterward.

## Honest boundary

Alertmanager currently uses the named
`unconfigured-operations-receiver` without an external integration. This
validates grouping, rule delivery, retention, and internal availability but
does not claim paging an operator. Selecting an incident channel and
provisioning its credential/endpoint is an operational owner decision and
must be completed before public production. Credentialed staging provider
verification is Step 22.10.

No business API, database schema, Mobile behavior, Admin behavior, external
provider, or financial contract changed in this step.

## Verification summary

- Ruff: passed
- compileall: passed
- Backend tests: `222 passed`, 27 known deprecation warnings
- Prometheus config/rules: passed, five rules
- Alertmanager config: passed
- Alert firing tests: passed
- Production topology drill: passed
