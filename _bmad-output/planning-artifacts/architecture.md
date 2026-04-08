---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-04-06'
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/product-brief-navigation-discovery.md
  - _bmad-output/planning-artifacts/product-brief-navigation-discovery-distillate.md
  - _bmad-output/planning-artifacts/research/market-free-cultural-events-colombia-research-2026-04-05.md
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
date: '2026-04-06'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (28 total):**

| Category | FRs | Architectural Implication |
|---|---|---|
| Contextual related content | FR1–FR3 | 5-tier cascading fallback on EventDetailView; early-exit sequential queries (30ms threshold triggers union Q() fallback); each tier must produce a visible label ("Por organizador", "Por categoría", "Eventos pasados") |
| Cross-entity navigation | FR4–FR7 | Annotated M2M counts via `.annotate(count=Count(...)).order_by('-count')`; multi-join annotation on co-speakers needs EXPLAIN ANALYZE on realistic data |
| Category discovery | FR8–FR10 | New `CategoryDetailView` inheriting `EventListView`; hardcoded `SLUG_MAP` constant; hard cap ≤20 events (paginated) — PRD gap closed here |
| Wayfinding / platform identity | FR11–FR13 | Single `breadcrumb_items` list drives both HTML partial AND JSON-LD BreadcrumbList (one source of truth); breadcrumb `<nav>` must appear before `<h1>` in DOM |
| Empty state discovery | FR14–FR15 | Two-phase context in SpeakerDetailView and OrganizerDetailView; must distinguish "no upcoming" from "no events ever" |
| Structured data / SEO | FR16–FR20 | Per-page `{% block structured_data %}` JSON-LD; `event_date` timezone-awareness is a hard pre-implementation blocker (not a suggestion) |
| Analytics instrumentation | FR21–FR28 | 8 Umami `data-event-*` attributes; confirm Umami `<script>` loads on all 4 affected page types; explicit per-attribute checklist tied to template file + DOM selector required |

**Non-Functional Requirements:**

- **NFR1–NFR3 (Performance):** ≤50ms added latency; ≤5 new queries per page; hard result caps (related events ≤3, co-speakers ≤5, hosting organizers ≤6, associated speakers ≤8, venue organizers ≤6, category page events ≤20 paginated). No caching — all targets via `select_related`/`prefetch_related` and indexed fields only.
- **NFR5–NFR8 (Accessibility):** WCAG 2.1 AA breadcrumb `<nav aria-label="breadcrumb">`; `aria-current="page"` on current item; semantic HTML; descriptive alt text on entity cards.
- **NFR9–NFR11 (Integration):** All 8 Umami events verified against explicit checklist before release; all JSON-LD passes Google Rich Results Test with zero errors; GSC monitored 30 days post-deploy.

**Scale & Complexity:**

- Primary domain: server-side Django web engineering + SEO
- Complexity level: **low** (brownfield; all data exists; no infrastructure changes)
- Estimated components: ~8 view changes + 1 new view + service functions in `events/services/` + ~15 template additions + 5 JSON-LD blocks + 1 breadcrumb partial

### Architecture Decision Records

| Decision | Options Considered | Decision | Rationale |
|---|---|---|---|
| Related events query strategy | Sequential 5-tier vs. union Q() | Sequential with explicit 30ms threshold trigger to switch | Readable, early-exit; measurable fallback condition |
| Cross-entity query location | Fat view / service function / model method | Service functions in `events/services/` | Consistent with existing `event_search.py` pattern; independently testable |
| Category slug mapping | Hardcoded dict vs. model-driven | Hardcoded `SLUG_MAP` constant | Categories are fixed (5); no DB round-trip; auditable at a glance |
| JSON-LD rendering | Template tag vs. template block | `{% block structured_data %}` per page type | Zero new dependencies; Django template inheritance pattern |
| Breadcrumb context | Mixin vs. per-view override | Per-view `get_context_data()` | PRD explicitly rules out new mixins; views stay self-contained |

### Technical Constraints & Dependencies

