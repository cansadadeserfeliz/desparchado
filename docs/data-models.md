# Data Models

Generated: 2026-04-06 | Scan level: exhaustive

All models extend `TimeStampedModel` from `django-model-utils` (adds `created` and `modified` DateTimeFields) unless noted otherwise. Primary keys are auto-incremented integers unless noted.

---

## App: events

### Event

The core domain entity. Represents a cultural or educational event.

| Field | Type | Notes |
|---|---|---|
| `title` | CharField(255) | Required |
| `slug` | AutoSlugField | Unique; auto-generated from `title` |
| `description` | TextField | HTML content; sanitized on input |
| `category` | CharField(20, choices) | `literature`, `society`, `environment`, `science`, `art`; blank allowed |
| `event_date` | DateTimeField | Indexed |
| `event_source_url` | URLField(500) | Required; external event page URL |
| `price` | DecimalField(9,2) | Default 0; 0 = free |
| `image` | ImageField | Optional; `upload_to='events'` |
| `image_source_url` | URLField | Optional; attribution link |
| `organizers` | M2M → `Organizer` | Via `events.Organizer` |
| `place` | FK → `Place` | `on_delete=DO_NOTHING`; indexed |
| `speakers` | M2M → `Speaker` | Optional |
| `is_featured_on_homepage` | BooleanField | Default False |
| `is_published` | BooleanField | Default True; contributor-set |
| `is_approved` | BooleanField | Default True; admin-set |
| `is_hidden` | BooleanField | Default False; used during bulk imports |
| `created_by` | FK → User | `on_delete=DO_NOTHING` |
| `editors` | M2M → User | Additional edit-permitted users |
| `source_id` | CharField(50, unique, nullable) | External deduplication key (e.g. `FILBO2026_12345`) |

**Computed property:** `is_visible = is_published AND is_approved`

**QuerySet helpers:**
- `.future()` — events with `event_date >= now()`
- `.past()` — events with `event_date < now()`
- `.published()` — events where `is_published=True AND is_approved=True`

**Image fallback logic:** If no `image` is set, `get_image_url()` falls back to a static image based on the `source_id` prefix (e.g., `FILBO2025_` → `filbo-2025.jpg`).

---

### Organizer

An organization that hosts events.

| Field | Type | Notes |
|---|---|---|
| `name` | CharField(255, unique) | |
| `slug` | AutoSlugField | |
| `description` | TextField | Default '' |
| `website_url` | URLField | Optional |
| `facebook_url` | URLField | Optional |
| `twitter_url` | URLField | Optional |
| `instagram_url` | URLField | Optional |
| `image` | ImageField | Optional; `upload_to='organizers'` |
| `image_source_url` | URLField | Optional |
| `created_by` | FK → User | |
| `editors` | M2M → User | |

---

### Speaker

A person presenting at events.

| Field | Type | Notes |
|---|---|---|
| `name` | CharField(255, unique) | |
| `slug` | AutoSlugField | Nullable (legacy) |
| `description` | TextField | Default '' |
| `image` | ImageField | Optional; `upload_to='speakers'` |
| `image_source_url` | URLField | Optional |
| `created_by` | FK → User | |
| `editors` | M2M → User | |

---

### SocialNetworkPost

A scheduled social media post linked to an event.

| Field | Type | Notes |
|---|---|---|
| `event` | FK → Event | `on_delete=DO_NOTHING` |
| `description` | TextField | Post copy |
| `published_at` | DateTimeField | Must be ≤ `event.event_date`; cannot be >30 min in the past |
| `created_by` | FK → User | |

**Validation:** `clean()` enforces that `published_at` is not in the past and does not exceed `event_date`.

---

## App: places

### Place

A physical venue where events occur.

