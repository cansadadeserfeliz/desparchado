---
project_name: 'desparchado'
user_name: 'Vera'
date: '2026-04-06'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

**Runtime**
- Python 3.14 (authoritative: `production-deploy/docker-containers/web/Dockerfile`)
- All development runs inside Docker; use `docker-compose` locally, never a bare venv

**Backend**
- Django + Django REST Framework
- PostgreSQL + PostGIS — use `django.contrib.gis.db.models.PointField` (not the plain
  `django.db` one); requires `django.contrib.gis` in INSTALLED_APPS and
  `django.contrib.gis.db.backends.postgis` as the DB engine
- django-allauth (authentication)
- django-axes (brute-force protection)
- `places/widgets/googlemap.py` — standalone `GoogleMapPointFieldWidget`; do NOT install
  or import from `mapwidgets`; configure via `settings.MAP_WIDGETS["GoogleMap"]`
- django-vite (Django ↔ Vite integration)

**Frontend**
- Vue.js 3 — Composition API, `<script setup>` only
- TypeScript 5.4.0 — strict mode, no `any` types
- Vite 6.4.1 — dev server on port 5173, static output to `desparchado/static/dist/`
- Sass 1.87.0
- Two asset roots — new code goes in `desparchado/frontend/`; legacy TypeScript lives in
  `desparchado/static/ts/` (do not add new features there)

**Testing**
- Python: pytest + pytest-django + **django-webtest** + **factory-boy**
  - View tests use the `django_app` fixture (webtest), not Django's test client
  - Model instances created via factories only — never `Model.objects.create()`
- Frontend: Vitest and Playwright are in `package.json` but NOT configured or used;
  do not generate config files or test scaffolding for them without being asked
- Storybook 8.6.17 — the only active frontend testing surface

**Code Quality**
- ruff — Python linting + formatting, line length 88, target py314
- ESLint 9.25.1 + Prettier 3.5.3 — TypeScript/Vue

---

## Critical Implementation Rules

### Python Rules

- Type hints required on all function signatures; no `Any` type
- Use early returns to avoid nested conditionals
- `from __future__ import annotations` is NOT used — avoid it
- Google-style docstrings with Args/Returns sections; omit those sections for
  Django overrides (`get_queryset`, `form_valid`, `dispatch`, etc.)
- Ruff rules in force include: `DJ` (Django conventions), `PTH` (use pathlib over
  os.path), `T20` (no print statements), `S` (bandit security), `ASYNC`
- `assert` is allowed in tests (S101 suppressed); forbidden in production code

### TypeScript / Vue Rules

- Strict mode is on — no implicit `any`, no type assertions to bypass the compiler
- All Vue components use `<script lang="ts" setup>` — no Options API, no class components
- Props defined with `defineProps<InterfaceName>()` using a typed interface
- Path aliases in use: `@presentational_components/`, `@styles/`, `@assets/`, `@fonts/`
  — always use aliases, never relative `../../` traversal into those directories
- All client-side HTTP calls live in `desparchado/frontend/scripts/api/`; do not
  inline fetch calls inside components
- Interfaces for API responses live in `desparchado/frontend/scripts/api/interfaces.ts`
- BEM methodology for CSS class names; use the `bem()` utility from
  `desparchado/frontend/scripts/utils/bem.ts`
- Component styles imported directly in the component script block (`import './styles.scss'`)

### Django Rules

**Project structure**
- Views are split into individual files per view class:
  `<app>/views/<action>.py` (e.g. `events/views/event_list.py`) — do not add new
  views to a monolithic `views.py`
- Business logic lives in `<app>/services/` — not in views or models
- Settings are split by environment: `desparchado/settings/base.py`,
  `dev.py`, `production.py`, `test.py` — never create a single `settings.py`

**Models & QuerySets**
- Content models (`Event`, `Organizer`, `Speaker`, `Place`) all carry:
  `created_by` (FK to user) and `editors` (M2M to users)
- Permission check: `can_edit(user)` method — use it, don't inline the logic
- Event visibility: `is_published AND is_approved` = visible; use `.published()`
  QuerySet helper; never filter by those flags manually
- Use `.future()` / `.past()` QuerySet helpers on Event — don't write date filters
  from scratch
- External events carry a `source_id` field for deduplication — always set it
  when importing from external sources

**Views**
- Prefer Class-Based Views; only use function-based views for trivial one-liners
- All dashboard views must inherit `SuperuserRequiredMixin` — never rely solely
  on `@login_required` or `is_staff` checks for the dashboard app

**User quotas**
- `UserSettings` is auto-created via signal on registration; superusers bypass all
  quotas — do not check quotas for superusers

### Vue / Frontend Rules

**Component mounting**
- Vue components are mounted from Django templates via `data-vue-component` attributes
- Props are passed as `data-vue-prop-<propName>` attributes (JSON-serialized)
- `mount-vue.ts` auto-discovers all `.vue` files under `@presentational_components/`
  by glob — placing a new component there registers it automatically; no manual
  registration needed

**Component location**
- Presentational / reusable components → `desparchado/frontend/components/presentational/`
- Each component lives in its own folder with `ComponentName.vue` + `styles.scss`

### Testing Rules

**Python test structure**
- All test functions use `@pytest.mark.django_db` — no `TestCase` classes
- View tests use the `django_app` fixture (pytest-webtest) — not Django's test client
- Service tests live in `<app>/tests/services/test_<module>.py`
- Test files elsewhere follow `<app>/tests/test_<subject>.py`
- Shared fixtures in root `conftest.py`; app-specific fixtures in
  `<app>/tests/conftest.py`