- **No caching layer** — NGINX + Gunicorn only; all query performance via ORM optimization
- **No frontend changes** — all new HTML is server-rendered and progressively enhanced; no Vite/Vue changes
- **No schema migrations** — all M2M and FK relationships already modeled
- **Single developer** — sequential delivery; no parallel implementation tracks
- **`Event.CATEGORY` field index** — must be verified before implementing CategoryDetailView; field needs a DB index for category page queries
- **`event_date` timezone-awareness** — hard pre-implementation blocker for all schema.org/Event JSON-LD work; must confirm timezone-aware storage before writing startDate field
- **`Event.CATEGORY` constant mapping** — `SLUG_MAP` must be verified against `events/models/event.py` before implementation; incorrect mapping silently returns empty querysets

### Cross-Cutting Concerns

1. **Query performance** — every new context var is a potential N+1; Django Debug Toolbar audit required before PR; co-speaker annotation query needs `EXPLAIN ANALYZE` on realistic data
2. **Breadcrumb single source of truth** — `breadcrumb_items` Python list must drive both HTML partial and JSON-LD BreadcrumbList; no separate maintenance
3. **Fallback tier labeling** — each related-events fallback tier must pass a label to the template; missing label causes silent stale-content display
4. **Analytics completeness** — 8 Umami `data-event-*` attributes across 4 page types; Umami script availability on all affected page types must be confirmed; explicit per-attribute QA checklist required
5. **Empty-state detection** — two-phase context construction (check upcoming → fall back to category events) needs test coverage for both phases
6. **Progressive enhancement** — all new navigation must function without JavaScript; no JS dependency introduced
7. **Deploy pre-condition** — Vite assets must be pre-built before `collectstatic`; not a new risk but worth noting since no frontend changes means this pipeline won't be exercised during this work

## Starter Template Evaluation

### Primary Technology Domain

Brownfield Django MPA enhancement — no new project initialization required.

### Existing Stack (Established Foundation)

This initiative adds no new technologies. The architectural foundation is:

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | Django 6.0 + Django REST Framework |
| Database | PostgreSQL + PostGIS |
| Frontend | Vue.js 3 + Vite 6 + TypeScript (no changes in this initiative) |
| Auth | django-allauth |
| Container | Docker (Gunicorn + NGINX) |
| Analytics | Umami |

### Initialization Command

None — existing codebase. First implementation story begins with view and service layer changes, not project scaffolding.

### Architectural Decisions Already Established

- **Language & Runtime:** Python 3.14; type hints required; no `Any` types
- **ORM:** Django ORM with PostGIS extension; `select_related`/`prefetch_related` for query optimization
- **Views:** Class-Based Views (CBV); `get_context_data()` for context extension
- **Services:** `events/services/` for business logic; independently testable
- **Templates:** Django template inheritance; `{% block %}` overrides per page type
- **Testing:** pytest + pytest-django + factory-boy; `@pytest.mark.django_db`; no `TestCase` classes
- **Linting:** ruff
- **Development workflow:** All commands run inside `desparchado-web-1` Docker container

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- `event_date` timezone-awareness verified before any JSON-LD work begins
- `Event.CATEGORY` constant names verified against `events/models/event.py` before implementing `CategoryDetailView`
- `Event.CATEGORY` field index confirmed before category page queries go live

**Important Decisions (Shape Architecture):**
- Related events as pure QuerySet service functions; tier-walking in view
- Empty-state trigger threshold and display pattern
- Category page URL structure
- Umami event naming convention (13 events)

**Deferred Decisions (Post-MVP):**
- URL translation to Spanish (separate feature)
- Category-level city filtering (`/events/category/literature/?city=bogota`)
- Per-page `<title>` / meta description for Phase 2

---

### Data Architecture

No schema changes. All M2M and FK relationships already modeled.

**Query strategy — related events (EventDetailView):**
Sequential 5-tier cascade; stops at first tier that returns results. Switch to union `Q()` query if Django Debug Toolbar shows >30ms from the cascade block alone.

Tier order:
1. Same organizer (most specific)
2. Same category
3. Same place
4. Random future events
5. Random past events

Hard cap: 3 results returned.

**Query strategy — empty state (SpeakerDetailView, OrganizerDetailView):**
Trigger when `upcoming_count + past_count < 5`. Display: upcoming events ordered by date (limit 3) + "Ver todos los eventos" CTA to `/`. No category detection. No explanatory copy.

