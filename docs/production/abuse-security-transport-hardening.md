# Step 22.7 — Abuse Protection, Security Headers + Transport Hardening

Date: 2026-07-25

## Abuse protection

The Backend supports two explicit rate-limit backends:

- `memory`: bounded single-process development mode;
- `redis`: shared production/staging mode using atomic Redis `INCR`/`EXPIRE`.

Production-like configuration now fails startup unless rate limiting is
enabled, `RATE_LIMIT_BACKEND=redis`, and at least one trusted immediate proxy
IP/CIDR is configured. Redis keys contain SHA-256 client identifiers rather
than raw IP addresses. If Redis protection becomes unavailable, production
requests fail closed with HTTP 503 and `RATE_LIMIT_UNAVAILABLE`; they are not
silently allowed.

Three independent limits apply:

- general API: configurable, development default 120 per 60 seconds;
- unified search: configurable, default 30 per 60 seconds;
- sensitive Auth routes: configurable, default 10 per 60 seconds.

Auth protection covers email login, OTP request, OTP verification, and refresh.
HTTP 429 responses expose `Retry-After`, `RateLimit-Limit`,
`RateLimit-Remaining: 0`, and `Cache-Control: no-store`.

## Trusted proxy chain

`X-Forwarded-For` and `X-Forwarded-Proto` are accepted only when the immediate
peer is an explicitly trusted host, IP, or CIDR. Client identity is selected by
walking the forwarded chain from right to left and skipping known proxies.
This prevents a user-supplied first XFF value from bypassing per-client limits.
Malformed chains fall back to the immediate peer.

Only the actual reverse-proxy network should be configured. Do not trust all
private networks when a narrower subnet or fixed address is available.

## Application security headers

All responses receive:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- a restrictive `Permissions-Policy`

API/health responses also receive a non-executable CSP with
`default-src 'none'` and `frame-ancestors 'none'`. Auth, Admin, Profile,
Notifications, and Finance responses default to `Cache-Control: no-store`.

Production HTTPS requests receive one-year HSTS with `includeSubDomains`.
Forwarded HTTPS is recognized only from a trusted proxy, preventing spoofed
HSTS decisions in direct local HTTP traffic.

## CORS

Production origins were already required to be explicit HTTPS origins. The
application no longer allows wildcard methods and headers:

- methods: GET, POST, PUT, PATCH, DELETE, OPTIONS;
- request headers: Accept, Authorization, Content-Type, X-Trace-Id;
- exposed response headers: X-Trace-Id, Retry-After, RateLimit-Limit, and
  RateLimit-Remaining;
- preflight cache: 600 seconds.

Known-origin preflight passes; an unapproved header receives HTTP 400.

## Nginx transport template

`infra/nginx/farmnet.conf` and `farmnet-proxy.conf` now provide a validated
reverse-proxy baseline:

- HTTP-to-HTTPS 308 redirect and ACME exception;
- TLS 1.2/1.3, disabled session tickets, HSTS, and security headers;
- edge general/Auth request limits;
- bounded request size and proxy timeouts;
- canonical Host, Real-IP, XFF, scheme, and forwarded-host headers.

The configuration passed `nginx -t` using `nginx:1.28-alpine` and an ephemeral
test certificate. It is a deployable template, not proof of a live production
deployment. Real domains, certificates, Docker network/topology, secrets,
certificate renewal, and external TLS scanning remain deployment work.

## Verification evidence

- Focused transport/abuse/config regressions: 19 passed.
- Backend Ruff and compileall: passed.
- Backend tests: 212 passed with 27 known warnings.
- Backup-tool tests: 8 passed.
- Real Redis atomic drill: `[allowed, allowed, denied]`; TTL valid; test key
  removed.
- Runtime Auth limit: ten validation responses followed by HTTP 429 on request
  eleven.
- Runtime 429 headers and stable error code: passed.
- Runtime security headers and known-origin CORS: passed.
- `nginx -t`: successful.
- Runtime app/database/Redis health: `ok`.
- Alembic remains `b8d4f2c71e04` with no drift.

Mobile and Admin source behavior did not change, so their previously passing
Step 22.6 analyze/test/Web-build gate was not repeated.
