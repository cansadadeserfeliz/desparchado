# Frontend Component Inventory

Generated: 2026-04-06 | Scan level: exhaustive

All components live in `desparchado/frontend/components/presentational/` and are **presentational only** — they accept props but make no API calls. API calls happen in script-layer classes (`EventContainer`, `getEventList`) which then pass data to components via props.

Components are auto-registered by `mount-vue.ts` and can be mounted in Django templates via:
```html
<div data-vue-component="event-card"
     data-vue-prop-title="My Event"
     data-vue-prop-location="Bogotá">
</div>
```

---

## Foundation

### Typography (`foundation/typography/Typography.vue`)

A polymorphic text element with variant and weight control.

| Prop | Type | Default | Values |
|---|---|---|---|
| `tag` | string | `'p'` | Any HTML tag |
| `type` | string | required | `h1`–`h6`, `body`, `body_highlight`, `caption` |
| `weight` | string | — | `regular`, `medium`, `bold` |
| `text` | string | required | Display text |
| `customClass` | string | — | Extra CSS class |
| `id` | string | — | HTML id attribute |

Used throughout other components for consistent typography.

---

### Icon (`foundation/icon/Icon.vue`)

SVG icon wrapper.

| Prop | Type | Notes |
|---|---|---|
| `name` | string | Icon name |
| `customClass` | string | Optional CSS class |

---

## Atoms

### Button (`atoms/button/Button.vue`)

A link or button element with type and size variants.

| Prop | Type | Default | Values |
|---|---|---|---|
| `type` | string | `'primary'` | `primary`, `secondary`, `ghost` |
| `label` | string | required | Button text |
| `link` | string | — | If set, renders `<a>` instead of `<button>` |
| `padding` | string | `'default'` | `default`, `condensed` |
| `customClass` | string | — | Extra CSS class |

---

### Logo (`atoms/logo/Logo.vue`)

Site logo, optionally linkable.

| Prop | Type | Notes |
|---|---|---|
| `link` | string | Optional URL |
| `customClass` | string | Optional CSS class |

---

### NavItem (`atoms/nav-item/NavItem.vue`)

A navigation menu item.

| Prop | Type | Notes |
|---|---|---|
| `label` | string | Display text |
| `link` | string | URL |
| `active` | boolean | Highlights active state |
| `customClass` | string | Optional |

---

## Components

### EventCard (`components/event-card/EventCard.vue`)

A standard event card for use in list views.

| Prop | Type | Default | Notes |
|---|---|---|---|
| `tag` | FeaturedEventTags | `'div'` | `div`, `li`, `section`, `article` |
| `location` | string | required | Place name |
| `title` | string | required | Event title |
| `description` | string | required | HTML content (rendered with `v-html`) |
| `day` | string | required | Formatted day (e.g., `"10 Apr"`) |
| `time` | string | required | Formatted time (e.g., `"18:00"`) |
| `imageUrl` | string | fallback URL | Event image URL |
| `link` | string | required | URL to event detail |
| `customClass` | string | — | Extra CSS class |

Used by `EventContainer` to render the dynamic events list on the homepage.

---

### EventCardFullWidth (`components/event-card-full-width/EventCardFullWidth.vue`)

Full-width variant of EventCard for featured placement.

Props mirror `EventCard`.

---

### FeaturedEventCard (`components/featured-event-card/FeaturedEventCard.vue`)

A card variant for homepage featured events with a background image style.

Props mirror `EventCard` with an emphasis on the `imageUrl` as a CSS background.

---

### Header (`components/header/Header.vue`)

Site header with navigation. Props include navigation items and current page info.

---

### MenuDropdown (`components/menu-dropdown/MenuDropdown.vue`)

A navigation dropdown menu for use inside the Header.

| Prop | Type | Notes |
|---|---|---|
| `label` | string | Trigger label |
| `items` | array | Navigation items (label + link) |

---

## Script-layer Components (Non-Vue)

These are TypeScript classes that orchestrate data fetching and Vue mounting. They are attached to DOM elements via the `data-url` or similar attributes.

### EventContainer (`scripts/event-container.ts`)

Fetches future events from the API and mounts an `EventsListApp` (a render-function component wrapping `EventCard`) into the target DOM element.

**Usage in template:**
```html
<div class="event-container" data-url="/events/api/v1/events/future/?limit=6">
</div>
```

**Registered in:** `home.ts` via `attachOnLoadListener`

**Flow:**
1. `EventContainer(el)` reads `el.dataset.url`
2. Calls `getEventList(url)` via fetch
3. Maps `IEvent[]` → `EventCardProps[]` via `mapEventToCardProps()`
4. Mounts `EventsListApp` (renders a list of `EventCard` components)

---

## Storybook Stories

Each component has a corresponding story in `desparchado/frontend/stories/`:

| Story file | Component |
|---|---|
| `Button.stories.ts` | Button |
| `EventCard.stories.ts` | EventCard |
| `EventCardFullWidth.stories.ts` | EventCardFullWidth |
| `FeaturedEventCard.stories.ts` | FeaturedEventCard |
| `Header.stories.ts` | Header |
| `Icon.stories.ts` | Icon |
| `Logo.stories.ts` | Logo |
| `MenuDropdown.stories.ts` | MenuDropdown |
| `NavItem.stories.ts` | NavItem |
| `Typography.stories.ts` | Typography |

Run Storybook: `make run-storybook` (port 6006)

---

## Vite Aliases

| Alias | Resolves to |
|---|---|
| `@presentational_components` | `desparchado/frontend/components/presentational` |
| `@styles` | `desparchado/frontend/styles` |
| `@fonts` | `desparchado/frontend/assets/fonts` |
| `@assets` | `desparchado/frontend/assets` |