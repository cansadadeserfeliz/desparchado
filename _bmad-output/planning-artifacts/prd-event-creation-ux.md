---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary, step-03-success, step-04-journeys, step-05-domain, step-06-innovation, step-07-project-type, step-08-scoping, step-09-functional, step-10-nonfunctional, step-11-polish, step-12-complete]
status: complete
completedAt: "2026-05-31"
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-event-creation-ux.md
  - _bmad-output/planning-artifacts/product-brief-event-creation-ux-distillate.md
  - _bmad-output/planning-artifacts/research/technical-vue-vs-vanilla-fe-django-drf-research-2026-04-05.md
  - docs/architecture.md
  - design-mockups: [event-creation-1.png, organizers-widget.png, speaker-widget.png, place-widget.png, figma-desparchado/]
workflowType: 'prd'
classification:
  projectType: web_app
  domain: general
  complexity: medium
  projectContext: brownfield
technicalDecisions:
  entryPoint: event-form.ts (dedicated Vite entry, not mount-vue.ts)
  rootComponent: EventWizard.vue owns all form state
  stepComponents: Step1/Step2/Step3 via v-show (always mounted)
  livePreview: EventPreview.vue, always visible, receives state as props
  condensedMode: hides help text and field descriptions; keeps 3-step navigation
  editIdentifier: slug (not PK)
  imageUpload: browser File in reactive state for preview; multipart on final POST
  stepValidation: blocking (Paso siguiente disabled until required fields valid)
  componentVariations: EventCreateForm + EventEditForm extending shared base
  multiDate: out of MVP - single event_date only
---

# Product Requirements Document — Event Creation & Editing UX

**Project:** Desparchado
**Author:** Vera
**Date:** 2026-05-31

---

## Executive Summary

Desparchado's event supply is bottlenecked by its creation experience. The current interface — two inconsistent Django form classes, a new-tab workflow for related entity creation, and zero funnel instrumentation — produces duplicate organizers, speakers, and places, and drops contributors before a single event is complete. The contributors who most need to be reached — independent cultural organizers, workshop facilitators, reading club coordinators — attempt submission once and leave if the process is confusing.

This PRD defines requirements for the **Event Creation & Editing UX**: a single-page, three-step Vue 3 wizard that replaces the existing `EventCreateForm`/`EventUpdateForm` pair with a guided, interactive experience backed by new DRF endpoints. The wizard covers both create (`/events/add/`) and edit (`/events/<slug>/edit/`) flows with full field parity. A live preview panel renders the event card in real time as the contributor types. A condensed rendering mode hides contextual help text for experienced or institutional contributors who submit multiple events per day.

Entity selection (organizers, speakers, places) is search-first, using accent-insensitive fuzzy matching built for Colombian Spanish — "feria libro" surfaces "Feria Internacional del Libro de Bogotá"; "BLAA" surfaces "Biblioteca Luis Ángel Arango". Existing records surface before a creation option appears.

All required infrastructure exists. Vue 3 + Vite + DRF are in production; the work is additive. MVP requires: (1) the Vue SPA component tree replacing two Django form views, (2) accent-insensitive fuzzy search endpoints for organizer, speaker, and place lookup, (3) inline creation modals for all three entity types, and (4) a single multipart DRF endpoint for event creation/update. No Event model schema changes required.

### What Makes This Special

**Search-before-create mandate.** The contributor cannot jump directly to entity creation. They search first — and the fuzzy, accent-insensitive matching ensures near-duplicates surface before "Crear nuevo" appears. Deduplication becomes the path of least resistance, not an afterthought.

**Single-submit architecture with in-browser state.** Three visual steps; one atomic payload. All state accumulates in the Vue component tree. The image preview is immediate — browser `File` object held in state, uploaded only on final submit. No partial saves, no orphaned records from abandoned mid-flow submissions.

**Direct creator voice.** "Publica tu evento" — unambiguous, active, addressed to the person with an event to share. Distinct from the discovery-oriented "parche" register used for the audience browsing events.

