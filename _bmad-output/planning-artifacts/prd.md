---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary, step-03-success, step-04-journeys, step-05-domain, step-06-innovation, step-07-project-type, step-08-scoping, step-09-functional, step-10-nonfunctional, step-11-polish, step-12-complete]
status: complete
completedAt: "2026-04-05"
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-navigation-discovery.md
  - _bmad-output/planning-artifacts/product-brief-navigation-discovery-distillate.md
  - docs/explanations/architecture.md
workflowType: 'prd'
classification:
  projectType: web_app
  domain: general
  complexity: low
  projectContext: brownfield
---

# Product Requirements Document — Navigation & Discovery UX

**Project:** Desparchado
**Author:** Vera
**Date:** 2026-04-05
**Stack:** Django MPA + Vue.js islands · PostgreSQL · NGINX + Docker · Umami analytics

---

## Executive Summary

Desparchado is a live cultural events guide for Colombia — the authoritative source for discovering concerts, book fairs, art shows, talks, and community events across Colombian cities. 94% of its traffic arrives via Google organic search, landing directly on speaker, organizer, event, and place detail pages. These pages have a 93% bounce rate and a 20-second average visit duration. Users find what they searched for and leave — the page gives them no visible path to anything else.

This PRD defines requirements for the **Navigation & Discovery UX** initiative: server-side improvements that transform detail pages from isolated records into interconnected entry points. The primary audience is the organic search visitor — someone who landed on a specific page with no context about the broader platform. The goal: make Desparchado legible as a guide at the moment of first contact.

Three pillars: (1) contextual related content replacing random event suggestions with relevance-ranked recommendations; (2) cross-entity navigation exposing relationships between speakers, organizers, venues, and categories already modeled in the database; (3) platform identity signals — breadcrumbs, `schema.org` structured data, and category pages — that communicate what Desparchado is and improve organic CTR before the user clicks.

All required data exists. Relationships between speakers, organizers, places, and event categories are fully modeled in Django M2M and FK relationships. Implementation is entirely server-side: view queryset changes and template additions. No frontend architecture changes, no schema migrations, no new infrastructure. Risk profile is unusually low for the engagement impact targeted.

The `schema.org` structured data compounds value: it enables rich SERP results (upcoming events for speakers, breadcrumb trails in search results) that increase CTR on the organic searches already driving 58% of traffic — before any on-page changes take effect.

## Success Criteria

### User Success

- Bounce rate ≤ 70% on speaker, organizer, event, and place detail pages within 60 days of launch (down from 93%)
- Pages per session ≥ 1.8 within 60 days (vs. implied ~1.05 today)
- Average visit duration ≥ 45 seconds within 60 days (up from 20s)
- Speaker/organizer pages with no upcoming events surface at least one relevant event to click through to

### Business Success

- All 5 category pages (`/eventos/literatura/` etc.) indexed in Google search results within 30 days of launch
- `schema.org` structured data for `Event`, `Person`, `Organization`, `Place` eligible for Google rich results within ~2–4 weeks of deploy (baseline established via Google Search Console — no quantitative CTR target for v1)
- All 8 Umami navigation custom events live on launch day, providing first funnel data for second-iteration optimization

### Technical Success

- All new view queries add ≤ 50ms to server response time (measured with Django Debug Toolbar; no caching available)
- Zero N+1 queries introduced (verified via query count in tests)
- All `schema.org` JSON-LD passes Google Rich Results Test with zero errors before deploy
- All new view logic covered by unit tests

### Measurable Outcomes

| Metric | Baseline | Target | Timeline |
|---|---|---|---|
| Bounce rate (detail pages) | 93% | ≤ 70% | 60 days post-launch |
| Average visit duration | 20s | ≥ 45s | 60 days post-launch |
| Pages per session | ~1.05 | ≥ 1.8 | 60 days post-launch |
| Category pages in Google index | 0 | 5/5 | 30 days post-launch |
| Umami navigation events live | 0 | 8 event types | Launch day |
| schema.org validation errors | Unknown | 0 | Launch day |

## Product Scope

### MVP (Phase 1)

Single release. All three pillars ship together — they are mutually reinforcing and their combined effect exceeds the sum of parts. If time is constrained, the initiative can be split: cross-entity navigation + breadcrumbs first (highest bounce-rate impact), then category pages + schema.org (highest SEO impact).

