---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-05-31'
inputDocuments:
  - _bmad-output/planning-artifacts/prd-event-creation-ux.md
  - _bmad-output/planning-artifacts/product-brief-event-creation-ux.md
  - _bmad-output/planning-artifacts/product-brief-event-creation-ux-distillate.md
  - _bmad-output/planning-artifacts/research/technical-vue-vs-vanilla-fe-django-drf-research-2026-04-05.md
  - _bmad-output/project-context.md
  - docs/index.md
  - docs/architecture.md
  - docs/data-models.md
  - docs/api-contracts.md
  - docs/source-tree.md
  - docs/component-inventory.md
  - docs/technology-stack.md
  - docs/development-guide.md
workflowType: 'architecture'
project_name: 'desparchado'
user_name: 'Vera'
date: '2026-05-31'
---

# Architecture Decision Document — Event Creation & Editing UX

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (44 total):**

| Category | FRs | Architectural Implication |
|---|---|---|
| Wizard navigation & layout | FR1–FR6 | Dedicated `event-form.ts` Vite entry; `EventWizard.vue` owns all state via `v-show` steps; `beforeunload` handler; 768px responsive breakpoint with modal preview path |
| Event fields | FR7–FR17 | Quill for rich text (B/I/U, HTML output); `MAX_IMAGE_SIZE_MB = 10` shared constant; `createObjectURL` for image preview; single `event_date` in `America/Bogota` |
| Entity search & selection | FR18–FR22 | Custom Vue combobox (no Select2/DAL); new `GET /api/v1/{organizers,speakers,places}/search/?q=` endpoints; `unaccent__icontains` baseline + `pg_trgm` escalation; "Crear nuevo" only on zero results |
| Inline entity creation | FR23–FR26 | Three inline modals (Organizer, Speaker, Place); Leaflet map in Place modal (existing `LeafletPointFieldWidget`); `provide/inject` for modal state; quota enforcement at DRF endpoint |
| Image handling | FR27–FR28 | Client-side size guard before any network call; `URL.createObjectURL` for immediate preview; `multipart/form-data` on final submit only |
| Quota & access | FR29–FR32 | Pre-form event quota check via DRF before wizard renders; entity quota surfaced as 400 in modal without state loss; superuser bypass; Django admin `UserSettings` for elevation |
| Edit flow | FR33–FR36 | `EventUpdateView.dispatch()` permission gate before template renders; `GET /api/v1/events/{slug}/` pre-population; `PATCH /api/v1/events/{slug}/`; `EventEditForm.vue` variant; slug is immutable |
| Live preview | FR37–FR38 | `EventPreview.vue` always mounted; receives wizard state as props; pure local Vue computation (≤50ms, no network calls) |
| Backend validation | FR39 | DRF 400 mapped to `DRFValidationError = Record<string, string[]>`; displayed inline per-field without clearing wizard state |
| Analytics | FR40–FR44 | 5 Umami custom event types; programmatic Umami calls or `data-umami-event` attributes; verified live on launch day |

**Non-Functional Requirements:**

- **NFR1 (search ≤300ms p95):** `unaccent__icontains` on indexed name fields; validate against real corpus before committing; `pg_trgm` GIN index as escalation path
- **NFR2 (edit pre-pop ≤500ms):** Single `GET /api/v1/events/{slug}/` with `select_related` covering all related entities
- **NFR3 (initial load ≤2s on 4G):** `event-form.ts` as isolated Vite chunk with Vue vendor split in `manualChunks`; no impact on MPA pages
- **NFR4 (preview ≤50ms):** Pure Vue computed from local state — enforced by design (no network call ever)
- **NFR6 (CSRF):** Token passed via `data-csrf` attribute on mount element; all DRF mutations include `X-CSRFToken` header
- **NFR7 (edit gate):** `EventUpdateView.dispatch()` → `can_edit(user)` → 403/redirect before template renders; Vue never initializes for unauthorized users
- **NFR8 (auth required):** All write DRF endpoints require `SessionAuthentication`; 401 for unauthenticated requests
- **NFR9 (WCAG 2.1 AA contrast):** All wizard UI, interactive elements, and error states
- **NFR12 (Leaflet, no API key):** Existing `LeafletPointFieldWidget` used in Place modal; no external key needed

**Scale & Complexity:**

- Primary domain: full-stack Django write API + Vue 3 SPA
- Complexity level: **medium** (concentrated in Vue SPA multi-step state + new DRF write API)
- Estimated new components: ~12 Vue SFCs, 2 Django views, 6–8 DRF endpoints, 3 DRF serializers, 2 search service modules

### Technical Constraints & Dependencies

- **`django-vite` multi-entry:** `event-form.ts` added as new entry in `rollupOptions.input`; loaded via `{% vite_asset 'event-form' %}` in create/edit templates only; independent of `mount-vue.ts` island system
- **No Select2 / DAL:** `django-autocomplete-light` and Select2 are not used; existing DAL autocomplete endpoints are replaced by new DRF search endpoints consumed directly by custom Vue combobox components
- **Quill rich text editor:** HTML output is compatible with existing `description` field storage; post-MVP upgrade path is lexical.dev
- **CSRF:** Passed from Django template as `data-csrf` on mount element; all DRF mutating requests include `X-CSRFToken` header
- **`SessionAuthentication`:** Same-origin session cookie; `credentials: 'same-origin'` on all fetch calls; no JWT
- **Multipart upload:** DRF `MultiPartParser` + `FormParser` on create/update endpoints; `formFetch` variant of `apiFetch` needed (omit `Content-Type` header so browser sets multipart boundary automatically)
- **`unaccent` extension:** Already active via `event_search.py`; search endpoints extend the same pattern
- **`pg_trgm` extension:** May need enabling if `unaccent__icontains` alone is insufficient for fuzzy matching
- **Leaflet:** Existing `LeafletPointFieldWidget` (`places/widgets/leaflet.py`) reused in Place modal; CDN-loaded, no API key
- **Slug immutability:** Slug never changes after creation; `PATCH /api/v1/events/{slug}/` is always stable; no redirect-after-slug-change logic needed
- **`UserSettings` quota:** Auto-created via signal; superusers bypass; quota enforcement must be extended to all new DRF write endpoints via shared service or DRF permission class

### Cross-Cutting Concerns Identified

