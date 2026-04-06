---
title: "Product Brief: Event Creation UX Redesign"
status: "complete"
created: "2026-04-05"
updated: "2026-04-05T21:45:00"
inputs:
  - "User conversation — Vera, 2026-04-05"
  - "Figma draft — multi-step event form wizard"
  - "_bmad-output/planning-artifacts/research/technical-vue-vs-vanilla-fe-django-drf-research-2026-04-05.md"
  - "Codebase analysis — events/forms/, events/views/, places/forms.py"
---

# Product Brief: Event Creation UX Redesign

## Executive Summary

Desparchado's event creation experience is a form that feels like a bureaucratic hurdle — fragmented across multiple tabs, non-interactive, and opaque about what already exists on the platform. The result: few users create events, and those who do often create duplicate organizers, places, and speakers by accident. This brief proposes replacing the current multi-page Django form with a single-page, interactive, multi-step wizard that guides contributors through event creation with live preview, search-first entity resolution, and inline creation for new organizers, places, and speakers. The Figma vision — "Construye tu parche / Arma tu parche" — captures the experience precisely: participatory, inviting, and Colombian in character. Getting this right directly grows the platform's event supply, data quality, and community of contributors.

## The Problem

Creating an event on Desparchado today requires navigating four separate forms: the event itself, the organizer, the place, and the speaker. Each lives on its own page. If an organizer doesn't exist yet, the contributor opens a new browser tab, fills out the organizer form, returns to the event form, and hopes the autocomplete now finds what they just created. If they miss that flow, they create a duplicate. There is no live preview, no field-by-field guidance, no inline validation. The form doesn't reveal what entities already exist until after the contributor starts typing — and even then, the autocomplete widget is a developer tool, not a UX pattern.

The consequences are measurable:
- **Low contributor volume.** The number of users who add events is disproportionately low relative to the platform's audience.
- **Duplicate data.** Organizers, places, and speakers accumulate near-duplicates ("Filbo", "FiLBo", "Feria Internacional del Libro de Bogotá") that erode content quality.
- **No funnel visibility.** There is currently no analytics instrumentation on the event form, so drop-off points are unknown. Fixing this is part of the work.

The platform already has all the underlying data; the bottleneck is the UX bridge between contributors and that data.

## The Solution

A single-page, multi-step event creation wizard that treats contributors like collaborators, not form-fillers.

**Step 1 — About the event:** Title (with contextual writing guidance), description (rich text with formatting toolbar), event URL, and category selection via visual cards. A live preview panel on the right updates in real time as the contributor types, showing exactly how the event will appear to visitors.

**Step 2 — Date & time:** Structured date/time picker with clear timezone handling (America/Bogota).

**Step 3 — Additional details:** Place selection (search-first, map preview), organizers and speakers (search-first; organizers required, speakers optional), image upload with drag-and-drop, and pricing. All fields are visible from the start — not progressively revealed — but optional fields carry explicit "(opcional)" labels and lower visual weight. This avoids the "is there more?" uncertainty of progressive disclosure while preserving a clear required/optional hierarchy.

**Search-first entity resolution with fuzzy matching:** Organizers, places, and speakers are surfaced as visual entity cards in a search-as-you-type dropdown — name, thumbnail, and a description snippet — as the contributor types. Selecting an existing record is one click. Only after an explicit search that returns no satisfying match does a "Create new organizer" option appear, making accidental duplication structurally difficult. Fuzzy matching via PostgreSQL `pg_trgm` (trigram similarity with a GIN index) surfaces near-matches across common spelling variants and abbreviations — "feria libro" finds "Feria Internacional del Libro de Bogotá", "BLAA" finds "Biblioteca Luis Ángel Arango". If the entity genuinely doesn't exist, an inline modal collects the minimum required fields and creates it without leaving the wizard.

**Umami custom events:** Instrument each wizard step transition, search interactions, inline-creation triggers, and final submission — giving the first meaningful funnel data on contributor behavior.

## What Makes This Different

The redesign is not just cosmetic. Three structural changes matter:

1. **Search-before-create mandate.** The current form allows jumping straight to organizer creation. The new flow requires searching first, making deduplication a natural part of the experience rather than an afterthought.

2. **Live preview as feedback.** The preview panel transforms an abstract form into a tangible output. Contributors can see how their title reads, whether their description is too short, and how the event card will look — before submitting anything.

3. **Inline entity creation.** Eliminating the new-tab pattern for organizer/place/speaker creation removes the #1 friction point that drops contributors mid-flow. The inline modal approach is the standard UX pattern for this problem (used by Eventbrite, Luma, and others) and is well-suited to Vue.js component composition.

The technical approach leverages the existing Vite + Vue 3 infrastructure. The event form becomes a Vue SPA backed by DRF endpoints — the right choice here because live preview requires reactive state that updates as the user types, and M2M list management (adding/removing multiple organizers and speakers before final submit) is significantly cleaner in Vue than HTMX. HTMX remains appropriate for simpler Django form interactions elsewhere on the platform, but the wizard's reactive requirements tip the balance. New DRF endpoints are needed for entity search and event create/update; image upload is handled via the existing file upload infrastructure.

## Who This Serves

**Primary: Cultural event organizers and contributors** — individuals and small organizations that run workshops, talks, art shows, reading clubs, and community gatherings in Colombian cities. They are comfortable with social media but not necessarily with data management. They may try to add an event once and abandon if the process feels complicated. Success for them: adding a complete, well-formed event in under five minutes, without needing to open a second tab.

**Secondary: Platform data stewards (superusers)** — reduced time spent merging duplicate organizers and places, and better data quality to work with in the dashboard.

## Success Criteria

| Metric | Baseline | Target |
|---|---|---|
| Events created per month | Current (measure at launch) | +40% within 60 days |
| Wizard completion rate | Unknown — establish baseline | ≥ 60% of started sessions |
| Duplicate organizer/place creation rate | Unknown — establish baseline | Reduce by 50% within 90 days |
| Form step drop-off funnel | No data | Visible in Umami within 30 days of launch |

## Scope

**In for v1:**
- Multi-step wizard UI (3 steps, matching Figma) with live preview panel
- Search-first organizer, place, and speaker resolution with inline creation modals (all three entity types, create and edit parity)
- Fuzzy search via PostgreSQL `pg_trgm` for entity resolution
- Vue 3 SPA backed by DRF endpoints for entity search and event creation/update
- Umami custom event instrumentation for full funnel visibility
- Image upload with drag-and-drop
- Apply to both create (`/events/add/`) and edit (`/events/<pk>/edit/`) flows with identical field set

**Explicitly out for v1:**
- AI-assisted title/description suggestions
- Bulk event import via spreadsheet (existing dashboard feature, separate concern)
- Redesign of standalone organizer/place/speaker edit forms (those pages remain as-is)
- Social URL fields for organizers (facebook_url, twitter_url, instagram_url) — available on the edit form post-creation, not surfaced in the inline creation modal to reduce first-time complexity

## Vision

If this works, Desparchado's event supply grows organically — not just from scrapers and manual admin imports, but from the cultural organizations and independent curators who know these events firsthand. A frictionless creation experience is the precondition for community-contributed content at scale. The wizard becomes a template for how any entity creation on the platform should feel: guided, visual, and forgiving of first-time users.

In 2-3 years, this foundation supports richer contributor features: recurring events, event series management, co-organizer collaboration, and publisher reputation signals — none of which are feasible without a healthy contributor base established now.