**Result caps (all cross-entity sections):**

| Section | Cap |
|---|---|
| Related events (event detail) | 3 |
| Co-speakers (speaker page) | 5 |
| Hosting organizers (speaker page) | 6 |
| Associated speakers (organizer page) | 8 |
| Venue organizers (place page) | 6 |
| Empty-state upcoming events | 3 |
| Category page events | 20 (paginated) |

---

### Authentication & Security

No changes. django-allauth + django-axes in place. All new views are public (read-only). No new permission checks required.

---

### API & Communication Patterns

No new API endpoints. All changes are server-rendered HTML via Django CBVs. DRF API unchanged.

---

### Frontend Architecture

No changes. Vue.js 3 + Vite unchanged. All new content is server-rendered; works with JavaScript disabled.

---

### Infrastructure & Deployment

No new containers or services. Standard pipeline: Vite build → collectstatic → Django container restart.

---

### Category Page URL Structure

English slugs, explicit namespace. URL translation deferred to separate feature.

| Category | URL |
|---|---|
| Literatura | `/events/category/literature/` |
| Arte | `/events/category/art/` |
| Sociedad | `/events/category/society/` |
| Ciencia | `/events/category/science/` |
| Medio Ambiente | `/events/category/environment/` |

Returns 404 for unknown slugs. `SLUG_MAP` constant verified against `Event.CATEGORY` choices before implementation.

---

### Analytics — Umami Event Names (13 total)

| Event name | Fires on | Interaction |
|---|---|---|
| `event-related-click` | Event detail | Related event card click |
| `event-category-click` | Event detail | Category tag click |
| `event-breadcrumb-click` | Event detail | Any breadcrumb link click |
| `speaker-cospeaker-click` | Speaker page | Co-speaker link click |
| `speaker-organizer-click` | Speaker page | Hosting organizer link click |
| `speaker-breadcrumb-click` | Speaker page | Any breadcrumb link click |
| `speaker-fallback-click` | Speaker page | Empty-state event card click |
| `organizer-speaker-click` | Organizer page | Associated speaker link click |
| `organizer-breadcrumb-click` | Organizer page | Any breadcrumb link click |
| `organizer-fallback-click` | Organizer page | Empty-state event card click |
| `place-organizer-click` | Place page | Venue organizer link click |
| `place-breadcrumb-click` | Place page | Any breadcrumb link click |
| `category-breadcrumb-click` | Category pages | Any breadcrumb link click |

---

### Cross-Component Dependencies

- Empty-state display depends on a combined count query (upcoming + past) — must be a single annotated query, not two separate `.count()` calls
- Breadcrumb JSON-LD (`BreadcrumbList`) generated from the same `breadcrumb_items` list that drives the HTML partial — one source of truth
- `CategoryDetailView` depends on verified `SLUG_MAP` constant and confirmed `Event.CATEGORY` field index
- All JSON-LD blocked until `event_date` timezone-awareness is confirmed

## Implementation Patterns & Consistency Rules

### Context Variable Names (Views → Templates)

All views passing new context must use these exact names. Deviating causes template breakage that fails silently.

| Variable | Type | Used in |
|---|---|---|
| `breadcrumb_items` | `list[tuple[str, str \| None]]` | All updated views |
| `related_events` | `QuerySet` | EventDetailView |
| `related_events_label` | `str` | EventDetailView |
| `co_speakers` | `QuerySet` | SpeakerDetailView |
| `hosting_organizers` | `QuerySet` | SpeakerDetailView |
| `associated_speakers` | `QuerySet` | OrganizerDetailView |
| `venue_organizers` | `QuerySet` | PlaceDetailView |
| `show_empty_state` | `bool` | SpeakerDetailView, OrganizerDetailView |
| `fallback_events` | `QuerySet` | SpeakerDetailView, OrganizerDetailView |

`breadcrumb_items` tuples: `(label: str, url: str | None)` — `None` for the current page (renders as non-linked span).

---

### Service Function Location & Naming

New service functions for this initiative live in:
- `events/services/related_events.py` — all related/fallback event queries
- `events/services/cross_entity.py` — co-speakers, hosting organizers, associated speakers, venue organizers

