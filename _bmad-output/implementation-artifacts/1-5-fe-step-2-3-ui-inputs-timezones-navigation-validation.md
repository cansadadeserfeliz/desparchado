---
story_key: 1-5-fe-step-2-3-ui-inputs-timezones-navigation-validation
status: done
baseline_commit: 90a6e94a8d1e6e033890f7b31d924a12d84a0892
---

# Story 1.5-FE: Step 2 & 3 UI Inputs, Timezones & Navigation Validation

Status: done

## Story

**As a** contributor,  
**I want** to fill out date/time, category cards, price, source URL, and drafts toggles, with strict required-field validation gating step progression,  
**So that** I cannot navigate away from a step with missing or invalid required data.

## Acceptance Criteria

1. **Given** the contributor is on Step 2
   * **When** they pick a date/time
   * **Then** `state.eventDate` is stored as an ISO string in the `America/Bogota` timezone (UTC-5 offset).
2. **Given** the contributor is on Step 3
   * **When** they click one of the 5 category cards (Literatura, Arte, Sociedad, Ciencia, Medio Ambiente)
   * **Then** the selection updates `state.category` and highlights the active card
   * **And** they can toggle `state.isPublished` and enter `state.price` and `state.eventSourceUrl`.
3. **Given** the step navigation validator evaluates progression:
   * **When** on **Step 1**: "Paso siguiente" is disabled unless **Title**, **Description** (Quill editor output), and **Organizers** (min 1) are populated. (Note: Organizers selection will be stubbed as a hardcoded ID for now so this story can be validated independently before Epic 2 is built).
   * **When** on **Step 2**: "Paso siguiente" is disabled unless **Date/Time** and **Place** are populated. (Place will be stubbed as a hardcoded ID for now).
   * **When** on **Step 3**: "Publicar" (or "Guardar cambios") is disabled unless **Event Source URL** is populated and contains a valid URL format.
   * **And** moving focus away from any required field without populating it displays a red validation error: "Este campo es requerido".

## Tasks / Subtasks

- [x] **Task 1: Create Reusable Form Fields (NumberField, TimeField, ToggleField, RadioCategoryField)** (AC: 1, 2, 3)
  - [x] Create a reusable `TimeField` component at [/desparchado/frontend/components/presentational/components/TimeField/TimeField.vue](/desparchado/frontend/components/presentational/components/TimeField/TimeField.vue) (with styles in `styles.scss`) wrapping `<input type="datetime-local">`. It should handle local timezone conversion, input blur validation error displaying `"Este campo es requerido"`, and emit updates.
  - [x] Create a reusable `NumberField` component at [/desparchado/frontend/components/presentational/components/NumberField/NumberField.vue](/desparchado/frontend/components/presentational/components/NumberField/NumberField.vue) (with styles in `styles.scss`) wrapping `<input type="number">`. It should support `v-model`, `min`, `placeholder`, and display any validation errors.
  - [x] Create a reusable `ToggleField` component at [/desparchado/frontend/components/presentational/components/ToggleField/ToggleField.vue](/desparchado/frontend/components/presentational/components/ToggleField/ToggleField.vue) (with styles in `styles.scss`) that behaves as a styled switch or checkbox input. It should accept `label` and support boolean binding for `v-model`.
  - [x] Create a reusable `RadioCategoryField` component at [/desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue](/desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue) (with styles in `styles.scss`) based on standard HTML `<input type="radio">` buttons styled to look like visual cards. It displays 5 visual cards for the choices (Literatura, Arte, Sociedad, Ciencia, Medio Ambiente), highlights the selected category, and supports toggle-to-deselect back to `'other'`.

- [x] **Task 2: Implement Timezone-Aware DateTime Picker & Validation in Step 2** (AC: 1, 3)
  - [x] Update [/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue) to use the new `<TimeField>` component instead of raw input.
  - [x] Implement computed writable binding or timezone offset setter inside `<TimeField>` or [/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue) to map `YYYY-MM-DDTHH:mm` to `America/Bogota` timezone suffix (`:00-05:00`) in `state.eventDate`.
  - [x] Configure `TimeField` blur handler to show `"Este campo es requerido"` if empty.
  - [x] Update the `isValid` computed property in [/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue) to return `true` only if `props.state.eventDate` and `props.state.placeId` are populated. Expose it via `defineExpose({ isValid })`.

