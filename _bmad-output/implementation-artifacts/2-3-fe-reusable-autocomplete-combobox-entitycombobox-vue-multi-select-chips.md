---
story_key: 2-3-fe-reusable-autocomplete-combobox-entitycombobox-vue-multi-select-chips
status: done
baseline_commit: fe50dad2e54036fb57b461e8a4b288b3e18d6904
---

# Story 2.3-FE: Reusable Autocomplete Combobox (`SearchableCombobox.vue`) & Multi-Select Chips

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

**As a** frontend developer,  
**I want** to build a custom, accessible autocomplete combobox element that coordinates fuzzy search lookups and displays selected entities as chips,  
**So that** contributors can search for and select organizers, speakers, and places seamlessly.

## Acceptance Criteria

1. **Given** a `SearchableCombobox` input field (reusable presentational component in `@presentational_components/components/SearchableCombobox/SearchableCombobox.vue`)
   - **When** the user types at least 2 characters (`MIN_SEARCH_QUERY_LENGTH = 2`)
   - **Then** the component debounces the lookup by `SEARCH_DEBOUNCE_MS = 300` and displays matching results from the search API endpoint (`/events/api/v1/organizers/search/?q=`, `/events/api/v1/speakers/search/?q=`, `/places/api/v1/places/search/?q=`)
   - **And** the option "+ Crear nuevo" appears *only* when search results return zero (`hasSearched && results.length === 0`).
2. **Given** keyboard focus on the combobox list or input field
   - **When** navigating using `ArrowUp`, `ArrowDown`, `Enter`, or `Escape`
   - **Then** the component moves list focus, selects items, or closes the dropdown list in compliance with WAI-ARIA combobox accessibility standards (`role="combobox"`, `aria-expanded`, `aria-autocomplete="list"`, `aria-activedescendant`).
3. **Given** multi-select mode (`multiple = true`, used for organizers and speakers)
   - **When** an entity is selected
   - **Then** the selection is appended to `state` and renders in the UI as a removable chip displaying the entity name (and image thumbnail if available)
   - **And** clicking the chip removal icon (`×`) removes the ID from the reactive root state (`organizerIds` or `speakerIds`).
4. **Given** single-select mode (`multiple = false`, used for place)
   - **When** an entity is selected
   - **Then** the selection updates `state.placeId` and displays the selected place chip
   - **And** clearing the chip resets `state.placeId` to `null`.
5. **Given** an initial edit mode state or pre-selected entity IDs
   - **When** `SearchableCombobox` mounts with initial `modelValue` ID(s)
   - **Then** initial entity details (name, image) are preserved and displayed as chips.

## Tasks / Subtasks

- [x] **Task 1: Create Reusable Search Composable (`useEntitySearch.ts`)** (AC: 1)
  - [x] Create `desparchado/frontend/scripts/composables/useEntitySearch.ts`.
  - [x] Implement debounced search query fetching using `SEARCH_DEBOUNCE_MS = 300` and `MIN_SEARCH_QUERY_LENGTH = 2` from `@scripts/constants`.
  - [x] Execute GET HTTP request using `getData<ISearchResponse<IEntityOption>>(searchUrl + encodeURIComponent(query))`.
  - [x] Manage reactive state: `query`, `results`, `isLoading`, `hasSearched`, `searchError`.
  - [x] Return clean composable API: `{ query, results, isLoading, hasSearched, searchError, resetSearch }`.