## Project Classification

- **Type:** Web application — brownfield, extending existing Django MPA
- **Domain:** General — cultural events; no regulated industry requirements
- **Complexity:** Medium — standard DRF/Vue patterns; complexity concentrated in Vue SPA architecture (reactive multi-step state, live preview, inline modal composition) and accent-insensitive entity search
- **Stack:** Django · DRF · PostgreSQL · Vue 3 + Vite · TypeScript

---

## Success Criteria

### User Success

- A contributor completes event creation on first attempt in under 5 minutes
- Wizard completion rate >= 60% of started sessions within 60 days of launch
- A contributor searching for an existing organizer, speaker, or place finds the correct record within 3 keystrokes, including queries with missing or incorrect accents (e.g. "feria libro" → "Feria Internacional del Libro de Bogotá")
- Contributors can create a new organizer, speaker, or place inline without leaving the wizard

### Business Success

- Events created per month increases >= 40% within 60 days of launch (baseline measured at launch day)
- Duplicate organizer, speaker, and place creation rate decreases >= 50% within 90 days of launch (baseline measured at launch day)
- Full contributor funnel visible in Umami (wizard start → step completions → submit) within 30 days of launch

### Technical Success

- Entity search returns results in <= 300ms at 95th percentile
- Edit pre-population completes in <= 500ms
- Image upload succeeds for files <= 10MB; browser preview renders before upload
- Zero orphaned records on wizard abandonment — single-submit guarantee, no partial saves
- All DRF endpoints enforce existing quota system; quota-exceeded responses include a human-readable message
- All Umami custom events live and verified on launch day

### Measurable Outcomes

| Metric | Baseline | Target | Timeline |
| --- | --- | --- | --- |
| Events created per month | Measure at launch | +40% | 60 days post-launch |
| Wizard completion rate | No data | >= 60% | 60 days post-launch |
| Duplicate entity creation rate | Measure at launch | -50% | 90 days post-launch |
| Contributor funnel visibility | No data | Live in Umami | Launch day |
| Time-to-first-event (new contributor) | No data | < 5 min | Establish within 30 days |

---

## Product Scope

### MVP — Minimum Viable Product

- `EventCreateForm` + `EventEditForm` Vue components (shared base, two explicit variations)
- **Step 1:** Title, Description (rich text B/U/I), Image (drag/drop, <= 10MB), Organizers (search-first, required >= 1), Speakers (search-first, optional)
- **Step 2:** Date/Time (single date, America/Bogota timezone), Place (search-first, required)
- **Step 3:** Category (5 visual cards: Literatura, Arte, Sociedad, Ciencia, Medio Ambiente), Price (optional free text), Event source URL (optional), is_published toggle
- Live preview (`EventPreview.vue`) always visible alongside the form
- Condensed mode: hides field help text and descriptions; keeps 3-step navigation
- Blocking step validation: "Paso siguiente" disabled until required fields on current step are valid
- Accent-insensitive fuzzy search for organizer, speaker, and place autocomplete
- Inline creation modals: Organizer (name, description, image, website URL), Speaker (name, description, image), Place (name, city dropdown, address, Leaflet map picker)
- Edit flow: slug-based pre-population from `GET /api/v1/events/{slug}/`
- Umami instrumentation: wizard start, step completions/abandonments, entity searches, inline creations, quota hits, final submit
- Quota enforcement on all entity creation endpoints; clear quota-exceeded messaging in modals

### Growth (Post-MVP)

- Social URL fields (Facebook, Twitter, Instagram) in organizer inline creation modal
- Contributor event management dashboard (list of own events with edit/unpublish actions)
- Quota self-service elevation request for institutions hitting daily limits
- Category and city filter on contributor's event list

### Vision (Future)

- Recurring event series management
- Co-organizer collaboration (multiple contributors editing the same event)
- AI-assisted title/description suggestions (once contributor volume data exists)
- Publisher reputation signals and verified contributor status
- Smart entity suggestions based on user submission history (most-used organizers and places surfaced at top of autocomplete)

