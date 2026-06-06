---
stepsCompleted: [step-01-extract, step-02-design-epics, step-03-create-stories, step-04-final-validation]
inputDocuments:
  - _bmad-output/planning-artifacts/prd-event-creation-ux.md
  - _bmad-output/planning-artifacts/architecture-event-creation-ux.md
---

# desparchado - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for desparchado, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

- **FR1:** Unauthenticated users who access the event creation wizard are redirected to login and returned to the wizard on completion
- **FR2:** Contributors can navigate a three-step event wizard (Step 1: About the event; Step 2: Date, time, and place; Step 3: Additional details)
- **FR3:** Contributors can advance to the next step only when all required fields on the current step are valid
- **FR4:** Contributors can toggle a condensed display mode that hides field guidance text and descriptions while keeping step navigation intact
- **FR5:** Contributors on viewports below 768px can access the live preview via a dedicated button that opens it in an overlay
- **FR6:** Contributors who attempt to leave the wizard with unsaved state receive a browser navigation warning
- **FR7:** Contributors can enter an event title
- **FR8:** Contributors can enter a rich-text event description with bold, underline, and italic formatting
- **FR9:** Contributors can upload an image for the event via drag-and-drop or file picker
- **FR10:** Contributors can enter a single event date and time (America/Bogota timezone)
- **FR11:** Contributors can select one or more event organizers (at least one required)
- **FR12:** Contributors can select zero or more event speakers (optional)
- **FR13:** Contributors can select one event place (required)
- **FR14:** Contributors can select one event category from five visual options (Literatura, Arte, Sociedad, Ciencia, Medio Ambiente)
- **FR15:** Contributors can enter an optional event price
- **FR16:** Contributors can enter a required event source URL (must be a valid URL)
- **FR17:** Contributors can set event publication status (published or draft) before submitting
- **FR18:** Contributors can search for existing organizers, speakers, and places using accent-insensitive fuzzy matching that normalizes Spanish diacritics and common abbreviations
- **FR19:** Entity search returns one canonical record per match — accent and spelling variants of the same entity resolve to the same result
- **FR20:** The option to create a new entity appears only when a search returns zero results
- **FR21:** Required entity fields (organizer, place) display an inline validation error when the contributor moves focus away without selecting a result
- **FR22:** Contributors can select multiple organizers and multiple speakers; each selection appears as a removable chip in the field
- **FR23:** Contributors can create a new organizer (name, description, image, website URL) inline without leaving the wizard
- **FR24:** Contributors can create a new speaker (name, description, image) inline without leaving the wizard
- **FR25:** Contributors can create a new place (name, city, address, map-based coordinates) inline without leaving the wizard
- **FR26:** The wizard preserves all previously entered data when an inline creation modal is opened or closed
- **FR27:** The system validates image file size on selection and displays an error immediately if the file exceeds the configured maximum; the maximum size is shown in the field guidance text
- **FR28:** Contributors can preview their uploaded image in the live preview panel before submitting
- **FR29:** Contributors who have reached their daily event creation quota see an informational message before the wizard renders; the form is not displayed
- **FR30:** Contributors who reach an entity creation quota mid-wizard see a human-readable message inside the inline creation modal; all other wizard state is preserved
- **FR31:** Superusers can create and edit events through the same wizard without quota restrictions
- **FR32:** Superusers can configure per-user daily quota limits via the administration interface
- **FR33:** Contributors can edit their own events via a pre-populated wizard identified by event slug
- **FR34:** The edit wizard pre-populates all fields from the existing event record on load
- **FR35:** The system prevents unauthorized users from accessing the edit wizard at the server level before any frontend code initializes; unauthorized requests receive an HTTP 403 response rendering the `desparchado/templates/403.html` permission-denied template — Vue is never initialized
- **FR36:** Contributors can submit edits as a single atomic update to the existing event record
- **FR37:** Contributors can view a real-time preview of the event card as it will appear on the platform, updated as they type
- **FR38:** The live preview reflects the current title, description, image, and category
- **FR39:** The system displays backend validation errors inline against the relevant fields without clearing other wizard state, allowing the contributor to correct only the flagged fields and resubmit
- **FR40:** The system records when a contributor starts the event creation or edit wizard
- **FR41:** The system records when a contributor completes or abandons each wizard step
- **FR42:** The system records each entity search performed, including whether an existing result was selected or a new entity was created inline
- **FR43:** The system records when a contributor encounters a quota limit
- **FR44:** The system records when a contributor successfully submits an event, including whether it was created or updated

### NonFunctional Requirements