- [x] **Task 3: Build Category Visual Cards & Inputs in Step 3** (AC: 2, 3)
  - [x] Update [/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue) to use `<RadioCategoryField>` for selecting the category, `<NumberField>` for the price, `<TextField>` for the event source URL, and `<ToggleField>` for the immediate publishing toggle.
  - [x] Add `@blur="handleUrlBlur"` to the event source URL field inside Step 3. If empty, set local validation error `"Este campo es requerido"`. If invalid URL format, set `"Formato de URL no válido"`.
  - [x] Update the `isValid` computed property in [/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue) to return `true` only if `props.state.eventSourceUrl` is a valid URL format. Expose it via `defineExpose({ isValid })`.

- [x] **Task 4: Refine Focus-Out Validation in Reusable Form Components & Step 1** (AC: 3)
  - [x] Update [/desparchado/frontend/components/presentational/components/TextField/TextField.vue](/desparchado/frontend/components/presentational/components/TextField/TextField.vue) to listen to `@blur="handleBlur"`. If `required` is true and `modelValue` is empty, set a local reactive error `localError.value = 'Este campo es requerido'`.
  - [x] Update [/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue](/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue) to register a `blur` event listener on `quillInstance.root`. If `required` is true and description content is empty (blank or only `<p><br></p>`), set a local error `localError.value = 'Este campo es requerido'`. Ensure to clean up the event listener on unmount.
  - [x] Update `isValid` computed property in [/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue) to check that `props.state.title` is non-empty, `props.state.description` has formatted text, and `props.state.organizerIds` has at least 1 item.

- [x] **Task 5: Initialize Stubs, Buttons and Styling in EventWizard** (AC: 3)
  - [x] Update [/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue) to use `<ToggleField>` for the condensed mode toggle switch.
  - [x] Replace the raw HTML footer navigation buttons with the reusable `<Button>` component imported from `@presentational_components/atoms/button/Button.vue`:
    - "Paso anterior": `<Button type="secondary" label="Paso anterior" :onClick="handlePrev" :disabled="currentStep === 1 || isSubmitting" />`
    - "Paso siguiente": `<Button type="primary" label="Paso siguiente" :onClick="handleNext" :disabled="!isCurrentStepValid" />`
    - Submit ("Crear evento" / "Guardar cambios"): `<Button type="primary" :label="isSubmitting ? 'Guardando...' : mode === 'edit' ? 'Guardar cambios' : 'Crear evento'" :onClick="handleSubmit" :disabled="!isCurrentStepValid || isSubmitting" />`
  - [x] Update reactive state initializer: set `organizerIds: props.mode === 'create' ? [1] : []` and `placeId: props.mode === 'create' ? 1 : null` so they are pre-populated with stub values during creation.
  - [x] Ensure that step validation checks `isCurrentStepValid` correctly disables the final submit button in Step 3 (`:disabled="!isCurrentStepValid || isSubmitting"`).

- [x] **Task 6: Storybook Integration** (AC: 1, 2, 3)
  - [x] Create Storybook stories for the new reusable inputs: `NumberField`, `TimeField`, `ToggleField`, and `RadioCategoryField`.
  - [x] Update stories in [/desparchado/frontend/stories/EventWizard.stories.ts](/desparchado/frontend/stories/EventWizard.stories.ts) to verify the new visual category card components, datetimepicker bindings, and step validation disabling behavior under different wizard state scenarios.

### Review Findings

