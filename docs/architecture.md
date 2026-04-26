# Architecture

Generated: 2026-04-06 | Scan level: exhaustive

## Executive Summary

Desparchado is a **Django monolith** that aggregates cultural and educational events in Colombian cities. It serves both server-rendered HTML pages (Django templates) and a minimal REST API consumed by co-located Vue.js 3 components. The application is deployed as a single Docker container (Gunicorn + Nginx) backed by PostgreSQL with the PostGIS extension for geographic data.

## Architecture Type

**Monolith with Embedded SPA Islands**

Django is responsible for all routing, authentication, permissions, business logic, and server-side rendering. Vue.js 3 components are mounted as isolated interactive islands on specific pages — they do not take over the entire page. Navigation between pages is handled by Django URL patterns and standard HTML links, not client-side routing.

## Application Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Browser / Client                     │
│  Django-rendered HTML + Vue 3 island components         │
└──────────────┬──────────────┬──────────────────────────-┘
               │ HTML pages   │ XHR (fetch)
               ▼              ▼
┌─────────────────────────────────────────────────────────┐
│               Django Application (Gunicorn)             │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Web Views  │  │  REST API    │  │  Dashboard    │  │
│  │  (CBVs)     │  │  (DRF)       │  │  (superuser)  │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                │                  │           │
│  ┌──────▼────────────────▼──────────────────▼───────┐   │
│  │              Services / QuerySets                 │   │
│  │  event_search.py | spreadsheet_sync.py | filbo   │   │
│  └─────────────────────────┬─────────────────────── ┘   │
│                             │                            │
│  ┌──────────────────────────▼─────────────────────────┐  │
│  │                    ORM / Models                    │  │
│  │  Event | Place | City | Organizer | Speaker | ...  │  │
│  └──────────────────────────┬─────────────────────── ┘  │
└─────────────────────────────┼───────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│          PostgreSQL + PostGIS (desparchado_dev)          │
└─────────────────────────────────────────────────────────┘
```

## Django App Structure

| App | Responsibility | Key models |
|---|---|---|
| `desparchado` | Root config, shared utils, homepage | — |
| `events` | Core event domain; CRUD, search, API | Event, Organizer, Speaker, SocialNetworkPost |
| `places` | Venue and city management | Place, City |
| `specials` | Named event collections | Special |
| `dashboard` | Superuser tools; spreadsheet imports | SpreadsheetSync |
| `users` | User profiles and quotas | UserSettings, UserEventRelation |
| `blog` | Blog articles | Post |
| `games` | "La caza del Snark" game | HuntingOfSnarkGame |
| `history` | Colombian cultural history timeline | HistoricalFigure, Event, Post, Group |
| `news` | Placeholder (no views yet) | — |
| `books` | Placeholder (empty) | — |

## URL Namespace Map

| Prefix | Namespace | App |
|---|---|---|
| `/` | — | Homepage (desparchado/views/home.py) |
| `/events/` | `events` | Events, Organizers, Speakers CRUD |
| `/events/api/v1/` | `events_api` | REST API |
| `/places/` | `places` | Places, Cities |
| `/specials/` | `specials` | Special collections |
| `/blog/` | `blog` | Blog posts |
| `/games/` | `games` | Hunting of Snark game |
| `/historia/` | `history` | Historical figures and timeline |
| `/dashboard/` | `dashboard` | Superuser internal tools |
| `/users/` | `users` | User profile and created-content lists |
| `/accounts/` | — | django-allauth authentication |
| `/admin/` | — | Django admin |
| `/swagger/` | — | API docs (admin-only) |
| `/sitemap.xml` | — | XML sitemap |
| `/rss/`, `/atom/` | — | Feed syndication |

## Event Visibility State Machine

An event has four independent boolean flags. The computed `is_visible` property is the gate for public display.

```
is_published (contributor) ──┐
                              ├─► is_visible = is_published AND is_approved
is_approved  (admin)     ────┘

is_featured_on_homepage ──► appears in HomeView featured section
is_hidden               ──► hidden from home (bulk import staging)
```

## Permission Architecture

### Content Editing (Event, Organizer, Speaker, Place)

```python
def can_edit(self, user):
    return user.is_superuser or user == self.created_by or user in self.editors.all()
