# Step 22.6 — Authentication, Session + Token Storage Hardening

Date: 2026-07-24

## Backend session contract

Every newly issued access and refresh token is bound to the database session
through the `sid` claim. Access tokens also contain a unique `jti`.

Every authenticated request now verifies:

- a valid access-token signature, expiry, and token type;
- a valid numeric user and session identity;
- an existing active, non-expired session;
- exact ownership of the session by the token subject;
- an existing non-suspended, non-deleted user.

Logout revokes both the supplied refresh token and its session. Because access
tokens are session-bound, they are rejected immediately after logout instead
of remaining usable until their JWT expiry.

## Refresh rotation and replay handling

Refresh tokens are one-time credentials:

1. the presented token row is locked for update;
2. JWT subject/session claims must match the stored token;
3. the session must be active, unexpired, and owned by the same user;
4. the old refresh token is revoked;
5. a new access/refresh pair is issued for the same fixed session lifetime.

Rotation does not extend the original 30-day session. Near session expiry,
access-token lifetime is capped by the remaining session lifetime.

Reuse of a known revoked refresh token is treated as a possible credential
replay. The whole session and every still-active refresh token in that session
are revoked. The user must authenticate again.

Existing pre-Step-22.6 refresh tokens already contain `sid` and can rotate.
Existing access tokens do not contain `sid`; clients will receive one
authentication failure, use their refresh token, and obtain a hardened pair.
If refresh is unavailable or invalid, reauthentication is required.

## Client token storage

Mobile and Admin now use `flutter_secure_storage` instead of storing bearer
tokens directly in `SharedPreferences`.

- Native platforms use the platform secure-storage implementation.
- Refresh token is written before access token, making interruption recovery
  safer.
- Logout clears both secure and legacy locations.
- Existing plaintext keys are migrated once into secure storage and erased.
- Mobile and Admin use separate versioned key namespaces.

The repository's previous broad `storage/` ignore rule also hid both client
source directories named `lib/core/storage`. It is now restricted to root and
Backend runtime storage, and the two token-storage source files are tracked.

The Web implementation uses browser WebCrypto-backed storage. Production Web
and Admin deployments must enforce HTTPS and HSTS. Secure storage does not
make bearer tokens immune to same-origin script execution; a strict CSP,
dependency integrity, XSS prevention, and careful third-party script policy
remain mandatory. Moving the Admin Web session to server-managed HttpOnly,
Secure, SameSite cookies would require a deliberate CSRF/CORS/API migration
and is not silently introduced by this step.

## Verification

- Backend auth hardening tests: 6 passed.
- Backend total: 203 passed; backup-tool suite: 8 passed.
- Backend Ruff and compileall: passed.
- Mobile secure-storage tests: 3 passed.
- Mobile analyze, all 57 tests, Web build, and Wasm dry run: passed.
- Admin secure-storage tests: 3 passed.
- Admin analyze, all 23 tests, Web build, and Wasm dry run: passed.
- Runtime OTP login: HTTP 200.
- Initial session-bound access: HTTP 200.
- Refresh token rotation: new token issued.
- Old refresh replay: HTTP 401.
- New access after replay-family revocation: HTTP 401.
- Runtime fixture cleanup: passed.
- Runtime app/database/Redis health: `ok`.
- Alembic current/check: `b8d4f2c71e04`, no drift.

No database migration was needed because the existing session and refresh-token
tables already support rotation, session binding, revocation, and expiry.