1. **Quota enforcement parity:** Existing quota logic lives in web view `dispatch()`. New DRF create endpoints for Event, Organizer, Speaker, Place must enforce the same quotas via a shared service or DRF permission class — not duplicated inline. Highest-risk integration boundary.
2. **`formFetch` vs `apiFetch`:** Existing `apiFetch` sets `Content-Type: application/json`. The wizard submit uses `FormData` (multipart). A `formFetch` variant must omit `Content-Type` so the browser sets the multipart boundary automatically.
3. **`beforeunload` lifecycle:** Active while wizard has unsaved state; explicitly removed on successful submit and on cancel.
4. **Mobile rendering path (< 768px):** `EventPreview.vue` hidden; preview button opens it in a modal. Place modal stacks Leaflet map below address fields. Two explicit rendering paths need component-level decisions.
5. **Vue vendor bundle split:** `manualChunks: { vue_vendor: ['vue'] }` isolates Vue runtime cache from app code changes on `event-form.ts`.
6. **Quill HTML output compatibility:** Existing `description` field stores HTML — Quill's output is drop-in compatible. No migration of existing descriptions needed.

## Starter Template Evaluation

### Primary Technology Domain

Brownfield Django MPA + Vue 3 SPA extension — no new project initialization required. This initiative adds a new Vite entry point and DRF write endpoints to an existing, running codebase. First implementation begins directly with Django views and Vue component authoring, not project scaffolding.

### Existing Stack (Established Foundation)

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | Django + Django REST Framework |
| Database | PostgreSQL + PostGIS |
| Frontend | Vue.js 3 + Vite 6.4.1 + TypeScript (strict) |
| Auth | django-allauth + django-axes |
| Container | Docker (Gunicorn + Nginx) |
| Analytics | Umami |

### New Dependency: Quill 2.0.3

The only new npm dependency introduced by this initiative.

**Installation:**
```bash
npm install quill@2.0.3
```

**Why Quill over TipTap:** Simpler API, smaller decision footprint, sufficient for B/I/U requirements. Post-MVP upgrade path is lexical.dev if richer editing needs emerge.

**Output format:** HTML — drop-in compatible with the existing `description` field which already stores HTML. No data migration needed.

### Architectural Decisions Already Established

All foundational decisions are inherited from the existing codebase:

- **Language & Runtime:** Python 3.14; TypeScript strict (no `any`)
- **Vue components:** `<script lang="ts" setup>` only; no Options API
- **HTTP layer:** `apiFetch` CSRF wrapper in `api/base.ts`; new `formFetch` variant for multipart
- **Component location:** `desparchado/frontend/components/presentational/` for reusable SFCs
- **API response types:** `desparchado/frontend/scripts/api/interfaces.ts`
- **CSS:** BEM via `bem()` utility; component-scoped SCSS colocated with component
- **Testing:** pytest + pytest-django + django-webtest; factory-boy; `@pytest.mark.django_db`
- **Linting:** ruff (Python), ESLint + Prettier (TypeScript/Vue)
- **Vite multi-entry:** new `event-form` entry added to `rollupOptions.input` in `vite.config.ts`

**Note:** No project initialization command. First implementation story begins with `event-form.ts` entry point + `EventWizard.vue` root component.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Custom 403 template that shows specific `exception` message (required before edit view ships)
- Quota-exceeded template for event creation (`event_quota_exceeded.html`) — distinct from 403
- DRF `QuotaPermission` classes with Spanish `message` attributes for all four entity types
- `EventDetailSerializer` and `EventWriteSerializer` split
- Full new API endpoint suite (9 endpoints)

**Important Decisions (Shape Architecture):**
- `reactive<IWizardState>` root state shape in `EventWizard.vue`
- Custom combobox components (no Headless UI package)
- City list passed as `data-vue-prop-cities` from Django template
- Create/update response returns `{url: absolute_url}`

**Deferred Decisions (Post-MVP):**
- Rich text upgrade to lexical.dev
- Headless UI ARIA reference → evaluate adopting maintained npm package

---

### Data Architecture

No schema changes. All M2M and FK relationships already modeled.

**Category field:** `Event.Category` choices verified — `literature`, `art`, `society`, `science`, `environment`. `db_index=True` already set. No migration needed.

**Search query strategy — organizers, speakers, places:**
`unaccent__icontains` on `name` field as baseline (same pattern as `event_search.py`). Validate against real corpus before committing to production. `pg_trgm` GIN index is the escalation path if accent-insensitive substring matching proves insufficient.

---

### Authentication & Security

**403 error messaging — three distinct scenarios:**

| Scenario | Mechanism | User sees |
|---|---|---|
| Not logged in | `LoginRequiredMixin` → 302 to `/accounts/login/` | Login page |
| Edit permission denied | `PermissionDenied(msg)` → custom `403.html` displaying `exception` | "No tienes permiso para editar este evento." |
| Event quota exceeded (create) | `EventWizardCreateView.dispatch()` renders `events/event_quota_exceeded.html` | Quota message; wizard never loads |
| Entity quota exceeded (modal) | DRF `QuotaPermission` → 403 `{detail: "..."}` | Message inline in modal; wizard state intact |

**DRF permission classes — one per entity type:**
```python
class EventCreationQuotaPermission(BasePermission):
    message = "Hoy alcanzaste el límite de eventos que puedes crear. Vuelve mañana."
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS and not request.user.is_superuser:
            return not request.user.settings.reached_event_creation_quota()
        return True
```
Same pattern for `OrganizerCreationQuotaPermission`, `SpeakerCreationQuotaPermission`, `PlaceCreationQuotaPermission`.

**Edit permission gate:**
`EventWizardUpdateView.dispatch()` calls `event.can_edit(request.user)` after fetching the event by slug. If denied, raises `PermissionDenied` with a specific message — Vue is never initialized.

---

### API & Communication Patterns

**New endpoint table:**

| Method | URL | Purpose | Serializer |
|---|---|---|---|
| `GET` | `/events/api/v1/events/{slug}/` | Edit pre-population | `EventDetailSerializer` |
| `POST` | `/events/api/v1/events/` | Create event (multipart) | `EventWriteSerializer` |
| `PATCH` | `/events/api/v1/events/{slug}/` | Update event (multipart) | `EventWriteSerializer` |
| `GET` | `/events/api/v1/organizers/search/?q=` | Fuzzy search organizers | `OrganizerSearchSerializer` |
| `POST` | `/events/api/v1/organizers/` | Inline create organizer | `OrganizerWriteSerializer` |
| `GET` | `/events/api/v1/speakers/search/?q=` | Fuzzy search speakers | `SpeakerSearchSerializer` |
| `POST` | `/events/api/v1/speakers/` | Inline create speaker | `SpeakerWriteSerializer` |
| `GET` | `/places/api/v1/places/search/?q=` | Fuzzy search places | `PlaceSearchSerializer` |
| `POST` | `/places/api/v1/places/` | Inline create place | `PlaceWriteSerializer` |

