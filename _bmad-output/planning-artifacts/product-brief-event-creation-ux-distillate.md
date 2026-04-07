---
title: "Product Brief Distillate: Event Creation UX Redesign"
type: llm-distillate
source: "product-brief-event-creation-ux.md"
created: "2026-04-05"
purpose: "Token-efficient context for downstream PRD creation"
---

# Detail Pack: Event Creation UX Redesign

## Current State (What We're Replacing)

- **Event form** (`/events/add/`, `/events/<pk>/edit/`): Traditional Django + crispy-forms. Two separate form classes: `EventCreateForm` (fewer fields) and `EventUpdateForm` (adds `is_published`, `speakers`, `image_source_url`, `price`). The create/edit split causes field inconsistency — speakers only appear on edit. Decision: v1 unifies them.
- **Related entity widgets**: `django-autocomplete-light` (DAL) Select2 widgets for organizers (M2M), place (FK), speakers (M2M). These call separate AJAX autocomplete endpoints (`/events/organizer-autocomplete/`, `/places/places-autocomplete/`, `/events/speaker-autocomplete/`).
- **New-tab pattern**: Inline "Añadir nuevo organizador / lugar / presentador" buttons open `/events/organizers/add/`, `/places/add/`, `/events/speakers/add/` in new tabs. No modal, no inline creation, no state handoff back to the parent form. High contributor drop-off risk.
- **No live preview**: Form submits to see result. No client-side feedback during entry.
- **No form analytics**: Umami is active (script in `base.html`, website ID `1ccee07e-d5e4-4c95-a986-3b1569f29d9b`) but fires only standard page views. Zero funnel visibility on the creation flow.
- **Organizer deduplication today**: A dynamic help text appears warning about duplicates. Blocks the user without guiding them on how to proceed. Known pain point — approach is explicitly rejected.

## Technical Architecture Decisions

### Vue SPA over HTMX — Rationale
- Live preview requires reactive state bound to multiple form fields simultaneously. HTMX's partial-swap model doesn't support this without significant JavaScript glue.
- M2M list management (adding/removing multiple organizers and speakers before final submit) requires an in-memory array that drives both the form state and the preview. Vue's reactivity handles this naturally; HTMX would need custom JS to manage the list anyway.
- Multi-step wizard with shared state across steps (e.g., title entered in Step 1 appears in preview during Step 3) is cleanest as a single Vue component tree.
- HTMX remains the right choice for simpler interactions elsewhere on the platform (the prior technical research recommendation stands for those cases).

### DRF Endpoints Needed (Don't Exist Yet)
Current API (`/events/api/v1/`) only exposes a paginated event list. The following need to be built:

| Endpoint | Method | Purpose |
|---|---|---|
| `/events/api/v1/organizers/search/` | GET `?q=` | Fuzzy search organizers — returns id, name, slug, image_url, description_snippet |
| `/events/api/v1/speakers/search/` | GET `?q=` | Fuzzy search speakers — same shape |
| `/places/api/v1/places/search/` | GET `?q=` | Fuzzy search places — returns id, name, slug, address, city_name, image_url |
| `/events/api/v1/organizers/` | POST | Create organizer inline (minimal fields: name, description, image) |
| `/events/api/v1/speakers/` | POST | Create speaker inline (name, description, image) |
| `/places/api/v1/places/` | POST | Create place inline (name, address, city, location PointField) |
| `/events/api/v1/events/` | POST | Create event (all fields, returns slug for redirect) |
| `/events/api/v1/events/<pk>/` | PUT/PATCH | Update event |
| `/events/api/v1/events/<pk>/image/` | POST | Image upload (multipart) — separate endpoint or part of create/update |

All POST endpoints must enforce user quota (same logic as existing `EventCreateView`, `OrganizerCreateView`, etc.). Quota system: `UserSettings.check_*_quota()` — raises or returns False if daily limit reached. Superusers bypass.

### Fuzzy Search Implementation
- Enable `pg_trgm` extension: `CREATE EXTENSION IF NOT EXISTS pg_trgm;`
- Add GIN trigram index on `name` field for Organizer, Speaker, Place
- DRF search view uses `SIMILARITY(name, query) > 0.2` threshold or `name ILIKE %query%` as fallback
- `unaccent` extension already in use for full-text search — combine with trigram for accent-insensitive fuzzy match
- Return results sorted by similarity score descending

### Frontend Architecture
- New Vue SPA entry point (e.g., `event-form.ts`) loaded only on create/edit pages via django-vite `{% vite_asset %}`
- Existing `mount-vue.ts` auto-mount system not used for this — the wizard is a full page component, not an island
- Reuse existing `api/` pattern: add `api/organizers.ts`, `api/speakers.ts`, `api/places.ts`, `api/events.ts` with typed interfaces
- CSRF token: pass from Django template as a `data-` attribute on the mount element; include in all DRF POST headers
- Image upload: multipart form data via `fetch`, not JSON — keep as a separate request after entity creation or as part of the final submit payload

### Place Creation Complexity
- Place has a PostGIS `PointField` for coordinates — currently uses `GoogleMapPointFieldWidget` (requires `GOOGLE_MAPS_API_KEY`)
- Inline place creation modal needs a map picker. Options:
  - **Leaflet + OpenStreetMap** (no API key, already used by `django-map-widgets` for admin): preferred
  - **Address geocoding**: use Nominatim (OSM, free) to convert typed address to coordinates automatically — reduces friction vs manual pin placement
- City FK: dropdown from existing City records — manageable as a simple `<select>`

## Field Inventory and Required/Optional Classification

