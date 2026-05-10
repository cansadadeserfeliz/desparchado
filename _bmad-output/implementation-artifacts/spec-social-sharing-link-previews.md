---
title: 'Improve social sharing link previews site-wide'
type: 'feature'
created: '2026-05-09'
status: 'done'
baseline_commit: '9bb58958388dcb000ed4cbc771e627a500d88f7e'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Social sharing link previews across Desparchado are incomplete and contain bugs: the event detail page renders a Place object instead of a description in `og:description`; the blog post uses `{{ post.subtitle.name }}` (renders empty since subtitle is a CharField); the special detail page shows the subtitle instead of the title in `twitter:title`; and no page defines `twitter:card`, `og:type`, `og:url`, `og:site_name`, or `og:locale`, making previews visually degraded or absent on Twitter/X and inconsistent on Facebook/LinkedIn. History and games pages share the same gaps.

**Approach:** Fix the three broken-tag bugs, add `og:site_name` and `og:locale` once in the main base template (covers all apps via inheritance), and add `og:type`, `og:url`, `twitter:card`, and `twitter:image` to every detail page across events, specials, blog, places, history, and games. For the event detail page, replace the place-as-description with a rich string combining date, venue, and a short description excerpt.

## Boundaries & Constraints

**Always:**
- All meta content must be plain text — run `description` fields through `striptags` before rendering.
- `og:url` must be the canonical path (no query string) — use `{{ request.scheme }}://{{ request.get_host }}{{ object.get_absolute_url }}` pattern; for pages without a model URL use `{{ request.path }}`.
- `twitter:card` = `summary_large_image` on pages that always have an image; `summary` where the image may be absent.
- `og:site_name` = `"Desparchado.co"`, `og:locale` = `"es_CO"` — added once to `layout/base.html`, inherited by all apps.
- For history `Event` and `Post` models (no `get_image_url()` method): render `og:image` only if `{{ model.image }}` is set, using `{{ model.image.url }}`; omit the tag otherwise.

**Ask First:** nothing unresolved.

**Never:**
- Do not introduce new view context variables or model changes.
- Do not change the `{% block meta %}` block structure — only add static tags outside it in the base template.
- Do not add meta tags to list views, form views, or authentication pages.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Event with description and image | og:description, twitter:description | Date · place — truncated description text | — |
| Event with no description | og:description, twitter:description | Date · place only, no trailing `—` | — |
| Event with no place | og:description | Date — truncated description, or date only | — |
| History model with no image | og:image, twitter:image | Tags omitted entirely | — |

</frozen-after-approval>

## Code Map

- `desparchado/templates/layout/base.html` — main base; `og:site_name` + `og:locale` go here; inherited by all apps
- `events/templates/events/event_detail.html` — primary focus; fix `og:description`, add all missing tags
- `specials/templates/specials/special_detail.html` — fix `twitter:title` bug; add missing tags
- `blog/templates/blog/post_detail.html` — fix `twitter:description` bug; add missing tags
- `events/templates/events/speaker_detail.html` — add missing tags only
- `events/templates/events/organizer_detail.html` — add missing tags only
- `places/templates/places/city_detail.html` — add missing tags only
- `history/templates/history/layout/base.html` — add `og:type=website` + `twitter:card=summary` as defaults for history pages without their own block
- `history/templates/history/historicalfigure_detail.html` — add `og:image`, `og:type=profile`, `og:url`, `twitter:card=summary_large_image`, `twitter:image`, `twitter:image:alt`
- `history/templates/history/event_detail.html` — add conditional `og:image`, `og:type=website`, `og:url`, `twitter:card=summary`, `twitter:image:alt`
- `history/templates/history/post_detail.html` — add conditional `og:image`, `og:type=article`, `og:url`, `twitter:card=summary`, `twitter:image:alt`
- `games/templates/games/hunting_of_snark_base.html` — add `og:type=website`, `twitter:card=summary_large_image`, `twitter:image` (static image already in `og:image`)
- `games/templates/games/hunting_of_snark_detail.html` — add `og:url`, overrides base with per-game values
- `games/templates/games/hunting_of_snark_criteria_list.html` — add `og:url`

## Tasks & Acceptance

