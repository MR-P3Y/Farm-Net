# Farm Net Social Community Foundation

This module adds the first foundation of the Farm Net community feature.

## Goal

The goal is to provide a safe, moderated, useful farmer community space inside Farm Net.

Users can:

- Read community posts
- Filter by category
- Create posts
- Add comments
- Add one-level replies
- React to posts/comments
- Bookmark posts
- Report bad content

Admins can:

- Review reports
- Change report status
- List posts
- Hide/unhide posts
- List comments
- Hide/unhide comments

## Design Decisions

### Feed

The current feed is newest-first.

A ranking algorithm is intentionally not included in this foundation.

Future versions may add:

- Helpful score
- Crop relevance
- Location relevance
- Expert answer boost
- Report penalty
- Admin pinning

### Moderation

Posts are published directly in MVP.

Moderation is handled by:

- User reports
- Admin report review
- Admin hide/unhide
- Soft delete for own content

This is acceptable for foundation, but production may need stronger moderation if social traffic grows.

### Replies

Only one-level replies are allowed.

Nested replies are rejected to keep UI and moderation simple.

### Media

Social posts can have one image through `media_file_id`.

Accepted media rules:

```text
purpose = social_post_image
visibility = public
status = active
owner_user_id = current user
```

Mobile create post image upload is not included yet. The API supports it, and feed/detail can display `media_public_url`.

### Notifications

Implemented social notifications:

```text
social.comment_created
social.reply_created
social.post_reported
social.comment_reported
social.post_hidden
social.comment_hidden
expert_answer_created
```

Reaction/bookmark notifications are intentionally skipped to avoid inbox noise.

### Expert Answers

Social post detail can include `expert_answers`:

```text
GET /api/v1/social/posts/{post_id}
```

Contract:

```text
expert_answers is detail-only and is not present on social post list responses.
Only published expert answers are returned.
Hidden/deleted expert answers are filtered by the backend.
consultant is nullable.
consultant summary is safe and excludes phone/email/admin_note.
```

## Database Tables

Social tables:

```text
social_categories
social_posts
social_comments
social_reactions
social_bookmarks
social_reports
social_moderation_actions
```

Related modules:

```text
media_files
notification_events
notifications
notification_delivery_logs
auth_permissions
auth_roles
auth_user_roles
```

## Backend Modules

```text
backend/app/modules/social/
  __init__.py
  enums.py
  models.py
  schemas.py
  repository.py
  service.py
  router.py
  admin_router.py
```

Related modules:

```text
backend/app/modules/media/
backend/app/modules/notifications/
backend/app/modules/auth/seed.py
backend/app/main.py
```

## Mobile Foundation

Mobile feature path:

```text
mobile/lib/features/social/
```

Implemented foundation:

- Feed screen
- Category chips
- Post detail screen
- Create post screen
- Comments
- Reply foundation
- Like post
- Bookmark post
- Report post
- Home entry
- Routes:
  - `/social`
  - `/social/create`
  - `/social/detail/:id`

Manual UI QA is still required.

## Admin Panel Foundation

Admin feature path:

```text
admin-panel/lib/features/social/
```

Implemented foundation:

- Social moderation page
- Reports tab
- Update report status
- Posts tab
- Hide/unhide post
- Comments tab
- Hide/unhide comment
- Sidebar entry
- Route:
  - `/social`

Manual UI QA is still required.

## Remaining Work

Before production release:

- Manual QA for mobile social screens
- Manual QA for admin social moderation page
- Better admin filters
- Better report detail view
- Better Persian labels for statuses/reasons
- Add image upload to mobile create post
- Add comment report UI in mobile
- Add comment reaction UI in mobile
- Improve empty/loading/error states
- Add integration tests for notification events
- Add pagination/infinite scroll
- Add abuse-rate limits for reports/comments/posts
- Add content length/rich validation if needed
- Add search and ranking later

## Release Readiness

Foundation is acceptable for merge/tag when:

```text
Backend compile/test/smoke: OK
Mobile analyze/test/build: OK
Admin analyze/test/build: OK
Docs/Postman: OK
Git status: clean
Manual QA note recorded
```