`places/api_urls.py` is a new file, registered in `desparchado/urls.py` at `places/api/v1/`.

**Serializer strategy:**

- `EventDetailSerializer` — `GET /{slug}/`; returns all fields for pre-population: `title`, `description`, `image_url`, `event_date`, `category`, `price`, `event_source_url`, `is_published`, `organizers: [{id, name}]`, `speakers: [{id, name}]`, `place: {id, name, city_id}`
- `EventWriteSerializer` — `POST`/`PATCH`; flat input: `title`, `description`, `image` (optional File), `event_date`, `category`, `price`, `event_source_url`, `is_published`, `organizer_ids: [int]`, `speaker_ids: [int]`, `place_id: int`; uses `MultiPartParser` + `FormParser`
- `perform_create()` sets `created_by = request.user` and `is_approved = True` (matching existing `EventCreateView.form_valid()` behavior)

**Create/update response:**
Both `POST` (201) and `PATCH` (200) return `{url: request.build_absolute_uri(obj.get_absolute_url())}`. Vue redirects via `window.location.href = response.url`.

**No DRF Router introduced.** New views use `APIView` / `ListAPIView` / `CreateAPIView` / `RetrieveUpdateAPIView` patterns. Registered explicitly in URL conf files.

**`formFetch` variant:**
New function in `desparchado/frontend/scripts/api/base.ts` that sends `FormData` and omits `Content-Type` header (browser sets multipart boundary). Used only for wizard submit. All other calls (search endpoints) use existing `apiFetch`.

---

### Frontend Architecture

**Wizard state — single root `reactive<IWizardState>`:**
```typescript
interface IWizardState {
  title: string
  description: string        // Quill HTML output
  image: File | null         // browser File; uploaded on submit only
  imagePreviewUrl: string    // URL.createObjectURL() result
  organizerIds: number[]
  speakerIds: number[]
  placeId: number | null
  eventDate: string          // ISO string, America/Bogota timezone
  category: string           // 'literature' | 'art' | 'society' | 'science' | 'environment'
  price: string
  eventSourceUrl: string
  isPublished: boolean
}
```
Owned by `EventWizard.vue`; passed to `EventPreview.vue` as props. Serialized to `FormData` on submit.

**Custom combobox components — no `@headlessui/vue`:**
Implemented from scratch using Headless UI source as ARIA reference. Required ARIA: `role="combobox"`, `aria-expanded`, `aria-autocomplete="list"`, `aria-activedescendant`, `role="listbox"`, `role="option"`, `aria-selected`. Keyboard: ↑↓ to navigate, Enter to select, Escape to close.

**City list for Place modal:**
Passed from Django template as `data-vue-prop-cities='[{"id": 1, "name": "Bogotá"}]'` on the mount element.

---

### Infrastructure & Deployment

No changes. Existing Docker (Gunicorn + Nginx) pipeline unchanged. `event-form.ts` is a new Vite entry in `rollupOptions.input` — built alongside existing entries.

---

### Cross-Component Dependencies

- `EventWizardUpdateView.dispatch()` fetches event by slug to run `can_edit()` — one additional query on edit page load before Vue renders
- `EventWriteSerializer.perform_create()` sets `is_approved = True` — must match existing `EventCreateView` behavior
- `formFetch` must omit `Content-Type` header — if set manually without boundary, server rejects the request
- Custom 403 template must be at `desparchado/templates/403.html` — Django's 403 handler serves it when `PermissionDenied` is raised
- `places/api_urls.py` requires registration in `desparchado/urls.py` before any Place endpoint is reachable

## Implementation Patterns & Consistency Rules

### Critical Conflict Points

10 areas where AI agents could make different choices without explicit rules:
component tree organization, modal/combobox reuse boundaries, validation parity
with existing forms, frontend API module structure, emit naming, loading/error
state variable names, search debounce, step validation logic, Umami event names,
serializer module organization.

---

### Vue Component Tree — Location & Naming

**Reusable components** (used outside EventWizard) — each in its own presentational folder:

```
desparchado/frontend/components/presentational/
├── EntityCombobox/
│   ├── EntityCombobox.vue      ← reusable search + chip-select; used for organizers,
│   └── styles.scss               speakers, and place (single select) across the wizard
└── BaseModal/
    ├── BaseModal.vue           ← generic modal: overlay, close button, trap focus;
    └── styles.scss               no form logic
```

**EventWizard feature folder** (tightly coupled sub-components — NOT independently reusable):

```
desparchado/frontend/components/presentational/EventWizard/
├── EventWizard.vue             ← root; owns IWizardState, step navigation, submit
├── EventWizardCreate.vue       ← thin wrapper for create flow
├── EventWizardEdit.vue         ← thin wrapper for edit flow
├── Step1.vue                   ← title, description, image, organizers, speakers
├── Step2.vue                   ← date, time, place
├── Step3.vue                   ← category, price, event_source_url, is_published
├── EventPreview.vue            ← live preview; always mounted; receives IWizardState as props
├── OrganizerModal.vue          ← uses BaseModal; organizer creation form
├── SpeakerModal.vue            ← uses BaseModal; speaker creation form
├── PlaceModal.vue              ← uses BaseModal; place creation form (includes Leaflet map)
└── styles.scss
```

`BaseModal.vue` handles: overlay render, `Teleport` to `<body>`, close-on-backdrop-click,
`Escape` key close, focus trap. Specific modals (`OrganizerModal`, `SpeakerModal`,
`PlaceModal`) slot their form content into `BaseModal`; they own form state and API calls.

Anti-pattern — do NOT put EntityCombobox or BaseModal inside EventWizard/:
```
# Wrong — these are reusable across the app
EventWizard/EntityCombobox.vue
EventWizard/BaseModal.vue
```

---

### Validation Parity with Existing Forms

All validations from the existing Django forms MUST be reproduced in DRF write
serializers. Agents must NOT rely on model-level validation alone — some form
constraints override model defaults.

**EventWriteSerializer field rules (from EventBaseForm + model):**

| Field | Rule | Source |
|---|---|---|
| `title` | Required; max 255 chars | Model |
| `description` | Optional; run through `sanitize_html()` in `validate_description()` | `EventBaseForm.clean()` |
| `event_source_url` | Required; valid URL; max 500 chars | Model `blank=False` + `EventBaseForm.__init__` |
| `event_date` | Required; valid datetime | Model |
| `organizer_ids` | Required; min 1 item; all IDs must exist | PRD FR11 + existing form |
| `place_id` | Required; ID must exist | Model FK |
| `image` | Optional file; client-side size guard only | Model `blank=True` |
| `category` | Optional; must be a valid `Event.Category` value if provided | Model `blank=True` |
| `price` | Optional; decimal; defaults to 0 | Model `default=0` |
| `is_published` | Optional boolean; defaults to False | Model |