**Naming convention:** `get_{what}_{for_entity}(entity, limit=N) -> QuerySet`

Examples:
```python
# events/services/related_events.py
def get_events_by_organizer(event: Event, limit: int = 3) -> QuerySet: ...
def get_events_by_category(event: Event, limit: int = 3) -> QuerySet: ...
def get_events_by_place(event: Event, limit: int = 3) -> QuerySet: ...
def get_random_future_events(event: Event, limit: int = 3) -> QuerySet: ...
def get_random_past_events(event: Event, limit: int = 3) -> QuerySet: ...

# events/services/cross_entity.py
def get_co_speakers(speaker: Speaker, limit: int = 5) -> QuerySet: ...
def get_hosting_organizers(speaker: Speaker, limit: int = 6) -> QuerySet: ...
def get_associated_speakers(organizer: Organizer, limit: int = 8) -> QuerySet: ...
def get_venue_organizers(place: Place, limit: int = 6) -> QuerySet: ...
```

---

### Breadcrumb Items Format

```python
# Correct — tuple of (label, url); url=None for current page
breadcrumb_items = [
    ("Inicio", "/"),
    ("Presentadores", reverse("events:speaker_list")),
    ("Carol Ann Figueroa", None),  # current page — no link
]
```

Anti-pattern — do NOT use dicts:
```python
# Wrong
breadcrumb_items = [{"label": "Inicio", "url": "/"}]
```

---

### Template Partial & Block Names

| Purpose | Path / Block name |
|---|---|
| Breadcrumb HTML | `{% include 'includes/_breadcrumbs.html' with items=breadcrumb_items %}` |
| Structured data | `{% block structured_data %}{% endblock %}` in base template |
| JSON-LD output | Inline `<script type="application/ld+json">` inside the block |

The `{% block structured_data %}` override goes in each page-type template, not in view code or template tags.

---

### Empty-State Threshold Constant

```python
# events/services/related_events.py
EMPTY_STATE_THRESHOLD = 5  # show fallback when upcoming + past < this

def should_show_empty_state(entity) -> bool:
    upcoming = entity.events.published().future().count()
    if upcoming >= EMPTY_STATE_THRESHOLD:
        return False
    past = entity.events.published().past().count()
    return (upcoming + past) < EMPTY_STATE_THRESHOLD
```

Anti-pattern — do NOT inline the magic number in the view:
```python
# Wrong
if self.object.events.count() < 5:  # unexplained magic number
```

---

### Test File Locations

| What | Location |
|---|---|
| Service function tests | `events/tests/services/test_related_events.py` |
| Cross-entity service tests | `events/tests/services/test_cross_entity.py` |
| View tests (new views) | `events/tests/test_views.py` (existing file) |
| Template rendering tests | `events/tests/test_views.py` (via `django_app` fixture) |

---

### Enforcement Rules

All agents implementing stories from this initiative MUST:

- Use exact context variable names from the table above — no aliases
- Place new service functions in `events/services/related_events.py` or `events/services/cross_entity.py` — not in view files
- Use `EMPTY_STATE_THRESHOLD` constant — never the raw number `5`
- Generate JSON-LD inside `{% block structured_data %}` — not in view code
- Use `breadcrumb_items` as `list[tuple[str, str | None]]` — not dicts
- Verify `event_date` timezone-awareness before implementing any JSON-LD `startDate` field

## Project Structure & Boundaries

### Files Modified by This Initiative

#### Views (existing files, modified)

| File | Changes |
|---|---|
| `events/views/event_detail.py` | Add related events (5-tier cascade) + breadcrumb_items + structured data context |
| `events/views/speaker_detail.py` | Add co_speakers, hosting_organizers, empty-state logic + breadcrumb_items |
| `events/views/organizer_detail.py` | Add associated_speakers, empty-state logic + breadcrumb_items |
| `places/views/place_detail.py` | Add venue_organizers + breadcrumb_items |

#### URL Config (existing files, modified)

| File | Changes |
|---|---|
| `events/urls.py` | Add 5 category page URL patterns under `/events/category/<slug>/` |

---

### New Files Added by This Initiative

#### Services