| Field | Type | Notes |
|---|---|---|
| `name` | CharField(255, unique) | MinLength 5; indexed |
| `slug` | AutoSlugField | Nullable (legacy) |
| `image` | ImageField | Optional; `upload_to='places'` |
| `image_source_url` | URLField | Optional |
| `address` | CharField(100) | MinLength 5 |
| `website_url` | URLField | Optional |
| `location` | PostGIS PointField | Required; geographic coordinates |
| `city` | FK → City | `on_delete=DO_NOTHING`; nullable |
| `created_by` | FK → User | |
| `editors` | M2M → User | |

---

### City

Groups places; primary filter for event discovery.

| Field | Type | Notes |
|---|---|---|
| `name` | CharField(255, unique) | Indexed |
| `slug` | AutoSlugField | Nullable |
| `image` | ImageField | Optional |
| `image_source_url` | URLField | Optional |
| `description` | TextField | Optional |
| `center_location` | PostGIS PointField | Required; center coordinates for map |

---

## App: specials

### Special

A named collection of related events (e.g., a festival, series, or program).

| Field | Type | Notes |
|---|---|---|
| `title` | CharField(255) | |
| `subtitle` | CharField(500) | Default '' |
| `slug` | AutoSlugField | |
| `is_published` | BooleanField | Default True |
| `is_featured_on_homepage` | BooleanField | Default False |
| `featured_on_homepage_until` | DateTimeField | Optional; nil = show indefinitely |
| `image` | ImageField | Optional; `upload_to='specials'` |
| `related_events` | M2M → Event | |
| `description` | TextField | Default '' |

**Property:** `events` returns only published events from `related_events`.

---

## App: dashboard

### SpreadsheetSync

Defines configuration for importing events from a Google Sheets spreadsheet.

| Field | Type | Notes |
|---|---|---|
| `title` | CharField(255) | Display name |
| `spreadsheet_id` | CharField(255) | Google Sheets document key |
| `worksheet_number` | IntegerField | Zero-based worksheet index; default 0 |
| `event_id_field` | CharField(choices) | `event_source_url` or `source_id`; determines deduplication key |
| `special` | FK → Special | Optional; newly synced events are added to this Special |
| `is_hidden` | BooleanField | If True, synced events have `is_hidden=True` (hidden from home, pending review) |

**Unique constraint:** `(spreadsheet_id, worksheet_number)`

---

## App: users

### UserSettings

Per-user quotas for content creation. Auto-created by a `post_save` signal on User.

| Field | Type | Notes |
|---|---|---|
| `user` | OneToOneField → User (PK) | Cascade delete |
| `event_creation_quota` | PositiveIntegerField | Default 10 |
| `organizer_creation_quota` | PositiveIntegerField | Default 5 |
| `speaker_creation_quota` | PositiveIntegerField | Default 5 |
| `place_creation_quota` | PositiveIntegerField | Default 5 |
| `quota_period_seconds` | PositiveIntegerField | Default 86400 (1 day) |

**Methods:** `reached_event_creation_quota()`, `reached_place_creation_quota()`, etc. — all return `False` for superusers.

---

### UserEventRelation

Tracks per-user interactions with events.

| Field | Type | Notes |
|---|---|---|
| `user` | FK → User | |
| `event` | FK → Event | |
| `is_bookmarked` | BooleanField | Default False |
| `is_visited` | BooleanField | Default False |

**Unique constraint:** `(user, event)`

---

## App: blog

### Post

A blog article on the platform.

| Field | Type | Notes |
|---|---|---|
| `title` | CharField(255) | |
| `subtitle` | CharField(255) | Default '' |
| `slug` | AutoSlugField | |
| `header_image` | ImageField | Optional; `upload_to='posts'` |
| `content` | TextField | Default '' |
| `is_published` | BooleanField | Default True |
| `is_approved` | BooleanField | Default True |
| `created_by_desparchado` | BooleanField | If True, `get_author_name()` returns `'desparchado.co'` |
| `created_by` | FK → User | |
| `related_events` | M2M → Event | Optional |

**QuerySet helper:** `.published()` filters `is_published=True AND is_approved=True`.

---

## App: games

### HuntingOfSnarkGame

A book-reading bingo game session.

