# Universal Favorites API

Universal Favorites is an authenticated owner-private capability shared by
public Products, Stores, Service offers, Rental equipment, Consultants, and
Social posts. It replaces domain-specific client state while keeping legacy
Social bookmarks synchronized in both directions.

All paths use `/api/v1`, the standard response envelope, and the permissions
`favorites.read_own` or `favorites.manage_own`.

| Method and path | Purpose |
|---|---|
| `GET /favorites` | Paginated owner list, optionally filtered by `subject_type` |
| `GET /favorites/status/{subject_type}?subject_ids=...` | Batch card/detail status lookup, up to 100 IDs |
| `PUT /favorites/{subject_type}/{subject_id}` | Idempotently add a public subject |
| `DELETE /favorites/{subject_type}/{subject_id}` | Idempotently remove an owned favorite |

The owner list resolves current public title, subtitle, image, and internal
route. A subject that later becomes unavailable is retained as a private
tombstone with `is_available=false`, so the user can remove it without leaking
private or moderated data. Add rejects missing, inactive, unapproved, or
otherwise non-public subjects.

The Mobile app exposes one shared favorite button on every supported public
detail domain and a bilingual, theme-aware `/favorites` center. Saved dates use
the shared Jalali calendar in Persian and Gregorian calendar in English.

Migration `n26b2c3d4e5f` copies existing Social bookmarks exactly once and adds
the unique owner/subject constraint. Add/remove operations are idempotent and
the authenticated smoke test must cover add, list, remove, and logout.
