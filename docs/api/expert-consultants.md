# Expert Answers and Consultants API

This document covers the API contract shared by social post detail, expert answers, consultant public profiles, and admin moderation.

## Social Post Detail Contract

```http
GET /api/v1/social/posts/{post_id}
```

The detail response includes `expert_answers`.

Important rules:

```text
expert_answers exists only on social post detail responses.
Social post list responses do not include expert_answers.
Only published expert answers are returned.
Hidden/deleted expert answers are excluded by the backend.
consultant can be null.
The consultant summary is safe and does not expose phone, email, admin_note, or moderation-only fields.
```

Expert answer item fields:

```text
id
answer_id
post_id
expert_user_id
expert_id
body
status
is_accepted
accepted_at
accepted_by_user_id
helpful_count
reports_count
created_at
updated_at
deleted_at
consultant
```

`id` and `answer_id` both identify the expert answer. `expert_user_id` and `expert_id` both identify the answering user.

## Public Expert Answer APIs

```http
GET  /api/v1/social/posts/{post_id}/expert-answers
POST /api/v1/social/posts/{post_id}/expert-answers
```

`GET` is public and returns published answers only.

`POST` requires:

```text
expert_answer.create
```

Request:

```json
{
  "body": "پاسخ تخصصی نمونه برای پست اجتماعی."
}
```

When a published answer is created for another user's post, the backend emits:

```text
expert_answer_created
```

The post owner receives an in-app notification. Republish/hide/delete moderation actions do not emit duplicate expert answer notifications.

## Expert User APIs

```http
GET    /api/v1/expert/me/answers
GET    /api/v1/expert/me/answers?status=published
DELETE /api/v1/expert/answers/{answer_id}
```

Permissions:

```text
expert_answer.manage_own
```

Own delete is a soft delete.

## Admin Expert Answer APIs

```http
GET    /api/v1/admin/expert/answers
GET    /api/v1/admin/expert/answers?status=published
GET    /api/v1/admin/expert/answers?post_id=1
GET    /api/v1/admin/expert/answers?expert_id=3
PATCH  /api/v1/admin/expert/answers/{answer_id}/status
DELETE /api/v1/admin/expert/answers/{answer_id}
```

Permissions:

```text
expert_answer.admin_read
expert_answer.admin_moderate
```

Admin list filters:

```text
status=published|hidden|deleted
post_id=...
expert_id=...
page=1
page_size=20
```

Admin response includes:

```text
answer_id
post_id
expert_id
expert_user_id
body
status
created_at
updated_at
deleted_at
post_title
post_preview
consultant
```

`post_preview` is a short text preview from the social post body/title.

PATCH status accepts:

```text
published
hidden
```

Use DELETE for soft delete:

```text
status = deleted
deleted_at = now()
```

## Consultant Summary in Expert Answers

`consultant` can be null. When present, it contains safe public metadata:

```text
consultant_id
user_id
display_name
name
title
avatar_file_id
avatar_media_file_id
avatar_url
status
is_verified
verification_status
is_featured
rating_average
reviews_count
specialties
```

It intentionally excludes:

```text
phone
email
admin_note
submitted_at
approved_by
rejected_by
suspended_by
moderation notes
```

## Public Consultant APIs

```http
GET /api/v1/consultants/specialties
GET /api/v1/consultants
GET /api/v1/consultants/{id}
```

These endpoints are public.

Public consultant profiles expose profile metadata currently supported by the backend:

```text
display_name
name
title
bio
experience_years
province/city metadata
avatar_file_id
avatar_media_file_id
avatar_url
status
is_verified
verification_status
is_featured
rating_average
reviews_count
requests_count
completed_requests_count
specialties
```

Public consultant listing/detail returns approved, non-deleted profiles.

Privacy contract:

```text
Public consultant responses do not include phone, email, or admin_note.
Owner-only /me responses can include phone and email.
Admin responses can include admin_note and moderation timestamps.
```

## Consultant User APIs

```http
GET  /api/v1/consultants/me/profile
POST /api/v1/consultants/me/profile
PUT  /api/v1/consultants/me/profile
POST /api/v1/consultants/me/profile/submit

POST /api/v1/consultants/requests
GET  /api/v1/consultants/requests/me
GET  /api/v1/consultants/requests/{request_id}
GET  /api/v1/consultants/requests/assigned
GET  /api/v1/consultants/requests/assigned/{request_id}
PATCH /api/v1/consultants/requests/{request_id}/status
PATCH /api/v1/consultants/requests/{request_id}/cancel
```

Permissions:

```text
GET/POST/PUT /me/profile and submit: consultants.profile_manage
POST /requests: consult_requests.create
GET /requests/me: consult_requests.read_own
GET /requests/{id}: consult_requests.read_own and requester ownership
PATCH /requests/{id}/cancel: consult_requests.manage_own
GET /requests/assigned, GET /requests/assigned/{id}, and PATCH /requests/{id}/status: consult_requests.manage_assigned
```

Assigned workbench rules:

```text
The consultant role includes consult_requests.manage_assigned.
The assigned requests endpoints also require the current user to have an approved consultant profile.
Non-approved consultant profiles are rejected by the service layer.
```

Consult request detail contract:

```text
GET /consultants/requests/{request_id} returns only requests owned by the current requester.
GET /consultants/requests/assigned/{request_id} returns only requests assigned to the current approved consultant profile.
Detail responses include status_logs plus consultant and specialty summaries when available.
List responses may include the same fields, but mobile uses detail endpoints for the full status timeline.
```

Consultant-managed status transitions:

```text
open -> accepted | rejected
accepted -> in_progress | cancelled
in_progress -> completed | cancelled
```

## Admin Consultant APIs

```http
GET   /api/v1/admin/consultants
GET   /api/v1/admin/consultants/{profile_id}
PATCH /api/v1/admin/consultants/{profile_id}/status

GET   /api/v1/admin/consultants/specialties
POST  /api/v1/admin/consultants/specialties
PATCH /api/v1/admin/consultants/specialties/{specialty_id}

GET   /api/v1/admin/consultants/requests
GET   /api/v1/admin/consultants/requests/{request_id}
PATCH /api/v1/admin/consultants/requests/{request_id}/status
```

Admin profile moderation statuses:

```text
approved
rejected
suspended
```

Admin permissions:

```text
consultants.read
consultants.approve
consultants.reject
consultants.suspend
consult_specialties.read
consult_specialties.create
consult_specialties.update
consult_requests.read
consult_requests.manage
```

Admin request detail contract:

```text
GET /admin/consultants/requests/{request_id} requires consult_requests.read.
It returns the full consult request response, including consultant summary, specialty summary, admin_note, consultant_note, cancel metadata, and status_logs.
The admin panel uses this endpoint for request detail/moderation context before changing status.
```

## Postman Coverage

Canonical collections:

```text
postman/collections/social-expert.postman_collection.json
postman/collections/consultants.postman_collection.json
postman/collections/notifications.postman_collection.json
```