| Field | Type | Notes |
|---|---|---|
| `token` | CharField(255, unique) | UUID hex; used in URLs instead of PK |
| `player_name` | CharField(255) | Optional display name |
| `total_points` | IntegerField | 1–50; number of books to read |
| `criteria` | M2M → HuntingOfSnarkCriteria | Selected reading criteria |
| `extra` | JSONField | Default `{}` |

### HuntingOfSnarkCriteria

A single reading criterion (e.g., "a book by a Colombian author").

| Field | Type | Notes |
|---|---|---|
| `public_id` | PositiveIntegerField(unique) | Stable identifier |
| `name` | CharField(500, unique) | Description of the criterion |
| `category` | FK → HuntingOfSnarkCategory | |

### HuntingOfSnarkCategory

Groups criteria into thematic categories.

| Field | Type | Notes |
|---|---|---|
| `name` | CharField(500, unique) | |
| `order` | FloatField | Nullable; controls display order |

---

## App: history

A standalone timeline/biography feature for Colombian cultural history.

### HistoricalFigure

A notable person in Colombian history.

| Field | Type | Notes |
|---|---|---|
| `token` | UUIDField(unique) | URL identifier |
| `name` | CharField(255) | Short name |
| `full_name` | CharField(500) | Optional full name |
| `description` | TextField | |
| `labels` | ArrayField(CharField(15)) | Tags/categories |
| `sources` | TextField | Citation text |
| `image` | ImageField | Optional |
| `date_of_birth` | DateTimeField | Indexed |
| `date_of_birth_precision` | CharField | `year`, `month`, `day`, `hour`, `minute` |
| `date_of_death` | DateTimeField | Nullable; indexed |
| `date_of_death_precision` | CharField | Same choices |
| `created_by` | FK → User | |

### history.Event

A historical event (distinct from `events.Event`).

| Field | Type | Notes |
|---|---|---|
| `token` | UUIDField(unique) | URL identifier |
| `title` | CharField(500) | |
| `description` | TextField | |
| `event_date` | DateTimeField | Indexed |
| `event_date_precision` | CharField | |
| `event_end_date` | DateTimeField | Optional |
| `location_name` | CharField(500) | Free-text location |
| `historical_figures` | M2M → HistoricalFigure | |
| `created_by` | FK → User | |

### history.Post

A social-feed-style post attributed to a historical figure (quote, travel, marriage, loss).

| Field | Type | Notes |
|---|---|---|
| `token` | UUIDField(unique) | |
| `type` | CharField(15, choices) | `quote`, `Travel`, `marriage`, `loss` |
| `text` | TextField | |
| `post_date` | DateTimeField | Optional; indexed |
| `post_date_precision` | CharField | |
| `historical_figure` | FK → HistoricalFigure | Author (nullable) |
| `historical_figure_mentions` | M2M → HistoricalFigure | Mentioned figures |
| `published_in_groups` | M2M → Group | |
| `created_by` | FK → User | |

### history.Group

A group of historical figures (e.g., a literary movement).

| Field | Type | Notes |
|---|---|---|
| `token` | UUIDField(unique) | |
| `title` | CharField(500) | |
| `description` | TextField | |
| `image` | ImageField | Optional |
| `members` | M2M → HistoricalFigure | |
| `created_by` | FK → User | |

---

## Model Relationship Summary

```
User ──────────┬── created_by ──► Event ──► Place ──► City
               │                    │
               │               organizers ──► Organizer
               │               speakers   ──► Speaker
               │               specials   ──► Special
               │               social_posts ► SocialNetworkPost
               │
               ├── UserSettings (1:1)
               └── UserEventRelation ──► Event

SpreadsheetSync ──► Special (optional)
```

---

## Permission Pattern (Content Editing)

Applied consistently on `Event`, `Organizer`, `Speaker`, and `Place`:

- `created_by` FK — the creating user owns the object
- `editors` M2M — additional users with edit access
- `can_edit(user)` method: returns `True` if `user.is_superuser`, `user == created_by`, or `user in editors`