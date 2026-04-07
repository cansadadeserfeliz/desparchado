---
title: "Product Brief Distillate: Navigation & Discovery UX"
type: llm-distillate
source: "product-brief-navigation-discovery.md"
created: "2026-04-05"
purpose: "Token-efficient context for downstream PRD creation"
---

# Detail Pack: Navigation & Discovery UX

## Current State (What We're Fixing)

- **Related events on event detail**: `order_by('?')[:3]` — pure random, zero filtering by category/organizer/place. Confirmed in `events/views/event_detail.py`.
- **Breadcrumbs**: None anywhere on the site. No `schema.org` structured data on any page.
- **Cross-entity navigation**: Non-existent. Speaker pages don't link to organizers or co-speakers. Organizer pages don't surface associated speakers. Place pages don't show which organizers use the venue. All relationships are in the database, none are exposed as navigation.
- **Platform identity on detail pages**: Tagline "tu guía cultural" is footer-only. Header has two nav links (eventos, archivo). No value proposition, no breadcrumbs, no category labels visible above the fold to a first-time visitor.
- **Category pages**: Do not exist. Category is a field on Event (5 choices: literature, society, environment, science, art) but has no dedicated list view or URL.
- **Sidebar**: Speaker and organizer detail pages have a right sidebar with generic static copy ("La ciudad está llena de nuevos parches" → "Busca eventos cerca" button). Event and place detail pages have no sidebar. Copy is identical on every speaker/organizer page regardless of context.
- **Empty state**: Speakers/organizers with no upcoming events show bio + archive only. No fallback content, no discovery path.
- **Analytics**: Umami active (base.html, ID `1ccee07e-d5e4-4c95-a986-3b1569f29d9b`). No custom events on any navigation interaction. Bounce rate 93%, visit duration 20s, 94% Google traffic, 58% organic search, 70% laptop.

## Related Content: ORM Queries

All queries operate on existing M2M/FK relationships — no schema changes needed.

### Event detail — cascading fallback for "related events"
```python
# Tier 1: same organizer(s), future
related = Event.objects.filter(organizers__in=event.organizers.all())
           .exclude(pk=event.pk).published().future()
           .distinct()[:3]

# Tier 2: same category, future
if len(related) < 3:
    related = Event.objects.filter(category=event.category)
              .exclude(pk=event.pk).published().future()
              .distinct()[:3]

# Tier 3: same place, future
if len(related) < 3:
    related = Event.objects.filter(place=event.place)
              .exclude(pk=event.pk).published().future()
              .distinct()[:3]

# Tier 4: any future events (random)
if len(related) < 3:
    related = Event.objects.exclude(pk=event.pk).published().future()
              .order_by('?')[:3]

# Tier 5: any past events (random) — last resort
if len(related) < 3:
    related = Event.objects.exclude(pk=event.pk).published().past()
              .order_by('?')[:3]
```
Label the section header dynamically based on which tier returned results ("Más eventos de [Organizer name]", "Más eventos de [Category]", "Otros eventos", etc.).

### Speaker detail — cross-entity navigation
```python
# Organizers who've hosted this speaker
hosting_organizers = Organizer.objects.filter(
    event__speakers=speaker
).distinct().order_by('name')[:6]

# Co-speakers (speakers who've shared events with this speaker)
co_speakers = Speaker.objects.filter(
    event__in=speaker.events.all()
).exclude(pk=speaker.pk).distinct()

# Rank co-speakers by frequency of co-appearance
from django.db.models import Count
co_speakers = co_speakers.annotate(
    shared_count=Count('event', filter=Q(event__speakers=speaker))
).order_by('-shared_count')[:5]

# Category-based fallback when no upcoming events
if not upcoming_events:
    # Find most common category in speaker's event history
    from django.db.models import Count
    top_category = speaker.events.values('category')
                   .annotate(c=Count('category')).order_by('-c')
                   .first()
    if top_category:
        fallback_events = Event.objects.filter(
            category=top_category['category']
        ).exclude(speakers=speaker).published().future()
        .order_by('?')[:3]
```

### Organizer detail — cross-entity navigation
```python
# Speakers who've appeared at this organizer's events
associated_speakers = Speaker.objects.filter(
    event__organizers=organizer
).distinct().annotate(
    appearance_count=Count('event', filter=Q(event__organizers=organizer))
).order_by('-appearance_count')[:8]
```

### Place detail — cross-entity navigation
```python
# Organizers whose events use this venue
venue_organizers = Organizer.objects.filter(
    event__place=place
).distinct().annotate(
    event_count=Count('event', filter=Q(event__place=place))
).order_by('-event_count')[:6]
```

## Category Pages

### URL structure
New `CategoryDetailView` with slug routing — one view handles all 5 categories:
```
/eventos/literatura/   → category='literatura' (maps to Event.LITERATURE)
/eventos/arte/         → category='arte'
/eventos/sociedad/     → category='sociedad'
/eventos/ciencia/      → category='ciencia'
/eventos/medio-ambiente/ → category='medio-ambiente'
```