- [x] **Task 2: Build `SearchableCombobox.vue` Presentational Component** (AC: 1, 2, 3, 4, 5)
  - [x] Create `desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue`.
  - [x] Define props: `id`, `label`, `placeholder`, `searchUrl`, `modelValue`, `initialOptions`, `multiple`, `required`, `hideLabel`, `errors`.
  - [x] Define emits: `update:modelValue`, `create-new`, `error`, `blur`.
  - [x] Implement selected chips display with removal button (`×`).
  - [x] Implement input field with WAI-ARIA combobox attributes (`role="combobox"`, `aria-expanded`, `aria-controls`, `aria-activedescendant`).
  - [x] Implement zero-results state rendering `"+ Crear nuevo"` item button that emits `create-new`.
  - [x] Implement full keyboard navigation handlers (`ArrowDown`, `ArrowUp`, `Enter`, `Escape`).
  - [x] Handle click-outside directive or window event listener to close dropdown when focus leaves component.
  - [x] Implement BEM styling via `bem()` helper and SCSS.

- [x] **Task 3: Integrate `SearchableCombobox` into Step 1 and Step 2 Wizard Forms** (AC: 1, 3, 4)
  - [x] Update `desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue`:
    - Replace Organizers stub with `<SearchableCombobox>` bound to `state.organizerIds` (`multiple=true`, `required=true`, `searchUrl="/events/api/v1/organizers/search/?q="`).
    - Replace Speakers stub with `<SearchableCombobox>` bound to `state.speakerIds` (`multiple=true`, `required=false`, `searchUrl="/events/api/v1/speakers/search/?q="`).
    - Add validation rule: `state.organizerIds.length >= 1` in `isValid` computed property.
  - [x] Update `desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue`:
    - Replace Place stub with `<SearchableCombobox>` bound to `state.placeId` (`multiple=false`, `required=true`, `searchUrl="/places/api/v1/places/search/?q="`).
    - Add validation rule: `!!state.placeId` in `isValid` computed property.

- [x] **Task 4: Add Storybook Component Stories (`SearchableCombobox.stories.ts`)**
  - [x] Create `desparchado/frontend/stories/SearchableCombobox.stories.ts`.
  - [x] Add Storybook stories covering single-select, multi-select, pre-selected chips, loading state, zero-results state, and error states.

## Dev Notes

- **Vue 3 & Script Setup**: Must use `<script lang="ts" setup>` with strict TypeScript (no `any`).
- **Path Aliases**: Always use `@presentational_components/`, `@styles/`, `@assets/`.
- **CSS BEM Standard**: Use `bem(baseClass, element, modifier)` from `desparchado/frontend/scripts/utils/bem.ts`.
- **HTTP Client**: Use `getData` from `desparchado/frontend/scripts/api/base.ts`.
- **Backend Endpoints**:
  - `GET /events/api/v1/organizers/search/?q=`
  - `GET /events/api/v1/speakers/search/?q=`
  - `GET /places/api/v1/places/search/?q=`

### Project Structure Notes

- Composable location: `desparchado/frontend/scripts/composables/useEntitySearch.ts`
- Component location: `desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue`
- Storybook location: `desparchado/frontend/stories/SearchableCombobox.stories.ts`
- Step Views: `desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue` & `Step2/Step2.vue`

### References