---

## Project Scoping & Risk Mitigation

### MVP Strategy

**Approach:** Experience MVP — prove that a frictionless contribution flow increases event supply and reduces duplicate entity creation. The minimum viable product is a fully working wizard covering all five contributor journeys with Umami instrumentation live from day one.

**Resources:** Single developer (Django/Python + Vue 3/TypeScript). No design resources required — Figma specs are complete. No new infrastructure — Vue 3 + Vite + DRF + PostgreSQL are all in production.

### Technical Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Fuzzy search insufficient for Spanish variants | Medium | Validate pg_trgm + unaccent against real organizer/speaker name corpus before committing; pgvector as escalation path if results are poor |
| Vue SPA bundle size impact on other pages | Low | Vite code-splitting ensures `event-form.ts` loads only on create/edit routes; no impact on MPA pages |
| Multipart POST timeout for large images on slow connections | Low | 10MB limit enforced client-side before upload attempt; compression as post-MVP option |
| Leaflet map UX on mobile | Medium | Accepted for MVP (touch-compatible); address geocoding improvement deferred to post-MVP |

### Market Risks

| Risk | Mitigation |
| --- | --- |
| Contributors don't discover or trust the new flow | Umami funnel live on launch day; 30-day review cycle; iterate on drop-off points |
| Existing duplicate data not cleaned by this feature | Search-first prevents new duplicates; existing duplicates require separate data quality tooling (future PRD) |
| Quota limits block institutional contributors | Superuser elevates quota via Django admin `UserSettings`; no self-service in MVP |

---

## User Journeys

### Journey 1: Catalina — The First-Time Organizer (Primary, Success Path)

Catalina teaches ceramics in Bogotá and runs a monthly workshop at her studio, Taller de Barro. She clicks "Crea un evento." Not logged in, she's redirected to login and returned to the wizard on completion.

Step 1: Title, description, photo — the live preview updates in real time alongside the form. She searches for her organizer: "Taller de Barro." Zero results. "Crear nuevo" appears. She fills the modal (name, description, image, website URL) in under a minute. The organizer chip appears. She leaves speakers empty.

Step 2: Date and time entered. She searches for the place: "Taller de Barro" — zero results (place and organizer are separate entities). She creates a new Place: name, city dropdown, address, Leaflet map pin. The place chip appears.

Step 3: She picks Arte from the five visual cards, leaves price blank (optional), adds her registration URL, toggles is_published on. "Publicar." Done in under 5 minutes. No second tab opened.

*On mobile (375px): the live preview is hidden; a "Ver vista previa" button opens it in a modal. The Place modal stacks the map below the address fields.*

**Capabilities revealed:** Auth gate → redirect to login → return to wizard; Step 1 organizer inline creation; Step 2 place inline creation (separate entity, Leaflet map); "Crear nuevo" only on zero results; blocking step validation; live preview; category cards; publish toggle; mobile layout with preview modal.

---

### Journey 2: Sebastián — Quotas and Edge Cases (Primary, Edge Cases)

**Scenario A — Single canonical search result:**
Sebastián types "Libreria Nacional" (no accent). Accent-insensitive normalization returns one result: "Librería Nacional." One match, no ambiguity. He selects it and moves on. If he clicks away from the organizer field without selecting, the field immediately shows: "Selecciona un organizador antes de continuar."

**Scenario B — Event quota fires before form loads:**
On a different afternoon, Sebastián has hit his daily event limit. He clicks "Crea un evento." Before the wizard renders, he sees: "Hoy alcanzaste el límite de eventos que puedes crear. Vuelve mañana para continuar publicando." The form never loads.

**Scenario C — Organizer quota hit inside modal:**
Mid-wizard, he tries to create a third new organizer. The inline modal opens; "Agregar organizador" shows: "Hoy alcanzaste el límite de nuevos organizadores." He closes the modal — wizard state is intact — and continues with the organizers already added.