**OrganizerWriteSerializer field rules (from OrganizerForm + model):**

| Field | Rule | Source |
|---|---|---|
| `name` | Required; max 255 chars; unique | Model |
| `description` | Optional; run through `sanitize_html()` in `validate_description()` | `OrganizerForm.clean()` |
| `image` | Required (form level — overrides model `blank=True`) | `OrganizerForm.__init__` |
| `website_url` | Optional; valid URL if provided | Model |

**SpeakerWriteSerializer field rules (from SpeakerForm + model):**

| Field | Rule | Source |
|---|---|---|
| `name` | Required; max 255 chars; unique | Model |
| `description` | Optional; run through `sanitize_html()` in `validate_description()` | `SpeakerForm.clean()` |
| `image` | Required (form level — overrides model `blank=True`) | `SpeakerForm.__init__` |

**PlaceWriteSerializer field rules (from PlaceForm + model):**

| Field | Rule | Source |
|---|---|---|
| `name` | Required; max 255 chars; unique | Model |
| `address` | Required; max 100 chars | Model |
| `location` | Required PointField `{lat, lng}` | Model `null=False` |
| `city` | Optional FK | Model `null=True, blank=True` |
| `image` | Optional | Model `blank=True` |

`sanitize_html()` pattern — apply in serializer `validate_description()`, not in view:
```python
# events/serializers/event.py
def validate_description(self, value: str) -> str:
    return sanitize_html(value)
```

---

### Python Serializer Module Structure

`app_name/serializers/` is a **module** (directory with `__init__.py`).
Files split by **model**, not by purpose. Serializer names include purpose suffix.

```
events/serializers/
├── __init__.py        ← re-exports all serializers
├── event.py           ← EventListSerializer (replaces EventSerializer),
│                           EventDetailSerializer, EventCreateSerializer, EventUpdateSerializer
├── organizer.py       ← OrganizerSearchSerializer, OrganizerCreateSerializer
└── speaker.py         ← SpeakerSearchSerializer, SpeakerCreateSerializer

places/serializers/
├── __init__.py
└── place.py           ← PlaceSearchSerializer, PlaceCreateSerializer
```

**Migration from existing flat file:**
`events/api/serializers.py` → `events/serializers/event.py`.
`EventSerializer` renamed to `EventListSerializer`.
All imports in `events/api/views.py` updated accordingly.

Anti-pattern — do NOT organize by purpose:
```
# Wrong
events/serializers/write_serializers.py
# Correct — by model
events/serializers/event.py
```

---

### Python Permissions Location

One file per app at app root (not inside `api/`):

- `events/permissions.py` — `EventCreationQuotaPermission`, `OrganizerCreationQuotaPermission`, `SpeakerCreationQuotaPermission`
- `places/permissions.py` — `PlaceCreationQuotaPermission`

---

### DRF URL Conventions — Conflict Prevention

**Issue:** `events/` path is already used by `EventListAPIView` (GET list).
Adding a separate `POST events/` view would require two views on the same path.

**Resolution:** Upgrade to `ListCreateAPIView` — standard REST pattern, one URL handles both methods:

```python
# events/api_urls.py
path('events/', EventListCreateAPIView.as_view(), name='event_list'),               # GET list + POST create
path('events/<slug:slug>/', EventDetailUpdateAPIView.as_view(), name='event_detail'), # GET detail + PATCH update
path('organizers/search/', OrganizerSearchAPIView.as_view(), name='organizer_search'),
path('organizers/', OrganizerCreateAPIView.as_view(), name='organizer_create'),
path('speakers/search/', SpeakerSearchAPIView.as_view(), name='speaker_search'),
path('speakers/', SpeakerCreateAPIView.as_view(), name='speaker_create'),

# places/api_urls.py (new; registered at places/api/v1/ in desparchado/urls.py)
path('places/search/', PlaceSearchAPIView.as_view(), name='place_search'),
path('places/', PlaceCreateAPIView.as_view(), name='place_create'),
```

URL name changes from `events_list` → `event_list`. Any reference to
`reverse('events_api:events_list')` must be updated to `reverse('events_api:event_list')`.

If a future endpoint needs `events/` for a different purpose (e.g., a separate admin list),
add it at a distinct path with a distinct name — do NOT reuse `event_list`.

---

### Frontend API Modules

```
desparchado/frontend/scripts/api/
├── base.ts          ← apiFetch, formFetch, getCsrfToken (extend existing)
├── events.ts        ← createEvent, updateEvent, getEventDetail
├── organizers.ts    ← searchOrganizers, createOrganizer
├── speakers.ts      ← searchSpeakers, createSpeaker
└── places.ts        ← searchPlaces, createPlace
```

`formFetch` — exact signature (must omit Content-Type):
```typescript
export async function formFetch(
  url: string,
  data: FormData,
  method: 'POST' | 'PATCH' = 'POST',
): Promise<Response> {
  return fetch(url, {
    method,
    body: data,
    headers: { 'X-CSRFToken': getCsrfToken() },
    credentials: 'same-origin',
  })
}
```

---

### TypeScript Interface Names

All in `desparchado/frontend/scripts/api/interfaces.ts`:

| Interface | Description |
|---|---|
| `IWizardState` | Root wizard reactive state (defined in Core Decisions) |
| `IEntityOption` | `{ id: number; name: string }` — combobox options and chip data |
| `IEventDetailResponse` | `GET /api/v1/events/{slug}/` response for edit pre-population |
| `IEventWriteResponse` | `POST`/`PATCH` response: `{ url: string }` |
| `ISearchResponse` | Search endpoint response: `{ results: IEntityOption[] }` |
| `DRFValidationError` | `Record<string, string[]>` — add if not already present |

---

### Vue Emit Conventions

**`EntityCombobox.vue` emits:**
```typescript
emit('entity:selected', payload: IEntityOption)
emit('entity:created', payload: IEntityOption)
emit('entity:cleared', payload: { id: number })
```

**Modal components emit:**
```typescript
emit('entity:created', payload: IEntityOption)
emit('modal:close')
```

**`BaseModal.vue` emits:**
```typescript
emit('modal:close')   // backdrop click, Escape, or close button
```

**Step components** expose `isValid` via `defineExpose({ isValid })` and do not emit events.

---

### Loading & Error State Naming

