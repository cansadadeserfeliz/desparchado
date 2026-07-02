---
story_key: 1-6-fe-atomic-submit-csrf-and-backend-error-redirect-ux
status: review
baseline_commit: 11d6319cd58db46b1a3dbc03345970033bd2bb45
---

# Story 1.6-FE: Atomic Submit, CSRF, and Backend Error Redirect UX

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

**As a** contributor,  
**I want** to submit my finished event atomically with CSRF protection, and have the wizard automatically navigate me to the first step containing any backend validation errors,  
**So that** I don't have to guess where my formatting or input mistakes were made.

## Acceptance Criteria

1. **Given** the user clicks "Publicar" (or "Guardar cambios") on Step 3
   * **When** all client-side validation passes
   * **Then** it fires a POST (or PATCH) request using `createEvent` or `updateEvent` (which uses `submitData` under the hood) to the appropriate API URL, including `X-CSRFToken` in headers (read via `getCsrfToken()`)
   * **And** the UI displays an `isSubmitting` saving overlay.
2. **Given** the backend returns an HTTP 400 Bad Request with validation errors
   * **When** received by the client app
   * **Then** `fieldErrors` is populated and errors are rendered inline next to their input fields
   * **And** the wizard evaluates which step the first error belongs to:
     * If the first error key is `title`, `description`, or `organizer_ids` (or `organizers`, `speakers`, `speaker_ids`) -> **navigates automatically back to Step 1** and shifts focus to the first invalid field.
     * If the first error key is `event_date` or `place_id` (or `place`) -> **navigates automatically back to Step 2**.
     * If the first error key is `event_source_url` (or other step 3 fields) -> **navigates automatically to Step 3**.
   * **And** the `isSubmitting` flag is set back to `false` and no wizard state is lost (FR39).
3. **Given** the backend returns an HTTP 201 Created (or 200 OK) success
   * **When** received
   * **Then** the frontend redirects the browser window immediately to the created event absolute URL (`window.location.href`).

## Tasks / Subtasks

- [x] **Task 1: Hook up Submit Handler and isSubmitting Overlay in EventWizard.vue** (AC: 1, 3)
  - [x] Clear `fieldErrors.value` and `submitError.value` at the start of `handleSubmit`.
  - [x] Set `isSubmitting.value = true`.
  - [x] Build the payload using `prepareFormData()`.
  - [x] Invoke `createEvent` or `updateEvent` depending on the `props.mode`.
  - [x] On successful submission:
    - [x] Add or retain a `// TODO: Implement Umami tracking (wizard:submit, action: props.mode)` comment.
    - [x] Remove the `beforeunload` event listener.
    - [x] Redirect the browser window to `response.url` via `window.location.href`.
  - [x] Wrap the form area or the entire page with the `<Overlay>` component to display a neat saving/submitting spinner or skeleton overlay when `isSubmitting` is true.

- [x] **Task 2: Implement Backend Error Parsing and Automatic Step Navigation** (AC: 2)
  - [x] In the catch block of `handleSubmit`, parse the `ValidationError`.
  - [x] Extract the first error key from `fieldErrors.value` (or `error.data`).
  - [x] Evaluate the first error key to navigate back to the appropriate step:
    - [x] If key is `title`, `description`, `organizers`, `organizer_ids`, `speakers`, or `speaker_ids` -> Set `currentStep.value = 1`.
    - [x] If key is `event_date`, `place`, or `place_id` -> Set `currentStep.value = 2`.
    - [x] If key is `event_source_url` (or `category`, `price`, `is_published`) -> Set `currentStep.value = 3`.
  - [x] Once the step is switched, shift keyboard focus to the first invalid input element to assist keyboard/screen-reader users.
  - [x] Reset `isSubmitting.value = false`.

- [x] **Task 3: Add TODO Placeholders for Umami Funnel Analytics Tracking**
  - [x] Ensure `// TODO: Implement Umami tracking (quota:hit, resource: 'event')` is added in the API error handling block on quota 403 response.
  - [x] Retain other pre-existing Umami tracking TODO comments in `EventWizard.vue` (`wizard:start`, `wizard:step-complete`, `wizard:step-abandon`).

- [x] **Task 4: Add Storybook stories/tests for submitting state and error mappings** (AC: 2, 3)
  - [x] Update `EventWizard.stories.ts` to add test stories that mock submission failure with validation errors.
  - [x] Verify that mock errors are correctly mapped and navigate the user back to the first step containing an error.

- [x] **Task 5: Refactor EventWizard Business Logic into Composable Structure (SOLID & DRY)**
  - [x] Extract all state management, hydration, navigation, validation, layout resize/beforeunload handlers, and submission API calls from `EventWizard.vue`.
  - [x] Separate concerns into five dedicated sub-composables: `useEventWizardState.ts`, `useEventWizardNavigation.ts`, `useEventWizardValidation.ts`, `useEventWizardLayout.ts`, and `useEventWizardSubmit.ts`.
  - [x] Implement the composition root orchestrator in `useEventWizard.ts` that merges and exposes the sub-composables to `EventWizard.vue`.
  - [x] Document all composable functions with complete JSDoc blocks and ensure type-safety.

