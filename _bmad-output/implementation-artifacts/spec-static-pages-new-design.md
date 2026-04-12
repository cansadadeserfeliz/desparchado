---
title: 'Migrate static pages to new Desparchado design'
type: 'refactor'
created: '2026-04-11'
status: 'done'
baseline_commit: 'f73d039b65f9ea8a89066344c6b6aaeceadb782d'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Five static pages (403, 404, 500, about, terms) still use Bootstrap classes (`btn btn-primary`, `container`, `row`, `col-*`) and raw HTML headings without typography tokens, creating visual inconsistency with the new design used across all other pages.

**Approach:** Convert each page to the new design system — opt out of Bootstrap, replace markup with BEM classes and Vue component attributes, add a shared `static.ts` entry + `pages/static.scss` for the new layout styles.

## Boundaries & Constraints

**Always:**
- Override `{% block bootstrap_css %}{% endblock %}` on every updated template to suppress Bootstrap, FontAwesome, and the old JS bundle.
- Use `{% vite_asset 'desparchado/frontend/scripts/static.ts' %}` inside `{% block extra_scripts %}` on each page.
- Load `{% load django_vite %}` on any template that uses `vite_asset`.
- Use Vue component attributes (`data-vue-component="button"`, `data-vue-component="typography"`) and existing typography classes (`text-subtitle-1`, `text-heading-3`, `text-body-lg`, `text-body-md`) consistent with the design system.
- Keep all existing Spanish-language copy unchanged, except the DigitalOcean referral badge which must be removed.

**Ask First:**
- If the about or terms pages need additional sections, ask before adding copy.

**Never:**
- Add new Bootstrap classes or CDN links.
- Create per-page SCSS files — all static page styles go in `pages/static.scss`.
- Delete or modify the base template (`layout/base.html`).
- Add Vue components that require async data fetching.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 404 page loads | Django raises Http404 | Page renders with new design, no Bootstrap styles, CTA button back to home | N/A |
| 500 page loads | Django raises 500 | Page renders without Bootstrap (Django serves 500 without request context) | N/A |
| About page loads | User navigates to /about/ | Full page with new typography, sections, CTA — no Bootstrap classes | N/A |

</frozen-after-approval>

## Code Map

- `desparchado/templates/403.html` -- error page: access denied
- `desparchado/templates/404.html` -- error page: page not found
- `desparchado/templates/500.html` -- error page: internal server error
- `desparchado/templates/desparchado/about.html` -- prose page: about Desparchado
- `desparchado/templates/desparchado/terms_and_conditions.html` -- prose page: T&C and privacy
- `desparchado/frontend/scripts/generic.ts` -- reference: pattern for page-scoped TS entry importing CSS
- `desparchado/frontend/styles/pages/generic.scss` -- reference: `.generic-detail` pattern for new design pages
- `desparchado/frontend/styles/_variables.scss` -- color/typography tokens
- `desparchado/frontend/styles/index.scss` -- new design style entry (excluded from pages that override `bootstrap_css` block)

## Tasks & Acceptance

**Execution:**
- [x] `desparchado/frontend/scripts/static.ts` -- CREATE: single-line file importing `../styles/pages/static.scss`, matching the pattern of `generic.ts`
- [x] `desparchado/frontend/styles/pages/static.scss` -- CREATE: `.error-page` block (for 403/404/500) and `.static-page` block (for about/terms). `.error-page` centers content vertically with generous padding, uses `$color-layout-foreground` for text and `$color-dp-orange-10` as background accent on the heading zone. `.static-page` has a max-width content column, uses `$hairline_regular` separators between sections.
- [x] `desparchado/templates/403.html` -- REWRITE: add `{% block bootstrap_css %}{% endblock %}`, load `django_vite`, load `static.ts` via vite_asset, use `.error-page` BEM structure with `text-heading-3` for title and `data-vue-component="button"` for CTA
- [x] `desparchado/templates/404.html` -- REWRITE: same pattern as 403
- [x] `desparchado/templates/500.html` -- REWRITE: same pattern as 403
- [x] `desparchado/templates/desparchado/about.html` -- REWRITE: add `{% block bootstrap_css %}{% endblock %}`, load `static.ts`, use `.static-page` with `.static-page__section` for each content block, typography classes on headings and paragraphs, Vue `button` component for the homepage CTA; remove the DigitalOcean referral badge entirely
- [x] `desparchado/templates/desparchado/terms_and_conditions.html` -- REWRITE: same pattern as about

**Acceptance Criteria:**
- Given any of the 5 pages loads, when inspecting the `<head>`, then no Bootstrap CDN link or FontAwesome CDN link is present.
- Given the 404 page renders, when reading the HTML, then CTA button uses `data-vue-component="button"` with `data-vue-prop-type="primary"`.
- Given the about page renders, when reading the HTML, then Bootstrap class names (`btn`, `container`, `row`, `col-*`, `text-lg`, `text-justify`, `text-center`) are absent.
- Given the about page renders, when reading the HTML, then all existing Spanish-language copy is preserved verbatim.
- Given the terms page renders, when reading the HTML, then all content sections (Términos y Condiciones, Privacidad) are present with new heading markup.
- Given `make lint` runs, then no ruff errors are introduced.

## Spec Change Log

## Design Notes

Error pages (403, 404, 500) should be visually spare — large italic title using `text-heading-3`, a short sentence in `text-body-lg`, and a single primary button. Matching the calm but typographically expressive style of the new design rather than a loud "oh no" aesthetic.

The `about.html` DigitalOcean referral badge should be removed.

## Verification

**Commands:**
- `docker exec -it desparchado-web-1 sh -c "cd app && python manage.py check --deploy 2>&1 | grep -i error || echo 'OK'"` -- expected: no errors
- `make lint` -- expected: exit 0

**Manual checks (if no CLI):**
- Load `/about/`, `/` (trigger 404 on unknown URL) in browser — confirm no Bootstrap grid classes visible in DevTools Elements panel, typography matches new design

## Suggested Review Order

**Vite entry point and CSS**

- New entry point mirrors `generic.ts` pattern; registers the stylesheet.
  [`static.ts:1`](../../desparchado/frontend/scripts/static.ts#L1)

- `.error-page` (403/404/500) and `.static-page` (about/terms) BEM blocks.
  [`static.scss:1`](../../desparchado/frontend/styles/pages/static.scss#L1)

- Must register `static` entry; without this, production `vite_asset` calls fail.
  [`vite.config.js:35`](../../vite.config.js#L35)

**Error page templates**

- 404 template: Bootstrap opt-out, `.error-page` structure, Vue button CTA.
  [`404.html:1`](../../desparchado/templates/404.html#L1)

- 403 and 500 follow identical pattern.
  [`403.html:1`](../../desparchado/templates/403.html#L1)

- 500 template: same pattern; note `vite_asset` inherits pre-existing base.html Vite risk.
  [`500.html:1`](../../desparchado/templates/500.html#L1)

**Prose page templates**

- About page: `.static-page__section` blocks, typography tokens, DigitalOcean badge removed.
  [`about.html:1`](../../desparchado/templates/desparchado/about.html#L1)

- Terms page: two sections (Términos y Condiciones, Privacidad) with new heading markup.
  [`terms_and_conditions.html:1`](../../desparchado/templates/desparchado/terms_and_conditions.html#L1)