| Variable | Type | Scope | Purpose |
|---|---|---|---|
| `isSearching` | `Ref<boolean>` | EntityCombobox | Search request in flight |
| `isSubmitting` | `Ref<boolean>` | EventWizard | Final wizard submit in flight |
| `isLoading` | `Ref<boolean>` | EventWizardEdit | Edit pre-population in flight |
| `isCreating` | `Ref<boolean>` | Modal components | Inline entity creation in flight |
| `fieldErrors` | `Ref<DRFValidationError>` | EventWizard | DRF 400 errors from last submit |
| `searchError` | `Ref<string>` | EntityCombobox | Non-field error from search |
| `modalError` | `Ref<string>` | Modal components | Non-field error incl. quota message |

`fieldErrors` cleared at the start of each new submit. `modalError` cleared when modal opens.

---

### Shared Constants

```typescript
// desparchado/frontend/scripts/constants.ts (create if absent)
export const SEARCH_DEBOUNCE_MS = 300
export const MAX_IMAGE_SIZE_MB = 10
export const MIN_SEARCH_QUERY_LENGTH = 2
```

Shared composable for all entity search UIs:
```typescript
// desparchado/frontend/scripts/composables/useEntitySearch.ts
export function useEntitySearch(searchFn: (q: string) => Promise<IEntityOption[]>) {
  const results = ref<IEntityOption[]>([])
  const isSearching = ref(false)
  let debounceTimer: ReturnType<typeof setTimeout>

  async function search(query: string) {
    clearTimeout(debounceTimer)
    if (query.length < MIN_SEARCH_QUERY_LENGTH) { results.value = []; return }
    debounceTimer = setTimeout(async () => {
      isSearching.value = true
      results.value = await searchFn(query)
      isSearching.value = false
    }, SEARCH_DEBOUNCE_MS)
  }

  return { results, isSearching, search }
}
```

---

### Step Validation Rules

| Step | Valid when |
|---|---|
| Step 1 | `title.trim().length > 0 && organizerIds.length >= 1` |
| Step 2 | `eventDate !== '' && placeId !== null` |
| Step 3 | Always `true` — all fields optional in UI; `event_source_url` validated server-side on submit |

---

### Dirty State & `beforeunload`

```typescript
const isDirty = computed(() =>
  state.title.trim().length > 0 || state.organizerIds.length > 0 || state.image !== null
)
```

Listener added in `onMounted`, removed in `onBeforeUnmount` and immediately before
`window.location.href` on successful submit.

---

### Umami Event Names (7 events)

| Event name | Fires when | Payload |
|---|---|---|
| `wizard:start` | Wizard mounts | `{ action: 'create' \| 'edit' }` |
| `wizard:step-complete` | "Paso siguiente" clicked | `{ step: 1 \| 2 \| 3 }` |
| `wizard:step-abandon` | "Anterior" clicked | `{ step: 1 \| 2 \| 3 }` |
| `entity:search` | Search fires (after debounce) | `{ type: 'organizer' \| 'speaker' \| 'place', found: boolean }` |
| `entity:created-inline` | Inline modal creation succeeds | `{ type: 'organizer' \| 'speaker' \| 'place' }` |
| `quota:hit` | Quota 403 received | `{ resource: 'event' \| 'organizer' \| 'speaker' \| 'place' }` |
| `wizard:submit` | Submit succeeds (201/200) | `{ action: 'create' \| 'edit' }` |

All calls: `window.umami?.track(name, payload)` — optional chaining always.

---

### Entity Search Service Location

- `events/services/entity_search.py` — `search_organizers(q, limit)`, `search_speakers(q, limit)`
- `places/services/place_search.py` — `search_places(q, limit)`

Pattern:
```python
def search_organizers(q: str, limit: int = 10) -> QuerySet:
    return Organizer.objects.filter(name__unaccent__icontains=q).order_by('name')[:limit]
```

Search logic NEVER inlined in DRF views.

---

### Test File Locations

| What | Location |
|---|---|
| Event list + create API | `events/tests/api/test_event_list_create.py` |
| Event detail + update API | `events/tests/api/test_event_detail_update.py` |
| Organizer search + create API | `events/tests/api/test_organizer_api.py` |
| Speaker search + create API | `events/tests/api/test_speaker_api.py` |
| Place search + create API | `places/tests/api/test_place_api.py` |
| Quota permission classes | `events/tests/test_permissions.py`, `places/tests/test_permissions.py` |
| Wizard Django views | `events/tests/views/test_event_wizard.py` |
| Entity search services | `events/tests/services/test_entity_search.py` |
| Place search service | `places/tests/services/test_place_search.py` |

---

### Enforcement Rules

All agents implementing stories from this initiative MUST:

- Place `EntityCombobox` in its own presentational folder — NOT inside `EventWizard/`
- Place `BaseModal` in its own presentational folder; wizard modals use it via slot
- Run `sanitize_html()` on `description` in every write serializer `validate_description()`
- Treat `image` as **required** in `OrganizerWriteSerializer` and `SpeakerWriteSerializer`
- Treat `event_source_url` as **required** in `EventWriteSerializer`
- Use `events/serializers/` and `places/serializers/` as modules, split by model
- Name serializers with model + purpose: `EventListSerializer`, `EventCreateSerializer`, etc.
- Place permission classes in `events/permissions.py` and `places/permissions.py`
- Upgrade `EventListAPIView` to `ListCreateAPIView`; rename URL `events_list` → `event_list`
- Use exact emit names: `entity:selected`, `entity:created`, `entity:cleared`, `modal:close`
- Use exact loading/error variable names from the table above
- Use `SEARCH_DEBOUNCE_MS`, `MAX_IMAGE_SIZE_MB`, `MIN_SEARCH_QUERY_LENGTH` constants
- Use `useEntitySearch` composable for all three entity search UIs
- Clear `fieldErrors` before every new submit
- Call `window.umami?.track(...)` with optional chaining — never assume Umami is present
- Omit `Content-Type` in `formFetch` — never set it manually

## Project Structure & Boundaries

### Files Modified by This Initiative

#### Django Views (replaced)

| Old file | New file | Change |
|---|---|---|
| `events/views/event_create.py` | `events/views/event_wizard_create.py` | `EventCreateView` → `EventWizardCreateView` (renders Vue template; quota pre-check; provides reversed API URLs in context) |
| `events/views/event_update.py` | `events/views/event_wizard_update.py` | `EventUpdateView` → `EventWizardUpdateView` (`can_edit()` check; provides reversed API URLs including slug-specific detail/update URLs) |

#### Modified Existing Files

