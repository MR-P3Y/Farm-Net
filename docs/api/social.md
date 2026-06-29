# Social / Community API

Farm Net Social Community Foundation provides public/user community APIs and admin moderation APIs.

Current foundation version: `v0.13.0-social-community-foundation`

## Scope

Implemented:

- Social categories
- Public feed
- Social post creation
- Post detail
- My posts
- Soft delete own post
- Comments
- One-level replies
- Post/comment reactions
- Bookmarks
- Reports
- Admin moderation
- Media image integration for social posts
- Notification integration
- Mobile social foundation
- Admin moderation foundation

Not implemented in this foundation:

- Private chat
- Private groups
- Follow/unfollow graph
- Ranking algorithm
- Advanced search
- Image upload from mobile social create screen
- Advanced moderation dashboard UX
- Manual QA pass for mobile/admin UI

---

## Permissions

### User/Public

| Permission | Purpose |
|---|---|
| `social.public_read` | Public social read access |
| `social.read` | User social read access |
| `social.post_create` | Create social posts |
| `social.post_manage_own` | Manage own posts |
| `social.comment_create` | Create comments and replies |
| `social.comment_manage_own` | Manage own comments |
| `social.react` | React to posts/comments |
| `social.bookmark` | Bookmark posts |
| `social.report` | Report posts/comments |

### Admin

| Permission | Purpose |
|---|---|
| `social.admin_read` | Read reports/posts/comments in admin panel |
| `social.admin_moderate` | Hide/unhide posts/comments and update reports |
| `social.admin_manage` | Reserved for future advanced social management |

---

## User/Public Endpoints

Base path:

```text
/api/v1/social
```

### Categories

```http
GET /api/v1/social/categories
```

Public endpoint.

Returns active social categories.

---

### List Posts

```http
GET /api/v1/social/posts?page=1&page_size=20
GET /api/v1/social/posts?category_id=1
GET /api/v1/social/posts?post_type=question
```

Public endpoint.

Returns published posts only.

Response note:

```text
The list response does not include expert_answers.
Expert answers are attached only to the post detail response.
```

---

### Create Post

```http
POST /api/v1/social/posts
Authorization: Bearer <access_token>
```

Required permission:

```text
social.post_create
```

Request:

```json
{
  "category_id": 1,
  "title": "مشکل زرد شدن برگ گندم",
  "body": "برگ‌های گندم من زرد شده‌اند. علت چیست؟",
  "post_type": "question",
  "visibility": "public",
  "media_file_id": null
}
```

Allowed `post_type`:

```text
question
experience
problem
guide
general
```

Allowed `visibility`:

```text
public
members
```

Media rule:

```text
media_file_id must point to a media file with:
purpose = social_post_image
visibility = public
status = active
owner_user_id = current user
```

Response includes:

```json
{
  "media_file_id": 18,
  "media_public_url": "..."
}
```

---

### Post Detail

```http
GET /api/v1/social/posts/{post_id}
```

Public endpoint.

Only published posts are visible.

This endpoint increments `views_count`.

The detail response may include expert answers:

```json
{
  "id": 11,
  "title": "مشکل زردی برگ گندم",
  "body": "...",
  "expert_answers": [
    {
      "id": 4,
      "answer_id": 4,
      "post_id": 11,
      "expert_user_id": 3,
      "expert_id": 3,
      "body": "پاسخ تخصصی...",
      "status": "published",
      "is_accepted": false,
      "accepted_at": null,
      "accepted_by_user_id": null,
      "helpful_count": 0,
      "reports_count": 0,
      "created_at": "...",
      "updated_at": "...",
      "deleted_at": null,
      "consultant": {
        "consultant_id": 2,
        "user_id": 3,
        "display_name": "نام مشاور",
        "name": "نام مشاور",
        "title": "متخصص تغذیه گیاه",
        "avatar_file_id": null,
        "avatar_media_file_id": null,
        "avatar_url": null,
        "status": "approved",
        "is_verified": true,
        "verification_status": "approved",
        "is_featured": false,
        "rating_average": 4.7,
        "reviews_count": 12,
        "specialties": []
      }
    }
  ]
}
```

Expert answer rules:

```text
Only published expert answers are returned.
Hidden/deleted expert answers are excluded by the backend.
consultant can be null when no approved public consultant profile is available.
The consultant summary is safe and does not expose phone, email, admin_note, or moderation-only fields.
```

---

### My Posts

```http
GET /api/v1/social/me/posts
Authorization: Bearer <access_token>
```

Required permission:

```text
social.read
```

---

### Delete Own Post

```http
DELETE /api/v1/social/posts/{post_id}
Authorization: Bearer <access_token>
```

Required permission:

```text
social.post_manage_own
```

Soft deletes the post.

---

## Comments / Replies

### List Comments

```http
GET /api/v1/social/posts/{post_id}/comments?page=1&page_size=100
```

Public endpoint.

Returns published comments only.

---

### Create Comment

```http
POST /api/v1/social/posts/{post_id}/comments
Authorization: Bearer <access_token>
```

Required permission:

```text
social.comment_create
```

Main comment:

```json
{
  "body": "به نظرم مشکل از کمبود نیتروژن است.",
  "parent_comment_id": null
}
```

Reply:

```json
{
  "body": "ممنون از راهنمایی.",
  "parent_comment_id": 12
}
```

Rules:

```text
Only one-level replies are allowed.
Reply to reply is rejected.
Self notification is prevented.
```

---

### Delete Own Comment

```http
DELETE /api/v1/social/comments/{comment_id}
Authorization: Bearer <access_token>
```

Required permission:

```text
social.comment_manage_own
```

Soft deletes the comment.

---

## Reactions

### React to Post

```http
POST /api/v1/social/posts/{post_id}/reactions
Authorization: Bearer <access_token>
```

Required permission:

```text
social.react
```

Request:

```json
{
  "reaction_type": "like"
}
```

Allowed reaction types:

```text
like
helpful
thanks
```

Duplicate reaction is idempotent and does not increase count twice.

---

### Remove Post Reaction

```http
DELETE /api/v1/social/posts/{post_id}/reactions/{reaction_type}
Authorization: Bearer <access_token>
```

---

### React to Comment

```http
POST /api/v1/social/comments/{comment_id}/reactions
Authorization: Bearer <access_token>
```

---

### Remove Comment Reaction

```http
DELETE /api/v1/social/comments/{comment_id}/reactions/{reaction_type}
Authorization: Bearer <access_token>
```

---

## Bookmarks

### Bookmark Post

```http
POST /api/v1/social/posts/{post_id}/bookmark
Authorization: Bearer <access_token>
```

Required permission:

```text
social.bookmark
```

Duplicate bookmark is idempotent.

---

### Remove Bookmark

```http
DELETE /api/v1/social/posts/{post_id}/bookmark
Authorization: Bearer <access_token>
```

---

### My Bookmarks

```http
GET /api/v1/social/me/bookmarks
Authorization: Bearer <access_token>
```

---

## Reports

### Report Post

```http
POST /api/v1/social/posts/{post_id}/report
Authorization: Bearer <access_token>
```

Required permission:

```text
social.report
```

Request:

```json
{
  "reason": "spam",
  "description": "این پست تبلیغاتی است."
}
```

Allowed reasons:

```text
spam
abuse
misinformation
advertisement
inappropriate
other
```

Creates admin notification:

```text
social.post_reported
```

---

### Report Comment

```http
POST /api/v1/social/comments/{comment_id}/report
Authorization: Bearer <access_token>
```

Creates admin notification:

```text
social.comment_reported
```

---

# Admin Social APIs

Base path:

```text
/api/v1/admin/social
```

Required permissions:

```text
social.admin_read
social.admin_moderate
```

---

## List Reports

```http
GET /api/v1/admin/social/reports?page=1&page_size=20
GET /api/v1/admin/social/reports?status=open
GET /api/v1/admin/social/reports?target_type=post
```

Required permission:

```text
social.admin_read
```

Allowed statuses:

```text
open
reviewed
dismissed
action_taken
```

Allowed target types:

```text
post
comment
```

---

## Update Report Status

```http
PATCH /api/v1/admin/social/reports/{report_id}/status
```

Required permission:

```text
social.admin_moderate
```

Request:

```json
{
  "status": "reviewed"
}
```

---

## List Posts

```http
GET /api/v1/admin/social/posts?page=1&page_size=20
GET /api/v1/admin/social/posts?status=published
GET /api/v1/admin/social/posts?post_type=question
```

Required permission:

```text
social.admin_read
```

---

## Hide Post

```http
PATCH /api/v1/admin/social/posts/{post_id}/hide
```

Required permission:

```text
social.admin_moderate
```

Request:

```json
{
  "reason": "محتوای نامناسب"
}
```

Creates notification for post author:

```text
social.post_hidden
```

---

## Unhide Post

```http
PATCH /api/v1/admin/social/posts/{post_id}/unhide
```

---

## List Comments

```http
GET /api/v1/admin/social/comments?page=1&page_size=20
GET /api/v1/admin/social/comments?status=published
GET /api/v1/admin/social/comments?post_id=1
```

Required permission:

```text
social.admin_read
```

---

## Hide Comment

```http
PATCH /api/v1/admin/social/comments/{comment_id}/hide
```

Creates notification for comment author:

```text
social.comment_hidden
```

---

## Unhide Comment

```http
PATCH /api/v1/admin/social/comments/{comment_id}/unhide
```

---

# Notification Events

Social notification events:

```text
social.comment_created
social.reply_created
social.post_reported
social.comment_reported
social.post_hidden
social.comment_hidden
expert_answer_created
```

Rules:

```text
No notification is sent when a user comments on their own post.
No notification is sent when a user replies to their own comment.
Reports notify admin/super_admin users.
Hide actions notify the content author.
expert_answer_created notifies the post owner when a published expert answer is created by another user.
```

---

# OpenAPI Expected Counts

As of Social Foundation:

```text
Social paths: 15
Social methods: 20
Admin Social paths: 8
Admin Social methods: 8
Notification endpoints: 5
Admin Notification endpoints: 3
Admin Expert paths: 3
```