- **NFR1:** Entity search endpoints (organizer, speaker, place) return results in <= 300ms at the 95th percentile
- **NFR2:** Edit pre-population (`GET /api/v1/events/{slug}/`) completes in <= 500ms
- **NFR3:** Wizard initial load (Vue bundle parse and mount) completes in <= 2 seconds on a 4G connection
- **NFR4:** Live preview updates in <= 50ms after any keystroke — local Vue state only, no network call
- **NFR5:** Image preview renders immediately on file selection using `URL.createObjectURL`; no upload occurs until final submit
- **NFR6:** All wizard form submissions include a valid CSRF token; requests without one are rejected server-side
- **NFR7:** Edit access is enforced at the Django view level before the template renders; unauthorized requests receive an HTTP 403 response rendering the `desparchado/templates/403.html` permission-denied template — Vue is never initialized
- **NFR8:** All DRF endpoints require an authenticated session; unauthenticated requests return 401
- **NFR9:** All text, interactive elements, and error states in the wizard meet WCAG 2.1 AA color contrast minimums (4.5:1 for normal text; 3:1 for large text and UI components)
- **NFR10:** All five Umami instrumentation event types (wizard start, step complete/abandon, entity search, quota hit, final submit) are verified live on launch day
- **NFR11:** Image uploads succeed for files up to `MAX_IMAGE_SIZE_MB`; the size limit is enforced client-side before any network request is initiated
- **NFR12:** The Leaflet map in the Place inline creation modal loads correctly on all supported browsers without requiring an external API key

### Additional Requirements

- **Multi-entry Vite config addition:** `event-form` must be added as a rollup input and loaded via `{% vite_asset %}` on create/edit views
- **Quill 2.0.3 integration:** Use Quill for rich-text event descriptions with HTML output drop-in compatible with database fields
- **Custom CSRF header integration:** Read CSRF token from mount element attribute and include `X-CSRFToken` header in all DRF mutating requests
- **Standard DRF ListCreateAPIView upgrade:** Upgrade `events/` endpoint to standard REST GET/POST, renaming URL pattern to `event_list`
- **Unified quota permissions:** Custom DRF permissions for Event, Organizer, Speaker, and Place to enforce daily quotas with Spanish error messages
- **Dedicated formFetch helper:** A `formFetch` utility in `api/base.ts` that handles multipart data and omits the `Content-Type` header
- **Shared frontend constants:** `SEARCH_DEBOUNCE_MS = 300`, `MAX_IMAGE_SIZE_MB = 10`, and `MIN_SEARCH_QUERY_LENGTH = 2` defined in `constants.ts`
- **Reusable search composable:** `useEntitySearch` to handle debounced autocomplete lookup for all three entity selectors
- **Backend HTML sanitization:** `sanitize_html()` validation in `validate_description()` across Event, Organizer, and Speaker serializers
- **Accent-insensitive search services:** Decouple search queries from views, placing them in specialized python services utilizing `unaccent__icontains`
- **Generic BaseModal:** Modal component in `presentational/BaseModal` that manages overlay, teleports to `body`, traps focus, and handles backdrop/Escape clicks

### UX Design Requirements

- **UX-DR1:** Three-step navigation flow where steps are mounted concurrently via `v-show` and state is preserved across steps (owning state in the root `EventWizard.vue`).
- **UX-DR2:** Two explicit wizard variations (`EventWizardCreate.vue` and `EventWizardEdit.vue`) sharing the base wizard composition but providing different submission text ("Publicar" vs "Guardar") and operations.
- **UX-DR3:** Real-time live preview panel (`EventPreview.vue`) on desktop, displaying the event card dynamically as the user types.
- **UX-DR4:** Responsive layout that displays form and preview side-by-side on screens >= 768px, and stacks into a single-column layout on screens < 768px with a "Ver vista previa" modal trigger.
- **UX-DR5:** Entity selection combobox (`EntityCombobox.vue`) in `presentational/` that behaves as a custom autocomplete element, supporting keyboard navigation (up/down arrow keys, Enter, Escape) and rendering selected entities as removable chips.
- **UX-DR6:** Displaying the "Crear nuevo" option inline in the combobox list *only* when search results return zero.
- **UX-DR7:** Inline creation modals (Organizer, Speaker, Place) that stack forms, with the Place modal integrating a touch-compatible Leaflet map pin picker and city dropdown, preserving all wizard state when modals are opened or closed.
- **UX-DR8:** Condensed display mode toggle that hides field guidance text and descriptions, compacts fields, and de-emphasizes the image upload zone while keeping the three steps intact.
- **UX-DR9:** In-browser image size guard validating file size immediately upon selection, and immediate browser-side image rendering via `URL.createObjectURL()`.
- **UX-DR10:** Blocking step-by-step validation (disabling "Paso siguiente" if required fields on the current step are invalid/missing) and displaying standard required-field validation error messages upon focus-out without selection.
- **UX-DR11:** Surfacing backend validation errors (DRF 400 validation dict mapped to `DRFValidationError`) inline next to the affected fields without clearing previously filled data.
- **UX-DR12:** Custom 403 template at `desparchado/templates/403.html` displaying the specific server-side `exception` message, and a dedicated `event_quota_exceeded.html` page when the daily event quota is hit.