**Scenario D — Draft save, MVP limitation:**
He saves with is_published off. In MVP there is no contributor event list — his draft is only accessible via a bookmarked or shared URL. Known MVP limitation; contributor event management is Growth scope.

**Capabilities revealed:** Accent-insensitive search returning one canonical result; required-field validation error on focus-out without selection; event quota check before form load; organizer quota messaging inside modal without state loss; draft save; MVP draft discoverability constraint noted.

---

### Journey 3: Ana María — The Institutional Contributor (Power User)

Ana María's `UserSettings` quota has been elevated to 50 events/day by a superuser via the Django admin. She toggles condensed mode — help text disappears, fields render compact, three-step navigation stays. She works at speed: organizer search (Idartes, two keystrokes), speakers if needed, date, venue from search, category, URL, publish. Ten events in under 40 minutes. The image upload zone is visually de-emphasized in condensed mode, making it easy to skip for events without a ready image.

When a POST returns a validation error, Vue displays it inline without losing any other wizard state. She corrects only the flagged field and resubmits.

**Capabilities revealed:** Admin-configured quota elevation via Django admin `UserSettings`; condensed mode (compact fields, hidden help text, steps retained); optional image clearly skippable; backend validation errors surfaced in Vue without state loss.

---

### Journey 4: Sebastián Returns — The Edit Flow (Primary, Edit Path)

Three days after publishing his event, Sebastián spots a time error. He navigates to the event page and clicks "Editar." Django evaluates his edit permission server-side before rendering the template — if he lacks permission, Vue is never initialized and he's redirected to the permission denied page. Since he's the creator, the template renders and `EventEditForm` mounts, calling `GET /api/v1/events/{slug}/` to hydrate all fields. He navigates to Step 2, corrects the time, clicks "Guardar." A `PATCH /api/v1/events/{slug}/` fires. Done.

If he attempts to navigate away mid-edit with unsaved changes, the browser fires: "Leave site? Changes you made may not be saved."

**Capabilities revealed:** Edit permission check 100% server-side — Vue never loads for unauthorized users; slug-based pre-population; `EventEditForm` variation ("Guardar" submit button); `PATCH` endpoint; `beforeunload` unsaved-changes warning.

---

### Journey 5: Vera — The Data Steward (Admin)

Vera creates events via the same wizard as any contributor — no quota ceiling for superusers, no other UI difference. She reviews three newly submitted events: each has a complete organizer profile because the inline creation modal enforced minimum fields. She approves all three without edits.

She grants Ana María editor access to the Idartes organizer by adding her to the `editors` M2M field in the Django admin. From that point Ana María can edit the Idartes record directly.

Data quality work — finding and merging duplicate organizers, speakers, and places; fixing errors in events created by other users — is handled via the dashboard and Django admin. **Out of scope for this PRD.** A separate PRD is needed for admin tooling covering duplicate detection and entity merging.

**Capabilities revealed:** Superuser uses same wizard (no quota); inline modals enforce minimum data quality at creation time; per-organizer editor delegation via Django admin; data quality tooling flagged as future PRD.

---

### Journey Requirements Summary

| Journey | Capabilities Required |
|---|---|
| Catalina (first-time, success) | Auth gate; organizer + place inline creation (separate entities); "Crear nuevo" on zero results only; live preview; mobile layout with preview modal; blocking validation; category cards; publish toggle |
| Sebastián (edge cases) | Accent-insensitive single canonical result; required-field focus-out validation; event quota before form load; organizer quota inside modal without state loss; draft save; MVP draft discoverability constraint |
| Ana María (institutional) | Admin-configured quota elevation; condensed mode; optional image skippable; BE validation errors surfaced inline without state loss |
| Sebastián — edit | Server-side permission check (Vue never loads if denied); slug pre-population; EventEditForm / PATCH; beforeunload warning |
| Vera (data steward) | Same wizard for superusers (no quota); minimum fields enforced by inline modals; per-organizer editor delegation via Django admin; data quality tooling as future PRD |

---

## Technical Requirements

