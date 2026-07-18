# Equipment Rental API

Base prefix: `/api/v1`

Equipment Rental is independent from Product sale inventory and Services work.
All responses use the standard Farm-Net success/error envelope.

## Categories and lessor profiles (Phase 16.3)

| Method | Path | Access |
|---|---|---|
| GET | `/rentals/categories` | Public, active only |
| GET | `/rentals/me/lessor-profile` | `rental_lessors.profile_manage` |
| PUT | `/rentals/me/lessor-profile` | `rental_lessors.profile_manage` |
| POST | `/rentals/me/lessor-profile/submit` | `rental_lessors.profile_manage` |
| GET | `/admin/rentals/categories` | `rental_categories.admin_read` |
| POST | `/admin/rentals/categories` | `rental_categories.create` |
| PATCH | `/admin/rentals/categories/{category_id}` | `rental_categories.update` |
| GET | `/admin/rentals/lessor-profiles` | `rental_lessors.admin_read` |
| PATCH | `/admin/rentals/lessor-profiles/{profile_id}/status` | `rental_lessors.admin_moderate` |

Profile editing is limited to `draft` and `rejected`. Submission requires
display name, phone, province, city, and address. Approval is allowed only from
`pending_review` and requires an approved Verification Request for target role
`lessor`. Rejection and suspension require an Admin note.

Category codes are stable lowercase identifiers. Parent clearing is explicit,
self-parenting and hierarchy cycles are rejected, and seeds create only missing
rows without overwriting Admin-owned values.

## Equipment listings and media (Phase 16.4)

| Method | Path | Access |
|---|---|---|
| GET | `/rentals/equipment` | Public approved listings |
| GET | `/rentals/equipment/{equipment_id}` | Public approved detail |
| GET | `/rentals/me/equipment` | Owner listing |
| POST | `/rentals/me/equipment` | Approved lessor |
| PUT | `/rentals/me/equipment/{equipment_id}` | Owning approved lessor |
| POST | `/rentals/me/equipment/{equipment_id}/submit` | Owning approved lessor |
| GET | `/admin/rentals/equipment` | `rental_equipment.admin_read` |
| PATCH | `/admin/rentals/equipment/{equipment_id}/status` | Status-specific moderation permission |

Owner media must be active, public, and owned by the same user. At most one
primary item is accepted and the first item becomes primary when omitted.
Public output excludes exact address, moderation notes, actor IDs, and internal
lifecycle timestamps. Public discovery requires both approved equipment and an
approved, non-deleted lessor profile.
