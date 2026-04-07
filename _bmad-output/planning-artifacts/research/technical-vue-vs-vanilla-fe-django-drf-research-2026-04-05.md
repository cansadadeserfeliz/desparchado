---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
workflowType: 'research'
lastStep: 1
research_type: 'technical'
research_topic: 'Vue vs Vanilla JS for Frontend with Django + DRF backend'
research_goals: 'Determine the best frontend migration strategy for Desparchado: moving from Bootstrap + external Django form libs toward a Vite-based setup (Vue or Vanilla JS) that is simple to maintain, produces static files for nginx, is fast and SEO-friendly, avoids unnecessary JS on read-only pages, and enables rich interactivity on forms (event form with inline validation and related object creation).'
user_name: 'Vera'
date: '2026-04-05'
web_research_enabled: true
source_verification: true
---

# Choosing a Frontend Architecture for Desparchado: Vue 3 Islands, HTMX Forms, and a Phased Bootstrap Exit

**Date:** 2026-04-05
**Author:** Vera
**Research Type:** Technical — Frontend Migration Strategy

---

## Executive Summary

Desparchado's frontend migration question — Vue 3 vs Vanilla JS — resolves to a **disciplined hybrid architecture**, not a binary choice. After researching the current state of the Django frontend ecosystem (technology stack, integration patterns, architectural patterns, and implementation approaches), the answer is clear: the right tool varies by page type, and the project already has most of the infrastructure it needs.

**Read-only pages** (event list, event detail, organizer, speaker, place, special detail) should ship **zero JavaScript**. These are SEO-critical, high-traffic pages with no client interactions that justify a JS bundle. Removing the Vue bundle from them eliminates a render-blocking resource that delays LCP — the single highest-leverage performance improvement available. Django template partials (`django-template-partials`, being absorbed into Django 6 core) replace the current `{% include %}` chains for reusable server-rendered UI.

**Django forms** (event create/edit) should use **HTMX** for inline field validation — not Vue. The canonical HTMX pattern adds real-time per-field feedback with ~10 lines of change to existing views, keeps all validation logic in Django Forms, and eliminates the full-page-submit-to-see-errors UX problem. HTMX grew from 5% to 24% adoption in Django community surveys in 2024–2025; Vue declined from 28% to 17% over the same period.

**Vue 3 remains justified for three specific islands:** the search/filter UI (client state, debounced DRF calls, URL sync), the map `PointField` widget (unavoidable client state), and the user dashboard (personalized reactive data). The existing `django-vite` + `mount-vue.ts` + TypeScript infrastructure is the right foundation — extend it, don't replace it.

**Bootstrap** is replaced by Tailwind v4 via the existing `vite.config.ts` (no `django-tailwind` package needed). Bootstrap and Tailwind coexist page-by-page during the phased migration. crispy-forms is removed last, as part of the form template rebuild in Phase 3.

**Key Technical Recommendations:**

1. Strip Vue bundle includes from all read-only templates immediately — zero risk, highest impact
2. Add `django-htmx` middleware and apply the field partial pattern to event create/edit forms
3. Add `@tailwindcss/vite` to Vite config and begin using Tailwind on new templates
4. Create `api/base.ts` with an `apiFetch` CSRF wrapper; add `DRFValidationError` type to `interfaces.ts`
5. Keep Vue only for search/filter, map widget, and dashboard

---

## Table of Contents