### FR Coverage Map

- **FR1:** Epic 1 - Unauthenticated users redirected to login
- **FR2:** Epic 1 - Contributors can navigate a three-step event wizard
- **FR3:** Epic 1 - Advance step blocked unless required fields valid
- **FR4:** Epic 1 - Condensed display mode toggle
- **FR5:** Epic 3 - Mobile overlay preview trigger below 768px
- **FR6:** Epic 3 - Unsaved changes beforeunload warning
- **FR7:** Epic 1 - Event title entry
- **FR8:** Epic 1 - Rich-text event description via Quill
- **FR9:** Epic 3 - Event image drag/drop or picker
- **FR10:** Epic 1 - Single event date and time america/bogota
- **FR11:** Epic 2 - Multi-organizer selection chip input
- **FR12:** Epic 2 - Multi-speaker selection chip input
- **FR13:** Epic 2 - Single place selection input
- **FR14:** Epic 1 - Five category visual cards
- **FR15:** Epic 1 - Optional price free text
- **FR16:** Epic 1 - Optional source URL
- **FR17:** Epic 1 - Publish status publish/draft toggle
- **FR18:** Epic 2 - Accent-insensitive fuzzy autocomplete search
- **FR19:** Epic 2 - Single canonical result search mapping
- **FR20:** Epic 2 - "Crear nuevo" appears only on zero results
- **FR21:** Epic 2 - Required entity validation errors on focus-out
- **FR22:** Epic 2 - Multi-select chips for organizers/speakers
- **FR23:** Epic 2 - Inline organizer creation modal
- **FR24:** Epic 2 - Inline speaker creation modal
- **FR25:** Epic 2 - Inline place creation modal with Leaflet map
- **FR26:** Epic 2 - Wizard state preservation during inline modal operations
- **FR27:** Epic 3 - Immediate client-side image size guard
- **FR28:** Epic 3 - Local image preview rendering in wizard preview card
- **FR29:** Epic 3 - Event quota check before wizard renders
- **FR30:** Epic 3 - Entity quota check inside inline modals
- **FR31:** Epic 3 - Superuser quota bypass
- **FR32:** Epic 3 - Quota configuration UI in Django admin
- **FR33:** Epic 4 - Edit own events via slug
- **FR34:** Epic 4 - Pre-populate all fields from existing event
- **FR35:** Epic 4 - Server-side edit permission enforcement
- **FR36:** Epic 4 - Atomic edit submission via PATCH
- **FR37:** Epic 1 - Real-time preview card update as user types
- **FR38:** Epic 1 - Card preview maps title, description, image, and category
- **FR39:** Epic 1 - Surfacing DRF validation errors inline without state loss
- **FR40:** Epic 3 - Track wizard start event in Umami
- **FR41:** Epic 3 - Track step transition events in Umami
- **FR42:** Epic 3 - Track entity search and creation events in Umami
- **FR43:** Epic 3 - Track quota hit events in Umami
- **FR44:** Epic 3 - Track submission success events in Umami

## Epic List

### Epic 1: Event Wizard Core Structure & Navigation
*   **Goal**: Contributors can access a blank/secured multi-step wizard, fill out the basic text-and-category fields, navigate steps with validation, and see a live preview of their event card in real-time.
*   **User Outcome**: Enables creators to fill out core event details and preview them dynamically before submitting.
*   **FRs Covered**: FR1, FR2, FR3, FR4, FR7, FR8, FR10, FR14, FR15, FR16, FR17, FR37, FR38, FR39

### Epic 2: Autocomplete Selection & Inline Creation of Related Entities
*   **Goal**: Contributors can seamlessly search for existing organizers, speakers, or places using accent-insensitive matching, and if they do not exist, create them inline via modal forms without losing wizard progress.
*   **User Outcome**: Dramatically reduces duplicate entity creation in the database while maintaining a seamless, zero-context-switch flow for creators.
*   **FRs Covered**: FR11, FR12, FR13, FR18, FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR26

### Epic 3: Advanced Safeguards, Image Management & Analytics
*   **Goal**: The system handles large image uploads safely with local previews, protects resource consumption with strict daily quotas, tracks usability metrics via Umami, and adapts responsively to mobile viewports.
*   **User Outcome**: Provides robust defensive validation for the platform and enables comprehensive funnel visualization for administrators, while making mobile creation easy.
*   **FRs Covered**: FR5, FR9, FR27, FR28, FR29, FR30, FR31, FR32, FR40, FR41, FR42, FR43, FR44

