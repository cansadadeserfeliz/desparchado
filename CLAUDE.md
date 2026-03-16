# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About the Project

Desparchado is a Django web application for discovering cultural and educational events in Colombian cities. The platform aggregates events from multiple sources (manual entry, Google Sheets imports, external scrapers) and presents them with filtering by city, category, and date.

**Stack**: Django, DRF, PostgreSQL (PostGIS), Vue.js 3, Vite, TypeScript, Gunicorn, Nginx

**Core entities:**
- **Event** — the main entity; belongs to a Place, has Organizers and Speakers
- **Place** — physical venue with a PostGIS `PointField` for geographic coordinates
- **City** — groups Places and is the primary filter for event lists
- **Organizer** — organization hosting events
- **Speaker** — person presenting at events
- **Special** — named collection of related events (festival, series, program)

**Key apps:**
- `desparchado/` — Django settings and root URL config
- `events/` — core domain logic and Event model
- `places/` — Place and City models, venue management
- `specials/` — Special groupings of events
- `dashboard/` — internal admin tools; all views must require `user.is_superuser`
- `users/` — custom user settings and quota system

## Commands

All commands run inside the Docker container `desparchado-web-1`.

```bash
make up           # Start Docker environment
make sh-web       # Open shell in web container
make test         # Run full test suite (pytest)
make lint         # Lint with ruff (--fix)
make migrate      # Apply database migrations
make pip-install  # Install Python dependencies
```

**Run a single test file:**
```bash
docker exec -it desparchado-web-1 sh -c "cd app && pytest events/tests/test_views.py"
```

**Run a single test by name:**
```bash
docker exec -it desparchado-web-1 sh -c "cd app && pytest -k test_event_list"
```

## Architecture

### Settings

Settings are split by environment under `desparchado/settings/`:
- `base.py` — shared config (PostGIS DB, allauth, axes, vite)
- `dev.py` — development overrides
- `production.py` — production overrides
- `test.py` — test overrides (used automatically by pytest)

### URL Structure

```
/                → events (homepage = future event list)
/events/         → events app (web views)
/events/api/v1/  → DRF REST API
/places/         → places app
/dashboard/      → superuser-only admin tools
/blog/           → blog app
/admin/          → Django admin
/swagger/        → API docs (drf-yasg)
/accounts/       → django-allauth authentication
```

### Event Visibility

An event has four boolean flags that control its state:
- `is_published` — set by contributors when ready
- `is_approved` — set by admins
- `is_featured_on_homepage` — promotes to homepage
- `is_hidden` — used for bulk imports (hides until reviewed)

The computed property `is_visible = is_published AND is_approved` determines whether an event appears publicly. QuerySet helpers: `.future()`, `.past()`, `.published()`.

### Permission Model

Content editing follows a consistent pattern across Event, Organizer, Speaker, and Place:
- `created_by` FK — the creating user
- `editors` M2M — additional users who can edit
- Superusers can edit/delete everything
- `can_edit(user)` method on each model checks these

Dashboard views enforce `is_superuser` via `SuperuserRequiredMixin`.

### User Quotas

`UserSettings` (auto-created via signal on user registration) enforces daily creation quotas:
- Events: 10/day, Organizers: 5/day, Speakers: 5/day, Places: 5/day

Superusers bypass all quotas.

### External Data Ingestion

Events from external sources carry a unique `source_id` field (e.g. `FILBO2025_123`) used for deduplication. Sources include:
- Google Sheets sync via the Dashboard (`SpreadsheetSyncFormView`)
- Management command scrapers (see `events/management/commands/`)

### Search

Full-text search is implemented in `events/services/` using PostgreSQL `SearchVector`/`SearchQuery` with `unaccent` support. Searches title, description, and speaker names. Requires minimum 3 characters.

### Frontend

Vue.js 3 + Vite integration via `django-vite`. The frontend dev server runs on port 5173. Templates use Django's template system; Vue components are embedded where interactivity is needed. Storybook is available for component development (`make run-storybook`).

- Vue 3 Composition API with `<script setup>` syntax
- Components mounted via `data-vue-component` attributes — see `desparchado/frontend/scripts/mount-vue.ts`
- All client-side HTTP calls live in `desparchado/frontend/scripts/api/`
- TypeScript strict mode; no `any` types

### Testing

- Uses pytest + pytest-django + django-webtest
- Test settings: `desparchado.settings.test`
- Test files live in `<app>/tests/test_*.py`
- All tests use `@pytest.mark.django_db` on standalone functions — no `TestCase` classes
- Model instances created via factory-boy — never `Model.objects.create()` directly
- View tests use the `django_app` fixture from pytest-webtest
- Shared fixtures in root `conftest.py`; per-app fixtures in `<app>/tests/conftest.py`
- Available factories: `EventFactory`, `UserFactory`, `PlaceFactory`, `CityFactory`, `OrganizerFactory`, `SpeakerFactory`, `SpecialFactory`

### Map Widget

The location `PointField` on Place and City uses `LeafletPointFieldWidget` from `django-map-widgets` (OpenStreetMap, no API key required). This applies in both forms (`places/forms.py`) and the Django admin (`places/admin.py`).

## Git Commits

A `commit-msg` hook at `.git/hooks/commit-msg` automatically prepends `[TYPE][TICKET]` to every commit message based on the branch name:
- Branch type is extracted from `feature`, `fix`, `hotfix`, or `refactor` in the branch name → uppercased
- Ticket number is extracted from `TAS-NNNNN` pattern in the branch name
- If either is absent, `NA` is used

**NEVER add the `[TYPE][TICKET]` prefix manually.** The hook adds it automatically. If you include it yourself, the message will have it duplicated (e.g. `[FIX][TAS-185] [FIX][TAS-185] ...`). Write only the plain description.

## Code Style

- Python 3.10+ with type hints required; no `Any` types
- Use early returns, avoid nested conditionals
- Prefer Class-Based Views
- Google-style docstrings with Args/Returns sections — omit these sections for Django overrides (e.g. `get_queryset`, `form_valid`)
- Primary language: Spanish (`es`), timezone: `America/Bogota`