### SEO templates per category
Each category page needs a unique `<title>` and meta description:

| Category | Title | Meta description |
|---|---|---|
| Literatura | Eventos de Literatura en Colombia — Desparchado | Presentaciones de libros, ferias literarias, lecturas y encuentros con autores en Colombia. |
| Arte | Eventos de Arte en Colombia — Desparchado | Exposiciones, performances, talleres y muestras de arte en Colombia. |
| Sociedad | Eventos de Sociedad en Colombia — Desparchado | Conversatorios, foros, activismo y encuentros ciudadanos en Colombia. |
| Ciencia | Eventos de Ciencia en Colombia — Desparchado | Conferencias, charlas y talleres de ciencia y tecnología en Colombia. |
| Medio Ambiente | Eventos de Medio Ambiente en Colombia — Desparchado | Encuentros, talleres e iniciativas de conservación y sostenibilidad en Colombia. |

### View logic
- Inherits from existing `EventListView` pattern (same `.published().future()` queryset)
- Filtered by `category=` param derived from URL slug
- Supports future/past toggle (same as main event list)
- Breadcrumb: `Inicio > Eventos > Literatura`
- `schema.org/CollectionPage` + `ItemList` structured data

### Category slug → model constant mapping
```python
CATEGORY_SLUG_MAP = {
    'literatura': Event.LITERATURE,   # confirm constant names from Event model
    'arte': Event.ART,
    'sociedad': Event.SOCIETY,
    'ciencia': Event.SCIENCE,
    'medio-ambiente': Event.ENVIRONMENT,
}
```
(Verify exact constant names in `events/models/event.py` — the model uses a `category` CharField with choices.)

## Breadcrumbs & Structured Data

### Breadcrumb HTML + JSON-LD pattern
Implement as a reusable Django template include `{% include 'includes/_breadcrumbs.html' with items=breadcrumb_items %}`.

Each view adds `breadcrumb_items` to context as a list of `(label, url)` tuples:
- Speaker: `[("Inicio", "/"), ("Presentadores", "/eventos/presentadores/"), ("Carol Ann Figueroa", None)]`
- Organizer: `[("Inicio", "/"), ("Organizadores", "/eventos/organizadores/"), ("Name", None)]`
- Event: `[("Inicio", "/"), ("Eventos", "/eventos/"), ("Event Title", None)]`
- Place: `[("Inicio", "/"), ("Lugares", "/lugares/"), ("Place Name", None)]`
- Category: `[("Inicio", "/"), ("Eventos", "/eventos/"), ("Literatura", None)]`