```

Applied via `EditorPermissionRequiredMixin` on update views.

### Dashboard

```python
class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
```

All dashboard views inherit this mixin.

### API

DRF uses `DjangoModelPermissionsOrAnonReadOnly`: anonymous users can read; write operations require authentication and model-level Django permissions.

### Authentication Stack

1. `axes.backends.AxesStandaloneBackend` — brute-force protection (first in chain)
2. `desparchado.backends.EmailBackend` — custom email login
3. `django.contrib.auth.backends.ModelBackend` — standard Django admin login
4. `allauth.account.auth_backends.AuthenticationBackend` — allauth email auth

## User Quota System

`UserSettings` (auto-created via `post_save` signal on User) enforces daily creation limits:

| Resource | Default quota | Period |
|---|---|---|
| Events | 10 | 24 hours |
| Organizers | 5 | 24 hours |
| Speakers | 5 | 24 hours |
| Places | 5 | 24 hours |

Superusers bypass all quotas. Quota enforcement happens in the `dispatch()` method of create views (e.g., `EventCreateView`).

## Search Architecture

Full-text search is implemented in `events/services/event_search.py`:

1. **PostgreSQL `SearchVector`** on `title` and `description` (indexed full-text).
2. **`unaccent__icontains`** for title, description, and speaker names — handles accented characters in Colombian Spanish.
3. **`SearchQuery`** for ranked full-text matching.
4. Minimum 3-character threshold to avoid noise.
5. `.distinct()` to collapse duplicates from the speaker JOIN.

Speaker names are matched via `Q(speakers__name__unaccent__icontains=search_str)` rather than including them in the `SearchVector` (which would produce duplicate rows from the M2M join).

## External Data Ingestion

### Generic Google Sheets Sync (SpreadsheetSyncFormView)

`dashboard/services/spreadsheet_sync.py` — `sync_events()`:

- Reads rows from a configured Google Sheets range (columns A–J)
- Upserts events via `Event.objects.update_or_create()` using either `event_source_url` or `source_id` as the deduplication key
- Resolves organizers and speakers by name (case-insensitive)
- Downloads and attaches event images from URLs
- Links events to a configured `Special` if set
- Returns `list[RowProcessingResult]` for the dashboard UI to display

### FILBo-specific Sync (dashboard/services/filbo.py)

Dedicated importer for the Feria Internacional del Libro de Bogotá:

- Source ID format: `FILBO2026_<numeric_id>` (extracted from event URL `/descripcion-actividad/<id>/`)
- Category mapping from FILBo-specific categories to the platform's 5 categories
- Organizer resolution: canonical name mapping via worksheet 2 (FILBO_NAME → CANONICAL_NAME)
- Speaker resolution: whole-word regex matching against participants, title, and description fields
- Place resolution: all FILBo venues created as `<venue_name> | Corferias` at Corferias coordinates
- After sync: events with `FILBO2026_` prefix not in the current sheet are unpublished

## Frontend Architecture

### Vue Component Mounting

```
Django template
  └─ <div data-vue-component="event-card" data-vue-prop-title="..." ...>

mount-vue.ts (loads on DOMContentLoaded)
  └─ VueComponentMount.mountAll()
       └─ Finds all [data-vue-component] elements
       └─ Resolves component by kebab-case name
       └─ Extracts props from data-vue-prop-* attributes (JSON-parsed)
       └─ createApp(component, props).mount(el)
```

### Event List Widget (Homepage)

```
home.ts
  └─ EventContainer (registered by data-url attribute)
       └─ getEventList(url) → fetch /events/api/v1/events/future/
       └─ mapEventToCardProps(results)
       └─ createApp(EventsListApp, { events }).mount(el)
```

### SCSS / Styling

- Component-scoped SCSS files colocated with Vue components
- Global styles in `desparchado/frontend/styles/`
- BEM methodology enforced via the `bem()` utility
- Bootstrap 5 via crispy-forms for Django form rendering

## Deployment Architecture

```
Internet
   │
   ▼
Nginx (reverse proxy + static file serving)
   │
   ▼
Gunicorn (Django WSGI, multiple workers)
   │
   ├── Django app
   │     ├── media/ (user uploads)
   │     └── desparchado/static/dist/ (Vite build output)
   │
   ▼
PostgreSQL + PostGIS
```

Production host: `desparchado.co`

### Environment differences

| Setting | Development | Production |
|---|---|---|
| `DEBUG` | True | False |
| Email backend | Console or SES | AWS SES |
| Sentry | Disabled | Enabled (100% traces) |
| Analytics | Disabled | Umami enabled |
| Vite | Dev server (HMR) | Compiled manifest |
| Cache | LocMemCache | LocMemCache (no Redis) |

## Geographic Data

- `Place.location` and `City.center_location` use PostGIS `PointField` (SRID 4326 WGS84).
- Map widgets in forms use **Leaflet.js** (OpenStreetMap, no API key) via a custom `LeafletPointFieldWidget` in `places/widgets/leaflet.py`.
- Coordinate retrieval: `place.get_longitude_str()` / `place.get_latitude_str()` return string `x`/`y` values.
- Events expose `get_longitude_str()` and `get_latitude_str()` by delegating to their associated Place.

## Testing Strategy

- Unit/integration tests with pytest + pytest-django
- View tests use `django-webtest` (`django_app` fixture)
- All tests use `@pytest.mark.django_db`
- No `TestCase` classes — standalone function tests only
- Database reused between runs (`--reuse-db`)
- Factories via `factory-boy` for all model creation
- Mocking used sparingly; tests hit the real test database

## Key Architectural Decisions

1. **Monolith over microservices**: Single codebase simplifies deployment and development for a small team.
2. **Server-rendered HTML + Vue islands**: Progressive enhancement — the site works without JS; Vue adds interactivity where needed.
3. **PostGIS**: Enables future geo-filtering (e.g., events near a point). Currently used for map display.
4. **Source ID deduplication**: External events carry a `source_id` (e.g., `FILBO2026_12345`) to prevent duplicates across sync runs.
5. **No caching layer (Redis)**: Uses Django's `LocMemCache`. The event list city filter IDs are cached in memory for 24h.
6. **Email-only authentication**: No username login for end users; allauth handles the flow.
7. **Quota system**: Prevents abuse from anonymous bulk event creation while allowing superusers to bypass limits.