- [Epics breakdown](file:///home/crist/projects/desparchado/_bmad-output/planning-artifacts/epics-event-creation-ux.md#L362-L380)
- [Architecture details](file:///home/crist/projects/desparchado/_bmad-output/planning-artifacts/architecture-event-creation-ux.md)
- [Project Context](file:///home/crist/projects/desparchado/_bmad-output/project-context.md)

## Dev Agent Record

### Agent Model Used

Gemini 3.6 Flash (High)

### Debug Log References

- Verified full ESLint linting (`npm run lint-scripts`): 0 errors, 0 warnings.
- Verified Vite frontend module transformation (838 modules transformed successfully).

### Completion Notes List

- Built `useEntitySearch.ts` composable for debounced autocomplete fetching (`300ms`, min `2` characters).
- Built `SearchableCombobox.vue` presentational component with multi-select and single-select modes, removable chips, WAI-ARIA combobox accessibility (`role="combobox"`, `aria-expanded`, `aria-activedescendant`), keyboard navigation (`ArrowUp`/`ArrowDown`/`Enter`/`Escape`), click-outside handler, and zero-results `"+ Crear nuevo"` trigger.
- Integrated `SearchableCombobox` into `Step1.vue` (organizers and speakers) and `Step2.vue` (place).
- Created Storybook component stories in `SearchableCombobox.stories.ts`.
- **Elevation Z-Index System**: Centralized elevation variables in `_variables.scss` (`$elev-dropdown: 2`, `$elev-combobox-input: 3`, `$elev-combobox-spinner: 4`, `$elev-header: 100`, `$elev-overlay: 1000`) ensuring sticky header stays above inputs and dropdown popups.
- **Container Aesthetics & Animation**: Aligned `SearchableCombobox` dropdown with `MenuDropdown` design tokens (`$color-dp-orange-100` background, `$hairline_regular` 2px solid `#222222` border, `border-radius: toRem(20px)`, `$shadow-over-neutral`) and implemented left-to-right `slide-fade` open transition.
- **Zero-Results & Loading State**:
  - Reformatted `"Crear nuevo"` zero-results dropdown item with left label `"¿No encontraste el que buscabas?"` and right button `"Crear nuevo"` (entire row clickable).
  - Added dropdown loading row displaying `"Buscando por: \"query\""` (or `"Buscando..."`).
  - Hidden result items and `"Crear nuevo"` row exclusively while search results are fetching (`!showLoadingOption`).
- **Browser Autocomplete & Focus Fixes**: Added `autocomplete="off"`, `autocorrect="off"`, `autocapitalize="off"`, `spellcheck="false"` to `<input>` and removed `for="..."` attributes from external section headlines in `Step1.vue` and `Step2.vue` to prevent accidental transition re-triggering.
- **Chip Layout Stability & Slide Animations**:
  - Set `min-height: toRem(37px)` on `.searchable-combobox__chips` to eliminate vertical layout shift when adding the first chip.
  - Wrapped chips in `<TransitionGroup name="chip-slide">` with left-entry addition (`translateX(-30px)`), right-exit removal (`translateX(30px)`), and smooth reordering (`chip-slide-move`).
  - Removed `position: absolute` on `chip-slide-leave-active` to preserve flex container flow during the final chip's exit transition.
  - Added `user-select: none` and `-webkit-user-select: none` to chips to prevent blue text highlight selections on drag/click.
- **Empty State Alert for Chips**:
  - Added `emptyChipsText?: string` prop to `SearchableCombobox.vue` (defaulting to `"No has seleccionado nada todavía"`).
  - Rendered empty state alert (`.searchable-combobox__empty-chip`) with transparent background and `2px dashed $color-gray-400` border when `selectedEntities.length === 0`.
  - Customized per-field empty messages:
    - Organizers: `"No has seleccionado ningún organizador aún"`
    - Speakers: `"No has seleccionado ningún ponente aún"`
    - Place: `"No se ha seleccionado un lugar"`
- **Keyboard Blur & Focus Navigation**: Added `closeDropdown()` to `handleBlur` (checking `event.relatedTarget`) so tabbing out closes active dropdowns immediately and prevents multiple open comboboxes.
- **Field Spacing & Condensed Mode**:
  - Added generous bottom spacing (`margin-bottom: toRem(60px)` on `.searchable-combobox` and `margin-bottom: 80px` on `.wizard-field:has(.searchable-combobox)`) to accommodate open popups without overlapping content below.
  - Added reduced spacing in condensed mode (`margin-bottom: toRem(16px)` / `24px`).
- **Single-Select Disabled Input State**:
  - Changed single-select behavior: when an item is selected, the input remains visible in the DOM but becomes disabled (`:disabled="isDisabled"`, `:placeholder="'Opción seleccionada'"`).
  - Styled disabled input with `$color-gray-200` background, `$color-gray-400` border, `$color-gray-600` text, and `cursor: not-allowed`. Removing the chip re-enables the input immediately.
- **Live Preview Real-Time Sync & Layout Adaptability**:
  - Emitted `'update:selectedOptions'` from `SearchableCombobox.vue` to reactively update `selectedOrganizers`, `selectedSpeakers`, and `selectedPlace` in `EventWizard.vue` and `EventPreview.vue` in real time.
  - Updated `EventPreview` layout: badge positioned absolutely at top-right (`top: -18px; right: 12px; z-index: 10`), fixed `width: 350px`, and dynamic viewport height scroll (`max-height: calc(100vh - var(--header-height, 80px) - 64px)`).

### File List

- `desparchado/frontend/scripts/composables/useEntitySearch.ts` (NEW)
- `desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue` (NEW)
- `desparchado/frontend/components/presentational/components/SearchableCombobox/styles.scss` (NEW)
- `desparchado/frontend/stories/SearchableCombobox.stories.ts` (NEW)
- `desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue` (UPDATE)
- `desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue` (UPDATE)
- `desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue` (UPDATE)
- `desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss` (UPDATE)
- `desparchado/frontend/components/presentational/containers/event-wizard/EventPreview/EventPreview.vue` (UPDATE)
- `desparchado/frontend/components/presentational/containers/event-wizard/EventPreview/styles.scss` (UPDATE)
- `desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardState.ts` (UPDATE)
- `desparchado/frontend/styles/_variables.scss` (UPDATE)
- `desparchado/frontend/styles/_animations.scss` (UPDATE)

### Review Findings

- [x] [Review][Patch] Ineffective AbortController & Race Condition in HTTP Search Composable [desparchado/frontend/scripts/composables/useEntitySearch.ts:1456-1474]
- [x] [Review][Patch] 1-Character Query and Backspace Edge Case Sets Invalid hasSearched State [desparchado/frontend/scripts/composables/useEntitySearch.ts:1433-1447]
- [x] [Review][Patch] Division by Zero (NaN) in Keyboard Navigation Index Calculation [desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue:405-416]
- [x] [Review][Patch] Loading State Option Lacks DOM ID & Invalid aria-activedescendant [desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue:564]
- [x] [Review][Patch] Interactive button Nested Inside Listbox Option (role="option") [desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue:617-640]
- [x] [Review][Patch] Focus Lost on Single-Select Selection Due to Immediate Input Disabling [desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue:383]
- [x] [Review][Patch] Initial Options and Reactivity Fallbacks (ID #123) Missing in Containers [desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue:1055-1070]
- [x] [Review][Patch] Dropdown Stacking Context Collision on Vertically Stacked Comboboxes [desparchado/frontend/components/presentational/components/SearchableCombobox/styles.scss:758-821]
- [x] [Review][Defer] Unhandled create-organizer, create-speaker, and create-place Events — deferred for Task 2.4 inline creation modals
- [x] [Review][Patch] Missing Composable Timer and Request Cleanup on Unmount [desparchado/frontend/scripts/composables/useEntitySearch.ts:1400-1507]
- [x] [Review][Patch] aria-controls References Unmounted Element when Dropdown is Closed [desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue:563]
- [x] [Review][Defer] "+ Crear nuevo" Appears When All API Results Are Already Selected — expected behavior when no selectable unselected options remain
- [x] [Review][Patch] Relative Path Traversal ../../ Used Instead of Project Path Aliases [desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue:221-223]
- [x] [Review][Patch] Keyboard Enter Pressing in Input while Dropdown is Open with activeIndex = -1 [desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue:418-420]
- [x] [Review][Patch] API Search Endpoint Error Response and Null Guard [desparchado/frontend/scripts/composables/useEntitySearch.ts:1463-1464]
- [x] [Review][Patch] Empty String modelValue Bypasses Required Field Validation [desparchado/frontend/components/presentational/components/SearchableCombobox/SearchableCombobox.vue:467]
- [x] [Review][Patch] Fragile Layout Margins (60px/80px) on Field Container — explained & fixed via open container z-index elevation