JSON-LD alongside:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Inicio", "item": "https://desparchado.co/"},
    {"@type": "ListItem", "position": 2, "name": "Presentadores", "item": "https://desparchado.co/eventos/presentadores/"},
    {"@type": "ListItem", "position": 3, "name": "Carol Ann Figueroa"}
  ]
}
</script>
```

### schema.org per page type

**Speaker page** (`schema.org/Person`):
```json
{
  "@type": "Person",
  "name": "Carol Ann Figueroa",
  "description": "[speaker.description truncated]",
  "image": "[speaker.image.url]",
  "url": "https://desparchado.co/events/speaker/[slug]/"
}
```

**Organizer page** (`schema.org/Organization`):
```json
{
  "@type": "Organization",
  "name": "[organizer.name]",
  "description": "[organizer.description truncated]",
  "url": "[organizer.website_url or desparchado URL]",
  "logo": "[organizer.image.url]",
  "sameAs": ["[facebook_url]", "[twitter_url]", "[instagram_url]"]
}
```

**Place page** (`schema.org/Place`):
```json
{
  "@type": "Place",
  "name": "[place.name]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[place.address]",
    "addressLocality": "[place.city.name]",
    "addressCountry": "CO"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "[place.get_latitude_str()]",
    "longitude": "[place.get_longitude_str()]"
  }
}
```

**Event page** (`schema.org/Event`):
```json
{
  "@type": "Event",
  "name": "[event.title]",
  "startDate": "[event.event_date.isoformat()]",
  "location": {
    "@type": "Place",
    "name": "[event.place.name]",
    "address": "[event.place.address]"
  },
  "organizer": {"@type": "Organization", "name": "[organizer.name]"},
  "image": "[event.image.url if available]",
  "description": "[event.description stripped of HTML, truncated]",
  "eventStatus": "https://schema.org/EventScheduled",
  "url": "https://desparchado.co/events/[slug]/"
}
```
Note: `event_date` is stored in America/Bogota timezone — ensure ISO 8601 output includes timezone offset.

## Umami Custom Events (Navigation)

| User action | Event name | Properties |
|---|---|---|
| Clicked related event (event detail) | `related_event_clicked` | `{ tier: 'organizer'|'category'|'place'|'random_future'|'random_past', position: 1|2|3 }` |
| Clicked co-speaker | `co_speaker_clicked` | `{ from_page: 'speaker' }` |
| Clicked hosting organizer (from speaker page) | `hosting_organizer_clicked` | — |
| Clicked associated speaker (from organizer page) | `associated_speaker_clicked` | — |
| Clicked venue organizer (from place page) | `venue_organizer_clicked` | — |
| Clicked category tag (event detail) | `category_tag_clicked` | `{ category: 'literatura'|... }` |
| Clicked breadcrumb | `breadcrumb_clicked` | `{ level: 1|2|3, label: '...' }` |
| Clicked fallback event (empty state) | `empty_state_event_clicked` | `{ page_type: 'speaker'|'organizer' }` |

## Template Changes Required

| Template | Changes |
|---|---|
| `events/templates/events/event_detail.html` | Replace random related events with cascading query; add category tag; add breadcrumbs + JSON-LD; add `schema.org/Event` |
| `events/templates/events/speaker_detail.html` | Add co-speakers section; add hosting organizers section; add empty-state fallback; add breadcrumbs + JSON-LD; add `schema.org/Person`; make sidebar contextual |
| `events/templates/events/organizer_detail.html` | Add associated speakers section; add empty-state fallback; add breadcrumbs + JSON-LD; add `schema.org/Organization`; make sidebar contextual |
| `places/templates/places/place_detail.html` | Add venue organizers section; add breadcrumbs + JSON-LD; add `schema.org/Place` |
| New: `events/templates/events/category_detail.html` | Category page — inherits event list layout, SEO title/description, breadcrumbs, `schema.org/CollectionPage` |
| New: `includes/_breadcrumbs.html` | Reusable breadcrumb include with JSON-LD output |

## View Changes Required

| View | Changes |
|---|---|
| `EventDetailView` | Replace `order_by('?')[:3]` with cascading fallback query; add `breadcrumb_items` to context |
| `SpeakerDetailView` | Add `hosting_organizers`, `co_speakers`, `fallback_events` to context; add `breadcrumb_items` |
| `OrganizerDetailView` | Add `associated_speakers`, `fallback_events` to context; add `breadcrumb_items` |
| `PlaceDetailView` | Add `venue_organizers` to context; add `breadcrumb_items` |
| New: `CategoryDetailView` | Filtered event list by category slug; `breadcrumb_items`; SEO meta per category |

## Rejected Approaches

- **URL parameter filter** (`/eventos/?category=literatura`) for category entry point — rejected in favour of dedicated category pages for SEO value (indexable URLs, unique meta per category).
- **Personalized recommendations** (based on user history or auth state) — rejected for v1; no usage data collected yet to base recommendations on.
- **Speaker/organizer notification subscriptions** ("notifícame cuando tenga nuevo evento") — valuable v2 retention feature, but requires email infrastructure and auth integration. Not in v1.
- **Site-wide header search** — higher complexity, different scope. Separate initiative.
- **A/B testing** — implement first, measure baseline, then test variants. Not in v1.

## Open Questions

- **Co-speaker section cap**: 5 is proposed. For very prolific speakers this may feel thin; for lesser-known speakers it may be fine. Consider showing at least 3 or none (don't show section if fewer than 3).
- **Category page pagination**: Should category pages paginate (like the main event list) or show a fixed cap? Main list uses infinite scroll / paginated DRF fetch — category page should follow the same pattern for consistency.
- **Sidebar on event and place detail**: Currently no sidebar exists on event or place pages. The brief proposes a contextual sidebar for speaker/organizer. Should event and place pages also get a sidebar, or keep the current full-width layout?
- **`event_date` timezone in schema.org**: Confirm the field stores naive or aware datetimes. The setting is `TIME_ZONE = 'America/Bogota'` (`UTC-5`). ISO 8601 output should be `-05:00` not `Z`.
- **"Presentadores" and "Organizadores" list URLs**: Breadcrumbs for speaker/organizer pages reference `/eventos/presentadores/` and `/eventos/organizadores/` — confirm these list views exist and are accessible (`/events/speakers/`, `/events/organizers/`).

## Scope Boundaries (Explicit)

**In v1:**
- 5-tier cascading related events on event detail
- Co-speakers + hosting organizers on speaker pages
- Associated speakers on organizer pages
- Venue organizers on place pages
- Breadcrumbs (HTML + `BreadcrumbList` JSON-LD) on all 4 detail page types + category pages
- `schema.org` structured data: `Event`, `Person`, `Organization`, `Place`
- 5 category pages with SEO-optimized templates and unique meta
- Category tag on event detail → links to category page
- Contextual sidebar copy on speaker/organizer pages
- Empty-state fallback content on speaker/organizer pages with no upcoming events
- Umami custom events for all navigation interactions

**Out of v1:**
- Header search
- Personalized recommendations
- Notification subscriptions
- A/B testing
- Category-level city filtering
- Related specials (already handled by existing Special section on event detail)