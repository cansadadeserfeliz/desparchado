# Technology Stack

Generated: 2026-04-06 | Scan level: exhaustive

## Overview

Desparchado is a **Django monolith** with a co-located **Vue.js 3** frontend compiled by Vite. The backend serves both HTML pages (Django templates) and a REST API consumed by Vue components. The entire stack runs inside Docker for local development.

## Backend

| Category | Technology | Version | Notes |
|---|---|---|---|
| Language | Python | 3.14 | |
| Framework | Django | ^6.0 | |
| API | Django REST Framework | ^3.16 | |
| API Docs | drf-yasg | ^1.21 | Swagger/ReDoc at `/swagger/` |
| Database | PostgreSQL + PostGIS | — | GIS extension for geo coordinates |
| ORM driver | psycopg | 3.3 | |
| Auth | django-allauth | ^65.14 | Email-only login, mandatory verification |
| Brute-force | django-axes | ^8.0 | 5-attempt lockout, 24h cooldown |
| Forms | django-crispy-forms + crispy-bootstrap5 | — | Bootstrap 5 rendering |
| Autocomplete | django-autocomplete-light | ^3.12 | Select2 widgets for M2M fields |
| Slugs | django-autoslug | ^1.9 | Auto-generated slugs |
| Filters | django-filter | ^25.2 | DRF filter backend |
| Map widgets | django-map-widgets | — | Leaflet/Google/Mapbox PointField widgets |
| Cleanup | django-cleanup | ^9.0 | Deletes orphaned media files |
| Frontend integration | django-vite | ^3.1 | Loads Vite manifest in templates |
| Email | django-ses | ^4.6 | AWS SES backend |
| HTML sanitizer | html-sanitizer | ^2.6 | Sanitizes user-provided HTML in descriptions |
| External data | gspread | ^6.2 | Google Sheets API client for event imports |
| Date parsing | python-dateutil | ^2.9 | Flexible date parsing in scrapers |
| Monitoring | sentry-sdk | ^2.47 | Error tracking + performance tracing (prod only) |
| WSGI | Gunicorn | ^22.0 | Production app server |
| Timestamps | django-model-utils | ^5.0 | `TimeStampedModel` base class |
| Debug | django-debug-toolbar | ^6.1 | Dev-only request profiling |

## Frontend

| Category | Technology | Version | Notes |
|---|---|---|---|
| Framework | Vue.js | 3 | Composition API, `<script setup>` |
| Language | TypeScript | ^5.4 | Strict mode, no `any` |
| Bundler | Vite | ^6.4 | Multi-entry build, HMR in dev |
| Plugin | @vitejs/plugin-vue | ^5.2 | `.vue` SFC support |
| CSS | SCSS | — | via sass-embedded ^1.86 |
| SVG | vite-svg-loader | ^5.1 | Import SVG as raw strings |
| Component docs | Storybook | ^8.6 | Vue3+Vite builder, port 6006 |
| Linting | ESLint + eslint-plugin-vue | ^9.25 / ^10.0 | |
| Formatting | Prettier | ^3.5 | |
| Testing | Vitest + Playwright | ^3.1 / ^1.56 | Browser-based unit tests |

## Infrastructure & Deployment

| Category | Technology | Notes |
|---|---|---|
| Containerization | Docker + docker-compose | 3 services: web, frontend, db |
| Production host | Gunicorn + Nginx | desparchado.co |
| Database service | PostGIS image (docker-containers/db) | Port 5032 local, 5432 internal |
| Frontend service | Node image (docker-containers/frontend) | Port 5173 (Vite), 6006 (Storybook) |
| CI/CD | GitHub Actions | Ruff lint, CodeQL security scan, Sentry release |
| Error tracking | Sentry | Production only; traces 100%, profiles 100% |
| Email delivery | AWS SES | Region us-east-1 |
| Storage | Django FileSystemStorage (media/static) | No S3 |
| Analytics | Umami | Optional (`ANALYTICS_ENABLED`) |

## Architecture Pattern

**Django Monolith + Embedded SPA Components**

- Django renders full HTML pages using Django templates.
- Vue 3 components are embedded in specific pages via `data-vue-component` attributes on DOM elements.
- The `VueComponentMount` class (`mount-vue.ts`) auto-discovers and mounts all registered Vue components on `DOMContentLoaded`.
- Vue components call the DRF REST API (`/events/api/v1/`) for dynamic data.
- No client-side routing; navigation is handled by Django URLs.

## Settings Split

| File | Purpose |
|---|---|
| `desparchado/settings/base.py` | Shared config (DB, auth, middleware, email, maps) |
| `desparchado/settings/dev.py` | Debug=True, relaxed hosts |
| `desparchado/settings/production.py` | Sentry init, tight ALLOWED_HOSTS, manifest path |
| `desparchado/settings/test.py` | Test DB name override, disables external services |