### Epic 4: Event Modification & Edit Permissions
*   **Goal**: Creators can securely edit their published events or drafts through a pre-hydrated wizard, protected by server-side permission gates.
*   **User Outcome**: Allows creators to update typos and event information post-publication safely and securely.
*   **FRs Covered**: FR33, FR34, FR35, FR36

---

## Epic 1: Event Wizard Core Structure & Navigation

### Story 1.1-BE: Django Routing, Views, and Quota 403 Context Providers

**As a** backend developer,  
**I want** to implement secure Django routing, views, and quota checks for the event creation flow,  
**So that** unauthenticated users are redirected to login, quota-restricted users receive a 403 page with an explanation, and authorized users can load the wizard shell.

**Acceptance Criteria:**
* **Given** an unauthenticated request to `/events/add/`
  * **When** processed by `EventWizardCreateView.dispatch()`
  * **Then** the request is redirected to the login page with `?next=/events/add/`.
* **Given** an authenticated request to `/events/add/`
  * **When** `request.user.settings.reached_event_creation_quota()` evaluates to `True`
  * **Then** the view raises `PermissionDenied("Hoy alcanzaste el límite de eventos que puedes crear. Vuelve mañana para continuar publicando.")`
  * **And** the server returns an HTTP 403 Forbidden response rendering the custom `desparchado/templates/403.html` template containing this exact exception message.
* **Given** an authenticated user who is within their event quota
  * **When** accessing `/events/add/`
  * **Then** it returns HTTP status code 200 and renders the `events/templates/events/event_wizard.html` template
  * **And** the template contains a mount element `<div id="event-wizard-app">` with attributes: `data-csrf`, `data-wizard-mode="create"`, and `data-api-url` (reversing `events_api:event_list`).

### Story 1.2-BE: Upgraded Event REST API Create Endpoint & Write Serializer

**As a** backend developer,  
**I want** to implement a robust write serializer and a secure REST API POST endpoint on the standard events path that validates inputs and sanitizes rich HTML description text,  
**So that** event creation requests are processed atomically in the database according to model/form validations.

**Acceptance Criteria:**
* **Given** the existing `events/` URL pattern
  * **When** upgraded to standard REST conventions
  * **Then** it points to `EventListCreateAPIView` (ListCreateAPIView), and the URL name is renamed to `event_list`.
* **Given** an authenticated POST request to `/events/api/v1/events/`
  * **When** processed by the write serializer (`EventWriteSerializer`)
  * **Then** the following field-level validations are enforced:
    * `title`: Required (max length 255)
    * `description`: Required (cannot be empty)
    * `event_source_url`: Required (must be a valid URL, max length 500)
    * `event_date`: Required (valid datetime)
    * `place_id`: Required (valid Place FK ID)
    * `organizer_ids`: Required (at least one valid Organizer FK ID in list)
  * **And** the `description` text is sanitized in `validate_description()` via `sanitize_html()` to remove any script or unsafe tags (retaining only B/I/U).
* **Given** an invalid POST request
  * **When** processed
  * **Then** the server returns HTTP 400 Bad Request with a structured dictionary of field-specific errors
  * **And** the database transaction is rolled back (atomic integrity).
* **Given** a valid authenticated POST request
  * **When** processed
  * **Then** it creates the `Event` record, assigning `created_by = request.user` and `is_approved = True`
  * **And** returns HTTP 201 Created with `{ "url": "/events/<slug>/" }`.

### Story 1.3-FE: Vite Entry, Root State & Multi-Step Skeleton Layout

**As a** frontend developer,  
**I want** to initialize the Vite entrypoint, the reactive wizard state interface, and the step navigation responsive skeleton,  
**So that** I have a stable framework for mounting Step inputs and transition screens.

**Acceptance Criteria:**
* **Given** the Vite entry `event-form.ts`
  * **When** mounted on the template element
  * **Then** it reads the `data-wizard-mode` attribute and successfully mounts `EventWizardCreate.vue`
  * **And** it initializes a single reactive root state `state: IWizardState` matching the exact TypeScript interfaces in `desparchado/frontend/scripts/api/interfaces.ts`.
* **Given** `EventWizard.vue` renders the interface
  * **When** loaded on desktop (>= 768px)
  * **Then** it renders a side-by-side layout: Form on the left, empty Event Card Preview panel on the right
  * **And** Step 1 is displayed, while Steps 2 and 3 are hidden (`v-show` strategy)
  * **And** the "Paso anterior" button is disabled.
* **Given** the user navigates between steps
  * **When** clicking "Paso siguiente" or "Paso anterior"
  * **Then** the wizard hides/reveals steps instantly, updating the progress indicator without reloading the page.