### Architecture Overview

The event creation wizard **replaces** the existing `EventCreateView` and `EventUpdateView` Django form views, their `EventCreateForm`/`EventUpdateForm` classes, and the django-autocomplete-light Select2 widgets. The new implementation is a **Vue 3 SPA** mounted on `/events/add/` and `/events/<slug>/edit/` via a dedicated Vite entry point (`event-form.ts`), loaded through `{% vite_asset %}`. This entry point is independent of the existing `mount-vue.ts` island auto-mount system. All other site pages remain Django server-rendered MPA.

### Browser & Device Support

- **Desktop:** Chrome, Firefox, Safari, Edge — last 2 major versions
- **Mobile:** Min 375px viewport width; layout stacks vertically
- **No IE support**

### Responsive Design

| Viewport | Layout | Live Preview |
|---|---|---|
| >= 768px | Side-by-side: form left, preview right | Always visible |
| < 768px | Single column, stacked | Hidden; "Ver vista previa" opens modal |

- Inline creation modals: full-width on mobile, constrained max-width on desktop
- Leaflet map in Place modal: touch-compatible; address geocoding deferred to post-MVP

### Accessibility

- **MVP:** Color contrast ratio compliance — all text, interactive elements, and error states meet WCAG 2.1 AA contrast minimums (4.5:1 for normal text, 3:1 for large text and UI components)
- **Post-MVP:** Full WCAG 2.1 AA (ARIA roles, focus management, keyboard navigation, screen reader compatibility)

### Implementation Patterns

- `EventCreateForm.vue` / `EventEditForm.vue` extend shared `EventWizardBase` composition
- Step components (`Step1.vue`, `Step2.vue`, `Step3.vue`) always mounted via `v-show`
- Entity search components emit `entity:selected` and `entity:created` to root state
- CSRF token passed from Django template via `data-csrf` attribute on mount element; included in all DRF request headers
- `beforeunload` event handler active when wizard has unsaved state
- `MAX_IMAGE_SIZE_MB = 10` defined as a named constant in shared frontend constants file

---

## Functional Requirements

### Wizard Navigation & Layout

- **FR1:** Unauthenticated users who access the event creation wizard are redirected to login and returned to the wizard on completion
- **FR2:** Contributors can navigate a three-step event wizard (Step 1: About the event; Step 2: Date, time, and place; Step 3: Additional details)
- **FR3:** Contributors can advance to the next step only when all required fields on the current step are valid
- **FR4:** Contributors can toggle a condensed display mode that hides field guidance text and descriptions while keeping step navigation intact
- **FR5:** Contributors on viewports below 768px can access the live preview via a dedicated button that opens it in an overlay
- **FR6:** Contributors who attempt to leave the wizard with unsaved state receive a browser navigation warning

### Event Fields

- **FR7:** Contributors can enter an event title
- **FR8:** Contributors can enter a rich-text event description with bold, underline, and italic formatting
- **FR9:** Contributors can upload an image for the event via drag-and-drop or file picker
- **FR10:** Contributors can enter a single event date and time (America/Bogota timezone)
- **FR11:** Contributors can select one or more event organizers (at least one required)
- **FR12:** Contributors can select zero or more event speakers (optional)
- **FR13:** Contributors can select one event place (required)
- **FR14:** Contributors can select one event category from five visual options (Literatura, Arte, Sociedad, Ciencia, Medio Ambiente)
- **FR15:** Contributors can enter an optional event price
- **FR16:** Contributors can enter an optional event source URL
- **FR17:** Contributors can set event publication status (published or draft) before submitting

### Entity Search & Selection

- **FR18:** Contributors can search for existing organizers, speakers, and places using accent-insensitive fuzzy matching that normalizes Spanish diacritics and common abbreviations
- **FR19:** Entity search returns one canonical record per match — accent and spelling variants of the same entity resolve to the same result
- **FR20:** The option to create a new entity appears only when a search returns zero results
- **FR21:** Required entity fields (organizer, place) display an inline validation error when the contributor moves focus away without selecting a result
- **FR22:** Contributors can select multiple organizers and multiple speakers; each selection appears as a removable chip in the field