```
events/services/
├── __init__.py          (existing)
├── event_search.py      (existing — unchanged)
├── related_events.py    (NEW) — 5-tier cascade + empty-state logic
└── cross_entity.py      (NEW) — co-speakers, hosting organizers,
                                  associated speakers, venue organizers
```

#### Views

```
events/views/
└── category_detail.py   (NEW) — CategoryDetailView, SLUG_MAP constant
```

#### Templates (new files)

```
desparchado/templates/includes/
└── _breadcrumbs.html    (NEW) — shared breadcrumb partial

events/templates/events/
└── category_detail.html (NEW) — category page template
```

#### Tests

```
events/tests/
├── services/            (NEW directory)
│   ├── __init__.py
│   ├── test_related_events.py
│   └── test_cross_entity.py
└── views/
    ├── test_event_detail.py     (existing — add related events tests)
    ├── test_speaker_detail.py   (existing — add cross-entity + empty-state tests)
    ├── test_organizer_detail.py (existing — add cross-entity + empty-state tests)
    └── test_category_detail.py  (NEW) — category page + 404 on unknown slug
```

---

### Templates Modified by This Initiative

| File | Changes |
|---|---|
| `desparchado/templates/layout/base.html` | Add `{% block structured_data %}{% endblock %}` in `<head>`; confirm Umami script is present |
| `events/templates/events/event_detail.html` | Add breadcrumbs include; related events section with label; category tag; `{% block structured_data %}` with Event JSON-LD |
| `events/templates/events/speaker_detail.html` | Add breadcrumbs include; co-speakers section; hosting organizers section; empty-state block; `{% block structured_data %}` with Person JSON-LD |
| `events/templates/events/organizer_detail.html` | Add breadcrumbs include; associated speakers section; empty-state block; `{% block structured_data %}` with Organization JSON-LD |
| `places/templates/places/place_detail.html` | Add breadcrumbs include; venue organizers section; `{% block structured_data %}` with Place JSON-LD |

---

### FR → File Mapping

| FR | File(s) |
|---|---|
| FR1–FR3 (related events) | `events/services/related_events.py` + `events/views/event_detail.py` + `events/templates/events/event_detail.html` |
| FR4 (hosting organizers on speaker) | `events/services/cross_entity.py` + `events/views/speaker_detail.py` |
| FR5 (co-speakers) | `events/services/cross_entity.py` + `events/views/speaker_detail.py` |
| FR6 (associated speakers on organizer) | `events/services/cross_entity.py` + `events/views/organizer_detail.py` |
| FR7 (venue organizers on place) | `events/services/cross_entity.py` + `places/views/place_detail.py` |
| FR8–FR10 (category pages) | `events/views/category_detail.py` + `events/urls.py` + `events/templates/events/category_detail.html` |
| FR11–FR12 (breadcrumbs) | `desparchado/templates/includes/_breadcrumbs.html` + all 4 detail views + category view |
| FR13 (contextual sidebar) | Removed — replaced by empty-state navigation pattern |
| FR14–FR15 (empty state) | `events/services/related_events.py` + `events/views/speaker_detail.py` + `events/views/organizer_detail.py` |
| FR16–FR20 (structured data) | `desparchado/templates/layout/base.html` + 4 detail templates + category template |
| FR21–FR28 (analytics) | All 4 detail templates + category template (Umami `data-umami-event` attributes) |

---

### Integration Boundaries

**View → Service boundary:**
Views call service functions and own tier-walking logic. Services have no knowledge of views or templates. Service functions are pure: take a model instance, return a QuerySet.

**View → Template boundary:**
Context variable names are the contract (defined in Implementation Patterns). Templates must not contain query logic — only iteration and conditionals on pre-fetched data.

**Template → Structured Data boundary:**
`breadcrumb_items` list is the single source of truth for both the HTML partial and the JSON-LD `BreadcrumbList`. Templates read the same context variable for both.

**External boundary — Umami:**
Umami analytics fires via `data-umami-event` HTML attributes on anchor elements. No JavaScript changes. Fires only when the Umami `<script>` is present in `base.html`.

## Architecture Validation Results

### Coherence Validation ✅

All decisions are mutually compatible. Service layer pattern is consistent with existing `event_search.py`. Template block override pattern is standard Django. No contradictory decisions found.

### Requirements Coverage

