---
story_key: 1-4-fe-step-1-ui-real-time-card-preview
status: done
baseline_commit: 8de405d39ae11e8124c0ef0350589a4f2b057168
---

# Story 1.4-FE: Step 1 UI & Real-Time Card Preview

Status: done

## Story

**As a** contributor,  
**I want** to fill out Step 1 fields (Title and a Quill rich text Description editor) and see them reflect immediately in the preview card,  
**So that** I have instant visual feedback on how my text formatting looks.

## Acceptance Criteria

1. **Given** the contributor is on Step 1
   * **When** typing in the Título input field
   * **Then** the state `state.title` is updated
   * **And** `EventPreview.vue` (rendered on the right on desktop) updates the title immediately (computed local update latency <= 50ms, NFR4).
2. **Given** the Description field on Step 1
   * **When** mounted
   * **Then** it initializes a Quill 2.0.3 editor showing Bold, Italic, Underline, Link insertion, Ordered List, and Unordered List formatting options
   * **And** Quill's HTML output directly updates `state.description`
   * **And** `EventPreview.vue` renders this HTML safely (using `v-html`).
3. **Given** the user is viewing the page on a mobile screen (< 768px)
   * **When** loading the wizard
   * **Then** the sidebar preview is hidden by default
   * **And** a "Ver vista previa" button is visible at the bottom
   * **And** clicking this button opens the preview card inside a mobile-friendly overlay modal (FR5).

## Tasks / Subtasks

