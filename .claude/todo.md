# Improvement suggestions

## 1. Event form: inline organizer and place creation

**Current problem**: Creating a new organizer or place while filling in the event form requires opening a new browser tab, completing a separate form, then manually returning and re-selecting the new item in the autocomplete. Context is lost and the UX is fragmented.

**Suggested solution**: Replace the "open in new tab" pattern with a modal dialog using `<dialog>` (native HTML5, no library needed).

**How it would work**:
1. Add a `+` button next to the organizer and place Select2 fields.
2. Clicking `+` opens a `<dialog>` containing a lightweight inline form (name, website URL for organizer; name, address, city for place).
3. On submit, POST to a new dedicated endpoint (e.g. `/events/organizers/quick-add/`) via `fetch`.
4. On success, the endpoint returns `{ id, name }` JSON; the JS code adds the new option to the Select2 field and selects it automatically.
5. Dialog closes.

**Backend changes**:
- Add `OrganizerQuickCreateView` and `PlaceQuickCreateView` — POST-only, login required, return JSON `{ id, name }`.
- Apply the same quota checks already used by the full create views.

**Frontend changes**:
- A small reusable `quick-create-dialog.ts` script (no Vue needed, plain JS with `<dialog>`).
- Inject the `+` button via the existing form template or a custom crispy layout element.

**Files to change**:
- `events/views/organizer_create.py` — add `OrganizerQuickCreateView`
- `places/views/place_create.py` — add `PlaceQuickCreateView`
- `events/urls.py`, `places/urls.py` — register new endpoints
- `events/templates/events/event_form.html` — add `+` buttons and `<dialog>` HTML
- New: `desparchado/frontend/scripts/quick-create-dialog.ts`

---

## 2. Frontend architecture: remove the dual mounting system

**Current problem**: There are two component systems running in parallel:
- `mount-vue.ts` — mounts Vue components via `data-vue-component` attributes
- `init-components.ts` / `event-container.ts` — a separate class-based system using `data-component` attributes

This creates two mental models, two initialization pipelines, and makes it unclear where new interactive behaviour should go.

**Suggested solution**: Consolidate everything into the `data-vue-component` / `mount-vue.ts` system. `EventContainer` is the only class-based component; it could be rewritten as a Vue component that accepts a `data-url` prop and performs the fetch internally.

**Benefits**: One mounting pattern to learn, one place to debug initialization, straightforward to add new interactive components.

**Files to change**:
- Replace `desparchado/frontend/scripts/event-container.ts` with `desparchado/frontend/components/presentational/components/event-container/EventContainer.vue`
- Update `desparchado/frontend/scripts/home.ts` to remove class-based initialization
- Remove `desparchado/frontend/scripts/init-components.ts` once no longer needed

---

## 3. Frontend architecture: retire `old_main.ts`

**Current problem**: `old_main.ts` bundles several unrelated responsibilities: the organizer suggestion warning, generic JS utilities, and legacy Bootstrap interactions. It is imported globally on every page.

**Suggested solution**: Break it up. Move each behaviour to the module or template that actually needs it:
- Organizer suggestion warning → absorbed into the inline creation dialog (item 1 above)
- Any remaining Bootstrap JS interactions → inline `<script>` in the relevant template or a small dedicated `.ts` file registered only on the pages that need it

---

## 4. Frontend architecture: standardise API layer

**Current problem**: The `events/api/` folder has `events.ts` and `interfaces.ts` but these only cover the event list endpoint. Other backend interactions (autocomplete, suggestion endpoint, quick-create endpoints once added) are done ad-hoc via DAL's own JS or inline fetch calls.

**Suggested solution**: Expand the `desparchado/frontend/scripts/api/` folder to be the single place for all client-side HTTP calls. Add typed interfaces for every endpoint the frontend touches. This makes mocking and testing easier and gives new contributors a clear map of the FE/BE contract.

**Files to add/update**:
- `desparchado/frontend/scripts/api/organizers.ts` — quick-create, suggestion
- `desparchado/frontend/scripts/api/places.ts` — quick-create
- `desparchado/frontend/scripts/api/interfaces.ts` — extend with new types

---

## 5. Event form: speakers follow the same pattern as organizers

The same "new tab" problem exists for speakers. Once the organizer quick-create dialog is in place (item 1), apply the same pattern to the speaker field. The backend `SpeakerQuickCreateView` would accept name and optionally an image.

---

## 6. Remove `playground` app or document its purpose

The `playground` app exists but its purpose is unclear. If it is for local experimentation it should not be in `INSTALLED_APPS` in production settings. If it serves a real function, it should be documented in `CLAUDE.md`.

---

## 7. Replace `LocMemCache` with Redis in production

`base.py` configures `LocMemCache`. In production with 5 Gunicorn workers, each worker has its own memory cache — cached values are not shared across workers and the cache is lost on restart. A Redis-backed cache (e.g. `django-redis`) would fix this and also enable proper rate-limiting with `django-axes`.