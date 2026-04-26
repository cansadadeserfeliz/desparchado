# Development Guide

Generated: 2026-04-06 | Scan level: exhaustive

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Docker | Any recent | Required for the full stack |
| docker-compose | v3.9+ | Included with Docker Desktop |
| Python | 3.14 | Only needed for IDE-level features; Docker runs the app |
| Node.js | LTS | Only needed outside Docker |

## Local Development Setup

All application code runs inside Docker. The following services are started together:

| Service | Port | Purpose |
|---|---|---|
| `web` | 8000 | Django dev server (Gunicorn in dev mode) |
| `frontend` | 5173 | Vite HMR dev server |
| `frontend` | 6006 | Storybook component explorer |
| `db` | 5032 | PostgreSQL + PostGIS |

### Start the stack

```bash
make up            # Build images and start all services
```

### Shell access

```bash
make sh-web        # Open shell in the web container
```

### Environment variables

The `web` service reads from `.env` at project root. Required variables:

| Variable | Example | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | `your-secret` | Django secret key |
| `DATABASE_NAME` | `desparchado_dev` | DB name |
| `DATABASE_USER` | `desparchado_dev` | DB user |
| `DATABASE_PASSWORD` | `secret` | DB password |
| `DATABASE_HOST` | `db` | Docker service name |
| `DATABASE_PORT` | `5432` | |
| `MAPBOX_ACCESS_TOKEN` | `not-set` | Optional; map widget |
| `AWS_SES_ACCESS_KEY_ID` | `not-set` | Optional; email |
| `AWS_SES_SECRET_ACCESS_KEY` | `not-set` | Optional; email |
| `SENTRY_CONFIG_DNS` | `not-set` | Optional; production only |

## Common Commands

All run inside `desparchado-web-1`:

```bash
make test          # Run full pytest suite
make lint          # Run ruff (with --fix)
make migrate       # Apply database migrations
make pip-install   # Install Python dependencies
```

### Run specific tests

```bash
# Single file
docker exec -it desparchado-web-1 sh -c "cd app && pytest events/tests/test_views.py"

# Single test by name
docker exec -it desparchado-web-1 sh -c "cd app && pytest -k test_event_list"
```

## Build Process

### Frontend (Vite)

The Vite dev server runs automatically in the `frontend` container with HMR. For production:

```bash
npm run build      # Outputs to desparchado/static/dist/
```

Build entry points (defined in `vite.config.js`):

| Entry | File | Loaded on |
|---|---|---|
| `mount_vue` | `scripts/mount-vue.ts` | All pages with Vue components |
| `main_styles` | `styles/index.scss` | All pages |
| `base` | `scripts/base.ts` | All pages |
| `events` | `scripts/events.ts` | Events list page |
| `events_details` | `scripts/event-details.ts` | Event detail page |
| `home` | `scripts/home.ts` | Homepage |
| `generic` | `scripts/generic.ts` | Generic pages |
| `allauth` | `scripts/allauth.js` | Auth pages |
| `dashboard` | `static/js/dashboard.js` | Dashboard (non-Vite legacy) |

### Python dependencies

Dependencies are managed with `pip-compile`:
- `requirements.in` → `requirements.txt` (production)
- `requirements-dev.in` → `requirements-dev.txt` (dev + test)

## Testing Approach

- **Framework:** pytest + pytest-django + django-webtest
- **Settings module:** `desparchado.settings.test`
- **DB strategy:** `--reuse-db` (reuses test DB between runs for speed)
- **Coverage:** `--cov=./` (collected automatically)
- **Factories:** factory-boy; never `Model.objects.create()` directly

### Test structure

```
<app>/tests/
├── conftest.py          # App-level fixtures (if needed)
├── factories.py         # Factory definitions
├── test_views.py        # View tests (or per-view files)
├── views/               # Per-view test files
│   └── test_event_list.py
├── api/
│   └── views/
│       └── test_event_list.py
└── services/
    └── test_event_search.py
```

Root `conftest.py` provides shared fixtures: `user`, `user_admin`, `event`, `place`, `city`, `organizer`, `speaker`, `special`, `blog_post`, `image`.

### Writing tests

```python
import pytest

@pytest.mark.django_db
def test_event_list(django_app, event):
    response = django_app.get('/events/')
    assert response.status_code == 200
```

## Code Style

- **Linter:** ruff (configured in `pyproject.toml`)
- **Line length:** 88
- **Python version target:** 3.14
- **Imports:** isort (enforced by ruff `I` rules)
- **Django conventions:** flake8-django `DJ` rules
- **Security:** bandit `S` rules (S101 asserts allowed in tests)
- **No print statements:** `T20` rule

### Frontend linting

```bash
npm run lint-scripts    # ESLint on .ts and .vue files
```

## Git Conventions

A `commit-msg` hook at `.git/hooks/commit-msg` prepends `[TYPE][TICKET]` automatically based on branch name:
- `feature/...` → `[FEATURE]`
- `fix/...` → `[FIX]`
- `TAS-12345` in branch name → `[TAS-12345]`

**Never write the `[TYPE][TICKET]` prefix manually** — the hook adds it. Writing it manually results in duplication.

## Storybook

```bash
make run-storybook      # Start Storybook at port 6006
```

Storybook config is in `desparchado/frontend/.storybook/`. Each component has a matching `.stories.ts` file in `desparchado/frontend/stories/`.

## Superuser Access (Dashboard)

The `/dashboard/` section requires `is_superuser=True`. To create a superuser in development:

```bash
docker exec -it desparchado-web-1 sh -c "cd app && python manage.py createsuperuser"
```

## Google Sheets Integration (Dashboard)

The spreadsheet sync features require a service account credentials file at `spreadsheet_credentials.json` in the project root. This file is not committed to the repository.