- [x] **Task 1: Create Reusable Reusable Presentational Form Components** (AC: 1, 2)
  - [x] Create a reusable `TextField` component under [desparchado/frontend/components/presentational/components/TextField/TextField.vue](/desparchado/frontend/components/presentational/components/TextField/TextField.vue) (with styles in `styles.scss`). This component should wrap a text input field, support `v-model` binding for strings, and render labels, subheadings, descriptive guidelines, and inline validation errors dynamically.
  - [x] Create a reusable `RichTextEditor` component under [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue](/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue) (with styles in `styles.scss` importing Quill's snow stylesheet):
    ```typescript
    import Quill from 'quill';
    import 'quill/dist/quill.snow.css';
    ```
    This component should wrap a Quill 2.0.3 editor instance, accept props for value, label, subheadline, description, and errors, and emit updates.
  - [x] Configure the `RichTextEditor` Quill instance with the `snow` theme and toolbar options:
    ```typescript
    ['bold', 'italic', 'underline'],
    [{ list: 'ordered' }, { list: 'bullet' }],
    ['link']
    ```
  - [x] Synchronize editor content with `props.modelValue` on Quill's `text-change` event. To prevent validation failure when Quill has empty content containing only a boilerplate paragraph tag (e.g. `<p><br></p>`), check and emit/store as an empty string `""`.
  - [x] Watch `props.modelValue` in `RichTextEditor` and synchronize changes back into the Quill editor if updated externally (to support hydration in update/edit flow).
  - [x] Clean up Quill listeners in `onBeforeUnmount()` inside the component.

- [x] **Task 2: Integrate Reusable Components in Step1.vue** (AC: 1, 2)
  - [x] In [desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue), import the newly created reusable components:
    ```typescript
    import TextField from '../../components/TextField/TextField.vue';
    import RichTextEditor from '../../components/RichTextEditor/RichTextEditor.vue';
    ```
  - [x] Replace the raw HTML inputs for Title and Description with `<TextField>` and `<RichTextEditor>` instances.
  - [x] Bind these components to `state.title` and `state.description` respectively, and map validation errors appropriately.

- [x] **Task 3: Refine client-side and server-side HTML Sanitization Whitelists** (AC: 2)
  - [x] Update client-side HTML sanitizer [desparchado/frontend/scripts/utils/sanitize.ts](/desparchado/frontend/scripts/utils/sanitize.ts) to include Quill-generated tags: `u` (underline) and `em` (italic) tags inside `ALLOWED_TAGS` to prevent formatting loss in the preview.

- [x] **Task 4: Adapt EventPreview for Mobile Overlay Views** (AC: 3) — **⚠️ PAUSE IMPLEMENTATION AFTER THIS TASK**
  - [x] Add CSS media query rules in [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss) (and/or [desparchado/frontend/components/presentational/containers/event-wizard/EventPreview/styles.scss](/desparchado/frontend/components/presentational/containers/event-wizard/EventPreview/styles.scss)) to hide the sidebar `.event-wizard__preview` on viewports below `768px` by default.
  - [x] Implement a floating or sticky "Ver vista previa" button at the bottom of the viewport visible *only* on mobile viewports (< 768px) when the wizard is active.
  - [x] Add a mobile overlay preview container or lightweight modal wrapper in [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue). Keep a reactive boolean flag `showMobilePreview` (default: `false`).
  - [x] When clicking "Ver vista previa", set `showMobilePreview` to `true` to mount/display the overlay containing the `EventPreview` card.
  - [x] Add a close button (or tap-outside mechanism) in the overlay to toggle `showMobilePreview` back to `false`.
  - [x] **⚠️ PAUSE POINT:** Stop execution here for validation and human verification of the core components and mobile preview overlay logic before proceeding to UI styling and Storybook.

- [x] **Task 5: UI & Styling Refinement** (AC: 1, 2, 3)
  - [x] Style the Quill editor container inside `RichTextEditor` to integrate cleanly with BEM-style forms (applying `.wizard-field__input` borders and focus styles to the `.ql-container` and `.ql-toolbar`).
  - [x] Add styling for the mobile overlay modal in [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss) to cover the full screen, set a high z-index, and enable scrollable preview content.

- [x] **Task 6: Storybook Integration** (AC: 1, 2, 3)
  - [x] Add or update Storybook stories in [desparchado/frontend/stories/EventWizard.stories.ts](/desparchado/frontend/stories/EventWizard.stories.ts) to show Step1 with the integrated components.
  - [x] Create a story showing the mobile overlay viewport preview mode in Storybook.
  - [x] Create a dedicated Storybook story for [desparchado/frontend/components/presentational/components/TextField/TextField.vue](/desparchado/frontend/components/presentational/components/TextField/TextField.vue) to document all its props (label, subheadline, description, error, and models).
  - [x] Create a dedicated Storybook story for [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue](/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue) to verify Quill editor load, formatting toolbar states, and validation error layouts.

## Dev Notes

### Architecture References
- Architecture document: [_bmad-output/planning-artifacts/architecture-event-creation-ux.md](/_bmad-output/planning-artifacts/architecture-event-creation-ux.md)
  - Sections: "Frontend Architecture", "Enforcement Rules", "Vue Component Tree — Location & Naming", "Step Validation Rules"
- PRD document: [_bmad-output/planning-artifacts/prd-event-creation-ux.md](/_bmad-output/planning-artifacts/prd-event-creation-ux.md)
  - Sections: "Functional Requirements" (FR5, FR8, FR37, FR38), "Non-Functional Requirements" (NFR4, NFR5)

### Project Structure & Component Locations
* Reusable presentational components belong to `desparchado/frontend/components/presentational/components/`
  - [desparchado/frontend/components/presentational/components/TextField/TextField.vue](/desparchado/frontend/components/presentational/components/TextField/TextField.vue) (Reusable title text field)
  - [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue](/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue) (Reusable rich text Quill editor)
* Event wizard components are colocated in `desparchado/frontend/components/presentational/EventWizard/`
  - [desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue) (Step 1 component)
  - [desparchado/frontend/components/presentational/containers/event-wizard/EventPreview/EventPreview.vue](/desparchado/frontend/components/presentational/containers/event-wizard/EventPreview/EventPreview.vue) (Live preview component)
  - [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue) (Root container)

### Code Reuse & Wheel Reinvention
- Use the BEM stylesheet conventions via the `bem()` helper in `desparchado/frontend/scripts/utils/bem.ts`.
- Ensure Quill stylesheet is imported inside `RichTextEditor.vue` (or scoped to it) to scope it properly without polluting global CSS.
- Since `BaseModal` is NOT implemented yet (it is planned for Epic 2), implement a simple, lightweight modal overlay component or slot directly in `EventWizard.vue` for the mobile preview overlay. Do not attempt to import `BaseModal` as it will cause build errors.

### Preserving Existing Systems & Sanitizer Whitelisting
- We must update the client-side [desparchado/frontend/scripts/utils/sanitize.ts](/desparchado/frontend/scripts/utils/sanitize.ts) to permit tags Quill creates, namely `u` and `em` tags.
- Ensure that Quill's HTML output is kept clean and synchronized with Vue's reactive state to allow the real-time card preview to render in `<EventPreview>` via `v-html`.

## File List

### UPDATE Files
- [desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue](/desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue)
- [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss](/desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss)
- [desparchado/frontend/scripts/utils/sanitize.ts](/desparchado/frontend/scripts/utils/sanitize.ts)
- [desparchado/frontend/stories/EventWizard.stories.ts](/desparchado/frontend/stories/EventWizard.stories.ts)
- [desparchado/frontend/styles/_common.scss](/desparchado/frontend/styles/_common.scss)

### NEW Files
- [desparchado/frontend/components/presentational/components/TextField/TextField.vue](/desparchado/frontend/components/presentational/components/TextField/TextField.vue)
- [desparchado/frontend/components/presentational/components/TextField/styles.scss](/desparchado/frontend/components/presentational/components/TextField/styles.scss)
- [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue](/desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue)
- [desparchado/frontend/components/presentational/components/RichTextEditor/styles.scss](/desparchado/frontend/components/presentational/components/RichTextEditor/styles.scss)
- [desparchado/frontend/components/presentational/components/Overlay/Overlay.vue](/desparchado/frontend/components/presentational/components/Overlay/Overlay.vue)
- [desparchado/frontend/components/presentational/components/Overlay/styles.scss](/desparchado/frontend/components/presentational/components/Overlay/styles.scss)
- [desparchado/frontend/stories/TextField.stories.ts](/desparchado/frontend/stories/TextField.stories.ts)
- [desparchado/frontend/stories/RichTextEditor.stories.ts](/desparchado/frontend/stories/RichTextEditor.stories.ts)
- [desparchado/frontend/stories/Overlay.stories.ts](/desparchado/frontend/stories/Overlay.stories.ts)

## Dev Agent Record

### Agent Model Used

Gemini 3.5 Flash (Medium)

### Debug Log References
- None.

### Completion Notes List
- Created reusable `TextField` and `RichTextEditor` components with custom SCSS styling.
- Configured Quill 2.0.3 Snow theme and toolbar settings inside `RichTextEditor.vue`.
- Sanitized rich text empty boilerplate paragraphs.
- Implemented responsive mobile layout that hides sidebar preview and provides a sticky "Ver vista previa" button.
- Handled mobile overlay modal for real-time card preview inside `EventWizard.vue`.
- Updated client-side sanitizer whitelist to allow `u` and `em` tags in `sanitize.ts`.
- Integrated components inside `Step1.vue`.
- Added new Storybook stories for `TextField`, `RichTextEditor`, and mobile preview in `EventWizard.stories.ts`.

### File List
- desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue
- desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue
- desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss
- desparchado/frontend/scripts/utils/sanitize.ts
- desparchado/frontend/stories/EventWizard.stories.ts
- desparchado/frontend/styles/_common.scss
- desparchado/frontend/components/presentational/components/TextField/TextField.vue
- desparchado/frontend/components/presentational/components/TextField/styles.scss
- desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue
- desparchado/frontend/components/presentational/components/RichTextEditor/styles.scss
- desparchado/frontend/components/presentational/components/Overlay/Overlay.vue
- desparchado/frontend/components/presentational/components/Overlay/styles.scss
- desparchado/frontend/stories/TextField.stories.ts
- desparchado/frontend/stories/RichTextEditor.stories.ts
- desparchado/frontend/stories/Overlay.stories.ts

### Review Findings

#### Decision Needed
- [x] [Review][Decision] Overlay component placement constraint deviation — Resolved: Keep the separate Overlay component.

#### Patches
- [x] [Review][Patch] Broken Relative Imports [desparchado/frontend/components/presentational/components/Overlay/Overlay.vue:219]
- [x] [Review][Patch] Deprecated Javascript Method Usage & Unsafe Redirect [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue:862]
- [x] [Review][Patch] Potential TypeError Crash (Optional Chaining Removal) [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/EventWizard.vue:861]
- [x] [Review][Patch] Lack of Keyboard Dismissal Support [desparchado/frontend/components/presentational/components/Overlay/Overlay.vue:200-216]
- [x] [Review][Patch] Scroll Leakage (Absent Body Scroll Lock) [desparchado/frontend/components/presentational/components/Overlay/Overlay.vue:218-237]
- [x] [Review][Patch] Missing Focus Trapping in Overlay/Modal [desparchado/frontend/components/presentational/components/Overlay/Overlay.vue]
- [x] [Review][Patch] Redundant DOM Reset when Clearing the RichTextEditor [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue:383-388]
- [x] [Review][Patch] Quill Editor Selection Index Crash on External Update [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue:424-429]
- [x] [Review][Patch] Erroneous Empty Content Detection in RichTextEditor [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue:382-385]
- [x] [Review][Patch] Broken Label-Input Association (A11y/HTML Validation) [desparchado/frontend/components/presentational/components/RichTextEditor/RichTextEditor.vue:321]
- [x] [Review][Patch] Incomplete Presentational Component Styles [desparchado/frontend/components/presentational/components/TextField/styles.scss]
- [x] [Review][Patch] Focus Visual Defect in RichTextEditor [desparchado/frontend/components/presentational/components/RichTextEditor/styles.scss:517-528]
- [x] [Review][Patch] Input event fired with null or non-input target [desparchado/frontend/components/presentational/components/TextField/TextField.vue:601-604]
- [x] [Review][Patch] Missing Subheadline and Description props in reusable Form Components [desparchado/frontend/components/presentational/components/TextField/TextField.vue]


#### Deferred Items
- [x] [Review][Defer] URL Sanitizer Bypassed via Uppercase Schemes [desparchado/frontend/scripts/utils/sanitize.ts:39-44] — deferred, pre-existing
- [x] [Review][Defer] Hardcoded Stacking Context Magic Numbers [desparchado/frontend/components/presentational/containers/event-wizard/EventWizard/styles.scss:924] — deferred, pre-existing