- [x] [Review][Decision] Step Validation Rule Discrepancy (Story Spec vs. Architecture Decision Document) — The Architecture Decision Document (under "Step Validation Rules") specifies that Step 3 is "Always true — all fields optional in UI; event_source_url validated server-side on submit." However, the Story Spec Acceptance Criteria 3 mandates that the wizard's progression/submit is disabled in Step 3 unless eventSourceUrl is populated and contains a valid URL format. The diff implements the Story Spec's constraint, making it a required field in the UI. This directly contradicts the architecture document. (Resolved: Option 1 selected, story spec is enforced)
- [x] [Review][Patch] Broken focus-out (blur) validation on URL Field in Step 3 [desparchado/frontend/components/presentational/components/TextField/TextField.vue] (Fixed)
- [x] [Review][Patch] Missing required Prop on Quill RichTextEditor in Step 1 [desparchado/frontend/containers/event-wizard/Step1/Step1.vue] (Fixed)
- [x] [Review][Patch] Invalid Link Disabling in Button.vue [desparchado/frontend/components/presentational/atoms/button/Button.vue] (Fixed)
- [x] [Review][Patch] TextField Validation Whitespace Bypass [desparchado/frontend/components/presentational/components/TextField/TextField.vue] (Fixed)
- [x] [Review][Patch] URL Whitespace Validation Failure [desparchado/frontend/containers/event-wizard/Step3/Step3.vue] (Fixed)
- [x] [Review][Patch] Loss of Type Safety in NumberField.vue [desparchado/frontend/components/presentational/components/NumberField/NumberField.vue] (Dismissed)
- [x] [Review][Patch] Misleading Error Messages for Invalid Numbers [desparchado/frontend/components/presentational/components/NumberField/NumberField.vue] (Fixed, with negative number validation rendering 0 on blur)
- [x] [Review][Patch] Timezone and Date parsing bugs in TimeField.vue [desparchado/frontend/components/presentational/components/TimeField/TimeField.vue] (Fixed)
- [x] [Review][Patch] False-positive Dirty Form Warnings due to serialization mismatch [desparchado/frontend/containers/event-wizard/EventWizard/EventWizard.vue] (Fixed)
- [x] [Review][Patch] Validation Error Cleared/Triggered Prematurely by Programmatic Clears [desparchado/frontend/components/presentational/components/TextField/TextField.vue] (Fixed)
- [x] [Review][Patch] Destructive Local Error Shadowing [reusable form fields] (Fixed)
- [x] [Review][Patch] Broken Keyboard Accessibility in RadioCategoryField.vue [desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue] (Fixed)
- [x] [Review][Defer] Aspect-Ratio Layout Overflow Risk [desparchado/frontend/components/presentational/components/RadioCategoryField/styles.scss] — deferred, pre-existing
- [x] [Review][Patch] Inconsistent Edit Mode State Initialization [desparchado/frontend/containers/event-wizard/EventWizard/EventWizard.vue] (Fixed)
- [x] [Review][Patch] ESLint Compatibility Hazard with import.meta.dirname [eslint.config.mjs] (Dismissed)
- [x] [Review][Patch] Critical Timezone Shift Bug in Edit Mode Form Submission [desparchado/frontend/containers/event-wizard/EventWizard/EventWizard.vue] (Dismissed)
- [x] [Review][Patch] Broken Vue 3 Reactivity in Wizard Step Navigation Validation [desparchado/frontend/containers/event-wizard/EventWizard/EventWizard.vue] (Dismissed)
- [x] [Review][Patch] Incorrect Error State Persistence when Clearing Invalid URL [desparchado/frontend/containers/event-wizard/Step3/Step3.vue] (Dismissed)
- [x] [Review][Patch] Premature blur validation in Quill editor [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue] (Dismissed)
- [x] [Review][Patch] Invalid or partial datetime inputs bypass required validation due to missing validity check [desparchado/frontend/components/presentational/components/TimeField/TimeField.vue] (Dismissed)
- [x] [Review][Patch] Incomplete HTML validation bypass in Step 1 description [desparchado/frontend/containers/event-wizard/Step1/Step1.vue] (Dismissed)
- [x] [Review][Patch] Incomplete server error clearing for organizers, speakers, and place [desparchado/frontend/containers/event-wizard/EventWizard/EventWizard.vue] (Dismissed)
- [x] [Review][Patch] Invalid HTML default type on non-submit buttons [desparchado/frontend/atoms/button/Button.vue] (Dismissed)

## Dev Notes


### Architecture References
- Architecture document: [/_bmad-output/planning-artifacts/architecture-event-creation-ux.md](/_bmad-output/planning-artifacts/architecture-event-creation-ux.md)
  - Sections: "Frontend Architecture", "Enforcement Rules", "Vue Component Tree — Location & Naming", "Step Validation Rules"
- PRD document: [/_bmad-output/planning-artifacts/prd-event-creation-ux.md](/_bmad-output/planning-artifacts/prd-event-creation-ux.md)
  - Sections: "Functional Requirements" (FR2, FR3, FR10, FR14, FR15, FR16, FR21), "Non-Functional Requirements" (NFR9)

### Project Structure & Component Locations
* Event wizard containers:
  - [/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue)
  - [/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue)
  - [/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue)
  - [/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue)
  - [/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss)
* Reusable components:
  - [/desparchado/frontend/components/presentational/components/TextField/TextField.vue](/desparchado/frontend/components/presentational/components/TextField/TextField.vue)
  - [/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue](/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue)
  - [/desparchado/frontend/components/presentational/components/NumberField/NumberField.vue](/desparchado/frontend/components/presentational/components/NumberField/NumberField.vue)
  - [/desparchado/frontend/components/presentational/components/TimeField/TimeField.vue](/desparchado/frontend/components/presentational/components/TimeField/TimeField.vue)
  - [/desparchado/frontend/components/presentational/components/ToggleField/ToggleField.vue](/desparchado/frontend/components/presentational/components/ToggleField/ToggleField.vue)
  - [/desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue](/desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue)

