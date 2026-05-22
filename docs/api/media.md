# Farm Net Media / File Storage API

## Purpose

Media foundation provides safe file upload, storage, access control, and admin review for Farm Net.

Supported use cases:

- Product images
- Store logo
- Store banner
- Profile / verification documents
- General files

## Storage

Current storage mode:

```text
local
```

Default storage path:

```text
backend/storage/media
```

Files are stored with generated `file_key` and safe relative paths.

Physical files are not deleted during soft delete. Status controls access.

## Visibility

### public

Public files are accessible without authentication:

```http
GET /api/v1/media/public/{file_key}
```

Used for:

- product_image
- store_logo
- store_banner

### private

Private files require authentication and ownership:

```http
GET /api/v1/media/private/{file_key}
```

Admin access for private files:

```http
GET /api/v1/admin/media/private/{file_key}
```

Used for:

- verification_document
- profile_document

## Status

Supported statuses:

```text
active
deleted
quarantined
```

Only `active` files are served by access endpoints.

`deleted` and `quarantined` files remain in database/storage but are not accessible through public/private access routes.

## Upload API

```http
POST /api/v1/media/upload
```

Auth required.

Form fields:

| Field | Required | Description |
| --- | ---: | --- |
| file | yes | Multipart file |
| purpose | yes | File purpose |
| visibility | yes | public/private |
| alt_text | no | Image alt text |
| description | no | Description |

Example purposes:

```text
product_image
store_logo
store_banner
profile_document
verification_document
general
```

Rules:

- Product/store images must be public.
- Verification/profile documents must be private.
- Invalid MIME types are rejected.
- Oversized files are rejected.

## My Media

```http
GET /api/v1/media/me
```

Returns current user's uploaded media files.

Optional filters:

```text
purpose
visibility
status
page
page_size
```

## Media Detail

```http
GET /api/v1/media/{file_key}
```

Returns media metadata for current user.

## Delete My Media

```http
DELETE /api/v1/media/{file_key}
```

Soft deletes current user's media file.

## Public Access

```http
GET /api/v1/media/public/{file_key}
```

Rules:

- No auth required.
- File must be `visibility=public`.
- File must be `status=active`.

Response header:

```text
Cache-Control: public, max-age=86400
```

## Private Access

```http
GET /api/v1/media/private/{file_key}
```

Rules:

- Auth required.
- File must be `visibility=private`.
- File must be `status=active`.
- User must own the file.

Response header:

```text
Cache-Control: private, no-store
```

## Admin Private Access

```http
GET /api/v1/admin/media/private/{file_key}
```

Required permission:

```text
media.admin_read
```

Rules:

- File must be `visibility=private`.
- File must be `status=active`.

## Admin Media Management

### List

```http
GET /api/v1/admin/media
```

Required permission:

```text
media.admin_read
```

Filters:

```text
purpose
visibility
status
owner_user_id
page
page_size
```

### Detail

```http
GET /api/v1/admin/media/{file_key}
```

Required permission:

```text
media.admin_read
```

### Update Status

```http
PATCH /api/v1/admin/media/{file_key}/status
```

Required permission:

```text
media.admin_manage
```

Body:

```json
{
  "status": "quarantined",
  "description": "Reason"
}
```

Allowed statuses:

```text
active
deleted
quarantined
```

## Product Integration

Product images support real media files.

Input:

```json
{
  "media_file_key": "..."
}
```

Rules:

```text
purpose = product_image
visibility = public
status = active
owner_user_id = current_user.id
```

Output fields:

```json
{
  "media_file_id": 1,
  "file_key": "...",
  "public_url": "/api/v1/media/public/..."
}
```

## Store Branding Integration

Stores support real logo/banner media.

Input:

```json
{
  "logo_media_file_key": "...",
  "banner_media_file_key": "..."
}
```

Rules:

```text
logo:
purpose = store_logo
visibility = public
status = active

banner:
purpose = store_banner
visibility = public
status = active

owner_user_id = current_user.id
```

Output fields:

```json
{
  "logo_media_file_id": 1,
  "logo_file_key": "...",
  "logo_url": "/api/v1/media/public/...",

  "banner_media_file_id": 2,
  "banner_file_key": "...",
  "banner_url": "/api/v1/media/public/..."
}
```

## User Documents Integration

User documents support real private media files.

Input:

```json
{
  "media_file_key": "..."
}
```

Rules:

```text
purpose = verification_document
visibility = private
status = active
owner_user_id = current_user.id
```

Output fields:

```json
{
  "media_file_id": 1,
  "file_key": "...",
  "private_url": "/api/v1/media/private/...",
  "admin_private_url": "/api/v1/admin/media/private/..."
}
```

## Permissions

Media permissions:

```text
media.upload
media.read
media.public_read
media.private_read
media.delete
media.admin_read
media.admin_manage
```

## Security Notes

- Paths are generated server-side.
- File keys are generated server-side.
- Path traversal is blocked.
- MIME validation is enforced.
- Size limits are enforced.
- Private files are not exposed through public routes.
- Non-owner private file access does not leak file existence.
- Quarantined/deleted files are not served.