* **Given** the user toggles the "Modo condensado" switch
  * **When** clicked
  * **Then** it hides step guidelines, compacts input field margins, and reduces whitespace, but keeps the 3-step navigation.

### Story 1.4-FE: Step 1 UI & Real-Time Card Preview

**As a** contributor,  
**I want** to fill out Step 1 fields (Title and a Quill rich text Description editor) and see them reflect immediately in the preview card,  
**So that** I have instant visual feedback on how my text formatting looks.

**Acceptance Criteria:**
* **Given** the contributor is on Step 1
  * **When** typing in the Título input field
  * **Then** the state `state.title` is updated
  * **And** `EventPreview.vue` (rendered on the right on desktop) updates the title immediately (computed local update latency <= 50ms, NFR4).
* **Given** the Description field on Step 1
  * **When** mounted
  * **Then** it initializes a Quill 2.0.3 editor showing Bold, Italic, and Underline formatting options
  * **And** Quill's HTML output directly updates `state.description`
  * **And** `EventPreview.vue` renders this HTML safely (using `v-html`).
* **Given** the user is viewing the page on a mobile screen (< 768px)
  * **When** loading the wizard
  * **Then** the sidebar preview is hidden by default
  * **And** a "Ver vista previa" button is visible at the bottom
  * **And** clicking this button opens the preview card inside a mobile-friendly overlay modal (FR5).

### Story 1.5-FE: Step 2 & 3 UI Inputs, Timezones & Navigation Validation

**As a** contributor,  
**I want** to fill out date/time, category cards, price, source URL, and drafts toggles, with strict required-field validation gating step progression,  
**So that** I cannot navigate away from a step with missing or invalid required data.

**Acceptance Criteria:**
* **Given** the contributor is on Step 2
  * **When** they pick a date/time
  * **Then** `state.eventDate` is stored as an ISO string in the `America/Bogota` timezone.
* **Given** the contributor is on Step 3
  * **When** they click one of the 5 category cards (Literatura, Arte, Sociedad, Ciencia, Medio Ambiente)
  * **Then** the selection updates `state.category` and highlights the active card
  * **And** they can toggle `state.isPublished` and enter `state.price` and `state.eventSourceUrl`.
* **Given** the step navigation validator evaluates progression:
  * **When** on **Step 1**: "Paso siguiente" is disabled unless **Title**, **Description** (Quill editor output), and **Organizers** (min 1) are populated. (Note: Organizers selection will be stubbed as a hardcoded ID for now so this story can be validated independently before Epic 2 is built).
  * **When** on **Step 2**: "Paso siguiente" is disabled unless **Date/Time** and **Place** are populated. (Place will be stubbed as a hardcoded ID for now).
  * **When** on **Step 3**: "Publicar" is disabled unless **Event Source URL** is populated and contains a valid URL format.
  * **And** moving focus away from any required field without populating it displays a red validation error: "Este campo es requerido".

### Story 1.6-FE: Atomic Submit, CSRF, and Backend Error Redirect UX

**As a** contributor,  
**I want** to submit my finished event atomically with CSRF protection, and have the wizard automatically navigate me to the first step containing any backend validation errors,  
**So that** I don't have to guess where my formatting or input mistakes were made.

**Acceptance Criteria:**
* **Given** the user clicks "Publicar" on Step 3
  * **When** all client-side validation passes
  * **Then** it fires a POST request using `formFetch` to `/events/api/v1/events/` including `X-CSRFToken` from template
  * **And** the UI displays an `isSubmitting` saving overlay.
* **Given** the backend returns an HTTP 400 Bad Request with validation errors
  * **When** received by the client app
  * **Then** `fieldErrors` is populated and errors are rendered inline next to their input fields
  * **And** the wizard evaluates which step the first error belongs to:
    * If the first error key is `title`, `description`, or `organizer_ids` -> **navigates automatically back to Step 1** and shifts focus to the first invalid field.
    * If the first error key is `event_date` or `place_id` -> **navigates automatically back to Step 2**.
    * If the first error key is `event_source_url` -> **navigates automatically to Step 3**.
  * **And** the `isSubmitting` flag is set back to `false` and no wizard state is lost (FR39).
* **Given** the backend returns an HTTP 201 Created success
  * **When** received
  * **Then** the frontend redirects the browser window immediately to the created event absolute URL (`window.location.href`).

---

## Epic 2: Autocomplete Selection & Inline Creation of Related Entities

### Story 2.1-BE: Autocomplete Fuzzy Search Services & Endpoints

**As a** backend developer,  
**I want** to implement high-speed fuzzy search services and read endpoints utilizing `unaccent` normalization for organizers, speakers, and places,  
**So that** frontend selectors can retrieve existing matching records in under 300ms to prevent duplicate database entries.