### Code Reuse & Anti-Patterns
- **Do not bypass computed bindings:** Use local computed writable variables for complex datetime input synchronization rather than directly mutating the parent state with unformatted values.
- **CSRF Token:** Mutations remain secure under CSRF checks via `formFetch`.
- **Don't hardcode timezone offsets elsewhere:** Treat `America/Bogota` as UTC-5 offset `-05:00`.

## File List

### UPDATE Files
- [/desparchado/frontend/components/presentational/components/TextField/TextField.vue](/desparchado/frontend/components/presentational/components/TextField/TextField.vue)
- [/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue](/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss)
- [/desparchado/frontend/stories/EventWizard.stories.ts](/desparchado/frontend/stories/EventWizard.stories.ts)

### NEW Files
- [/desparchado/frontend/components/presentational/components/NumberField/NumberField.vue](/desparchado/frontend/components/presentational/components/NumberField/NumberField.vue)
- [/desparchado/frontend/components/presentational/components/NumberField/styles.scss](/desparchado/frontend/components/presentational/components/NumberField/styles.scss)
- [/desparchado/frontend/components/presentational/components/TimeField/TimeField.vue](/desparchado/frontend/components/presentational/components/TimeField/TimeField.vue)
- [/desparchado/frontend/components/presentational/components/TimeField/styles.scss](/desparchado/frontend/components/presentational/components/TimeField/styles.scss)
- [/desparchado/frontend/components/presentational/components/ToggleField/ToggleField.vue](/desparchado/frontend/components/presentational/components/ToggleField/ToggleField.vue)
- [/desparchado/frontend/components/presentational/components/ToggleField/styles.scss](/desparchado/frontend/components/presentational/components/ToggleField/styles.scss)
- [/desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue](/desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue)
- [/desparchado/frontend/components/presentational/components/RadioCategoryField/styles.scss](/desparchado/frontend/components/presentational/components/RadioCategoryField/styles.scss)
- [/desparchado/frontend/stories/NumberField.stories.ts](/desparchado/frontend/stories/NumberField.stories.ts)
- [/desparchado/frontend/stories/TimeField.stories.ts](/desparchado/frontend/stories/TimeField.stories.ts)
- [/desparchado/frontend/stories/ToggleField.stories.ts](/desparchado/frontend/stories/ToggleField.stories.ts)
- [/desparchado/frontend/stories/RadioCategoryField.stories.ts](/desparchado/frontend/stories/RadioCategoryField.stories.ts)

## Dev Agent Record

### Agent Model Used

Gemini 3.5 Flash (Medium)

### Debug Log References

- None (all local linting/testing ran cleanly)

### Completion Notes List

- Created reusable BEM-styled components: `NumberField`, `TimeField`, `ToggleField`, and `RadioCategoryField` under `/desparchado/frontend/components/presentational/components/`.
- Handled timezone mapping inside `TimeField.vue` to map user datetime inputs to the `America/Bogota` timezone (`-05:00`) inside the wizard state (`state.eventDate`).
- Implemented responsive, real-time focus-out (`blur`) validation to display "Este campo es requerido" or "Formato de URL no válido" error messages.
- Updated `Step1.vue`, `Step2.vue`, and `Step3.vue` step validation computed properties to correctly check that all required fields are valid before allowing transition.
- Pre-populated the event creation wizard stubs for `organizerIds` (`[1]`) and `placeId` (`1`) so that validation is successful.
- Created custom Storybook stories for the new components and updated `EventWizard.stories.ts` with test stories for the wizard steps.
- Excluded coverage output `**/htmlcov/**` and root configuration `backstop.config.js` from ESLint.
- Added visual disabled states and pointer-events prevention to `Button.vue` and its stylesheet.
- Added the `unit` prop to `NumberField.vue` to render a gray helper unit to the right inside the input field, and updated the price input in `Step3.vue` to use it (rendering `COP` inside the field).
- Used the global `.visually-hidden` class utility on inputs in `ToggleField.vue` and `RadioCategoryField.vue` templates rather than manually setting visually hidden CSS properties inside their SCSS files.
- Redesigned `RadioCategoryField.vue` to render 6 distinct grid cards, each containing a category value title, a descriptive subtitle, and using the reusable `Icon` component.
- Registered custom SVG shapes (book, pencil, codesandbox, loader, feather, ghost) as symbols inside the global `icons.svg` asset sprite, inheriting text/interaction colors dynamically.
- Adjusted `RadioCategoryField` styling to format cards with a squared aspect ratio, align titles and icons horizontally in a top header row, space details appropriately, and use heading 4 typography for titles and heading 5 typography for descriptions, with consistent active color state- Reduced category card dimensions by rendering 3 columns on desktop (and 2 on mobile) and aligned descriptions to the bottom of each card using flexible margin-top.
- Configured category cards with a fully transparent background and applied color inheritance so that all elements (title, description, and icon wrapper) share the exact same foreground color in normal, hover, and selected states.
- Implemented support for the condensed variation of category cards, reducing their padding, unsetting the square aspect ratio, and omitting category descriptions when the wizard is in condensed mode.
- Configured field title headlines (`.wizard-field__headline`) to scale down to heading 4 typography inside the condensed EventWizard layout.
- Decoupled category selections by refactoring `RadioCategoryField.vue` to receive choices as a prop, declaring the `categoryChoices` configuration array directly inside its parent `Step3.vue` component.