- Cascading related events on event detail (5-tier fallback: same organizer → same category → same place → random future → random past)
- Co-speakers and hosting organizers on speaker detail pages
- Associated speakers on organizer detail pages
- Venue organizers on place detail pages
- Breadcrumbs (HTML + `schema.org/BreadcrumbList` JSON-LD) on all 4 detail page types and all 5 category pages
- `schema.org` structured data: `Event`, `Person`, `Organization`, `Place`
- 5 category pages with unique SEO-optimized titles and meta descriptions
- Category tag on event detail linking to the category page
- Empty-state fallback content (category-based) on speaker/organizer pages with no upcoming events
- Contextual sidebar copy on speaker/organizer pages replacing static generic text
- 8 Umami custom events for all new navigation interactions

**Resources:** Single developer, Django/Python. No design resources required. No new infrastructure.

### Phase 2 — Growth

- Category-level city filtering (`/eventos/literatura/?ciudad=bogota`)
- Per-page `<title>` and `<meta name="description">` generated from object data (speaker name + event count + city) — currently global defaults; compounds schema.org SEO value
- Co-speaker ranking refinement based on observed click patterns
- Speaker/organizer "notify me" subscriptions (requires email infrastructure)

### Phase 3 — Expansion

- Personalized recommendations based on authenticated user history
- Content graph explorer — visual map of entity connections in a city
- Site-wide search with entity-type filtering

### Out of Scope (All Phases)

- Header navigation redesign
- A/B testing infrastructure
- Site-wide search

## User Journeys

### Journey 1: Valentina — The Curious Googler (Primary, Success Path)

Valentina is a 34-year-old architect in Bogotá. She searches "Carol Ann Figueroa escritora" after hearing the name at a dinner party. She lands on Carol Ann's speaker page — reads the bio, sees a 2019 archive event and a sidebar saying "La ciudad está llena de nuevos parches." She doesn't know what Desparchado is. She closes the tab.

**With the new navigation:** The breadcrumb `Inicio > Presentadores > Carol Ann Figueroa` immediately signals she's in a directory, not on a personal site. Below the bio: "Organizaciones que han presentado a Carol Ann" — Casa Tomada Libros y Café, with thumbnail and link. She clicks, lands on Casa Tomada's organizer page, finds a reading circle about Colombian journalism happening this month, clicks through to the event, gets the address. Three pages, 90 seconds, zero bounce.

**Capabilities revealed:** Breadcrumbs; hosting organizers on speaker page; organizer page with upcoming events.

---

### Journey 2: Rodrigo — The Dead-End Visitor (Primary, Edge Case)

Rodrigo is a 28-year-old grad student in Medellín searching for a speaker his professor mentioned. He finds the speaker's Desparchado page — no upcoming events, just a bio and a 2022 archive entry. He sees a generic "Busca eventos cerca" button and leaves.

**With the new navigation:** The empty upcoming events section is replaced by: "Este presentador no tiene eventos próximos. Mientras tanto, hay 4 eventos de Ciencia en Medellín este mes:" with three event cards from the Science category. One is a public lecture at Universidad EAFIA that fits his interests. He clicks through.

**Capabilities revealed:** Empty-state fallback using speaker's top category; category-filtered event cards.

---

### Journey 3: Lucía — The Explorer (Secondary, Repeat Visitor)

Lucía runs a cultural blog in Cali and uses Desparchado to research the literary scene — which organizers are active, which speakers cluster together. Today she opens a literature event, spots the "Literatura" category tag, clicks it, and lands on `/eventos/literatura/`. She finds an organizer she didn't know — La Librería Nacional — and opens their page. Their "Presentadores frecuentes" section shows 6 speakers with appearance counts. She finds two new names for her blog. Under 3 minutes, no manual tab-switching.

**Capabilities revealed:** Category tag on event detail; category pages; associated speakers with counts on organizer page.

---

### Journey 4: Vera — The Data Steward (Admin/Superuser)

Vera reviews content quality periodically. Cross-entity sections surface a secondary benefit: an organizer showing zero associated speakers signals their events are missing speaker data; a speaker with no hosting organizers signals data entry gaps. No new admin tooling required — the cross-entity navigation surfaces quality signals passively.

**Capabilities revealed:** Cross-entity sections as passive data quality indicators.

---

### Journey Requirements Summary