**Acceptance Criteria:**
* **Given** search queries with missing/incorrect accents or capitalization (e.g., "feria libro" or "blaa")
  * **When** evaluated by search services `search_organizers(q)` and `search_speakers(q)` in `events/services/entity_search.py`, and `search_places(q)` in `places/services/place_search.py`
  * **Then** they utilize PostgreSQL `unaccent__icontains` to retrieve accent-insensitive normalized matches (e.g. returning "Biblioteca Luis Ángel Arango").
* **Given** the autocomplete endpoints:
  * `GET /events/api/v1/organizers/search/?q=`
  * `GET /events/api/v1/speakers/search/?q=`
  * `GET /places/api/v1/places/search/?q=`
  * **When** queried with a parameter `q` of at least 2 characters
  * **Then** they return HTTP 200 with `{ "results": [{ "id": 1, "name": "..." }] }`
  * **And** search execution completes in <= 300ms at the 95th percentile (NFR1).

### Story 2.2-BE: Inline Creation Endpoints & Write Serializers for Related Entities

**As a** backend developer,  
**I want** to create robust REST serializers and POST creation endpoints for Organizers, Speakers, and Places,  
**So that** new entities can be created inline with complete validation parity to the existing Django forms.

**Acceptance Criteria:**
* **Given** creation endpoints `/events/api/v1/organizers/`, `/events/api/v1/speakers/`, and `/places/api/v1/places/`
  * **When** accessed by unauthenticated sessions
  * **Then** they return HTTP 401 Unauthorized.
* **Given** write requests to the Organizer and Speaker create endpoints
  * **When** processed by `OrganizerCreateSerializer` and `SpeakerCreateSerializer`
  * **Then** the `image` field is strictly enforced as **required** (matching `OrganizerForm` and `SpeakerForm` parity)
  * **And** description texts are sanitized via `sanitize_html()` before database insertion.
* **Given** write requests to the Place create endpoint
  * **When** processed by `PlaceCreateSerializer`
  * **Then** `name`, `address` (max length 100), and `location` (PointField `{lat, lng}`) are strictly enforced as **required** (matching `PlaceForm` parity).

### Story 2.3-FE: Reusable Autocomplete Combobox (`EntityCombobox.vue`) & Multi-Select Chips

**As a** frontend developer,  
**I want** to build a custom, accessible autocomplete combobox element that coordinates fuzzy search lookups and displays selected entities as chips,  
**So that** contributors can search for and select organizers, speakers, and places seamlessly.

**Acceptance Criteria:**
* **Given** an `EntityCombobox` input field (reusable, placed in presentational components folder)
  * **When** the user types at least 2 characters
  * **Then** the component debounces the lookup by `SEARCH_DEBOUNCE_MS = 300` and displays matching results from the search API
  * **And** the option "Crear nuevo" appears *only* when search results return zero.
* **Given** keyboard focus on the combobox list
  * **When** navigating using Arrow Up/Down, Enter, or Escape
  * **Then** the component moves list focus, selects items, or closes the list in full compliance with WAI-ARIA combobox accessibility specs.
* **Given** multi-select mode (for organizers and speakers)
  * **When** an entity is selected
  * **Then** the selection is appended to `state` and renders in the UI as a removable chip displaying the entity name
  * **And** clicking the chip removal icon fires `entity:cleared` and removes the ID from the reactive root state.

### Story 2.4-FE: Reusable `BaseModal` & Inline Forms for Organizer and Speaker

**As a** contributor,  
**I want** to open a modal inside Step 1 of the wizard to create a new Organizer or Speaker inline,  
**So that** I don't lose any of my progress in the main wizard form.

**Acceptance Criteria:**
* **Given** the "Crear nuevo" option is clicked in the organizer or speaker combobox
  * **When** triggered
  * **Then** a `BaseModal.vue` presentational component (mounted to `body` via Vue Teleport and trapping keyboard focus) is displayed
  * **And** the wizard preserves all previously filled event wizard state intact.
* **Given** the modal forms are populated by the user
  * **When** the user submits the form
  * **Then** the form performs a `multipart/form-data` upload (due to required images) and displays inline modal errors on failures
  * **And** on success, the modal closes, fires `entity:created` with the newly created `{ id, name }` chip object, and automatically selects it in the combobox.

### Story 2.5-FE: Inline Place Modal with Leaflet Map Pin Picker and Address Search

**As a** contributor,  
**I want** to create a new Place inline in Step 2 by filling out address inputs, searching for locations by name, and clicking on an interactive map,  
**So that** I can precisely specify the event's geographical location without leaving the wizard.

