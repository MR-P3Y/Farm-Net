# Auth API Documentation
# مستندات API احراز هویت فارم نت

## Base URL

```text
http://localhost:8000/api/v1
```

## Standard Success Response

```json
{
  "success": true,
  "data": {},
  "message": "OK",
  "meta": {
    "trace_id": "..."
  }
}
```

## Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Invalid email, phone, or password",
    "details": {}
  },
  "meta": {
    "trace_id": "..."
  }
}
```

---

# 1. Register With Email

```http
POST /auth/register/email
```

## Body

```json
{
  "email": "user@example.com",
  "password": "Test@123456"
}
```

## Success

```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer",
    "user": {
      "id": 2,
      "email": "user@example.com",
      "phone": null,
      "status": "active",
      "is_email_verified": false,
      "is_phone_verified": false
    }
  },
  "message": "User registered successfully",
  "meta": {
    "trace_id": "..."
  }
}
```

## Errors

```text
AUTH_USER_ALREADY_EXISTS
VALIDATION_ERROR
```

---

# 2. Login With Email

```http
POST /auth/login/email
```

## Body

```json
{
  "email": "admin@example.com",
  "password": "change-me"
}
```

## Success

```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "admin@example.com",
      "phone": "989120000000",
      "status": "active",
      "is_email_verified": true,
      "is_phone_verified": true
    }
  },
  "message": "Login successful",
  "meta": {
    "trace_id": "..."
  }
}
```

## Errors

```text
AUTH_INVALID_CREDENTIALS
USER_SUSPENDED
AUTH_USER_NOT_FOUND
```

---

# 3. OTP Request

```http
POST /auth/otp/request
```

## Body

```json
{
  "phone": "09123456789",
  "purpose": "login"
}
```

## Success

```json
{
  "success": true,
  "data": {
    "phone": "989123456789",
    "expires_in_seconds": 120,
    "dev_code": "111111"
  },
  "message": "OTP requested successfully",
  "meta": {
    "trace_id": "..."
  }
}
```

## Notes

در محیط development، مقدار `dev_code` برمی‌گردد. در production این مقدار نباید به client داده شود.

## Errors

```text
VALIDATION_ERROR
```

---

# 4. OTP Verify

```http
POST /auth/otp/verify
```

## Body

```json
{
  "phone": "09123456789",
  "code": "111111",
  "purpose": "login"
}
```

## Success

```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer",
    "user": {
      "id": 4,
      "email": null,
      "phone": "989123456789",
      "status": "active",
      "is_email_verified": false,
      "is_phone_verified": true
    }
  },
  "message": "OTP verified successfully",
  "meta": {
    "trace_id": "..."
  }
}
```

## Errors

```text
AUTH_OTP_INVALID
AUTH_OTP_EXPIRED
AUTH_OTP_TOO_MANY_ATTEMPTS
```

---

# 5. Refresh Token

```http
POST /auth/refresh
```

## Body

```json
{
  "refresh_token": "..."
}
```

## Success

```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "admin@example.com",
      "phone": "989120000000",
      "status": "active",
      "is_email_verified": true,
      "is_phone_verified": true
    }
  },
  "message": "Token refreshed successfully",
  "meta": {
    "trace_id": "..."
  }
}
```

## Errors

```text
AUTH_TOKEN_INVALID
AUTH_TOKEN_EXPIRED
USER_SUSPENDED
```

---

# 6. Logout

```http
POST /auth/logout
```

## Body

```json
{
  "refresh_token": "..."
}
```

## Success

```json
{
  "success": true,
  "data": null,
  "message": "Logout successful",
  "meta": {
    "trace_id": "..."
  }
}
```

## Notes

بعد از logout، همان refresh token دیگر نباید قابل استفاده باشد.

## Expected Error After Logout

```text
AUTH_TOKEN_INVALID
```

---

# 7. Current User

```http
GET /auth/me
```

## Headers

```http
Authorization: Bearer <access_token>
```

## Success

```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "admin@example.com",
    "phone": "989120000000",
    "status": "active",
    "is_email_verified": true,
    "is_phone_verified": true,
    "roles": ["super_admin"],
    "permissions": ["users.read", "users.read_detail"]
  },
  "message": "OK",
  "meta": {
    "trace_id": "..."
  }
}
```

## Errors

```text
AUTH_TOKEN_INVALID
AUTH_TOKEN_EXPIRED
AUTH_USER_NOT_FOUND
```

---

# 8. Admin Users List

```http
GET /admin/users?page=1&page_size=20
```

## Headers

```http
Authorization: Bearer <admin_access_token>
```

## Required Permission

```text
users.read
```

## Success

```json
{
  "success": true,
  "data": [],
  "message": "OK",
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 6,
    "total_pages": 1,
    "trace_id": "..."
  }
}
```

## Query Params

```text
page
page_size
q
status
```

## Errors

```text
AUTH_TOKEN_INVALID
PERMISSION_DENIED
```

---

# 9. Admin User Detail

```http
GET /admin/users/{user_id}
```

## Required Permission

```text
users.read_detail
```

## Errors

```text
AUTH_TOKEN_INVALID
PERMISSION_DENIED
AUTH_USER_NOT_FOUND
```

---

# 10. Admin Update User Status

```http
PATCH /admin/users/{user_id}/status
```

## Required Permission

```text
users.update_status
```

## Body

```json
{
  "status": "suspended"
}
```

## Allowed Statuses

```text
pending
active
suspended
deleted
```

## Errors

```text
AUTH_TOKEN_INVALID
PERMISSION_DENIED
AUTH_USER_NOT_FOUND
VALIDATION_ERROR
```

---

# 11. Admin Roles

```http
GET /admin/roles
```

## Required Permission

```text
roles.read
```

## Expected Count

```text
12
```

---

# 12. Admin Permissions

```http
GET /admin/permissions
```

## Required Permission

```text
permissions.read
```

## Expected Count

```text
144
```

## Filter By Module

```http
GET /admin/permissions?module=users
```

Expected count for `users`:

```text
4
```

---

# Important Error Codes

```text
AUTH_USER_ALREADY_EXISTS
AUTH_INVALID_CREDENTIALS
AUTH_TOKEN_INVALID
AUTH_TOKEN_EXPIRED
AUTH_OTP_INVALID
AUTH_OTP_EXPIRED
AUTH_OTP_TOO_MANY_ATTEMPTS
USER_SUSPENDED
PERMISSION_DENIED
VALIDATION_ERROR
AUTH_USER_NOT_FOUND
```

---

# Manual Test Checklist

```text
register email موفق
register تکراری
login email موفق
login رمز اشتباه
otp request
otp verify موفق
otp verify اشتباه
refresh
logout
refresh بعد logout
auth/me
admin/users
admin/users/{id}
admin/users/{id}/status
admin/roles
admin/permissions
admin بدون token
admin بدون permission
```