| Journey | Capabilities Required |
|---|---|
| Valentina (success path) | Breadcrumbs; hosting organizers on speaker page; organizer page with upcoming events |
| Rodrigo (empty state) | Category-aware fallback events; empty-state detection in view |
| Lucía (explorer) | Category tag; category pages; associated speakers with counts on organizer page |
| Vera (superuser) | Cross-entity sections (passive quality signal; no new tooling) |

## Technical Requirements

### Architecture

Desparchado is a **Multi-Page Application** — Django server-renders all pages; Vue.js components mount as islands where interactivity is needed (event list, header). All changes in this PRD are server-side: view queryset changes, template additions, and `<script type="application/ld+json">` blocks. No frontend architecture changes, no Vite config changes, no new Vue components.

**Deployment:** Standard Docker pipeline (Vite build → collectstatic → Django container restart). No new containers or services.

**Caching:** Not available. Stack is NGINX + Django (Gunicorn) in Docker only. All query performance achieved through ORM optimization: indexed fields, `select_related`, `prefetch_related`, hard result caps.

### SEO Architecture

- **Breadcrumbs:** Server-rendered HTML `<nav>` + `schema.org/BreadcrumbList` JSON-LD in `<head>` on all 4 detail page types and all 5 category pages
- **Structured data per page type:**
  - Event → `schema.org/Event` (name, startDate, location, organizer, image, url)
  - Speaker → `schema.org/Person` (name, description, image, url)
  - Organizer → `schema.org/Organization` (name, description, logo, url, sameAs social links)
  - Place → `schema.org/Place` (name, address, geo coordinates)
  - Category pages → `schema.org/CollectionPage` + `ItemList`
- **Category pages:** Dedicated URL per category (`/eventos/literatura/` etc.) with unique `<title>` and `<meta name="description">`; not URL parameters. Each is independently indexable.
- **Per-page meta:** Detail page `<title>` and meta description generated from object data; existing base template global defaults must be overridden per page type.

### Browser & Device

- **Target:** Chrome, Firefox, Safari, Edge — last 2 major versions. No IE support.
- **Progressive enhancement:** All navigation improvements are server-rendered HTML; work with JavaScript disabled. No JS dependency introduced.
- **Mobile:** 29% of traffic. Breadcrumbs and cross-entity sections use the existing responsive grid — no new layout components.

### Implementation Patterns

- **Breadcrumb include:** `{% include 'includes/_breadcrumbs.html' with items=breadcrumb_items %}` — one partial, all views pass their own `breadcrumb_items` list of `(label, url)` tuples
- **JSON-LD:** Per-page-type `{% block structured_data %}` overrides in base template
- **View changes:** Each updated view adds new querysets and `breadcrumb_items` to `get_context_data()`. No new mixins — straightforward CBV overrides.
- **Category view:** `CategoryDetailView` inherits `EventListView` pattern, filtered by `category=CATEGORY_SLUG_MAP[slug]`; returns 404 for unknown slugs. Verify `Event.CATEGORY` constant names against `events/models/event.py` before implementing the slug map — incorrect mapping silently returns empty querysets.
- **Timezone in JSON-LD:** `schema.org/Event startDate` requires timezone offset (`-05:00`); confirm `event_date` is stored timezone-aware before implementation.

### Risk Mitigation

- **Cascading fallback performance:** Up to 5 sequential queries on event detail page load. Profile with Django Debug Toolbar; if any tier is slow, combine tiers 1–3 into a single query using `Q(organizers__in=...) | Q(category=...) | Q(place=...)` ordered by specificity.
- **Bounce rate ceiling:** Some bounces are intentional. The 93% → ≤70% target may be optimistic; 80% is a realistic first milestone. Reassess at 30 days.
- **Google indexing lag:** Schema.org rich results and category page indexing depend on Google's crawl schedule. No SERP CTR target is set for v1.

## Functional Requirements

### Contextual Related Content

- **FR1:** Visitors can view a curated list of upcoming events on an event detail page, selected based on relevance to the current event
- **FR2:** The related events section displays a label identifying the basis of the recommendation (e.g., by organizer, category, or venue)
- **FR3:** The related events section always contains content, falling back through progressively broader pools until events are found, including past events as a last resort

### Cross-Entity Navigation