**Acceptance Criteria:**
* **Given** the Place creation modal is opened
  * **When** rendered
  * **Then** it dynamically parses and loads Leaflet CDN assets (CSS/JS)
  * **And** it populates the City selector dropdown using the `data-vue-prop-cities` provided from the Django template context.
* **Given** the address geocoding search input in the Place modal
  * **When** the user types at least 3 characters
  * **Then** the component debounces and fetches matching address suggestions from Nominatim:
    `https://nominatim.openstreetmap.org/search?q=<QUERY>&format=json&limit=5&countrycodes=co` (enforcing Spanish `Accept-Language: es` header)
  * **And** it displays a dropdown list of up to 5 suggestions.
* **Given** an address suggestion from the geocoding dropdown is clicked
  * **When** selected
  * **Then** the dropdown list closes, the address field is filled with the suggestion's descriptive name, and the Leaflet map centers immediately on the resolved coordinates (`lat`, `lon`) at zoom level 15
  * **And** a draggable pin marker is placed at that location, updating the form state coordinate variables (`lat` and `lng`).
* **Given** the Leaflet map widget inside the Place modal
  * **When** the user manually clicks on the map viewport
  * **Then** the widget renders the pin marker at the clicked point, updating the local coordinates state
  * **And** on successful submit, it POSTs the coordinates as a standard GeoJSON Point type to `/places/api/v1/places/`, closes the modal, and assigns the place chip to Step 2.
  * **And** on viewports below 768px, the map container stacks vertically below the address inputs with scroll-wheel zoom disabled to prevent touch layout distortion.

---

## Epic 3: Advanced Safeguards, Image Management & Analytics

### Story 3.1-BE: DRF Quota Permission Classes (DRY Integration)

**As a** backend developer,  
**I want** to implement lightweight DRF custom permission classes that utilize the existing `UserSettings` model quota checks,  
**So that** new REST write endpoints enforce the same daily limits as traditional forms with zero code duplication.

**Acceptance Criteria:**
* **Given** creation endpoints `/events/api/v1/events/`, `/events/api/v1/organizers/`, `/events/api/v1/speakers/`, and `/places/api/v1/places/`
  * **When** queried with write mutations (`POST`)
  * **Then** they enforce their respective lightweight permission classes: `EventCreationQuotaPermission`, `OrganizerCreationQuotaPermission`, `SpeakerCreationQuotaPermission`, and `PlaceCreationQuotaPermission` in `events/permissions.py` and `places/permissions.py`.
  * **And** these permissions directly return the boolean of the corresponding pre-existing model method on `request.user.settings` (e.g. `reached_organizer_creation_quota()`), utilizing the built-in superuser bypass with zero duplicated query/user checks.
* **Given** a user has reached their daily limit
  * **When** attempting to POST to a quota-restricted endpoint
  * **Then** the permission class returns HTTP 403 Forbidden with the designated Spanish error message (e.g., `{"detail": "Hoy alcanzaste el límite de nuevos organizadores."}`).

### Story 3.2-FE: Client-side Image Size Validation & Local Previews

**As a** contributor,  
**I want** to drag-and-drop or select an event image with immediate size verification and local preview rendering,  
**So that** I don't wait for server uploads only to discover my image is too large.

**Acceptance Criteria:**
* **Given** the Event Image upload input zone on Step 1
  * **When** a file is selected or dropped
  * **Then** the component validates that the file size is <= `MAX_IMAGE_SIZE_MB = 10` (shared constant)
  * **And** if it exceeds 10MB, it immediately blocks selection and displays: "La imagen supera el límite de 10MB." (NFR11).
* **Given** a valid image selection
  * **When** processed by the frontend
  * **Then** it generates a local object URL using `URL.createObjectURL(file)` and assigns it to `state.imagePreviewUrl`
  * **And** the Event Card Preview immediately renders the image locally (latency <= 50ms, no network call or early upload occurs, NFR5).

### Story 3.3-FE: Unsaved State Warnings (`beforeunload` lifecycle)

**As a** contributor,  
**I want** the browser to warn me if I attempt to close the tab or navigate away after entering data in the wizard,  
**So that** I do not accidentally lose my progress.

**Acceptance Criteria:**
* **Given** the wizard contains unsaved modifications
  * **When** `isDirty` evaluates to `True` (computed when `title` is not empty, `organizerIds` has items, or `image` is uploaded)
  * **And** the user attempts to close the browser tab or navigate away
  * **Then** the browser fires a `beforeunload` dialog: "Leave site? Changes you made may not be saved."
* **Given** the user clicks "Publicar" (submitting the form) or "Cancelar"
  * **When** triggered
  * **Then** the wizard removes the `beforeunload` event listener immediately before redirecting, allowing seamless navigation.

### Story 3.4-FE: Umami Analytics Funnel Trackers