### Step 1 — Sobre el evento
| Field | Required | Notes |
|---|---|---|
| title | Yes | Writing guidance tip shown inline |
| description | Yes | Rich text (bold, italic, underline — matches Figma toolbar) |
| event_source_url | Yes | URL of event page (Instagram, Facebook, website) |
| category | Yes | Visual card selection (5 categories: literature, society, environment, science, art) |
| organizers | Yes (≥1) | Search-first M2M; inline creation modal |

### Step 2 — Fecha y hora
| Field | Required | Notes |
|---|---|---|
| event_date | Yes | Datetime picker, timezone America/Bogota |

### Step 3 — Detalles adicionales
| Field | Required | Notes |
|---|---|---|
| place | Yes | Search-first FK; inline creation modal (with map picker) |
| image | No (opcional) | Drag-and-drop upload; affects listing quality — shown prominently |
| image_source_url | No (opcional) | Attribution URL for image |
| speakers | No (opcional) | Search-first M2M; inline creation modal |
| price | No (opcional) | Free-text or numeric; many events are free |
| is_published | No (opcional) | Toggle — allow contributor to save as draft vs publish immediately |

### Inline Creation Modal Fields (minimal set)
| Entity | Fields in modal | Fields deferred to edit |
|---|---|---|
| Organizer | name, description, image | website_url, facebook_url, twitter_url, instagram_url |
| Speaker | name, description, image | — (no deferred fields) |
| Place | name, address, city (dropdown), location (map picker) | website_url, image |

## Quota System Behavior in the Wizard
- Current quotas: Events 10/day, Organizers 5/day, Speakers 5/day, Places 5/day
- Superusers bypass all quotas
- **Graceful handling needed**: If a contributor hits their organizer quota mid-wizard (while trying to create an inline organizer), the modal should show a clear message ("Hoy alcanzaste el límite de nuevos organizadores. Puedes continuar con el evento y agregar el organizador mañana, o buscar uno existente.") — not a generic 403
- Quota state should be checked before opening the inline creation modal, not only on submit — reduces wasted effort
- Quota check endpoint: can reuse existing view logic or expose a lightweight `/users/api/quota/` endpoint

## Umami Custom Event Instrumentation Plan
All events use `umami.track()` with structured names:

| User action | Event name | Properties |
|---|---|---|
| Wizard started | `event_form_started` | `{ flow: 'create' | 'edit' }` |
| Step completed | `event_form_step_completed` | `{ step: 1 | 2 | 3 }` |
| Step abandoned (back button / navigation away) | `event_form_step_abandoned` | `{ step: 1 | 2 | 3 }` |
| Organizer search performed | `organizer_search` | `{ results_count: n }` |
| Organizer selected from search | `organizer_selected_existing` | — |
| Inline organizer creation opened | `organizer_create_modal_opened` | — |
| Inline organizer created | `organizer_created_inline` | — |
| Same pattern for speaker and place | — | — |
| Image uploaded | `event_image_uploaded` | — |
| Form submitted successfully | `event_form_submitted` | `{ flow: 'create' | 'edit', has_image: bool, has_speakers: bool }` |
| Quota limit hit | `event_form_quota_hit` | `{ entity: 'organizer' | 'speaker' | 'place' | 'event' }` |

## Rejected Approaches
- **Dynamic help text for duplicates** (current approach): Blocks user without guiding them. Explicitly rejected by Vera — replaced by search-as-you-type entity cards.
- **HTMX for the wizard**: Technically feasible for simple field validation, but reactive live preview + M2M list management tips the balance to Vue. HTMX remains appropriate for other form interactions on the platform.
- **Progressive disclosure of optional fields**: Hiding optional fields and revealing them as the user progresses creates "is there more?" uncertainty. All fields visible from the start, with explicit "(opcional)" labels and visual weight hierarchy.
- **Speaker-only-on-edit split** (current form design): Confusing for contributors who expect create and edit to have the same fields. Unified field set in v1.
- **Google Maps for inline place creation**: Requires API key, costs money. Replace with Leaflet + OSM for the inline modal (consistent with the admin's `LeafletPointFieldWidget`).
- **AI-assisted suggestions**: Out of scope for v1 — not enough contributor volume data to train on, and adds complexity before the baseline is established.

## Open Questions Not Resolved in Brief
- **Image upload via API**: Should image upload be part of the event create/update payload (base64 or multipart) or a separate endpoint? Separate endpoint is cleaner for large files but requires two requests on submit. Needs decision at PRD/architecture stage.
- **Edit form pre-population**: For the edit flow, the Vue SPA needs to load existing event data on mount. A `GET /events/api/v1/events/<pk>/` endpoint with full field detail is needed — verify whether to reuse the existing event API or create a separate admin-detail endpoint.
- **`is_published` default on create**: Currently new events are unpublished by default. Should the wizard default to "save as draft" or "publish immediately"? Draft is safer but may reduce visible event supply.
- **Place location on mobile**: Manual pin placement on a map is awkward on mobile. Nominatim geocoding from address is a better mobile UX but requires an async call and user confirmation. Worth designing explicitly.
- **Recurrent events**: The `IEvent` TypeScript interface has an `is_recurrent` flag. Not currently exposed in the form. Leave out of v1 scope but don't design around it.

## Scope Boundaries (Explicit)
**In v1:**
- Wizard create + edit parity (same fields, same steps)
- Inline creation for organizer, place, speaker
- Fuzzy search with `pg_trgm`
- Live preview panel (updates reactively on title, description, image, category)
- Umami full funnel instrumentation
- Drag-and-drop image upload

**Out of v1:**
- Standalone organizer/place/speaker edit pages (unchanged)
- Social URL fields in inline creation modals (deferred to post-creation edit)
- Bulk import / spreadsheet sync (separate dashboard feature)
- AI suggestions
- Recurrent event fields
- Contributor dashboard / event management list (separate initiative)