**Execution:**
- [x] `desparchado/templates/layout/base.html` — add `og:site_name` and `og:locale` as static tags directly before `{% block meta %}`
- [x] `events/templates/events/event_detail.html` — fix `og:description` (date · place — description excerpt via `striptags|truncatewords:25`); add `og:type=website`, `og:url`, `twitter:card=summary_large_image`, `twitter:image`, `twitter:image:alt={{ event.title }}`
- [x] `specials/templates/specials/special_detail.html` — fix `twitter:title` (subtitle → title); add `og:type=website`, `og:url`, `twitter:card=summary_large_image`, `twitter:image`, `twitter:image:alt`
- [x] `blog/templates/blog/post_detail.html` — fix `twitter:description` (remove `.name`); add `og:type=article`, `og:url`, `twitter:card=summary_large_image`, `twitter:image`, `twitter:image:alt`
- [x] `events/templates/events/speaker_detail.html` — add `og:type=profile`, `og:url`, `twitter:card=summary`, `twitter:image`, `twitter:image:alt`
- [x] `events/templates/events/organizer_detail.html` — add `og:type=website`, `og:url`, `twitter:card=summary`, `twitter:image`, `twitter:image:alt`
- [x] `places/templates/places/city_detail.html` — add `og:type=website`, `og:url`, `twitter:card=summary_large_image`, `twitter:image`, `twitter:image:alt`
- [x] `history/templates/history/layout/base.html` — add `og:type=website` and `twitter:card=summary` inside the existing `{% block meta %}` defaults
- [x] `history/templates/history/historicalfigure_detail.html` — add `og:image` (`get_image_url`), `og:type=profile`, `og:url`, `twitter:card=summary_large_image`, `twitter:image`, `twitter:image:alt`
- [x] `history/templates/history/event_detail.html` — add `{% if event.image %}og:image{% endif %}`, `og:type=website`, `og:url`, `twitter:card=summary`
- [x] `history/templates/history/post_detail.html` — add `{% if post.image %}og:image{% endif %}`, `og:type=article`, `og:url`, `twitter:card=summary`
- [x] `games/templates/games/hunting_of_snark_base.html` — add `og:type=website`, `twitter:card=summary_large_image`, `twitter:image` matching `og:image`
- [x] `games/templates/games/hunting_of_snark_detail.html` — add `og:url` using `request.path`
- [x] `games/templates/games/hunting_of_snark_criteria_list.html` — add `og:url` using `request.path`

**Acceptance Criteria:**
- Given any detail page is shared on Twitter/X, when the URL is pasted, then a card renders because `twitter:card` is present.
- Given the event detail page is shared, when the preview renders, then `og:description` shows human-readable text (not a Python object repr).
- Given the blog post detail page is shared, then `twitter:description` shows the post subtitle (not empty).
- Given the special detail page is shared, then `twitter:title` shows the title (not the subtitle).
- Given any page is fetched by a crawler, then `og:site_name` = `"Desparchado.co"` and `og:locale` = `"es_CO"`.
- Given a history event or post with no image is shared, then no `og:image` tag is rendered.
- Given the event detail page has no description, then `og:description` contains no trailing `—` separator.

## Design Notes

Rich description format for event detail:

```
8 de mayo de 2026 · Teatro Colón — Concierto de música sacra con la Orquesta...
```

Template sketch:
```django
{{ event.event_date|date:"j \d\e N \d\e Y" }}{% if event.place %} · {{ event.place.name }}{% endif %}{% if event.description %} — {{ event.description|striptags|truncatewords:25 }}{% endif %}
```

`og:url` pattern (swap object name per page):
```django
{{ request.scheme }}://{{ request.get_host }}{{ event.get_absolute_url }}
```

## Verification

**Commands:**
- `docker exec desparchado-web-1 sh -c "cd app && pytest events/tests/ specials/tests/ blog/tests/ places/tests/ history/tests/ -q"` — expected: all pass

**Manual checks:**
- View source of any page → `og:site_name` and `og:locale` present.
- View source of event detail → `og:description` contains date text, not `<Place:`.
- Paste an event URL into https://cards-dev.twitter.com/validator → card with image renders.