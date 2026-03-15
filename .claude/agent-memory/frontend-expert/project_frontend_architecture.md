---
name: Frontend component architecture
description: Key facts about the presentational component system — directory layout, styling conventions, and BEM usage
type: project
---

## Component location

All presentational Vue components live under:
`desparchado/frontend/components/presentational/`

Subdirectory layout:
- `components/` — compound components (event-card, featured-event-card, event-card-full-width, header, menu-dropdown)
- `atoms/` — primitive components (button, nav-item, logo)
- `foundation/` — design tokens rendered as components (typography, icon)

## Event card variants

Three event card components exist:

1. **EventCard.vue** (`components/event-card/`)
   - Props include: `link`, `title`, `imageUrl`, `description`, `location`, `day`, `time`, `tag`, `customClass`
   - Has a `Button` at the bottom with `:link="link"` and label "Leer más"
   - Image is a CSS background-image `div`, NOT an `<img>` tag

2. **FeaturedEventCard.vue** (`components/featured-event-card/`)
   - Props include: `link`, `title`, `imageUrl`, `location`, `day`, `time`, `dateCopy`, `tag`, `customClass`
   - The entire card root element is already rendered as `<a :href="link">` when `link` is present — the whole card is already a link
   - No separate Button

3. **EventCardFullWidth.vue** (`components/event-card-full-width/`)
   - Props include: `link`, `title`, `imageUrl`, `description`, `location`, `day`, `time`, `dateCopy`, `speakers`, `tag`, `customClass`
   - Has a `Button` with `:link="link"` and label "Ver evento"
   - Supports a `speakers` prop (array of `{ imageUrl, name, link }`)
   - Image is a CSS background-image `div`

## Styling conventions

- Styles are kept in sibling `styles.scss` files, imported inside `<script setup>` via `import './styles.scss'`
- No `<style>` blocks inside `.vue` files
- BEM naming is enforced via a `bem(baseClass, element)` utility imported from `../../../../scripts/utils/bem`
- SCSS files use `$self: &;` pattern for nested self-references
- Style imports use path aliases: `@styles/variables`, `@styles/breakpoints`, `@styles/functions`, `@styles/animations`, `@styles/mixins`
- Component imports use `@presentational_components/` alias

## Utility functions

- `bem(baseClass, element?)` — BEM class name generator, from `scripts/utils/bem`
- `generateUID()` — generates a unique ID for accessibility id attributes, from `scripts/utils/generate-uid`
