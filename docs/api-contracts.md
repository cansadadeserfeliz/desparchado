# API Contracts

Generated: 2026-04-06 | Scan level: exhaustive

Base path: `/events/api/v1/`  
Auth: `DjangoModelPermissionsOrAnonReadOnly` — unauthenticated users get read-only access.  
Pagination: `LimitOffsetPagination`, default page size 10.  
Interactive docs: `/swagger/` (admin-only) and `/redoc/`.

---

## GET /events/api/v1/events/

Returns all published events (past and future), paginated.

### Query parameters

| Parameter | Type | Notes |
|---|---|---|
| `place__city__slug` | string | Filter by city slug (e.g. `bogota`) |
| `ordering` | string | Field to order by. Allowed: `event_date`, `-event_date` |
| `limit` | int | Page size |
| `offset` | int | Pagination offset |

### Response

```json
{
  "count": 142,
  "next": "/events/api/v1/events/?limit=10&offset=10",
  "previous": null,
  "results": [
    {
      "title": "Presentación del libro X",
      "slug": "presentacion-del-libro-x",
      "url": "/events/presentacion-del-libro-x/",
      "event_date": "2026-04-10T18:00:00Z",
      "formatted_hour": "13:00",
      "formatted_day": "10 Apr",
      "place": {
        "name": "Biblioteca Luis Ángel Arango",
        "slug": "biblioteca-luis-angel-arango"
      },
      "image_url": "/static/images/default_event_image.jpg",
      "description": "<p>Full HTML description...</p>",
      "truncated_description": "Truncated to 50 words...",
      "is_recurrent": false
    }
  ]
}
```

### Notes

- `formatted_hour` and `formatted_day` are localized to `America/Bogota`.
- `image_url` falls back to a static default image if the event has no uploaded image. Source-specific fallbacks exist for events with known `source_id` prefixes (`FILBO2025_`, `FILBO2026_`, `FLCM2025_`, `PEREIRAFIL_25`).
- `is_recurrent` always returns `false` (reserved for future use).
- `description` is full HTML; `truncated_description` is HTML truncated to 50 words.

---

## GET /events/api/v1/events/future/

Returns only **future** published events that are **not hidden** (`is_hidden=False`), paginated.

### Query parameters

Same as `/events/api/v1/events/`. Filtering and ordering are inherited.

### Response

Same schema as `/events/api/v1/events/`.

### Notes

- This is the endpoint consumed by the Vue.js `EventContainer` component on the homepage to render the interactive event list.
- Excludes events with `is_hidden=True` (bulk-imported events pending review).
- Always selects related `place` and `place.city` to avoid N+1 queries.

---

## Internal / RSS Feeds

These are not REST API endpoints but are used programmatically.

| URL | Format | Description |
|---|---|---|
| `/rss/` | RSS 2.0 | All published future events feed (for social networks) |
| `/atom/` | Atom | Same content, Atom format |
| `/sitemap.xml` | XML | Sitemap covering events, places, posts, speakers, specials, history |

---

## Autocomplete Endpoints (DAL / Select2)

These endpoints power the Select2 widgets in event and place forms. They require authentication.

| URL | Name | Returns |
|---|---|---|
| `/events/organizers-autocomplete/` | `events:organizer_autocomplete` | Organizer name/id matches |
| `/events/speaker-autocomplete/` | `events:speaker_autocomplete` | Speaker name/id matches |
| `/events/organizers-suggestions/` | `events:organizer_suggestions` | Suggestions for new events |
| `/places/place-autocomplete/` | `places:place_autocomplete` | Place name/id matches |

---

## Authentication Endpoints

Managed by `django-allauth` at `/accounts/`:

| URL | Action |
|---|---|
| `/accounts/login/` | Email + password login |
| `/accounts/signup/` | Registration (email + password) |
| `/accounts/logout/` | Logout |
| `/accounts/email/` | Email management |
| `/accounts/password/change/` | Password change |
| `/accounts/confirm-email/<key>/` | Email confirmation |

---

## Admin API (Django Admin)

Available at `/admin/` for staff/superuser users. Registered models include all core entities.

---

## Serializer Reference

### EventSerializer

Fields: `title`, `slug`, `url`, `event_date`, `formatted_hour`, `formatted_day`, `place` (nested PlaceSerializer), `image_url`, `description`, `truncated_description`, `is_recurrent`

### PlaceSerializer (nested)

Fields: `name`, `slug`