**As an** administrator,  
**I want** to track contributor interactions, search actions, inline creations, and quota hits in the event wizard,  
**So that** I can monitor and optimize the submission funnel.

**Acceptance Criteria:**
* **Given** the event wizard mounted on the page
  * **When** user actions occur
  * **Then** the frontend executes safe optional-chaining trackers (`window.umami?.track(...)`) matching the exact spec:
    * `wizard:start` (on mount)
    * `wizard:step-complete` (when advancing steps)
    * `wizard:step-abandon` (when clicking previous)
    * `entity:search` (when debounced autocompletes fire)
    * `entity:created-inline` (when modal creation succeeds)
    * `quota:hit` (when receiving quota 403 responses)
    * `wizard:submit` (when successfully created/edited)
  * **And** tracking logic functions safely even if Umami is blocked or missing (no Javascript console errors, NFR10).

---

## Epic 4: Event Modification & Edit Permissions

### Story 4.1-BE: Django Edit View Permission Gate & Custom 403 Template

**As a** backend developer,  
**I want** to implement a secure, view-level permission gate for the edit path that intercepts unauthorized requests at the server level,  
**So that** only authorized editors can load the template, and unauthorized users see a clear, custom 403 page.

**Acceptance Criteria:**
* **Given** a request to `/events/<slug>/edit/`
  * **When** processed by `EventWizardUpdateView` in `events/views/event_wizard_update.py`
  * **Then** the view inherits from `EditorPermissionRequiredMixin` to leverage existing permissions logic
  * **And** if `obj.can_edit(request.user)` returns `False`, it raises `PermissionDenied("No tienes permiso para editar este evento.")` (NFR7).
* **Given** a `PermissionDenied` exception is raised
  * **When** handled by Django
  * **Then** it returns HTTP status code 403 and renders a new custom template at `desparchado/templates/403.html` displaying the `{{ exception }}` message clearly in Spanish.
* **Given** an authorized editor loads `/events/<slug>/edit/`
  * **When** processed
  * **Then** it returns HTTP 200 and renders the same `events/templates/events/event_wizard.html` shell
  * **And** it injects the mount attributes: `data-wizard-mode="edit"`, and `data-api-url` (pointing to `/events/api/v1/events/{slug}/`).

### Story 4.2-BE: REST API GET Hydration & PATCH Update Endpoints

**As a** backend developer,  
**I want** to implement the event detail hydration and update API views and serializers on the standard events path,  
**So that** the editor frontend can load existing event fields cleanly and save edits atomically.

**Acceptance Criteria:**
* **Given** the slug-based API endpoint `/events/api/v1/events/{slug}/`
  * **When** a `GET` request is received
  * **Then** it processes via `EventDetailSerializer`, returning the complete event fields in under 500ms (NFR2)
  * **And** nested organizers, speakers, and place fields are returned with their complete representation (`{ id, name }`) to populate frontend chips.
* **Given** a `PATCH` request is received
  * **When** evaluated at the API level
  * **Then** the endpoint enforces standard permissions to ensure only users with `can_edit()` permission can modify it
  * **And** the request accepts a multipart payload (allowing optional image file updates)
  * **And** it performs HTML sanitization in `validate_description()` via `sanitize_html()`
  * **And** it saves the modifications atomically and returns HTTP 200 with `{ "url": "/events/<slug>/" }`.

### Story 4.3-FE: Edit Flow State Hydration & "Guardar" Submit Variation

**As a** registered editor,  
**I want** the wizard to load in Edit Mode, fetch the existing event details to populate all steps, and submit my changes as a PATCH,  
**So that** I can update typos or times quickly.

**Acceptance Criteria:**
* **Given** the wizard mounts on `/events/<slug>/edit/`
  * **When** mounted
  * **Then** the app initializes in edit mode (`EventWizardEdit.vue` wrapper is mounted)
  * **And** `isLoading` is set to `true`, showing a neat loading skeleton/spinner
  * **And** the app fetches the event detail via `GET /events/api/v1/events/{slug}/` (using `getEventDetail(url)`).
* **Given** the API returns the event details
  * **When** resolved
  * **Then** the frontend hydrates `state: IWizardState` fields, populating title, Quill description, dates, categories, price, source URL, and resolving selected organizers, speakers, and place chips
  * **And** `isLoading` is set to `false`, rendering Step 1 with pre-populated data.
* **Given** the hydrated form is modified
  * **When** on Step 3, the user clicks the submission button (which is dynamically labeled **"GUARDAR"**)
  * **Then** it performs an atomic `PATCH` request using `formFetch` to the `/events/api/v1/events/{slug}/` endpoint
  * **And** on success, redirects the browser window immediately to the absolute event URL.
