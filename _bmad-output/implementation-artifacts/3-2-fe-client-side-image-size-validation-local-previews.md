---
story_key: 3-2-fe-client-side-image-size-validation-local-previews
status: done
baseline_commit: 66004b57fc74eebb4026a97a09eac98e16159761
---

# Story 3.2-FE: Client-side Image Size Validation & Local Previews

Status: done

## Story

**As a** contributor,  
**I want** to drag-and-drop or select an event image with immediate size verification and local preview rendering,  
**So that** I don't wait for server uploads only to discover my image is too large.

## Acceptance Criteria

1. **Given** the Event Image upload input zone on Step 1 of the event wizard
   - **When** a file is selected via file picker or drag-and-drop
   - **Then** the component validates that the file size is <= `MAX_IMAGE_SIZE_MB = 10` (shared constant in `desparchado/frontend/scripts/constants.ts`)
   - **And** if the file exceeds 10MB, it immediately blocks selection and displays the inline error: `"La imagen supera el límite de 10MB."` (NFR11).
2. **Given** a valid image file selection (<= 10MB)
   - **When** processed by the frontend
   - **Then** it revokes any previously created object URL via `URL.revokeObjectURL()` to prevent memory leaks
   - **And** it generates a new local object URL using `URL.createObjectURL(file)`, assigning `state.image = file` and `state.imagePreviewUrl = objectUrl`
   - **And** `EventPreview.vue` immediately renders the image locally (latency <= 50ms, no network call or early upload occurs, NFR5).
3. **Given** an uploaded or selected image preview zone
   - **When** the contributor clicks the remove/clear button
   - **Then** `URL.revokeObjectURL(state.imagePreviewUrl)` is called
   - **And** `state.image = null` and `state.imagePreviewUrl = ''` are reset
   - **And** `EventPreview.vue` reverts to displaying the "Sin imagen seleccionada" placeholder.
4. **Given** condensed display mode (`condensed = true`)
   - **When** rendered
   - **Then** the image upload zone de-emphasizes padding and height while keeping drop zone functionality intact (UX-DR8).

---

## Tasks / Subtasks

- [x] **Task 1: Create `ImageUpload.vue` Presentational Component & Styles** (AC: 1, 2, 3, 4)
  - [x] Create `desparchado/frontend/components/presentational/components/ImageUpload/ImageUpload.vue` and `styles.scss`.
  - [x] Support props: `id: string`, `label: string`, `hideLabel?: boolean`, `modelValue: File | null`, `previewUrl?: string`, `maxSizeMb?: number`, `errors?: string[]`, `disabled?: boolean`, `condensed?: boolean`.
  - [x] Support emits: `update:modelValue`, `update:previewUrl`, `error`, `blur`.
  - [x] Implement drag-and-drop event listeners (`dragover`, `dragleave`, `drop`) with active drop zone visual state.
  - [x] Validate image file type (`image/*`) and file size against `MAX_IMAGE_SIZE_MB = 10`.
  - [x] Handle object URL creation (`URL.createObjectURL`) and cleanup (`URL.revokeObjectURL`).
  - [x] Render image preview thumbnail inside component with a remove image button (`×`).
  - [x] Use BEM methodology via `bem()` helper.

- [x] **Task 2: Integrate `ImageUpload` into `Step1.vue`** (AC: 1, 2)
  - [x] Import `ImageUpload.vue` in `desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue`.
  - [x] Add Image field group to `Step1.vue` template with label `"Imagen del evento"`.
  - [x] Bind `v-model="state.image"` and `:previewUrl="state.imagePreviewUrl"`.
  - [x] Pass `condensed` prop to compact layout when condensed mode is active.

- [x] **Task 3: Add Storybook Component Stories**
  - [x] Create `desparchado/frontend/stories/ImageUpload.stories.ts`.
  - [x] Cover stories for empty drop zone, selected image preview state, error state (>10MB file), and condensed mode.

---

## Dev Notes

### Critical Guardrails & Architecture Rules

- **Vue 3 `<script lang="ts" setup>` ONLY**: No Options API, no class components.
- **Strict TypeScript**: No `any` types.
- **Path Aliases**: Always use `@presentational_components/`, `@styles/`, `@assets/`.
- **Shared Constants**:
  - `MAX_IMAGE_SIZE_MB = 10` defined in `desparchado/frontend/scripts/constants.ts`.
- **Immediate Local Preview (NFR5)**:
  - Generate preview via `URL.createObjectURL(file)`. No upload occurs until final wizard submission.
  - Always clean up previous URLs with `URL.revokeObjectURL(oldUrl)` to prevent memory leaks.
- **BEM Methodology**: Use `bem(baseClass, element, modifier)` from `@scripts/utils/bem.ts`.
- **File Locations**:
  - Component: `desparchado/frontend/components/presentational/components/ImageUpload/ImageUpload.vue`
  - SCSS: `desparchado/frontend/components/presentational/components/ImageUpload/styles.scss`
  - Integration: `desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue`
  - Storybook: `desparchado/frontend/stories/ImageUpload.stories.ts`

---

## Dev Agent Record

### Agent Model Used

Gemini 3.6 Flash (High)

### Debug Log References

- Verified ESLint script checks (`npm run lint-scripts`): 0 errors, 0 warnings.
- Verified Vite frontend module transformation (841 modules transformed).
- Verified full Python test suite (`pytest events`): 138 passed, 0 failed.

### Completion Notes List

- Built `ImageUpload.vue` presentational component supporting drag-and-drop, file input selection, local image size validation (max 10MB), local object URL preview generation (`URL.createObjectURL`), memory cleanup (`URL.revokeObjectURL`), remove image button (`×`), and condensed display mode.
- Integrated `ImageUpload.vue` into `Step1.vue` under the "Imagen del evento" field group, bound to `state.image` and `state.imagePreviewUrl`.
- Created Storybook component stories in `ImageUpload.stories.ts`.

### File List

- `desparchado/frontend/components/presentational/components/ImageUpload/ImageUpload.vue` (NEW)
- `desparchado/frontend/components/presentational/components/ImageUpload/styles.scss` (NEW)
- `desparchado/frontend/stories/ImageUpload.stories.ts` (NEW)
- `desparchado/frontend/components/presentational/containers/event-wizard/Step1/Step1.vue` (UPDATE)

### Change Log

- Initial implementation of `ImageUpload.vue` with client-side 10MB size guard and local image preview.
- Integrated `ImageUpload` component into `Step1.vue` form layout.
- Added Storybook stories for `ImageUpload.vue`.

---

## Project Context Reference

- [Project Context Rules](file:///home/crist/projects/desparchado/_bmad-output/project-context.md)
- [Architecture Decision Document](file:///home/crist/projects/desparchado/_bmad-output/planning-artifacts/architecture-event-creation-ux.md)
- [Epics Document](file:///home/crist/projects/desparchado/_bmad-output/planning-artifacts/epics-event-creation-ux.md#L442-L457)

---

## Story Completion Status

- **Status**: done
- **Completion Note**: Implementation complete and verified. Code review completed and approved. All acceptance criteria satisfied.