- **FR4:** Visitors on a speaker detail page can view the organizers who have hosted that speaker
- **FR5:** Visitors on a speaker detail page can view other speakers who have appeared at the same events, ordered by frequency of co-appearance
- **FR6:** Visitors on an organizer detail page can view speakers who have appeared at that organizer's events, ordered by frequency of appearance
- **FR7:** Visitors on a place detail page can view organizers whose events have been held at that venue, ordered by event count

### Category Discovery

- **FR8:** Visitors can browse a dedicated page listing upcoming events for each of the five event categories (Literatura, Arte, Sociedad, Ciencia, Medio Ambiente)
- **FR9:** Visitors can navigate from an event detail page to the corresponding category page via a clickable category label on the event
- **FR10:** Each category page has a unique page title and meta description specific to that category

### Wayfinding & Platform Identity

- **FR11:** Visitors see a hierarchical breadcrumb trail on all detail pages (event, speaker, organizer, place) and all category pages
- **FR12:** Each breadcrumb item except the current page is a clickable link to its corresponding level in the site hierarchy
- **FR13:** Visitors on speaker and organizer detail pages see sidebar content relevant to that specific entity's event activity, not generic static copy

### Empty State Discovery

- **FR14:** Visitors on a speaker detail page with no upcoming events see suggested events drawn from the speaker's most-represented event category
- **FR15:** Visitors on an organizer detail page with no upcoming events see suggested events drawn from the organizer's most-represented event category

### Structured Data

- **FR16:** Search engines can read event structured data on event detail pages, including event name, start date, location, and organizer
- **FR17:** Search engines can read person structured data on speaker detail pages, including name, description, and image
- **FR18:** Search engines can read organization structured data on organizer detail pages, including name, description, logo, and social media links
- **FR19:** Search engines can read place structured data on place detail pages, including name, address, and geographic coordinates
- **FR20:** Search engines can read breadcrumb structured data on all detail pages and category pages

### Analytics & Instrumentation

- **FR21:** The system records when a visitor clicks a related event, capturing the recommendation basis and card position
- **FR22:** The system records when a visitor clicks a co-speaker link on a speaker page
- **FR23:** The system records when a visitor clicks a hosting organizer link on a speaker page
- **FR24:** The system records when a visitor clicks an associated speaker link on an organizer page
- **FR25:** The system records when a visitor clicks a venue organizer link on a place page
- **FR26:** The system records when a visitor clicks the category tag on an event detail page
- **FR27:** The system records when a visitor clicks a breadcrumb link, capturing the breadcrumb level
- **FR28:** The system records when a visitor clicks a fallback event card on a speaker or organizer page with no upcoming events

## Non-Functional Requirements

### Performance

- **NFR1:** New view queries (cascading related events, cross-entity navigation, empty-state fallback) add ≤ 50ms to server response time, measured with Django Debug Toolbar before and after implementation. No caching infrastructure is available — all targets met through ORM optimization alone.
- **NFR2:** All new querysets use `select_related` and/or `prefetch_related`. Query count per page load increases by no more than 5 queries on any detail page.
- **NFR3:** Result sets are hard-capped: related events ≤ 3, co-speakers ≤ 5, hosting organizers ≤ 6, associated speakers ≤ 8, venue organizers ≤ 6, empty-state fallback events ≤ 3.
- **NFR4:** `schema.org` JSON-LD blocks render inline in `<head>` — zero additional HTTP requests from structured data.

### Accessibility

- **NFR5:** Breadcrumb `<nav>` includes `aria-label="breadcrumb"`; current page item includes `aria-current="page"`. Meets WCAG 2.1 AA criterion 2.4.8.
- **NFR6:** All new content sections use semantic HTML (`<section>`, `<h2>`, `<ul>`/`<li>`). No `<div>` substitutes for structural elements.
- **NFR7:** Category tag on event detail pages uses the category name as visible link text, not an icon alone.
- **NFR8:** All new entity card images include descriptive `alt` text (entity name at minimum).

### Integration

- **NFR9:** All 8 Umami custom navigation events fire on the expected user interactions and appear in the Umami dashboard within 24 hours of deploy. Verified by manual testing of each interaction before release.
- **NFR10:** All `schema.org` JSON-LD blocks on all 4 detail page types and 5 category pages pass Google's Rich Results Test with zero errors before deploy.
- **NFR11:** Google Search Console is monitored for structured data errors and breadcrumb indexing issues for a minimum of 30 days post-deploy.