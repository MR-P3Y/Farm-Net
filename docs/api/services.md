# Services API

The Services module implements the operational-services marketplace request
workflow. It does not cover payment, commission, invoices, chat, reviews,
mobile UI, or admin-panel UI.

## Request roles and privacy

All paths use the `/api/v1` prefix and the standard
`success/data/message/meta` response envelope.

| Role | List | Detail and mutation | Ownership |
|---|---|---|---|
| Requester | `GET /services/requests/me` | `POST /services/requests`, `GET /services/requests/{id}`, `PATCH /services/requests/{id}/cancel` | Own requests only |
| Approved provider | `GET /services/requests/assigned` | `GET /services/requests/assigned/{id}`, `PATCH /services/requests/{id}/status` | Assigned provider profile only |
| Admin | `GET /admin/services/requests` | `GET /admin/services/requests/{id}`, `PATCH /admin/services/requests/{id}/status` | Permission-controlled platform scope |

Requester list items intentionally omit description, contact method, address,
coordinates, notes, cancel reason, and status logs. Provider list items add the
requester ID and coarse province/city names. Admin list items additionally
include contact method. Full operational fields are returned only by authorized
detail endpoints. `admin_note` is exclusive to the admin detail contract.

Status logs are ordered oldest-first and expose exactly:
`id`, `request_id`, `changed_by_user_id`, `old_status`, `new_status`, `note`,
and `created_at`.

## Workflow

- Initial status: `open`.
- Provider: `open -> accepted|rejected`, `accepted -> in_progress`,
  `in_progress -> completed`.
- Requester cancel: only from `open` or `accepted`.
- Admin: the explicit transition table enforced by the service layer.
- Same-status, invalid, and terminal transitions are rejected before a status
  log or notification is written.

## Notifications

In-app events are emitted atomically with request changes:

- `service_request.created`
- `service_request.accepted`
- `service_request.rejected`
- `service_request.in_progress`
- `service_request.completed`
- `service_request.cancelled`

Stable event keys make each request transition idempotent. A recipient receives
at most one in-app notification for an event, duplicate recipient IDs are
collapsed, and the actor is excluded. Payloads contain identifiers, titles, and
old/new status only; contact, address, coordinates, and notes are excluded.