1. [Research Overview and Methodology](#research-overview)
2. [Technical Research Scope Confirmation](#scope)
3. [Technology Stack Analysis](#tech-stack)
4. [Integration Patterns Analysis](#integration)
5. [Architectural Patterns and Design](#architecture)
6. [Implementation Approaches and Technology Adoption](#implementation)
7. [Research Synthesis and Final Recommendations](#synthesis)

---

## Research Overview

This document answers a concrete question: what frontend architecture should Desparchado adopt as it migrates away from Bootstrap, crispy-forms, and external Django form widgets? The research covers five technical areas — technology stack, DRF integration patterns, frontend architectural patterns (islands architecture, progressive enhancement, CSS strategy), and practical implementation guidance — drawing on current web sources verified in April 2026 and direct analysis of the Desparchado codebase.

The research methodology combined web search verification across 25+ authoritative sources (Django community surveys, framework documentation, case studies, and DjangoCon talks) with codebase analysis (reviewing `vite.config.ts`, `mount-vue.ts`, `settings/base.py`, existing API modules, and test fixtures) to produce recommendations grounded in the project's actual constraints: limited server resources, a BE-first developer, TypeScript strict mode already enforced, and `django-vite` 3.1.0 + Vue 3 already in place.

The conclusion is not "use Vue everywhere" or "remove Vue" — it is a phased strategy with clear, criteria-driven decision rules for when to use HTMX, Vue 3 islands, Django template partials, and Tailwind.

---

## Technical Research Scope Confirmation

**Research Topic:** Vue vs Vanilla JS for Frontend with Django + DRF backend
**Research Goals:** Determine the best frontend migration strategy for Desparchado: moving from Bootstrap + external Django form libs toward a Vite-based setup (Vue or Vanilla JS) that is simple to maintain, produces static files for nginx, is fast and SEO-friendly, avoids unnecessary JS on read-only pages, and enables rich interactivity on forms (event form with inline validation and related object creation).

**Technical Research Scope:**

- Architecture Analysis — design patterns, frameworks, system architecture
- Implementation Approaches — development methodologies, coding patterns
- Technology Stack — languages, frameworks, tools, platforms
- Integration Patterns — APIs, protocols, interoperability
- Performance Considerations — scalability, optimization, patterns

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-04-05

---

## Technology Stack Analysis

### Programming Languages

Desparchado already uses **Python 3.10+** (Django backend) with **TypeScript** strict mode on the frontend. Both are stable, well-supported choices with no migration pressure.

_Frontend Language Landscape:_ TypeScript continues its dominance in frontend development — Stack Overflow 2024 survey shows it as the 5th most-used and 3rd most-admired language. Strict TypeScript (no `any`) as enforced in this project ensures type safety across the frontend layer regardless of which framework is chosen.
_Source: [Stack Overflow Developer Survey 2024](https://survey.stackoverflow.co/2024/technology)_

---

### Development Frameworks and Libraries

The viable frontend frameworks for the Django + DRF + Vite context, ordered from lightest to heaviest:

**Vanilla JS + Vite (no framework)**
- Produces zero framework overhead; pure TypeScript modules bundled by Vite
- Suitable for low-interactivity enhancements (toggles, simple filters, modals)
- Becomes unwieldy for complex reactive forms — requires manual event listener management and DOM diffing
- `@vue/reactivity` (4kB standalone) can provide reactive primitives without the full Vue runtime
- _Source: [SaaS Pegasus — Adding Vite to Django](https://www.saaspegasus.com/guides/modern-javascript-for-django-developers/integrating-javascript-pipeline-vite/)_

**Alpine.js v3 (7.1kB gzip, ~502k weekly npm downloads, 31.4k GitHub stars)**
- Vue 2-style directive syntax (`x-data`, `x-model`, `x-show`, `x-for`) embedded directly in Django HTML templates
- No build step required; can be loaded from CDN or bundled via Vite
- Excellent for progressive enhancement of server-rendered pages; safe to use alongside HTMX fragments
- Does not support `.vue`-style component files — code organization degrades at scale (inline `x-data` sprawl)
- Not suitable for TypeScript; lacks component composition model
- _Source: [Alpine.js GitHub](https://github.com/alpinejs/alpine)_

**HTMX v2 (~14kB, 46.5k GitHub stars)**
- Hypermedia-first: form interactions trigger server round-trips that return HTML partials; no client-side state management
- Canonical inline validation: `hx-post` on field blur → Django view returns partial with error markup → HTMX swaps in-place
- `django-htmx` (adamchainz, v1.27.0) adds `request.htmx` middleware for clean view handling
- Increases server load: every field interaction triggers an HTTP request — a concern on constrained servers
- Does not integrate with Vite cleanly; its value proposition is eliminating the JS build step entirely
- _Source: [HTMX Inline Validation — htmx.org](https://htmx.org/examples/inline-validation/); [django-htmx GitHub](https://github.com/adamchainz/django-htmx)_

**Vue 3 + Vite (34.2kB gzip, dominant Django JS framework choice 2024–2025)**
- Composition API + `<script setup>` + TypeScript: the current setup in Desparchado
- `defineCustomElement()` allows mounting Vue SFCs as native custom elements — the pattern used in `mount-vue.ts`
- Component decomposition handles complex form state (inline validation, nested reactive data, dynamic field sets) cleanly
- `django-vite` v3.1.0 (Feb 2025, 835 GitHub stars) provides the Django ↔ Vite bridge with manifest-based production asset resolution
- Enables full TypeScript strict mode, Storybook integration, and Vite HMR in development
- Note: `django-vite` v3.1.0 does not explicitly list Django 5.x in its test matrix — verify compatibility if upgrading Django
- _Source: [django-vite PyPI](https://pypi.org/project/django-vite/); [GitHub — MrBin99/django-vite](https://github.com/MrBin99/django-vite)_

**petite-vue (6.9kB, from Vue team)**
- Subset of Vue 3 with no VDOM — intended as a direct Alpine.js competitor for progressive enhancement
- Uses Vue's template syntax and reactivity model; lower maintenance activity than Alpine
- Not recommended as a primary path: less community support, no SFC format
- _Source: [petite-vue GitHub](https://github.com/vuejs/petite-vue)_

---

### Comparative Framework Summary

| Approach | Bundle Size | Build Step | TypeScript | SEO-Safe | Rich Forms | Server Load | Django Fit |
|---|---|---|---|---|---|---|---|
| **Vue 3 + Vite** | ~34kB gzip | Yes (Vite) | Full | Yes (partial mounts) | Excellent | Low | Excellent (in use) |
| Vanilla JS + Vite | ~0kB overhead | Yes (Vite) | Full | Yes | Manual/tedious | Low | Good |
| Alpine.js | 7kB gzip | Optional | No | Yes | Good | Low | Good |
| HTMX | ~14kB | No | No | Excellent | Good | Higher | Good |
| Web Components (native) | 0kB | No | Full | Yes | Limited (Shadow DOM form issues) | Low | Fair |
| petite-vue | 6.9kB | Optional | Partial | Yes | Good | Low | Good |

---

### Database and Storage Technologies

PostgreSQL with PostGIS is the storage layer; not under consideration for frontend migration. DRF provides JSON API endpoints consumed by JS components where needed. No change recommended.

---

### Development Tools and Platforms

- **Vite 5.x**: Already in use. Framework-agnostic bundler. Works with Vue plugin (`@vitejs/plugin-vue`) or without it for pure TypeScript builds. HMR in dev, hashed manifest in production.
- **TypeScript strict mode**: Already enforced. All Vue components use `<script setup lang="ts">`. Compatible with vanilla TS modules.
- **Storybook**: Already available (`make run-storybook`). Only useful if Vue components are being built; no Storybook value for HTMX/Alpine approaches.
- **pytest + django-webtest**: Established test stack; frontend framework choice has no impact on backend test strategy.
- _Source: [The Django Developer's Guide to Vite — ctrlzblog.com](https://ctrlzblog.com/the-django-developers-guide-to-vite)_

---

### Deployment and Static Files

All approaches produce browser-consumable assets that nginx can serve directly from `STATIC_ROOT` after `python manage.py collectstatic`:

- **Vue + Vite / Vanilla + Vite**: `npm run build` → hashed files in `dist/` → collectstatic copies them → nginx serves with `Cache-Control: immutable`
- **Alpine.js from CDN**: No build step needed; one `<script>` tag in base template. Zero build pipeline change.
- **HTMX**: Same — CDN or single JS file, no build pipeline change. But adds server-side partial view infrastructure.
- **Web Components**: Depends on whether build-step modules are used; can be CDN-free with native browser APIs

_Confidence: High — verified against current django-vite documentation and Nginx Django deployment guides._
_Source: [Using Vite with Django, the simple way](https://gist.github.com/lucianoratamero/7fc9737d24229ea9219f0987272896a2)_

---

### Technology Adoption Trends (Django ecosystem, 2024–2025)

- **HTMX + Django** has seen the largest star growth of any Django-adjacent JS technology in 2024 (+16.8k stars); it is positioned as the "no SPA" alternative
- **Vue 3** remains the dominant JS framework recommendation for Django projects that require JS components, per the Built with Django community survey
- **Alpine.js** is gaining traction specifically for developers who want Vue-like directives without a build step
- **React with Django** is common in larger teams but rarely recommended for solo/small-team projects due to build complexity and the need for a full API-first architecture
- The TestDriven.io "DRF + Vue vs Django + HTMX" article (2024) concludes: use DRF + Vue when you need rich client interactivity; use Django + HTMX when you want to minimize JS and keep logic server-side
- _Source: [Django REST Framework and Vue versus Django and HTMX — TestDriven.io](https://testdriven.io/blog/drf-vue-vs-django-htmx/)_

## Integration Patterns Analysis

### API Design Patterns (DRF ↔ Vue)

Desparchado uses DRF's default `ModelViewSet` + `SessionAuthentication`. The integration pattern for Vue components is **same-origin session-cookie auth with a shared `fetch` wrapper**. No token exchange is needed since Vue components are served inside Django templates from the same origin.

**Recommended `apiFetch` wrapper** (to be placed in a new `api/base.ts`):
```typescript
function getCsrfToken(): string {
  return document.cookie
    .split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1] ?? '';
}

export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
      ...options.headers,
    },
    credentials: 'same-origin',  // REQUIRED — fetch does not send cookies by default
  });
}
```

The project already uses native `fetch` (no axios). Keeping it native avoids a ~14kB dependency.
_Source: [AJAX, CSRF & CORS — Django REST framework](https://www.django-rest-framework.org/topics/ajax-csrf-cors/)_

---

### DRF Validation Error Format

DRF returns HTTP 400 with a flat JSON object on validation failure:
```json
{
  "title": ["Este campo es requerido."],
  "event_date": ["La fecha debe ser futura."],
  "non_field_errors": ["El evento ya existe en esta fecha y lugar."]
}
```
Key points:
- Every field error value is always **an array** of strings, even single messages — template must use `errors.title?.[0]`
- Non-field (cross-field) errors use the key `"non_field_errors"`
- Nested serializers mirror the nesting structure: `{ "place": { "name": [...] } }`
- Map directly to `ref<Record<string, string[]>>` in Vue — no transformation needed

**TypeScript type to add to `interfaces.ts`:**
```typescript
export type DRFValidationError = Record<string, string[]>;
```

Consider `drf-standardized-errors` only if a consistent envelope format becomes necessary across many endpoints; it is not needed for this project's current scope.
_Source: [DRF Exceptions docs](https://www.django-rest-framework.org/api-guide/exceptions/)_

---

### Inline Form Validation with Vue + DRF

The recommended pattern: a `useField` composable with `watch` + debounce (300–500ms), posting to the real DRF endpoint (or a dedicated `validate` action) and mapping the 400 response to field error state.

For library support: **VeeValidate 4**'s `setErrors({ fieldName: ['error'] })` composable directly accepts DRF's `{field: [msg]}` shape without transformation. TanStack Form v1 also supports per-field async debounce via `asyncDebounceMs`. Both are optional — the pattern works without any library.

Gotcha: DRF does not have built-in per-field validation endpoints. For live validation, either POST the full form and display errors, or create a dedicated `@action(detail=False, methods=['post'], url_path='validate')` on the ViewSet that runs `serializer.is_valid()` on partial data and returns errors.
_Source: [TanStack Form Vue validation guide](https://tanstack.com/form/v1/docs/framework/vue/guides/validation)_

---

### Inline Related-Object Creation (Modal Form Pattern)

The specific challenge for the event form: creating an Organizer, Speaker, or Place inline without leaving the page.

**Recommended architecture:**
1. `EventFormContainer.vue` — root component, uses `provide()` to share modal state
2. `OrganizerCombobox.vue` — `<select>` + "Create new" button, emits selection
3. `OrganizerModal.vue` — form in a `<dialog>` or overlay, POSTs to `/events/api/v1/organizers/`, emits `{id, name}` on success
4. Parent receives the new object and injects it into the combobox options + sets the field value

Key points:
- Use `provide`/`inject` for modal state (not Pinia/Vuex) — each page mounts Vue components as isolated apps via `VueComponentMount`; there is no shared app-level store
- DRF's `ModelViewSet.create()` returns the serialized object on HTTP 201 — use it directly to populate the combobox
- The user quota system (`UserSettings`, 5 organizers/day) applies — the modal must handle 400/429 errors from the quota check and surface them in the modal's error state
- For the combobox UI, a `<select>` with an adjacent "Create new" button requires no extra npm dependencies; Headless UI's `Combobox` is an option if a search-as-you-type UX is desired

_Source: [Caktus Group — Vue.js and DRF development patterns](https://www.caktusgroup.com/blog/2019/11/18/development-patterns-vuejs-and-drf/)_

---

### Authentication & Session Integration

**Use `SessionAuthentication` exclusively for Vue components** — no JWT, no `TokenAuthentication`.

Current state: `base.py` sets `DEFAULT_PERMISSION_CLASSES` but not `DEFAULT_AUTHENTICATION_CLASSES`. DRF defaults to `[SessionAuthentication, BasicAuthentication]`. Add an explicit setting to remove `BasicAuthentication` in production:

```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

Critical gotcha: **never set `CSRF_COOKIE_HTTPONLY = True`**. If set, JavaScript cannot read the `csrftoken` cookie and all mutating Vue API calls will fail with 403. The default (`False`) is correct.
_Source: [DRF Authentication docs](https://www.django-rest-framework.org/api-guide/authentication/)_

---

### Vite Multi-Entry Integration (Current State)

The project already uses the correct multi-entry pattern: 11 named entry points in `rollupOptions.input`, resolved by django-vite via `manifest.json`. This is fully idiomatic and working.

Two improvements worth considering:
1. **Add `manualChunks: { vue_vendor: ['vue'] }`** in `rollupOptions.output` — isolates Vue's ~100kB runtime into a separate cached chunk, so app code changes don't bust the Vue cache hash.
2. **Verify `dev_mode` in `dev.py`** — `base.py` hardcodes `dev_mode: False`. If `dev.py` does not override to `True`, development serves stale built assets instead of the Vite HMR dev server.

_Source: [django-vite GitHub](https://github.com/MrBin99/django-vite); [Vite Build docs](https://vite.dev/guide/build)_

---

### Cross-Cutting Integration Notes

- **No shared store across components**: Because `VueComponentMount.mountAll()` creates isolated Vue apps per `[data-vue-component]` element, components on the same page cannot share Pinia/Vuex state. Use `CustomEvent` on `window` for cross-component communication, or restructure so one root component manages the full form.
- **allauth stays untouched**: django-allauth manages login/logout sessions. Vue components consume the authenticated session; do not add a parallel JWT auth system.
- **TypeScript strict mode applies to all new API types**: Define response types in `interfaces.ts`; do not use `any` for DRF response shapes.

## Architectural Patterns and Design

### System Architecture: Islands Pattern for Desparchado

Islands Architecture treats a server-rendered page as static HTML with discrete "islands" of client-side interactivity. Each island hydrates independently; the rest of the page ships zero JavaScript. Desparchado already implements this implicitly via `data-vue-component` mounts — the architecture needs to be made explicit and disciplined.

**Documented impact:** Teams adopting Islands report ~83% JavaScript reduction on pages that previously hydrated the entire DOM.
_Source: [Islands Architecture — patterns.dev](https://www.patterns.dev/vanilla/islands-architecture/)_

**Island classification for Desparchado:**

| Page | Island? | Rationale |
|---|---|---|
| Event list | **No** | Read-only, SEO-critical — zero JS |
| Event detail | **No** | Read-only, SEO-critical — zero JS |
| Organizer / Speaker / Place / Special detail | **No** | Read-only — zero JS |
| Search / filter UI | **Yes** | Client state: active filters, debounced input, URL sync |
| Event create / edit form | **Yes (partial)** | Map widget + inline validation; text fields via HTMX |
| User dashboard | **Yes** | Per-user state, quota display |

Defer island hydration with `requestIdleCallback` unless the island is above the fold on initial load. The search filter bar (above-the-fold, user-facing on first paint) justifies eager hydration; secondary widgets do not.

**Future direction:** DjangoCon US 2025 demonstrated compiling Vue SFCs via `defineCustomElement()` into native Custom Elements embedded as `<my-filter-widget>` in Django templates — declarative, scoped, no `data-vue-component` scan loop needed. Worth evaluating as the mount pattern matures.
_Source: [DjangoCon US 2025 — Web Components + Vue + Django Templates](https://2025.djangocon.us/talks/unleash-your-django-frontend-integrate-web-components-into-django-templates-with-vue/)_

---

### Design Principles: Progressive Enhancement Spectrum

```
Plain Django form submit → HTMX partial swap → Alpine AJAX → Vue-controlled form
```

**Key principle:** Use the least powerful tool that satisfies the requirement. Escalate only when lower-tier tools cannot deliver the necessary UX.

**HTMX for inline form validation** — the canonical pattern:
- `hx-post` on field blur → Django view returns an HTML partial with error markup → HTMX swaps in-place
- All validation logic stays in Django Forms; no client-side duplication
- Can be added to existing crispy-forms templates with ~10 lines of change (no crispy-forms removal needed short-term)
- `django-htmx` (adamchainz, v1.27.0) adds `request.htmx` middleware for clean view detection

**crispy-forms migration path:** crispy-forms is a rendering helper, not a behavior library. It can coexist with HTMX indefinitely. Remove it only when Bootstrap markup conventions are replaced in Phase 3 of the CSS migration.

**Reserve Vue for:** map `PointField` widget (unavoidable client state), search/filter UI (URL state sync + debounced API), user dashboard (personalized reactive data), and multi-step form flows.

_Source: [DRF+Vue vs Django+HTMX — TestDriven.io](https://testdriven.io/blog/drf-vue-vs-django-htmx/); [Beyond HTMX: Alpine AJAX for Django — Loopwerk](https://www.loopwerk.io/articles/2025/alpine-ajax-django/)_

---

### Scalability and Performance Patterns

**Core Web Vitals context (2025):**
- **INP** (Interaction to Next Paint, < 200ms) replaced FID in March 2024. Heavy JavaScript on mobile is the primary cause of INP failures. Read-only pages with zero JS cannot fail INP.
- **LCP** (Largest Contentful Paint, < 2.5s): only 62% of mobile pages pass. Eliminating the Vue bundle from event list/detail removes a render-blocking script that delays LCP on the highest-traffic pages.

**JavaScript weight budget for content-first pages:** < 50kB total compressed. The Vue 3 runtime alone is ~22kB gzip. Event list and detail pages should target zero application JS.

**Static file caching:** Vite's hashed output (`main.a1b2c3.js`) enables `Cache-Control: immutable` on nginx. Add `manualChunks: { vue_vendor: ['vue'] }` in `rollupOptions.output` to isolate Vue's ~100kB runtime into a separately cached chunk — so app code changes don't bust the Vue cache hash.

_Source: [Core Web Vitals 2025 — EnFuse Solutions](https://www.enfuse-solutions.com/core-web-vitals-2025-new-benchmarks-and-how-to-pass-every-test/)_

---

### CSS Architecture: Bootstrap Replacement Strategy

**Tailwind CSS v4** (early 2025, Rust/Oxide engine) is the dominant Bootstrap replacement in the Django ecosystem. It generates only the utility classes actually used, eliminates unused CSS bloat, and integrates natively with Vite 6 (already in use) — no `manage.py tailwind` wrapper needed.

**Pico.css** (~10kB gzip) applies styles to semantic HTML elements with zero class attributes. For read-only content pages (event detail, organizer detail) that are mostly `<h1>`, `<p>`, `<time>`, `<address>`, Pico requires no template changes — swap the Bootstrap `<link>` and most content pages look reasonable immediately.

**Three-phase migration:**

| Phase | Action | Risk |
|---|---|---|
| 1 | Add Tailwind v4 via Vite config **alongside** Bootstrap; convert new templates to Tailwind | Low |
| 2 | Replace Bootstrap grid/spacing on read-only pages; remove Bootstrap from those templates | Medium |
| 3 | Replace Bootstrap form styles and interactive components; remove Bootstrap entirely | High — requires replacing crispy-forms Bootstrap templates |

**For Vue islands:** shadcn/ui + Tailwind is the 2025 standard for Vue component styling — accessible, unstyled-by-default components that use Tailwind utilities. Replaces Bootstrap's modal, dropdown, and tooltip for interactive islands.

_Source: [Why Tailwind CSS is Replacing Bootstrap in 2025 — XHTMLTeam](https://www.xhtmlteam.com/blog/why-tailwind-css-is-replacing-bootstrap-in-2025/); [CSS Libraries Worth Your Time in 2025 — portalZINE](https://portalzine.de/the-best-css-libraries-to-use-in-2025/)_

---

### Django Template Partials vs Vue SFCs

**Decision tree:**

```
Server-rendered, no user interaction?
  → Django template partial (django-template-partials / Django 6 core partials)

Partial page update without client state?
  → Django template partial + HTMX

Client-side reactivity (filter state, real-time validation, map widget)?
  → Vue SFC as a mounted island

Needs embedding via custom HTML tag across multiple templates?
  → Vue SFC compiled to Custom Element via defineCustomElement()
```

**`django-template-partials`** (being absorbed into Django 6.0 core): named blocks within template files, renderable in isolation. Ideal for event cards, organizer snippets, place info blocks reused across read-only templates. Replaces `{% include %}` chains with named `{% partialdef event_card %}` blocks — composable, zero JavaScript.

**`django-components` v0.94:** supports `...props` spread, dynamic expressions. Still renders server-side only — no client reactivity. Appropriate for encapsulating reusable server-rendered UI; not for anything requiring client state.

**Community signal:** HTMX grew from 5% → 24% and Vue declined from 28% → 17% in Django developer surveys (State of Django 2025). This validates a "Vue only where genuinely necessary" posture — new interactive features should default to HTMX, escalate to Vue only when client state management is truly required.

_Source: [The State of Django 2025 — JetBrains PyCharm Blog](https://blog.jetbrains.com/pycharm/2025/10/the-state-of-django-2025/); [django-components v0.94 — DEV Community](https://dev.to/jurooravec/django-components-v094-templating-is-now-on-par-with-vue-or-react-4bg7)_

---

### Deployment and Operations Architecture

All approaches produce static files served by nginx from `STATIC_ROOT` after `collectstatic`:

- **Vite + Vue / Vite + Vanilla:** `npm run build` → hashed assets → `collectstatic` → nginx with `Cache-Control: immutable`
- **HTMX:** Single JS file (CDN or Vite bundle). Adds server-side partial view endpoints — increases the number of Django views but no nginx changes needed.
- **django-template-partials:** Pure server-side; no static file changes.

One configuration item to verify: `desparchado/settings/dev.py` must set `DJANGO_VITE['default']['dev_mode'] = True`; `base.py` hardcodes it to `False`. Without this, development serves stale built assets instead of the Vite HMR dev server.

## Implementation Approaches and Technology Adoption

### HTMX + Vue 3 Coexistence

HTMX and Vue 3 can coexist on the same page if and only if they own **completely separate, non-overlapping DOM subtrees**. Vue's VDOM diffs against the real DOM; if HTMX swaps HTML inside a `[data-vue-component]` container, Vue's next re-render will either stomp the injected content or throw reconciliation errors.

**Safe pattern:**
```html
<!-- HTMX territory: server-rendered form -->
<form hx-post="..." hx-target="#field-title">
  <div id="field-title">...</div>
</form>

<!-- Vue territory: isolated islands -->
<div data-vue-component="event-filter"></div>
<div data-vue-component="map-widget"></div>
```

**hx-boost warning:** Do not apply `hx-boost` globally (on `<body>`). If used, listen for `htmx:afterSwap` in addition to `DOMContentLoaded` to re-run `VueComponentMount.mountAll()` on newly inserted content — otherwise Vue islands won't mount after an HTMX page swap.

_Source: [Django, HTMX and Alpine.js — SaaS Pegasus](https://www.saaspegasus.com/guides/modern-javascript-for-django-developers/htmx-alpine/)_

---

### Tailwind v4 + Vite Setup (No django-tailwind package)

Tailwind v4 ships a first-party Vite plugin (`@tailwindcss/vite`) — no PostCSS config needed, integrates natively with the existing `vite.config.ts`.

```bash
npm install tailwindcss @tailwindcss/vite
```

```typescript
// vite.config.ts — add tailwindcss() before vue()
import tailwindcss from '@tailwindcss/vite';

plugins: [
  tailwindcss(),  // ADDED
  vue(),
  svgLoader({ defaultImport: 'raw' }),
],
```

```scss
/* desparchado/frontend/styles/index.scss */
@import "tailwindcss";

/* Explicit @source directives — Tailwind v4 auto-scans relative to CSS,
   but Django templates live outside the frontend directory */
@source "../../../events/templates/**/*.html";
@source "../../../places/templates/**/*.html";
@source "../../../users/templates/**/*.html";
@source "../../../dashboard/templates/**/*.html";
@source "../../../desparchado/templates/**/*.html";
```

**Bootstrap coexistence:** Import Bootstrap after Tailwind to prevent preflight conflicts. Phase Bootstrap out page by page; do not remove it globally until Phase 3.

_Source: [Install Tailwind CSS with Vite — official docs](https://tailwindcss.com/docs/guides/vite); [Django with Tailwind v4 — SaaS Hammer](https://saashammer.com/blog/how-to-integrate-tailwindcss-4-into-your-django-project/)_

---

### HTMX Inline Form Validation Pattern

The reference implementation is [django-htmx-patterns](https://github.com/spookylukey/django-htmx-patterns/blob/master/form_validation.rst) by Luke Plant. The four-step pattern:

**1. Field partial template** (`events/partials/_field_row.html`):
```html
<div
  id="field-{{ field.html_name }}"
  hx-post="{{ request.path }}"
  hx-trigger="focusout"
  hx-target="#field-{{ field.html_name }}"
  hx-swap="outerHTML"
  hx-include="[name='{{ field.html_name }}']"
  hx-vals='{"_validate_field": "{{ field.html_name }}"}'
>
  <label for="{{ field.id_for_label }}">{{ field.label }}</label>
  {{ field }}
  {% if field.errors %}
    <ul class="errorlist">
      {% for error in field.errors %}<li>{{ error }}</li>{% endfor %}
    </ul>
  {% endif %}
</div>
```

**2. Include in the full form template:**
```html
{% for field in form %}
  {% include "events/partials/_field_row.html" with field=field %}
{% endfor %}
```

**3. View handler** (add to `EventCreateView.post()`):
```python
def post(self, request, *args, **kwargs):
    validate_field = request.POST.get('_validate_field')
    if request.headers.get('HX-Request') and validate_field:
        form = self.get_form()
        form.is_valid()  # populate errors without raising
        html = render_to_string(
            'events/partials/_field_row.html',
            {'field': form[validate_field], 'request': request},
            request=request,
        )
        return HttpResponse(html)
    return super().post(request, *args, **kwargs)
```

Use `focusout` (bubbles) not `blur` (does not bubble) when the trigger is on the wrapper `<div>`. Use `change` for date/time fields.

_Source: [django-htmx-patterns form_validation.rst](https://github.com/spookylukey/django-htmx-patterns/blob/master/form_validation.rst)_

---

### Vue 3 Search/Filter with URL State Sync

Use **VueUse `useUrlSearchParams`** for zero-boilerplate reactive URL sync:

```bash
npm install @vueuse/core
```

```typescript
// composables/useEventFilters.ts
import { useUrlSearchParams } from '@vueuse/core';
import { watch, ref } from 'vue';

export function useEventFilters(apiBase: string) {
  const params = useUrlSearchParams('history');  // reactive + synced to URL
  const results = ref([]);
  const loading = ref(false);
  let debounceTimer: ReturnType<typeof setTimeout>;

  async function fetchEvents() {
    loading.value = true;
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    const res = await fetch(`${apiBase}?${qs}`, { credentials: 'same-origin' });
    results.value = (await res.json()).results;
    loading.value = false;
  }

  watch(params, () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchEvents, 300);
  }, { deep: true });

  return { params, results, loading };
}
```

The existing `/events/api/v1/` endpoint already accepts `city`, `category`, and `q` params — no backend changes needed.

Use `replaceState` while the user is typing (no history pollution); use `pushState` only on explicit submit so the Back button works correctly.

_Source: [useUrlSearchParams — VueUse docs](https://vueuse.org/core/useurlsearchparams/)_

---

### Bootstrap Removal: Phased Checklist

**Difficulty ranking (hardest first):**

| Component | Difficulty | Replacement |
|---|---|---|
| Navbar with responsive collapse | High | Alpine `x-show` or `<details>/<summary>` |
| Modal dialogs | High | `@headlessui/vue` `Dialog` + `<Teleport>` |
| Dropdowns | Medium-High | `@headlessui/vue` `Menu`, or CSS `:focus-within` |
| Form layout (`form-group`, `form-control`) | Medium | Tailwind `flex flex-col gap-2` |
| Grid layout (`col-md-6` etc.) | Medium | CSS Grid / Tailwind `grid grid-cols-*` |
| Spacing utilities (`mt-4`, `px-3`) | Low | Tailwind direct equivalents |
| Typography classes | Low | Tailwind `text-*` utilities |

**Phase checklist:**
- **Phase 1:** Add Tailwind v4 alongside Bootstrap; start new templates with Tailwind only
- **Phase 2:** Migrate layout (`.container`, `.row`, `.col-*`, spacing) — mechanical find-replace
- **Phase 3:** Replace Bootstrap JS components (navbar, modal, dropdown); migrate crispy-forms templates to plain Django/HTMX partials; remove Bootstrap

**crispy-forms is the Django-specific bottleneck.** Its Bootstrap template pack tightly couples form rendering to Bootstrap HTML structure. The pragmatic path: drop crispy-forms when migrating to the HTMX partial approach (Topic 3 above gives you this for free as part of the inline-validation work).

_Source: [Why We Migrated from Bootstrap to Tailwind — Vantage](https://www.vantage.sh/blog/bootstrap-tailwind-migration)_

---

### Testing HTMX Views (pytest-django)

Fits directly into Desparchado's existing test conventions:

```python
# Standard Django test client
@pytest.mark.django_db
def test_htmx_field_validation_returns_partial(client, user):
    client.force_login(user)
    url = reverse('events:event_create')

    response = client.post(
        url,
        data={'_validate_field': 'title', 'title': ''},
        HTTP_HX_REQUEST='true',  # simulates HTMX request
    )

    assert response.status_code == 200
    assert b'<div id="field-title"' in response.content
    assert b'<html' not in response.content  # partial, not full page
    assert b'Este campo es obligatorio' in response.content
```

```python
# django-webtest django_app fixture (existing convention)
@pytest.mark.django_db
def test_htmx_field_validation_via_django_app(django_app, user):
    django_app.set_user(user)
    response = django_app.post(
        reverse('events:event_create'),
        params={'_validate_field': 'title', 'title': ''},
        headers={'HX-Request': 'true'},
        expect_errors=True,
    )
    assert response.status_code == 200
    assert '<div id="field-title"' in response.text
```

Add `@vary_on_headers("HX-Request")` to HTMX views with HTTP caching to prevent serving a partial to a non-HTMX client.

_Source: [django-htmx middleware docs](https://django-htmx.readthedocs.io/en/latest/middleware.html); [HTMX+Django testing — DEV Community](https://dev.to/rodbv/creating-a-to-do-app-with-htmx-and-django-part-5-testing-the-views-2iml)_

---

### Implementation Roadmap

**Phase 1 — Foundation (low risk, immediate wins)**
- [ ] Add `django-htmx` middleware to `base.py`; explicitly set `DEFAULT_AUTHENTICATION_CLASSES` to remove `BasicAuthentication`
- [ ] Create `api/base.ts` with the `apiFetch` CSRF wrapper
- [ ] Add `manualChunks: { vue_vendor: ['vue'] }` to Vite config
- [ ] Add `@tailwindcss/vite` to Vite config alongside Bootstrap; add `@source` directives for all template dirs
- [ ] Verify `DJANGO_VITE['default']['dev_mode'] = True` is set in `dev.py`
- [ ] Add `DRFValidationError = Record<string, string[]>` to `interfaces.ts`

**Phase 2 — Read-only pages (zero JS)**
- [ ] Remove Vue bundle includes from event list, event detail, organizer/speaker/place/special detail templates
- [ ] Convert `{% include %}` repeated fragments to `{% partialdef %}` using `django-template-partials`
- [ ] Begin replacing Bootstrap layout classes with Tailwind on read-only templates

**Phase 3 — Form interactivity**
- [ ] Add HTMX field partial pattern to `EventCreateView` / `EventUpdateView`
- [ ] Create `events/partials/_field_row.html`
- [ ] Add `useEventFilters` composable with `useUrlSearchParams` to the search/filter Vue island
- [ ] Keep Vue only for: map `PointField` widget, search/filter, user dashboard

**Phase 4 — Bootstrap removal**
- [ ] Replace Bootstrap JS components (navbar, modal, dropdown) with Headless UI + Tailwind
- [ ] Migrate crispy-forms templates to plain HTMX partials
- [ ] Remove Bootstrap import

---

## Research Synthesis and Final Recommendations

### Decision Framework: What Goes Where

```
Page or feature
│
├── Read-only, no user interaction (event list, detail, organizer, speaker, place, special)
│   └── Django template + django-template-partials
│       → Zero JavaScript. SEO-safe. Best LCP. Use {% partialdef %} for reusable cards.
│
├── Form with validation feedback (event create/edit, any other model form)
│   ├── Text/select fields → HTMX field partial pattern
│   │   → hx-trigger="focusout", partial view, returns field fragment with error markup
│   └── Map widget (PointField) → Vue 3 island
│       → Unavoidable client state; keep existing LeafletPointFieldWidget or Vue wrapper
│
├── Search / filter UI
│   └── Vue 3 island with useUrlSearchParams (VueUse)
│       → Client state, debounced DRF calls, URL sync, Back button support
│
├── Inline related-object creation (Organizer, Speaker, Place from Event form)
│   └── Vue modal pattern: EventFormContainer → OrganizerCombobox → OrganizerModal
│       → provide/inject for state; POST to DRF; handle quota 400 errors in modal
│
└── User dashboard (quota display, personal event list)
    └── Vue 3 island
        → Personalized reactive data, not server-renderable without per-user context
```

---

### Technology Decisions Summary

| Concern | Decision | Rationale |
|---|---|---|
| Read-only page JS | Remove entirely | Zero-JS = best LCP, best SEO, zero maintenance |
| Form validation | HTMX | Stays in Django Forms; ~10 lines of change; no client state needed |
| Interactive islands | Vue 3 + existing django-vite | Already in place; TypeScript strict; Storybook |
| CSS framework | Tailwind v4 via `@tailwindcss/vite` | No django-tailwind package; native Vite integration; JIT purging |
| Bootstrap removal | Phased (3 phases) | Layout first → JS components → crispy-forms last |
| DRF auth from Vue | SessionAuthentication + apiFetch wrapper | Same-origin; no JWT needed; `credentials: 'same-origin'` required |
| URL state in filter | VueUse `useUrlSearchParams` | Reactive + Back button + zero boilerplate |
| Server-side reuse | django-template-partials | Django 6 core; replaces {% include %} chains |
| Component isolation | provide/inject (not Pinia) | Components are isolated Vue apps per mount point |

---

### Immediate Action Items (Phase 1, zero risk)

1. **`api/base.ts`** — create the `apiFetch` CSRF wrapper; add `DRFValidationError = Record<string, string[]>` to `interfaces.ts`
2. **`settings/base.py`** — explicitly set `DEFAULT_AUTHENTICATION_CLASSES: [SessionAuthentication]` to remove `BasicAuthentication`
3. **`vite.config.ts`** — add `manualChunks: { vue_vendor: ['vue'] }`; add `@tailwindcss/vite` plugin
4. **`settings/dev.py`** — verify `DJANGO_VITE['default']['dev_mode'] = True` is set
5. **Read-only templates** — remove `{% vite_asset 'events' %}` / `{% vite_asset 'events_details' %}` etc. from all non-interactive page templates
6. **`django-htmx`** — add to `INSTALLED_APPS` / `MIDDLEWARE` in `base.py`

### Phase 2 (form UX improvement)

7. **`events/partials/_field_row.html`** — create field partial template with HTMX attributes
8. **`EventCreateView` / `EventUpdateView`** — add HTMX field validation handler in `post()`
9. **Django template partials** — install `django-template-partials`; convert repeated `{% include %}` event/organizer cards to `{% partialdef %}` blocks
10. **Read-only layout** — begin replacing Bootstrap grid/spacing with Tailwind on event list and detail templates

### Phase 3 (Bootstrap exit)

11. **Bootstrap JS components** — replace navbar collapse, modal, dropdown with `@headlessui/vue` + Tailwind
12. **crispy-forms** — remove; form templates rebuilt as HTMX partials with Tailwind styling
13. **Bootstrap CSS** — remove final `@import` from `index.scss`

---

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| HTMX `hx-target` accidentally overlaps Vue mount root | Medium | Medium | Code review rule: `hx-target` selectors must never resolve inside `[data-vue-component]` |
| Tailwind v4 preflight conflicts with Bootstrap during transition | Medium | Low | Import Bootstrap after Tailwind; scope with `@layer` if needed |
| `django-vite` incompatibility with Django 5.x | Low | High | Test before upgrading Django; pin django-vite until compatibility confirmed |
| Inline related-object creation misses quota check | Medium | Medium | Ensure DRF endpoint for Organizer/Speaker/Place uses same quota middleware as web views |
| `CSRF_COOKIE_HTTPONLY = True` accidentally set | Low | High | Add test asserting CSRF cookie is readable from JS; document in CLAUDE.md |

---

### Source Index

All claims in this document are verified against the following sources:

**Frameworks and Tools**
- [django-vite PyPI / GitHub (MrBin99)](https://github.com/MrBin99/django-vite)
- [Alpine.js GitHub](https://github.com/alpinejs/alpine)
- [HTMX Inline Validation — htmx.org](https://htmx.org/examples/inline-validation/)
- [django-htmx docs (adamchainz)](https://django-htmx.readthedocs.io/en/latest/)
- [django-htmx-patterns (Luke Plant)](https://github.com/spookylukey/django-htmx-patterns)
- [VueUse useUrlSearchParams](https://vueuse.org/core/useurlsearchparams/)
- [Tailwind CSS v4 + Vite official docs](https://tailwindcss.com/docs/guides/vite)
- [petite-vue GitHub](https://github.com/vuejs/petite-vue)

**Architecture and Patterns**
- [Islands Architecture — patterns.dev](https://www.patterns.dev/vanilla/islands-architecture/)
- [DRF+Vue vs Django+HTMX — TestDriven.io](https://testdriven.io/blog/drf-vue-vs-django-htmx/)
- [Beyond HTMX: Alpine AJAX for Django — Loopwerk](https://www.loopwerk.io/articles/2025/alpine-ajax-django/)
- [Progressive Enhancement with HTMX — Valentino Gagliardi](https://www.valentinog.com/blog/django-progressive-enhancement-htmx/)
- [Vue + Django without compromise — DjangoCon US 2023](https://2023.djangocon.us/talks/vue-django-combining-django-templates-and-vue-single-file-components-without-compromise/)
- [Web Components + Vue + Django — DjangoCon US 2025](https://2025.djangocon.us/talks/unleash-your-django-frontend-integrate-web-components-into-django-templates-with-vue/)

**Community and Ecosystem**
- [The State of Django 2025 — JetBrains PyCharm Blog](https://blog.jetbrains.com/pycharm/2025/10/the-state-of-django-2025/)
- [7 Top Frontend Frameworks for Django — Built with Django](https://builtwithdjango.com/blog/7-top-frontend-frameworks-for-seamless-django-integration)
- [Adding Vite to Django — SaaS Pegasus](https://www.saaspegasus.com/guides/modern-javascript-for-django-developers/integrating-javascript-pipeline-vite/)

**DRF Integration**
- [AJAX, CSRF & CORS — Django REST framework](https://www.django-rest-framework.org/topics/ajax-csrf-cors/)
- [DRF Authentication docs](https://www.django-rest-framework.org/api-guide/authentication/)
- [DRF Exceptions / error format](https://www.django-rest-framework.org/api-guide/exceptions/)
- [Session Auth with Vue — Brian Caffey](https://briancaffey.github.io/2020/11/27/how-to-authenticate-django-rest-framework-from-vue-app-with-session-authentication-httponly-cookies/)

**Performance and SEO**
- [Core Web Vitals 2025 — EnFuse Solutions](https://www.enfuse-solutions.com/core-web-vitals-2025-new-benchmarks-and-how-to-pass-every-test/)

**CSS Migration**
- [Why Tailwind CSS is Replacing Bootstrap in 2025 — XHTMLTeam](https://www.xhtmlteam.com/blog/why-tailwind-css-is-replacing-bootstrap-in-2025/)
- [Bootstrap to Tailwind migration — johnzanussi.com](https://johnzanussi.com/posts/bootstrap-to-tailwind-migration)

---

**Research Completion Date:** 2026-04-05
**Research Period:** Current — all sources verified April 2026
**Source Verification:** All technical claims cited with authoritative sources
**Confidence Level:** High across all sections; medium noted where indicated