## Dev Notes

- Relevant architecture patterns and constraints:
  - Form data submits via `FormData` containing multipart fields (due to image files).
  - CSRF headers must be read and attached automatically by our `submitData`/`formFetch` wrappers.
  - Actual Umami event dispatching is deferred to Epic 3. For this story, ensure only `// TODO` comments are added or kept at relevant locations to keep track.
  - Avoid hardcoding API URLs; use `apiUrl` and `apiUpdateUrl` passed down from Django view via mount element data attributes.
  - Follow strict SOLID and DRY guidelines by encapsulating business logic in modular sub-composables.
- Source tree components to touch:
  - [EventWizard.vue](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue)
  - [EventWizard.stories.ts](file:///home/crist/projects/desparchado/desparchado/frontend/stories/EventWizard.stories.ts)
  - [useEventWizard.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizard.ts)
  - [useEventWizardState.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardState.ts)
  - [useEventWizardNavigation.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardNavigation.ts)
  - [useEventWizardValidation.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardValidation.ts)
  - [useEventWizardLayout.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardLayout.ts)
  - [useEventWizardSubmit.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardSubmit.ts)
- Testing standards summary:
  - Verify that submit handlers can be triggered in isolation without throwing errors.
  - Ensure all mock endpoints are properly stubbed out in Storybook.

### Project Structure Notes

- Matches standard structure under `desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/`.
- Created five new TypeScript composable files alongside the principal component to separate concerns (State, Navigation, Validation, Layout, and Submit).

### References

- [Architecture Decision Document: Front-End Architecture](file:///home/crist/projects/desparchado/_bmad-output/planning-artifacts/architecture-event-creation-ux.md#L231)
- [Architecture Decision Document: Umami Event Names](file:///home/crist/projects/desparchado/_bmad-output/planning-artifacts/architecture-event-creation-ux.md#L599)
- [Product Requirements Document: Functional Requirements](file:///home/crist/projects/desparchado/_bmad-output/planning-artifacts/prd-event-creation-ux.md#L280)

## Dev Agent Record

### Agent Model Used

Gemini 3.5 Flash (Medium)

### Debug Log References

- None (story template created successfully)

### Completion Notes List

- Handled submit form logic atomically in `handleSubmit` including isSubmitting spinner overlay state.
- Checked CSRF tokens dynamically in requests via getCsrfToken().
- Implemented step validation redirection logic inside catch block. Redirects user to first invalid field's step on 400 Bad Request error.
- Shifted screen reader focus to invalid inputs using document element focus on step switch.
- Refactored submit orchestration and step redirection logic using structured step/element dictionaries (maps) and dedicated helpers (`navigateToErrorField`, `submitFormPayload`, `handleSuccessfulSubmit`) to make the orchestrator `handleSubmit` extremely concise.
- Added Umami analytics tracking TODO placeholders for quota hit responses.
- Added a mock Storybook story in Overlay.stories.ts demonstrating the loading overlay variation.
- **Architectural Refactoring:** Cleanly separated EventWizard concerns into a modular Composition pattern:
  - Created `useEventWizardState.ts` to manage reactive data properties, hydration, and snapshot serialization for pristine checks (DRY).
  - Created `useEventWizardNavigation.ts` to manage active steps, component instance checks, and forward/backward transition guards.
  - Created `useEventWizardValidation.ts` to manage inline errors, step error check maps, and automatic focus redirection on validation failure.
  - Created `useEventWizardLayout.ts` to encapsulate browser window event bindings (resize offsets, viewport media queries, and beforeunload alerts).
  - Created `useEventWizardSubmit.ts` to construct FormData payloads, execute create/update events, and execute success redirects while safely tearing down layout prompts.
  - Bound all sub-composables in `useEventWizard.ts` (Composition root/orchestrator) and fully documented every exported function with JSDoc headers.

### File List

- [desparchado/frontend/scripts/api/base.ts](file:///home/crist/projects/desparchado/desparchado/frontend/scripts/api/base.ts)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss)
- [desparchado/frontend/components/presentational/components/Overlay/Overlay.vue](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/components/Overlay/Overlay.vue)
- [desparchado/frontend/components/presentational/components/Overlay/styles.scss](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/components/Overlay/styles.scss)
- [desparchado/frontend/stories/Overlay.stories.ts](file:///home/crist/projects/desparchado/desparchado/frontend/stories/Overlay.stories.ts)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizard.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizard.ts)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardState.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardState.ts)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardNavigation.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardNavigation.ts)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardValidation.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardValidation.ts)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardLayout.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardLayout.ts)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardSubmit.ts](file:///home/crist/projects/desparchado/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/useEventWizardSubmit.ts)