| FR Range | Coverage | Notes |
|---|---|---|
| FR1–FR3 | ✅ | 5-tier cascade in `related_events.py` + `event_detail.py` |
| FR4–FR7 | ✅ | `cross_entity.py` + 4 detail views |
| FR8–FR10 | ✅ | `category_detail.py` + `urls.py` |
| FR11–FR12 | ✅ | `_breadcrumbs.html` + all views |
| FR13 | ⚠️ Intentional deviation | PRD required contextual sidebar copy. Replaced with empty-state navigation pattern (no copy, just content + CTA). Simpler and solves the same core problem. Agents must NOT implement FR13 as written. |
| FR14–FR15 | ✅ Simplified | Category-based fallback replaced with generic upcoming events + CTA. Threshold: `upcoming + past < 5`. |
| FR16–FR20 | ✅ | `{% block structured_data %}` + per-template JSON-LD |
| FR21–FR28 | ✅ Extended | 13 Umami event names (up from PRD's 8, due to page-type disambiguation) |

**NFR Coverage:**

| NFR | Coverage | Notes |
|---|---|---|
| NFR1–NFR3 (performance) | ✅ | Sequential cascade with 30ms threshold; result caps; `EMPTY_STATE_THRESHOLD` constant |
| NFR5–NFR8 (accessibility) | ✅ | WCAG 2.1 AA breadcrumbs defined; semantic HTML in enforcement rules |
| NFR9–NFR11 (integration) | ✅ | 13 Umami events; schema.org pre-deploy validation; GSC monitoring |

### Corrections Applied

**Test file location fix:** Venue organizer tests belong to the `places` app, not `events`:

```
places/tests/views/
└── test_place_detail.py   (existing — add venue organizer tests here)
```

**Additional enforcement rules:**

- Use semantic HTML for all new content sections: `<section>`, `<h2>`, `<ul>`/`<li>` — never `<div>` substitutes for structural elements (NFR6)
- Place `<nav aria-label="breadcrumb">` before the page `<h1>` in template source order

**`event_date` timezone verification pattern:**

Before implementing any JSON-LD `startDate` field, confirm with:
```python
from django.utils import timezone
assert timezone.is_aware(Event.objects.first().event_date), \
    "event_date must be timezone-aware for schema.org startDate"
```

### Architecture Completeness Checklist

- [x] Project context analysed; scale and complexity assessed
- [x] 28 FRs mapped to files; 11 NFRs addressed
- [x] FR13 deviation documented; agents warned not to implement original
- [x] Critical blockers identified (`event_date`, `Event.CATEGORY` index, `SLUG_MAP`)
- [x] 5 ADRs documented with rationale
- [x] 2 new service files defined with function signatures
- [x] 1 new view, 2 new templates, 1 new template partial
- [x] 5 new URL patterns specified
- [x] 13 Umami event names defined with page-type and interaction
- [x] Context variable names locked (9 variables)
- [x] Test file locations specified (3 new, 5 modified across events + places)
- [x] All enforcement rules complete

### Architecture Readiness Assessment

**Overall status:** READY FOR IMPLEMENTATION

**Confidence level:** High

**Key strengths:**
- Zero infrastructure risk — no new containers, no schema migrations
- All data already exists; implementation is queryset + template work only
- Service layer pattern established and consistent with existing codebase
- Clear pre-implementation blockers prevent silent failures

**Deferred to post-MVP:**
- URL translation to Spanish
- Category-level city filtering
- Per-page `<title>` / meta description generation

### Implementation Handoff

**First steps before writing any code:**
1. Verify `event_date` timezone-awareness
2. Verify `Event.CATEGORY` constant names in `events/models/event.py`
3. Verify `Event.CATEGORY` field has a DB index
4. Confirm Umami `<script>` is in `desparchado/templates/layout/base.html`

**Implementation order (suggested):**
1. Service functions (`related_events.py`, `cross_entity.py`) + tests
2. Breadcrumb partial + base template `{% block structured_data %}`
3. View changes (event detail, speaker, organizer, place) + tests
4. Category pages + URL config + tests
5. JSON-LD blocks (after `event_date` confirmed timezone-aware)
6. Umami attributes (last — verify all 13 before release)