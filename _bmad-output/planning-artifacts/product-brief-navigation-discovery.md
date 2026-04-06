---
title: "Product Brief: Navigation & Discovery UX"
status: "complete"
created: "2026-04-05"
updated: "2026-04-05"
inputs:
  - "User conversation — Vera, 2026-04-05"
  - "Screenshot — speaker detail page, Carol Ann Figueroa"
  - "Umami analytics — bounce rate 93%, visit duration 20s, sources: 94% Google, 58% organic"
  - "Codebase analysis — detail page templates, views, EventDetailView related_events logic"
---

# Product Brief: Navigation & Discovery UX

## Executive Summary

94% of Desparchado's traffic arrives from Google, lands on a speaker, event, or organizer page, and leaves in 20 seconds — 93% of the time without clicking anything. The platform has a search-engine visibility problem that is actually a navigation problem: users find exactly what they searched for, but the page gives them no reason to stay and no visible path to anything else. Desparchado's identity as a living cultural events guide is invisible on the pages where it matters most. This brief proposes three targeted interventions — contextual related content, cross-entity navigation, and platform identity signals on detail pages — all achievable through server-side template improvements without frontend architecture changes.

## The Problem

### Users don't know where they've landed

A user searches "Carol Ann Figueroa escritora" and lands on her speaker page. They see a biography, a 2019 event, and a sidebar that says "La ciudad está llena de nuevos parches." Nothing on the page explains that Desparchado is a cultural events directory for Colombia, that there are active events happening right now, or that this speaker is part of an ecosystem of organizers and venues. The tagline "tu guía cultural" appears only in the footer — never seen by someone who bounces. There are no breadcrumbs, no category labels, no platform context visible above the fold.

### The related content is not related

Event detail pages show three "related" events selected at random — `order_by('?')` in the database. A literature festival event might show an environmental science talk and a hip-hop concert as suggestions. The platform has rich relationship data (category, organizer, place, co-speakers) that is completely unused for recommendations. A user who liked what they saw has no curated path forward.

### Cross-entity navigation doesn't exist

A user on a speaker page cannot discover which organizations have hosted that speaker, or which other speakers have appeared alongside them. An organizer page doesn't surface the speakers who've worked with that organizer. A place page doesn't show which organizations use that venue. These relationships are in the database — they just aren't exposed as navigation. Every detail page is a dead end except for the event cards directly beneath it.

### The worst case: no upcoming events

When a speaker or organizer has no upcoming events, the page shows a bio, a generic CTA, and an archive. There is nothing that communicates the platform is alive, that events are happening right now, or that the user can explore further. This is a page that was built to showcase future events — and its fallback state is a dead end.

## The Solution

Three interventions, each independently valuable:

### 1. Contextual related content — replace random with relevant

**Event detail:** Replace the three random "Otros parecidos" events with a weighted relevance strategy: first show upcoming events by the same organizer, then upcoming events in the same category, then upcoming events at the same place, then any random upcoming events on the platform, and finally random past events if no upcoming events exist at all. Fall back to the next tier only if the previous tier returns nothing. Each result set is capped and labeled by its source ("Más eventos de [Organizer]", "Más eventos de [Category]"). This turns "Otros parecidos" into something that actually feels similar, while guaranteeing the section always has content.

**Speaker and organizer detail:** When a speaker or organizer has no upcoming events, replace the empty section with a city-aware events suggestion drawn from their event history categories — surfacing active events in the same genre. This transforms a dead-end page into a discovery prompt.

### 2. Cross-entity navigation — expose the relationships in the data

Each detail page surfaces the entities it's related to through events:

- **Speaker page** → "Organizaciones que han presentado a [Speaker]" (organizers of their events) + "Otros presentadores con quienes ha compartido escenario" (co-speakers from the same events, top 3–5)
- **Organizer page** → "Presentadores que han participado en nuestros eventos" (speakers from their events)
- **Place page** → "Organizaciones que presentan aquí" (organizers whose events use this venue)

All of these are straightforward Django ORM queries on existing M2M and FK relationships — no new data, no schema changes. Each exposed relationship is a navigation node that keeps the user moving through the platform's content graph.

### 3. Platform identity — make Desparchado legible on landing

Three lightweight additions to detail page templates:

- **Breadcrumbs with structured data:** A `Inicio > Presentadores > Carol Ann Figueroa` navigation trail at the top of every detail page, implemented as server-rendered HTML with `schema.org/BreadcrumbList` JSON-LD. The HTML breadcrumb makes page hierarchy legible to first-time visitors; the structured data tells Google the page hierarchy and enables enhanced SERP display — directly improving CTR on the organic searches that already drive 58% of traffic.
- **`schema.org` structured data on all detail pages:** `Person` markup on speaker pages, `Organization` on organizer pages, `Place` on place pages, and `Event` on event detail pages (including upcoming event dates, location, and organizer). Google can display rich results — including upcoming events in the SERP — for speakers and organizers, improving click-through before the user even lands.
- **Contextual sidebar value proposition:** Replace the generic "La ciudad está llena de nuevos parches" with content specific to what the user can do next — on a speaker page with no upcoming events, show a count of events in their genre happening this month; on an event page, show the organizer's upcoming event count. The copy becomes a live invitation rather than a static slogan.
- **Category pages and label on event detail:** Display the event's category as a clickable tag near the title linking to a dedicated category page (e.g., `/eventos/literatura/`). Each category page is a filtered event list with its own SEO-optimized title, meta description, and URL — a quick structural win that creates six new indexable entry points for organic search and gives users landing on an event an obvious one-click path to more of the same.

## What Makes This Different

All three interventions are **data already in the database**. This is not a content strategy problem or a curation problem — the relationships between speakers, organizers, places, and categories are fully modeled in Django. The gap is entirely in the templates and views: the wrong query (random) or no query (cross-entity navigation). The implementation is server-side template work — no new frontend infrastructure, no Vue components, no API changes. This is a high-leverage, low-risk set of changes.

Category pages require one new view and URL pattern per category (or a single `CategoryDetailView` with slug routing), plus SEO-optimized templates. This is the highest-leverage SEO addition in this brief: six new indexable URLs targeting specific cultural event genres in Colombia.

## Who This Serves

**Primary: Organic search visitors** — users who arrive from Google looking for a specific speaker, event, or organizer. They found what they searched for; the goal is to convert that single-page visit into a session. 94% of traffic, 93% bounce rate — this is the highest-leverage audience on the platform.

**Secondary: Repeat visitors and explorers** — users who know what Desparchado is and use it to browse. Better cross-entity navigation makes the platform richer for them too, without changing the primary user flows they already use.

## Success Criteria

| Metric | Baseline | Target |
|---|---|---|
| Bounce rate (speaker/organizer/event detail) | 93% | ≤ 70% within 60 days |
| Average visit duration | 20s | ≥ 45s within 60 days |
| Pages per session | Unknown — establish at launch | ≥ 1.8 (vs implied ~1.05 today) |
| Click-through rate on related content | 0 (random, not tracked) | Establish baseline; optimize in second iteration |

Note: Umami custom events should be added for related content clicks (which entity type, which position) and cross-entity navigation clicks to enable second-iteration optimization.

## Scope

**In for v1:**
- Contextual related events on event detail: cascading fallback (same organizer → same category → same place → random future → random past)
- Co-speakers and hosting organizers on speaker detail page
- Event speakers on organizer detail page
- Venue organizers on place detail page
- Breadcrumbs (HTML + `schema.org/BreadcrumbList` JSON-LD) on all detail page types
- `schema.org` structured data: `Event`, `Person`, `Organization`, `Place` on respective detail pages
- Category pages (`/eventos/literatura/`, `/eventos/arte/`, etc.) with SEO-optimized templates
- Category label as clickable tag on event detail, linking to the category page
- Category-based fallback content on speaker/organizer pages with no upcoming events
- Umami custom events for all new navigation interactions (related content clicks by type and position)

**Explicitly out for v1:**
- Site-wide search in the header (separate initiative — higher complexity, different scope)
- Personalized recommendations based on user history (requires auth state and usage data not yet collected)
- Speaker/organizer notification subscriptions ("notifícame cuando tenga nuevo evento") — v2, after traffic baseline is established
- "Related specials" on event detail (Specials already shown when an event belongs to one — no change needed)
- Redesign of the header navigation links (functional, low bounce-rate impact compared to page-level changes)
- A/B testing infrastructure (implement changes first, measure, then test variants in a follow-up)

## Vision

Desparchado's content graph — events, speakers, organizers, places, categories — is richer than the current navigation suggests. Every speaker page is a node connected to organizers, venues, genres, and co-presenters. Every event is a node connected to a community. When those connections are visible as navigation, the platform stops feeling like a database of individual records and starts feeling like a guide — something worth exploring, not just landing on.

The 93% bounce rate is not a rejection of the content. It's a failure of wayfinding. Fixing it turns every Google-sourced landing page into a platform entry point.