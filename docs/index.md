# Desparchado — Project Documentation Index

**Type:** Monolith (Django + Vue.js 3)  
**Language:** Python 3.14 / TypeScript 5.4  
**Architecture:** Django Monolith with Embedded Vue.js Island Components  
**Scan date:** 2026-04-06 | Scan level: exhaustive

---

## Quick Reference

| Item | Value |
|---|---|
| Framework | Django 6.0 + DRF |
| Frontend | Vue.js 3 + Vite 6 + TypeScript |
| Database | PostgreSQL + PostGIS |
| Auth | django-allauth (email-only) |
| Entry point | `desparchado/urls.py` |
| Homepage view | `desparchado/views/home.py` |
| API base | `/events/api/v1/` |
| Dashboard | `/dashboard/` (superuser only) |
| Production | `desparchado.co` |

---

## Generated Documentation

### Architecture & Design
- [Architecture](./architecture.md) — Application architecture, layers, URL map, permission model, search, geo, deployment
- [Technology Stack](./technology-stack.md) — Full dependency table (backend, frontend, infra)

### Data & API
- [Data Models](./data-models.md) — All 16 models with field tables, relationships, and permission patterns
- [API Contracts](./api-contracts.md) — REST endpoints, request/response schemas, autocomplete, feeds

### Source & Structure
- [Source Tree](./source-tree.md) — Annotated directory tree with integration points
- [Component Inventory](./component-inventory.md) — All 10 Vue components with prop tables; script-layer components

### Development
- [Development Guide](./development-guide.md) — Local setup, Docker commands, testing, code style, git conventions

---

## Existing Documentation

- [Architecture Explanation](./explanations/architecture.md) — Narrative architecture overview
- [How-to Guides](./how-to-guides/index.md) — Task-oriented guides
- [References](./references/index.md) — Reference material
- [Create an Event (Tutorial)](./tutorials/create-event.md) — Step-by-step event creation tutorial

---

## Getting Started

```bash
# Start the full local stack
make up

# Open a shell in the web container
make sh-web

# Run the test suite
make test

# Run linting
make lint

# Apply migrations
make migrate
```

See the [Development Guide](./development-guide.md) for environment variables, test commands, and more.

---

## Core Domain Summary

**Events** are the central entity. An event:
- Belongs to a **Place** (with PostGIS coordinates) which belongs to a **City**
- Has **Organizers** and **Speakers** (M2M)
- Has four visibility flags: `is_published`, `is_approved`, `is_featured_on_homepage`, `is_hidden`
- Is publicly visible when `is_published AND is_approved`
- Can be grouped into **Specials** (festivals, series)
- Can be imported from Google Sheets via the **Dashboard** (`SpreadsheetSync`)
- Has a `source_id` for external deduplication (e.g., `FILBO2026_12345`)

**Users** have per-resource daily creation quotas (events: 10, organizers/speakers/places: 5). Superusers bypass all quotas.

**Search** uses PostgreSQL `SearchVector` + `unaccent__icontains` on title, description, and speaker names.

---

## Key File Locations

| What | Where |
|---|---|
| Root URL config | `desparchado/urls.py` |
| Django settings | `desparchado/settings/` |
| Event model | `events/models/event.py` |
| Event search service | `events/services/event_search.py` |
| API views | `events/api/views.py` |
| Homepage view | `desparchado/views/home.py` |
| Spreadsheet sync | `dashboard/services/spreadsheet_sync.py` |
| FILBo sync | `dashboard/services/filbo.py` |
| Vue mount system | `desparchado/frontend/scripts/mount-vue.ts` |
| Event API client | `desparchado/frontend/scripts/api/events.ts` |
| Root test fixtures | `conftest.py` |
| Vite config | `vite.config.js` |
| Docker services | `docker-compose.yml` |