### Inline Entity Creation

- **FR23:** Contributors can create a new organizer (name, description, image, website URL) inline without leaving the wizard
- **FR24:** Contributors can create a new speaker (name, description, image) inline without leaving the wizard
- **FR25:** Contributors can create a new place (name, city, address, map-based coordinates) inline without leaving the wizard
- **FR26:** The wizard preserves all previously entered data when an inline creation modal is opened or closed

### Image Handling

- **FR27:** The system validates image file size on selection and displays an error immediately if the file exceeds the configured maximum; the maximum size is shown in the field guidance text
- **FR28:** Contributors can preview their uploaded image in the live preview panel before submitting

### Quota & Access Control

- **FR29:** Contributors who have reached their daily event creation quota see an informational message before the wizard renders; the form is not displayed
- **FR30:** Contributors who reach an entity creation quota mid-wizard see a human-readable message inside the inline creation modal; all other wizard state is preserved
- **FR31:** Superusers can create and edit events through the same wizard without quota restrictions
- **FR32:** Superusers can configure per-user daily quota limits via the administration interface

### Edit Flow

- **FR33:** Contributors can edit their own events via a pre-populated wizard identified by event slug
- **FR34:** The edit wizard pre-populates all fields from the existing event record on load
- **FR35:** The system prevents unauthorized users from accessing the edit wizard at the server level before any frontend code initializes; unauthorized users are redirected to a permission-denied page
- **FR36:** Contributors can submit edits as a single atomic update to the existing event record

### Live Preview

- **FR37:** Contributors can view a real-time preview of the event card as it will appear on the platform, updated as they type
- **FR38:** The live preview reflects the current title, description, image, and category

### Backend Validation

- **FR39:** The system displays backend validation errors inline against the relevant fields without clearing other wizard state, allowing the contributor to correct only the flagged fields and resubmit

### Analytics & Instrumentation

- **FR40:** The system records when a contributor starts the event creation or edit wizard
- **FR41:** The system records when a contributor completes or abandons each wizard step
- **FR42:** The system records each entity search performed, including whether an existing result was selected or a new entity was created inline
- **FR43:** The system records when a contributor encounters a quota limit
- **FR44:** The system records when a contributor successfully submits an event, including whether it was created or updated

---

## Non-Functional Requirements

### Performance

- **NFR1:** Entity search endpoints (organizer, speaker, place) return results in <= 300ms at the 95th percentile
- **NFR2:** Edit pre-population (`GET /api/v1/events/{slug}/`) completes in <= 500ms
- **NFR3:** Wizard initial load (Vue bundle parse and mount) completes in <= 2 seconds on a 4G connection
- **NFR4:** Live preview updates in <= 50ms after any keystroke — local Vue state only, no network call
- **NFR5:** Image preview renders immediately on file selection using `URL.createObjectURL`; no upload occurs until final submit

### Security

- **NFR6:** All wizard form submissions include a valid CSRF token; requests without one are rejected server-side
- **NFR7:** Edit access is enforced at the Django view level before the template renders; unauthorized requests receive a 403 and are redirected to the permission-denied page — Vue is never initialized
- **NFR8:** All DRF endpoints require an authenticated session; unauthenticated requests return 401

### Accessibility

- **NFR9:** All text, interactive elements, and error states in the wizard meet WCAG 2.1 AA color contrast minimums (4.5:1 for normal text; 3:1 for large text and UI components)

### Integration

- **NFR10:** All five Umami instrumentation event types (wizard start, step complete/abandon, entity search, quota hit, final submit) are verified live on launch day
- **NFR11:** Image uploads succeed for files up to `MAX_IMAGE_SIZE_MB`; the size limit is enforced client-side before any network request is initiated
- **NFR12:** The Leaflet map in the Place inline creation modal loads correctly on all supported browsers without requiring an external API key