| File | Change |
|---|---|
| `events/api/views.py` | Add `EventListCreateAPIView`, `EventDetailUpdateAPIView`, `OrganizerSearchAPIView`, `OrganizerCreateAPIView`, `SpeakerSearchAPIView`, `SpeakerCreateAPIView` |
| `events/api_urls.py` | Add 6 new URL patterns; rename `events_list` → `event_list`; upgrade to `ListCreateAPIView` |
| `desparchado/urls.py` | Register `places/api/v1/` namespace |
| `desparchado/frontend/scripts/api/base.ts` | Add `formFetch` function |
| `desparchado/frontend/scripts/api/interfaces.ts` | Add `IWizardProps`, `IWizardState`, `IEntityOption`, `IEventDetailResponse`, `IEventWriteResponse`, `ISearchResponse`, `DRFValidationError` |
| `vite.config.ts` | Add `event-form` entry to `rollupOptions.input` |
| `package.json` | Add `quill@2.0.3` |

---

### New Files Added by This Initiative

#### Python — Events App

```
events/
├── permissions.py                     (NEW) EventCreationQuotaPermission,
│                                             OrganizerCreationQuotaPermission,
│                                             SpeakerCreationQuotaPermission
├── serializers/                       (NEW module — replaces events/api/serializers.py)
│   ├── __init__.py
│   ├── event.py                       EventListSerializer (was EventSerializer),
│   │                                  EventDetailSerializer, EventCreateSerializer,
│   │                                  EventUpdateSerializer
│   ├── organizer.py                   OrganizerSearchSerializer, OrganizerCreateSerializer
│   └── speaker.py                     SpeakerSearchSerializer, SpeakerCreateSerializer
├── services/
│   └── entity_search.py               (NEW) search_organizers(), search_speakers()
├── templates/events/
│   ├── event_wizard.html              (NEW) Mount template for create + edit flows
│   └── event_quota_exceeded.html      (NEW) Shown when daily event quota is hit
└── views/
    ├── event_wizard_create.py         (NEW) EventWizardCreateView
    └── event_wizard_update.py         (NEW) EventWizardUpdateView
```

`events/api/serializers.py` is deleted and its content migrated to `events/serializers/event.py`.

#### Python — Places App

```
places/
├── api/                               (NEW directory)
│   ├── __init__.py
│   └── views.py                       PlaceSearchAPIView, PlaceCreateAPIView
├── api_urls.py                        (NEW) place_search, place_create URL patterns
├── permissions.py                     (NEW) PlaceCreationQuotaPermission
├── serializers/                       (NEW module)
│   ├── __init__.py
│   └── place.py                       PlaceSearchSerializer, PlaceCreateSerializer
└── services/
    └── place_search.py                (NEW) search_places()
```

#### Python — Shared Templates

```
desparchado/templates/
└── 403.html                           (NEW) Custom permission-denied page; renders
                                             {{ exception }} for specific error message
```

#### TypeScript / Vue — Frontend

```
desparchado/frontend/
├── scripts/
│   ├── event-form.ts                  (NEW) Vite entry; reads data-wizard-mode attr;
│   │                                        mounts EventWizardCreate or EventWizardEdit
│   ├── api/
│   │   ├── events.ts                  (NEW) createEvent(url, data), updateEvent(url, data),
│   │   │                                    getEventDetail(url) — urls passed in, not built
│   │   ├── organizers.ts              (NEW) searchOrganizers(url, q), createOrganizer(url, data)
│   │   ├── speakers.ts                (NEW) searchSpeakers(url, q), createSpeaker(url, data)
│   │   └── places.ts                 (NEW) searchPlaces(url, q), createPlace(url, data)
│   ├── composables/
│   │   └── useEntitySearch.ts         (NEW) shared debounced search composable
│   └── constants.ts                   (NEW or extend) SEARCH_DEBOUNCE_MS,
│                                             MAX_IMAGE_SIZE_MB, MIN_SEARCH_QUERY_LENGTH
└── components/presentational/
    ├── BaseModal/                     (NEW)
    │   ├── BaseModal.vue              Overlay, Teleport, Escape/backdrop close, focus trap
    │   └── styles.scss
    ├── EntityCombobox/                (NEW)
    │   ├── EntityCombobox.vue         Custom ARIA combobox; no external library
    │   └── styles.scss
    └── EventWizard/                   (NEW feature folder)
        ├── EventWizard.vue            Root; owns IWizardState; step nav; submit
        ├── EventWizardCreate.vue      Thin wrapper for create flow
        ├── EventWizardEdit.vue        Thin wrapper for edit flow; hydrates state from API
        ├── Step1.vue                  Title, Quill description, image, organizers, speakers
        ├── Step2.vue                  event_date, place
        ├── Step3.vue                  category, price, event_source_url, is_published
        ├── EventPreview.vue           Live preview; receives IWizardState as props
        ├── OrganizerModal.vue         Uses BaseModal; organizer creation form
        ├── SpeakerModal.vue           Uses BaseModal; speaker creation form
        ├── PlaceModal.vue             Uses BaseModal; place creation form + Leaflet map
        └── styles.scss
```

#### Tests

```
events/tests/
├── api/
│   ├── __init__.py
│   ├── test_event_list_create.py      GET list + POST create; multipart; quota; auth
│   ├── test_event_detail_update.py    GET pre-population + PATCH; permission gate
│   ├── test_organizer_api.py          Search + inline create; quota; sanitize_html
│   └── test_speaker_api.py            Search + inline create; quota; sanitize_html
├── test_permissions.py                Quota permission classes
├── services/
│   └── test_entity_search.py          search_organizers, search_speakers; unaccent
└── views/
    └── test_event_wizard.py           Create/edit views; quota redirect; permission gate

places/tests/
├── api/
│   ├── __init__.py
│   └── test_place_api.py              Search + inline create; quota; PointField
├── test_permissions.py                PlaceCreationQuotaPermission
└── services/
    ├── __init__.py
    └── test_place_search.py
```

---

### Template → Vue Props Boundary

Django views provide **all API URLs pre-reversed** in template context. The frontend
never constructs or hard-codes URL patterns.

**Mount element — create flow:**
```html
<div
  data-event-wizard
  data-wizard-mode="create"
  data-csrf="{{ csrf_token }}"
  data-vue-prop-api-create-url="{{ api_create_url }}"
  data-vue-prop-api-organizer-search-url="{{ api_organizer_search_url }}"
  data-vue-prop-api-organizer-create-url="{{ api_organizer_create_url }}"
  data-vue-prop-api-speaker-search-url="{{ api_speaker_search_url }}"
  data-vue-prop-api-speaker-create-url="{{ api_speaker_create_url }}"
  data-vue-prop-api-place-search-url="{{ api_place_search_url }}"
  data-vue-prop-api-place-create-url="{{ api_place_create_url }}"
  data-vue-prop-cities="{{ cities_json }}"
></div>
```