### File List

- [/desparchado/frontend/components/presentational/components/TextField/TextField.vue](/desparchado/frontend/components/presentational/components/TextField/TextField.vue)
- [/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue](/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step2/Step2.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step3/Step3.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue)
- [/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss)
- [/desparchado/frontend/stories/EventWizard.stories.ts](/desparchado/frontend/stories/EventWizard.stories.ts)
- [/desparchado/frontend/components/presentational/components/NumberField/NumberField.vue](/desparchado/frontend/components/presentational/components/NumberField/NumberField.vue)
- [/desparchado/frontend/components/presentational/components/NumberField/styles.scss](/desparchado/frontend/components/presentational/components/NumberField/styles.scss)
- [/desparchado/frontend/components/presentational/components/TimeField/TimeField.vue](/desparchado/frontend/components/presentational/components/TimeField/TimeField.vue)
- [/desparchado/frontend/components/presentational/components/TimeField/styles.scss](/desparchado/frontend/components/presentational/components/TimeField/styles.scss)
- [/desparchado/frontend/components/presentational/components/ToggleField/ToggleField.vue](/desparchado/frontend/components/presentational/components/ToggleField/ToggleField.vue)
- [/desparchado/frontend/components/presentational/components/ToggleField/styles.scss](/desparchado/frontend/components/presentational/components/ToggleField/styles.scss)
- [/desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue](/desparchado/frontend/components/presentational/components/RadioCategoryField/RadioCategoryField.vue)
- [/desparchado/frontend/components/presentational/components/RadioCategoryField/styles.scss](/desparchado/frontend/components/presentational/components/RadioCategoryField/styles.scss)
- [/desparchado/frontend/stories/NumberField.stories.ts](/desparchado/frontend/stories/NumberField.stories.ts)
- [/desparchado/frontend/stories/TimeField.stories.ts](/desparchado/frontend/stories/TimeField.stories.ts)
- [/desparchado/frontend/stories/ToggleField.stories.ts](/desparchado/frontend/stories/ToggleField.stories.ts)
- [/desparchado/frontend/stories/RadioCategoryField.stories.ts](/desparchado/frontend/stories/RadioCategoryField.stories.ts)
- [/desparchado/frontend/components/presentational/atoms/button/Button.vue](/desparchado/frontend/components/presentational/atoms/button/Button.vue)
- [/desparchado/frontend/components/presentational/atoms/button/styles.scss](/desparchado/frontend/components/presentational/atoms/button/styles.scss)
- [/desparchado/frontend/assets/icons.svg](/desparchado/frontend/assets/icons.svg)
- [/eslint.config.mjs](/eslint.config.mjs)

## Change Log

- 2026-07-01: Implemented reusable NumberField, TimeField, ToggleField, and RadioCategoryField components. Added timezone handling for America/Bogota in TimeField. Implemented focus-out blur validation across form components. Refined Step 1, Step 2, and Step 3 validation gates. Integrated components into EventWizard and created Storybook stories. Handled disabled states on buttons without !important rules, and refactored the price input COP label into a field unit helper. Refactored ToggleField and RadioCategoryField inputs to use the global .visually-hidden class utility. Redesigned RadioCategoryField visual cards with descriptions, registered category icons in the global icons.svg sprite, and utilized the reusable Icon component. Configured cards with a squared ratio, aligned titles/icons in a top header row, used heading 4 and 5 typographies with matched states, reduced card dimensions with a 3-column layout, aligned description bodies to the bottom of the card, made card backgrounds transparent, synchronized foreground color inheritance using gray-900 by default, added condensed layout overrides to support reduced padding and hidden descriptions on smaller aspect ratios, scaled down field titles in condensed mode to heading 4, and decoupled options by declaring categoryChoices directly inside the parent Step3.vue component. All frontend checks and backend tests passed.
