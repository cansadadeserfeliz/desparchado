# Source Tree

Generated: 2026-04-06 | Scan level: exhaustive

```
desparchado/                         # Project root
│
├── manage.py                        # Django management entry point
├── pyproject.toml                   # Python project config + ruff + pytest settings
├── requirements.in                  # Direct Python dependencies (pip-compile source)
├── requirements.txt                 # Pinned, hashed Python dependencies
├── requirements-dev.in              # Dev-only deps (pytest, coverage, etc.)
├── vite.config.js                   # Vite build config (multi-entry, aliased paths)
├── package.json                     # Node.js deps (Vue, Vite, Storybook, ESLint)
├── tsconfig.json                    # TypeScript compiler config
├── eslint.config.mjs                # ESLint config
├── Makefile                         # Dev shortcuts: make up, make test, make lint, etc.
├── docker-compose.yml               # 3-service local stack: web, frontend, db
├── Dockerfile                       # Web container build
├── conftest.py                      # Root pytest fixtures (user, event, place, etc.)
│
├── desparchado/                     # Django project package (settings + root URLs)
│   ├── settings/
│   │   ├── base.py                  # Shared settings (DB, auth, middleware, email, maps)
│   │   ├── dev.py                   # DEBUG=True, relaxed hosts
│   │   ├── production.py            # Sentry, tight ALLOWED_HOSTS, manifest path
│   │   └── test.py                  # Test DB override
│   ├── urls.py                      # Root URL configuration → all app namespaces
│   ├── wsgi.py                      # WSGI entry point for Gunicorn
│   ├── sitemap.py                   # XML sitemaps for all public entities
│   ├── views/
│   │   ├── home.py                  # HomeView: featured events + specials on homepage
│   │   └── rss.py                   # RSS/Atom feed views
│   ├── mixins.py                    # EditorPermissionRequiredMixin (can_edit check)
│   ├── utils.py                     # send_notification, sanitize_html, get_natural_day
│   ├── autocomplete.py              # Generic autocomplete helpers
│   ├── backends.py                  # EmailBackend (login by email)
│   ├── template/
│   │   └── context_processors.py   # `constants` context processor (shared template vars)
│   ├── templatetags/
│   │   └── desparchado_tags.py      # Custom template tags (format_currency, etc.)
│   ├── templates/                   # Base templates, about, error pages
│   ├── static/                      # Global static files (images, legacy JS, old TS)
│   │   ├── ts/
│   │   │   ├── old_main.ts          # Legacy scripts (pre-Vite era)
│   │   │   └── posts_pagination_initializer.ts
│   │   └── js/
│   │       └── dashboard.js         # Dashboard JS (non-Vite)
│   └── frontend/                    # Vue + Vite frontend source
│       ├── scripts/
│       │   ├── mount-vue.ts         # Auto-discovers and mounts Vue components via data-vue-component
│       │   ├── event-container.ts   # EventContainer: fetches API + mounts EventCard list
│       │   ├── event-details.ts     # Event detail page scripts
│       │   ├── events.ts            # Events list page scripts
│       │   ├── home.ts              # Homepage scripts (registers EventContainer)
│       │   ├── base.ts              # Base scripts loaded on all pages
│       │   ├── generic.ts           # Generic page scripts
│       │   ├── init-components.ts   # Component initialization helper
│       │   ├── api/
│       │   │   ├── events.ts        # getEventList() → calls /events/api/v1/events/future/
│       │   │   └── interfaces.ts    # TypeScript interfaces: IEvent, IApiPaginatedResponse
│       │   └── utils/
│       │       ├── bem.ts           # BEM CSS class helper
│       │       ├── generate-uid.ts  # UID generator for accessibility IDs
│       │       └── page-load-listener.ts  # Attaches class instances to DOM elements on load
│       ├── components/
│       │   └── presentational/      # Presentational-only Vue components (no API calls)
│       │       ├── atoms/
│       │       │   ├── button/Button.vue       # Button atom (primary/secondary, link/action)
│       │       │   ├── logo/Logo.vue           # Site logo
│       │       │   └── nav-item/NavItem.vue    # Navigation item
│       │       ├── foundation/
│       │       │   ├── icon/Icon.vue           # SVG icon wrapper
│       │       │   └── typography/Typography.vue  # Text with variant/weight/tag props
│       │       └── components/
│       │           ├── event-card/EventCard.vue               # Standard event card
│       │           ├── event-card-full-width/EventCardFullWidth.vue  # Full-width card variant
│       │           ├── featured-event-card/FeaturedEventCard.vue     # Homepage featured card
│       │           ├── header/Header.vue                      # Site header
│       │           └── menu-dropdown/MenuDropdown.vue         # Navigation dropdown
│       ├── styles/                  # SCSS stylesheets
│       ├── assets/                  # Fonts, icons, images
│       └── stories/                 # Storybook stories for all components
│           └── .storybook/          # Storybook config (main.ts, preview.ts)
│
├── events/                          # Core event domain
│   ├── models/
│   │   ├── event.py                 # Event model + EventQuerySet
│   │   ├── organizer.py             # Organizer model
│   │   ├── speaker.py               # Speaker model
│   │   └── social_network_post.py   # SocialNetworkPost model
│   ├── views/
│   │   ├── event_list.py            # EventListView (future), PastEventListView
│   │   ├── event_detail.py          # EventDetailView
│   │   ├── event_create.py          # EventCreateView (login + quota check)
│   │   ├── event_update.py          # EventUpdateView (editor permission)
│   │   ├── organizer_*.py           # Organizer CRUD + autocomplete + suggestions
│   │   └── speaker_*.py             # Speaker CRUD + autocomplete
│   ├── api/
│   │   ├── views.py                 # EventListAPIView, FutureEventListAPIView
│   │   └── serializers.py           # EventSerializer, PlaceSerializer
│   ├── forms/
│   │   ├── event.py                 # EventCreateForm, EventUpdateForm
│   │   ├── organizer.py             # OrganizerForm
│   │   └── speaker.py               # SpeakerForm
│   ├── services/
│   │   └── event_search.py          # search_events() — PostgreSQL full-text search
│   ├── widgets/
│   │   └── datetime.py              # DateTimeWidget for event_date field
│   ├── management/commands/
│   │   ├── generate_random_event_data.py  # Dev data generation
│   │   └── migrate_markdown_to_html.py    # One-off migration utility
│   ├── urls.py                      # Web URL patterns
│   ├── api_urls.py                  # REST API URL patterns
│   ├── templates/                   # Event HTML templates
│   └── tests/                       # Tests: views (CRUD, auth), API, admin
│
├── places/                          # Places and cities
│   ├── models.py                    # Place, City models (PostGIS PointField)
│   ├── views/
│   │   ├── place_*.py               # Place CRUD + autocomplete
│   │   └── city_detail.py           # CityDetailView
│   ├── forms.py                     # PlaceForm (with map widget)
│   ├── widgets/
│   │   └── leaflet.py               # LeafletPointFieldWidget (custom, no third-party map library)
│   ├── urls.py
│   ├── templates/
│   └── tests/
│
├── specials/                        # Named event collections
│   ├── models.py                    # Special model
│   ├── views.py                     # SpecialDetailView, SpecialListView
│   ├── urls.py
│   ├── templates/
│   └── tests/
│
├── dashboard/                       # Superuser-only internal tools
│   ├── mixins.py                    # SuperuserRequiredMixin
│   ├── models/
│   │   └── spreadsheet_sync.py      # SpreadsheetSync model
│   ├── views/
│   │   ├── home.py                  # Dashboard home with statistics
│   │   ├── spreadsheet_sync.py      # SpreadsheetSyncFormView
│   │   ├── filbo.py                 # FilboEventFormView
│   │   ├── places.py                # PlacesListView (places without coordinates)
│   │   ├── social.py                # SocialPostsListView
│   │   └── users.py                 # UsersView
│   ├── services/
│   │   ├── spreadsheet_sync.py      # sync_events() — Google Sheets → Event upsert
│   │   └── filbo.py                 # sync_filbo_events() — FILBo-specific import
│   ├── forms/
│   │   ├── spreadsheet_sync.py      # SpreadsheetSyncForm
│   │   └── filbo.py                 # FilboForm
│   ├── management/commands/
│   │   └── sync_filbo_events.py     # Management command wrapper for FILBo sync
│   ├── templatetags/
│   │   └── dashboard_tags.py        # Dashboard-specific template tags
│   ├── urls.py
│   ├── templates/
│   └── tests/                       # View access tests, spreadsheet sync tests
│
├── users/                           # User profiles and quotas
│   ├── models.py                    # UserSettings, UserEventRelation + post_save signal
│   ├── views.py                     # User profile, created events list
│   ├── urls.py
│   ├── templates/
│   └── tests/
│
├── blog/                            # Blog posts
│   ├── models.py                    # Post model + PostQuerySet
│   ├── views.py                     # PostListView, PostDetailView
│   ├── urls.py
│   ├── templates/
│   └── tests/
│
├── games/                           # "La caza del Snark" book reading game
│   ├── models.py                    # HuntingOfSnarkGame, Criteria, Category
│   ├── services.py                  # get_random_hunting_of_snark_criteria()
│   ├── views.py                     # Game creation, detail views
│   ├── forms.py
│   ├── urls.py
│   ├── templates/
│   └── tests/
│
├── history/                         # Colombian cultural history timeline
│   ├── models.py                    # HistoricalFigure, Event, Post, Group
│   ├── services.py                  # Query helpers for timeline
│   ├── views.py                     # Figure/event/post/group list + detail views
│   ├── urls.py
│   ├── templates/
│   └── tests/
│
├── news/                            # News app (placeholder, no views/urls yet)
│   └── models.py                    # Minimal placeholder
│
├── books/                           # Books app (placeholder, empty)
│   └── __init__.py
│
├── docs/                            # Project documentation (this folder)
│   ├── index.md                     # Main index
│   ├── technology-stack.md          # Tech stack reference
│   ├── data-models.md               # All database models
│   ├── api-contracts.md             # REST API endpoints
│   ├── source-tree.md               # This file
│   ├── project-scan-report.json     # Scan state file
│   ├── tutorials/                   # Step-by-step tutorials
│   ├── how-to-guides/               # Practical guides
│   ├── references/                  # Reference material
│   └── explanations/
│       └── architecture.md          # Architecture decisions
│
├── locale/                          # Django i18n translation files (es)
├── scripts/                         # Utility shell scripts
├── docker-containers/               # Per-service Dockerfiles and run scripts
│   ├── web/
│   ├── frontend/
│   └── db/
│
├── .github/workflows/               # GitHub Actions CI/CD
│   ├── ruff.yml                     # Ruff linting on push/PR
│   ├── codeql-analysis.yml          # CodeQL security scan
│   └── sentry-release.yml           # Sentry release tracking
│
├── .circleci/config.yml             # CircleCI pipeline
├── backstop.config.js               # BackstopJS visual regression testing config
├── mkdocs.yml                       # MkDocs config for docs site (Diataxis)
└── .codacy.yaml                     # Codacy config (excludes test dirs from bandit S101)
```

---

## Key Integration Points

| From | To | Mechanism |
|---|---|---|
| Django templates | Vue components | `data-vue-component` attributes; `mount-vue.ts` discovers and mounts |
| Vue `EventContainer` | DRF API | `fetch()` → `GET /events/api/v1/events/future/` |
| `SpreadsheetSyncFormView` | Google Sheets | `gspread` library + service account credentials |
| `sync_filbo_events` management command | FILBo spreadsheet | Same `gspread` mechanism |
| `EventCreateView` | Email | `send_notification()` → AWS SES |
| `UserSettings` | User creation | `post_save` signal auto-creates settings |
| `Place.location` | PostGIS | `PointField` enables geo queries; map widgets use Leaflet |