**Mount element — edit flow (adds slug-specific URLs):**
```html
  data-vue-prop-api-detail-url="{{ api_detail_url }}"
  data-vue-prop-api-update-url="{{ api_update_url }}"
```

**Django view context:**
```python
# EventWizardCreateView.get_context_data()
context['api_create_url'] = reverse('events_api:event_list')
context['api_organizer_search_url'] = reverse('events_api:organizer_search')
context['api_organizer_create_url'] = reverse('events_api:organizer_create')
context['api_speaker_search_url'] = reverse('events_api:speaker_search')
context['api_speaker_create_url'] = reverse('events_api:speaker_create')
context['api_place_search_url'] = reverse('places_api:place_search')
context['api_place_create_url'] = reverse('places_api:place_create')

# EventWizardUpdateView.get_context_data() — adds slug-specific URLs
context['api_detail_url'] = reverse('events_api:event_detail', args=[self.object.slug])
context['api_update_url'] = reverse('events_api:event_detail', args=[self.object.slug])
```

**`IWizardProps` interface:**
```typescript
interface IWizardProps {
  apiCreateUrl?: string        // create flow only
  apiDetailUrl?: string        // edit flow only
  apiUpdateUrl?: string        // edit flow only
  apiOrganizerSearchUrl: string
  apiOrganizerCreateUrl: string
  apiSpeakerSearchUrl: string
  apiSpeakerCreateUrl: string
  apiPlaceSearchUrl: string
  apiPlaceCreateUrl: string
  cities: Array<{ id: number; name: string }>
}
```

**API function signatures — URL always first parameter:**
```typescript
// events.ts
export async function createEvent(url: string, data: FormData): Promise<IEventWriteResponse>
export async function updateEvent(url: string, data: FormData): Promise<IEventWriteResponse>
export async function getEventDetail(url: string): Promise<IEventDetailResponse>

// organizers.ts
export async function searchOrganizers(url: string, q: string): Promise<ISearchResponse>
export async function createOrganizer(url: string, data: FormData): Promise<IEntityOption>
```

---

### FR → File Mapping

| FR Range | Files |
|---|---|
| FR1–FR6 (Wizard nav & layout) | `event-form.ts`, `EventWizard.vue`, `EventWizardCreate.vue`, `EventWizardEdit.vue`, `event_wizard.html`, `event_wizard_create.py`, `event_wizard_update.py` |
| FR7–FR17 (Event fields) | `Step1.vue`, `Step2.vue`, `Step3.vue`, `EventPreview.vue`, `events/serializers/event.py` |
| FR18–FR22 (Entity search) | `EntityCombobox.vue`, `useEntitySearch.ts`, `organizers.ts`, `speakers.ts`, `places.ts`, `entity_search.py`, `place_search.py`, `events/api/views.py`, `places/api/views.py` |
| FR23–FR26 (Inline creation) | `OrganizerModal.vue`, `SpeakerModal.vue`, `PlaceModal.vue`, `BaseModal.vue`, `events/serializers/organizer.py`, `events/serializers/speaker.py`, `places/serializers/place.py` |
| FR27–FR28 (Image handling) | `Step1.vue`, `EventPreview.vue`, `constants.ts` |
| FR29–FR32 (Quota & access) | `event_wizard_create.py`, `events/permissions.py`, `places/permissions.py`, `event_quota_exceeded.html` |
| FR33–FR36 (Edit flow) | `event_wizard_update.py`, `EventWizardEdit.vue`, `events/serializers/event.py` (EventDetailSerializer) |
| FR37–FR38 (Live preview) | `EventPreview.vue` |
| FR39 (Backend validation) | `EventWizard.vue`, all write serializers |
| FR40–FR44 (Analytics) | All Vue SFCs |

---

### Integration Boundaries

**View → Template boundary:**
Views provide all reversed API URLs in context — no URL construction in frontend.
`EventWizardUpdateView` fetches the event by slug to run `can_edit()` and to provide
slug-specific `api_detail_url` / `api_update_url`.

**Vue → DRF boundary:**
All HTTP calls via `api/` modules receiving URL as first parameter from `IWizardProps`.
No `fetch()` calls inside components. No URL strings hardcoded in Vue.

**DRF → Service boundary:**
Views call service functions; services return `QuerySet`; no HTTP/request knowledge in services.

**DRF → Serializer boundary:**
Read: `EventListSerializer` (list) / `EventDetailSerializer` (edit pre-pop).
Write: `EventCreateSerializer` (POST) / `EventUpdateSerializer` (PATCH).
All `description` fields sanitized in `validate_description()`.

**Quota enforcement boundary:**
- Event quota: `EventWizardCreateView.dispatch()` — renders `event_quota_exceeded.html`
- Entity quotas: `QuotaPermission` classes on DRF create endpoints — 403 `{detail: "..."}` read by Vue in `modalError`

**Template → 403 boundary:**
`PermissionDenied` in `EventWizardUpdateView.dispatch()` → `desparchado/templates/403.html` → renders `{{ exception }}`.

## Architecture Validation Results

### Coherence Validation ✅

All decisions are mutually compatible. DRF + PostGIS + Vue 3 + Vite are all in
production. Quill 2.x is a vanilla JS library — Vue integration uses `onMounted`
with a DOM `ref<HTMLElement>`; it is NOT a Vue plugin and does not call `app.use()`.
`formFetch` and `apiFetch` coexist cleanly in `api/base.ts`. The custom combobox
pattern (no Headless UI package) is consistent with the "no additional frameworks"
constraint. No contradictory decisions found.

### Requirements Coverage

**FR Coverage:**

| FR Range | Coverage | Notes |
|---|---|---|
| FR1–FR3 | ✅ | Auth gate, 3-step nav, blocking validation |
| FR4 | ✅ Clarified | `isCondensed` is a separate `ref<boolean>` in `EventWizard.vue` — NOT in `IWizardState`; not serialized to FormData |
| FR5–FR6 | ✅ | Mobile preview modal; beforeunload |
| FR7–FR17 | ✅ | All event fields in `IWizardState`; see Correction 1 |
| FR18–FR22 | ✅ | EntityCombobox + useEntitySearch + DRF search endpoints |
| FR23–FR26 | ✅ | Three modals using BaseModal; wizard state preserved |
| FR27–FR28 | ✅ | MAX_IMAGE_SIZE_MB constant; createObjectURL |
| FR29–FR32 | ✅ | Pre-form quota template + DRF QuotaPermission classes |
| FR33–FR36 | ✅ | Server-side permission gate; EventDetailSerializer; PATCH |
| FR37–FR38 | ✅ | EventPreview receives IWizardState as props; pure local state |
| FR39 | ✅ | fieldErrors cleared before submit; DRFValidationError type |
| FR40–FR44 | ✅ | 7 Umami events with optional chaining |