**Factories (critical)**
- NEVER use `Model.objects.create()` in tests — always use factory-boy
- Available factories: `EventFactory`, `UserFactory`, `PlaceFactory`,
  `CityFactory`, `OrganizerFactory`, `SpeakerFactory`, `SpecialFactory`
- Import factories from their app: e.g. `from events.tests.factories import EventFactory`
- `EventFactory` defaults: `is_published=True`, `is_approved=True`,
  `is_featured_on_homepage=True`, future `event_date` — override explicitly when
  testing unpublished/unapproved/past states
- Factories use `django_get_or_create` on name fields — be aware duplicate names
  return existing records

**Test settings**
- Settings module: `desparchado.settings.test` (set automatically by pytest)
- `--reuse-db` is on by default — run with `--create-db` when changing models

**Commands**
- Full suite: `docker exec -it desparchado-web-1 sh -c "cd app && pytest"`
- Single file: `docker exec -it desparchado-web-1 sh -c "cd app && pytest <path>"`
- By name: `docker exec -it desparchado-web-1 sh -c "cd app && pytest -k <name>"`

### Code Quality & Style Rules

**Python**
- Line length: 88 (ruff enforced)
- Import order managed by ruff (`I` ruleset) — do not manually sort imports
- No `os.path` — use `pathlib` (`PTH` ruleset)
- No `print()` statements in production code (`T20` ruleset)
- Use f-strings over `.format()` or `%` formatting (`FLY` ruleset)
- Trailing commas required in multi-line collections (`COM` ruleset)
- `migrations/` is excluded from ruff — do not hand-edit migration style

**TypeScript / Vue**
- Prettier enforces formatting — do not configure competing formatters
- ESLint `eslint-plugin-vue` is active — follow Vue 3 specific lint rules
- No barrel `index.ts` re-exports — import directly from the component file

**Naming**
- Python: `snake_case` for files, functions, variables; `PascalCase` for classes
- Vue components: `PascalCase` filename and folder (e.g. `EventCard/EventCard.vue`)
- TypeScript interfaces prefixed with `I` (e.g. `IEvent`, `IApiPaginatedResponse`)
- CSS: BEM (`block__element--modifier`) via the `bem()` utility

**Comments & docs**
- Google-style docstrings on Python functions/classes
- Omit Args/Returns in Django method overrides (`get_queryset`, `form_valid`, etc.)
- Only comment where logic is non-obvious — do not narrate what the code does

### Development Workflow Rules

**Git & commits**
- Branch naming drives the commit hook: type extracted from `feature`, `fix`,
  `hotfix`, `refactor`; ticket from `TAS-NNNNN` pattern
- The `commit-msg` hook at `.git/hooks/commit-msg` auto-prepends `[TYPE][TICKET]`
  — NEVER write this prefix manually; doing so duplicates it
  (e.g. `[FIX][NA] [FIX][NA] message`)
- Write only the plain description in commit messages
- Main branch for PRs: `development` (not `main`)

**Docker commands**
- `make up` — start Docker environment
- `make sh-web` — open shell in web container (`desparchado-web-1`)
- `make test` — run full test suite
- `make lint` — ruff with `--fix`
- `make migrate` — apply migrations
- `make pip-install` — install Python dependencies

**Frontend dev**
- `npm run start` — Vite dev server (port 5173)
- `npm run build` — production build to `desparchado/static/dist/`
- `npm run storybook` — Storybook on port 6006
- `npm run lint-scripts` — ESLint on `.ts` and `.vue` files

### Critical Don't-Miss Rules

**Anti-patterns — never do these**
- Never use `Model.objects.create()` in tests — use factories
- Never filter events by `is_published`/`is_approved` directly — use `.published()`
- Never write `[TYPE][TICKET]` in commit messages — the hook does it
- Never add new views to a monolithic `views.py` — use per-view files
- Never put business logic in views or models — use `<app>/services/`
- Never import from `mapwidgets` — use `places/widgets/googlemap.py` directly
- Never use Django's test client in view tests — use `django_app` (webtest)
- Never add new frontend features to `desparchado/static/ts/` — use `desparchado/frontend/`
- Never use `any` type in TypeScript
- Never use the Options API or class components in Vue

**Security**
- Dashboard views must use `SuperuserRequiredMixin` — `is_staff` alone is not enough
- django-axes is active — do not bypass or disable login throttling in tests
  without understanding the impact
- No secrets in code — Google Maps API key read from `settings.GOOGLE_MAPS_API_KEY`

**PostGIS gotchas**
- `libgdal-dev` must be installed in the OS layer (it's in the Dockerfile) — any
  new environment setup must include it
- Always use `django.contrib.gis.db.models.PointField`, never `django.db.models.PointField`

**User quotas**
- `UserSettings` is created by signal — never create it manually
- Superusers bypass all quotas; tests using `UserFactory(is_superuser=True)` will
  not hit quota limits

**External data imports**
- Always set `source_id` on externally imported events (format: `SOURCENAME_id`)
- Use `source_id` for upsert deduplication, never title matching

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code in this project
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- The production Dockerfile is authoritative for runtime environment

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack or project conventions change
- Remove rules that become obvious over time

_Last updated: 2026-04-06_