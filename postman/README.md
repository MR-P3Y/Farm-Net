# Postman Collections

این پوشه شامل collectionهای تست API پروژه است.

هر ماژول Backend باید collection جدا داشته باشد:

- auth
- geo
- notification
- media
- verification
- billing
- finance
- store
- promotion

هر collection باید شامل سناریوهای موفق، خطا، permission denied و validation error باشد.

## Expert / Consultant Flow

The expert answer and consultant flow is covered by:

```text
postman/collections/social-expert.postman_collection.json
postman/collections/consultants.postman_collection.json
postman/collections/notifications.postman_collection.json
```

Use generic token variables only:

```text
access_token
expert_access_token
consultant_user_access_token
admin_access_token
```

The consultant collection covers the public privacy contract, owner profile management, user request creation/cancellation, approved-consultant assigned workbench, and admin moderation flows. Public consultant responses must not expose `phone`, `email`, or `admin_note`; use `/consultants/me/profile` or admin endpoints when those fields are expected.