**NFR Coverage:**

| NFR | Coverage |
|---|---|
| NFR1 (search ≤300ms p95) | ✅ `unaccent__icontains` + SEARCH_DEBOUNCE_MS; pg_trgm escalation path |
| NFR2 (pre-pop ≤500ms) | ✅ `select_related('place__city').prefetch_related('organizers', 'speakers')` on EventDetailSerializer |
| NFR3 (load ≤2s on 4G) | ✅ Isolated `event-form.ts` Vite chunk + `manualChunks: { vue_vendor: ['vue'] }` |
| NFR4 (preview ≤50ms) | ✅ Pure Vue computed from local state — no network call possible |
| NFR5 (image preview immediate) | ✅ `URL.createObjectURL` in Step1.vue on file selection |
| NFR6 (CSRF) | ✅ `data-csrf` attribute + `X-CSRFToken` header on all mutations |
| NFR7 (edit gate) | ✅ `EventWizardUpdateView.dispatch()` → `can_edit()` before template renders |
| NFR8 (auth required) | ✅ `LoginRequiredMixin` on both wizard views + DRF `SessionAuthentication` |
| NFR9 (WCAG AA contrast) | ✅ All wizard UI, interactive elements, error states |
| NFR10 (Umami verified) | ✅ 7 events with exact names and payloads defined |
| NFR11 (image size client-side) | ✅ `MAX_IMAGE_SIZE_MB` constant; validation before any fetch |
| NFR12 (Leaflet no API key) | ✅ Existing `LeafletPointFieldWidget` reused in PlaceModal |

---

### Corrections Applied

**Correction 1 — `IWizardState` entity fields (chip display names):**

Original state stored `organizerIds: number[]`, `speakerIds: number[]`,
`placeId: number | null`. `EntityCombobox` chips require `{id, name}` to render
labels — IDs alone are insufficient. Edit pre-population also returns `{id, name}`
objects from `EventDetailSerializer`. Corrected state:

```typescript
interface IWizardState {
  title: string
  description: string
  image: File | null
  imagePreviewUrl: string
  organizers: IEntityOption[]       // replaces organizerIds: number[]
  speakers: IEntityOption[]         // replaces speakerIds: number[]
  place: IEntityOption | null       // replaces placeId: number | null
  eventDate: string
  category: string
  price: string
  eventSourceUrl: string
  isPublished: boolean
}
```

On submit, IDs extracted: `organizer_ids: state.organizers.map(o => o.id)`.

Step validation rules updated:
- Step 1: `state.title.trim().length > 0 && state.organizers.length >= 1`
- Step 2: `state.eventDate !== '' && state.place !== null`

**Correction 2 — FR4 condensed mode scope:**

`isCondensed` is a `ref<boolean>` owned by `EventWizard.vue`. Controls CSS class
on the wizard wrapper — not serialized to `FormData`. NOT part of `IWizardState`.
Dirty state check does NOT include `isCondensed`.

**Correction 3 — `send_notification()` in `perform_create()`:**

Existing `EventCreateView.form_valid()` calls `send_notification(request, event, 'event', True)`.
`EventCreateSerializer.perform_create()` must replicate this:

```python
def perform_create(self, serializer: EventCreateSerializer) -> None:
    event = serializer.save(
        created_by=self.request.user,
        is_approved=True,
    )
    send_notification(self.request, event, 'event', True)
```

**Correction 4 — `select_related` spec for `EventDetailSerializer`:**

Pre-population query must use:
```python
Event.objects.select_related('place__city').prefetch_related('organizers', 'speakers')
```
Ensures NFR2 (≤500ms) without N+1 queries on organizer/speaker names.

---

### Architecture Completeness Checklist

- [x] Project context analysed; 44 FRs + 12 NFRs mapped to files
- [x] FR4 condensed mode clarified — UI state separate from form state
- [x] All entity search/creation endpoints defined (9 total)
- [x] Quota enforcement at two levels: Django view (events) + DRF permissions (entities)
- [x] Custom 403 template with exception message
- [x] All API URLs reversed by Django; zero URL construction in frontend
- [x] Serializer module structure defined (`app/serializers/model.py`)
- [x] `send_notification()` preserved in DRF `perform_create()`
- [x] `select_related` spec on `EventDetailSerializer`
- [x] 7 Umami event names with payloads locked
- [x] `IWizardState` corrected — entity fields store `IEntityOption` not bare IDs
- [x] Quill integration pattern noted — vanilla JS, `onMounted` DOM ref
- [x] Enforcement rules complete — 18 mandatory patterns
- [x] Test file locations specified for all new test files

### Architecture Readiness Assessment

**Overall status:** READY FOR IMPLEMENTATION

**Confidence level:** High

**Key strengths:**
- All infrastructure already in production — zero new services or containers
- Single-submit guarantee: no partial saves, no orphaned records on abandonment
- URL reversal in Django views means frontend never constructs paths
- Quota enforcement is belt-and-suspenders: Django view pre-check + DRF permission class
- `IWizardState` correction eliminates a chip display bug before it is written

**Deferred to post-MVP:**
- Rich text upgrade to lexical.dev
- `pg_trgm` fuzzy search (only if `unaccent__icontains` proves insufficient)

### Implementation Handoff

**Pre-implementation checklist:**
1. Verify `unaccent` extension is active in the database
2. Verify or add `manualChunks: { vue_vendor: ['vue'] }` in `vite.config.ts`
3. Verify `DJANGO_VITE['default']['dev_mode'] = True` in `dev.py`
4. Update any existing test referencing `events_api:events_list` → `events_api:event_list`

**Suggested implementation order:**
1. Serializer module migration (`events/api/serializers.py` → `events/serializers/`) + tests
2. Permission classes (`events/permissions.py`, `places/permissions.py`) + tests
3. Entity search services + DRF search endpoints + tests
4. Entity create endpoints (organizer, speaker, place) + tests
5. Event create/update DRF endpoints + `EventWizardCreateView` / `EventWizardUpdateView` + tests
6. `event-form.ts` + `EventWizard.vue` root + step components
7. `EntityCombobox.vue` + `BaseModal.vue` (reusable components first)
8. Inline creation modals
9. `EventPreview.vue`
10. Edit flow (`EventWizardEdit.vue` pre-population)
11. Umami instrumentation (last — verify all 7 events before release)