# Phase 23.8 Role Setup/Verification + Multi-Role Hardening

## Result

The Activity Center now has a typed professional-role journey for the four
Mobile business roles:

- `shop_owner` — Seller and Store Owner;
- `service_provider` — agricultural Service Provider;
- `lessor` — Equipment Lessor;
- `consultant` — agricultural Consultant.

Each role is rendered as active only when it is present in authoritative
`AuthUser.roles`. Inactive roles link to their real first action: Verification
for Shop Owner/Lessor and profile setup for Service Provider/Consultant. The
card also links to the complete Verification request list.

## Multi-role hardening

- The role journey has deterministic order and deduplicates repeated auth roles
  through set membership.
- Admin/support/data roles are not counted as Mobile professional roles.
- The identity summary counts only the four business roles.
- All active roles can coexist; no destructive role switch is introduced.
- A refresh control calls the real authenticated identity load so newly
  approved roles and permissions become visible without logout/login.
- Role status is never inferred from a profile or Verification row; only the
  refreshed auth contract marks it active.

## Verification evidence

Backend Admin Verification approval calls `assign_role_to_user` with the exact
request `target_role`. Runtime OpenAPI exposes authenticated identity refresh,
own Verification list, create, attach-document, and submit contracts. Existing
Mobile notification routing accepts both legacy `/verification` and canonical
`/verifications`; the Activity Center emits only the canonical route.

- Mobile format/analyze: passed with no issues.
- Mobile tests: all 50 passed, including ordered/deduplicated role journey,
  active role flags, and exact setup routes.
- Mobile Web build and Wasm dry-run: passed.
- Runtime health: application, database, and Redis `ok`.
- Runtime OpenAPI: 254 paths; five identity/Verification contracts passed exact
  method checks.

No role was assigned during verification, no document was uploaded, and no
Backend/API/database/Admin behavior changed.
