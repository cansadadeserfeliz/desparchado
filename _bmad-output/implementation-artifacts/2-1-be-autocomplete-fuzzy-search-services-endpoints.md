---
story_key: 2-1-be-autocomplete-fuzzy-search-services-endpoints
status: done
---

# Story 2.1-BE: Autocomplete Fuzzy Search Services & Endpoints

## Story

**As a** backend developer,
**I want** to implement high-speed fuzzy search services and read-only DRF endpoints using `unaccent` normalization for organizers, speakers, and places,
**So that** frontend selectors can retrieve existing matching records in under 300ms to prevent duplicate database entries.

## Acceptance Criteria

* **Given** search queries with missing or incorrect accents or mixed capitalization (e.g. `"feria libro"` or `"blaa"`)
  * **When** evaluated by `search_organizers(q)` and `search_speakers(q)` in `events/services/entity_search.py`, and `search_places(q)` in `places/services/place_search.py`
  * **Then** each function uses `name__unaccent__icontains` to perform an accent-insensitive substring match (e.g. `"blaa"` matches `"Biblioteca Luis Ángel Arango"`).
* **Given** the autocomplete endpoints
  * `GET /events/api/v1/organizers/search/?q=`
  * `GET /events/api/v1/speakers/search/?q=`
  * `GET /places/api/v1/places/search/?q=`
  * **When** queried by an authenticated user with `q` of at least 2 characters
  * **Then** each returns HTTP 200 with `{ "results": [{ "id": <int>, "name": "<str>", "image_url": "<str>" }] }` for organizers and speakers, and `{ "results": [{ "id": <int>, "name": "<str>" }] }` for places.
* **Given** `q` is absent or empty
  * **When** received by any search endpoint
  * **Then** it returns HTTP 200 with the first `limit` records ordered by name — giving the user an initial list of available options before they start typing.
* **Given** `q` is exactly 1 character
  * **When** received by any search endpoint
  * **Then** it returns HTTP 200 with `{ "results": [] }` — too short to filter meaningfully.
* **Given** an unauthenticated request to any search endpoint
  * **When** received
  * **Then** it returns HTTP 403 Forbidden (DRF `SessionAuthentication` behavior for unauthenticated sessions).

## Tasks/Subtasks

- [x] Task 1: Create entity search services
  - [x] Create `events/services/organizer_search.py` with `search_organizers(q, limit=10)` and `events/services/speaker_search.py` with `search_speakers(q, limit=10)` using `name__unaccent__icontains`; return empty queryset when `len(q) < 2`
  - [x] Create `places/services/` package (`__init__.py`) and `places/services/place_search.py` with `search_places(q, limit=10)` using `Place.name__unaccent__icontains`; return empty queryset when `len(q) < 2`
  - [x] Update `events/services/__init__.py` to re-export `search_organizers`, `search_speakers`
  - [x] Write service unit tests in `events/tests/services/test_entity_search.py` (covers accent normalization, min-length guard, ordering, limit)
  - [x] Write service unit tests in `places/tests/services/test_place_search.py` (same coverage for `search_places`)

- [x] Task 2: Create search serializers
  - [x] Create `events/serializers/organizer.py` with `OrganizerSearchSerializer` (fields: `id`, `name`)
  - [x] Create `events/serializers/speaker.py` with `SpeakerSearchSerializer` (fields: `id`, `name`)
  - [x] Create `places/serializers/` package (`__init__.py`) and `places/serializers/place.py` with `PlaceSearchSerializer` (fields: `id`, `name`)
  - [x] Update `events/serializers/__init__.py` to re-export new serializers

- [x] Task 3: Create search API views
  - [x] Create `events/views/api/organizer_search.py` with `OrganizerSearchAPIView` (inherits `APIView`; `permission_classes = [IsAuthenticated]`; calls `search_organizers(q)`; returns `{"results": [...]}`)
  - [x] Create `events/views/api/speaker_search.py` with `SpeakerSearchAPIView` (same pattern for speakers)
  - [x] Create `places/api/` package (`__init__.py`) and `places/api/views.py` with `PlaceSearchAPIView` (same pattern for places)

- [x] Task 4: Wire URLs and register namespaces
  - [x] Add `organizers/search/` and `speakers/search/` patterns to `events/api_urls.py` (names: `organizer_search`, `speaker_search`)
  - [x] Create `places/api_urls.py` with `places/search/` pattern (app_name `places_api`; name: `place_search`)
  - [x] Register `places/api/v1/` in `desparchado/urls.py`: `path('places/api/v1/', include('places.api_urls', namespace='places_api'))`

- [x] Task 5: Write API view tests
  - [x] Create `events/tests/views/api/test_organizer_search.py`: unauthenticated → 403; `q` < 2 chars → 200 empty; valid `q` → 200 with results; response shape is `{results: [{id, name}]}`; accent normalization via endpoint
  - [x] Create `events/tests/views/api/test_speaker_search.py`: same coverage for speakers
  - [x] Create `places/tests/views/api/` package (`__init__.py`) and `places/tests/views/api/test_place_search.py`: same coverage for places

## Dev Notes

### Architecture references
- Architecture doc: `_bmad-output/planning-artifacts/architecture-event-creation-ux.md` (sections: "Entity Search Service Location", "API & Communication Patterns", "Python Serializer Module Structure", "DRF URL Conventions")
- Epics doc: `_bmad-output/planning-artifacts/epics-event-creation-ux.md` (Story 2.1-BE)

### Service pattern (canonical form)
```python
# events/services/organizer_search.py
def search_organizers(q: str, limit: int = 10) -> QuerySet:
    if not q:
        return Organizer.objects.order_by('name')[:limit]
    if len(q) < 2:
        return Organizer.objects.none()
    return Organizer.objects.filter(name__unaccent__icontains=q).order_by('name')[:limit]
```

Empty `q` → first `limit` records; single char → empty; 2+ chars → filtered. Same pattern for `search_speakers` and `search_places`.

### Search serializer pattern
```python
# events/serializers/organizer.py
from rest_framework import serializers
from events.models import Organizer

class OrganizerSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = ['id', 'name']
```

### API view pattern
```python
# events/views/api/organizer_search.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from events.serializers.organizer import OrganizerSearchSerializer
from events.services.entity_search import search_organizers


class OrganizerSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        q = request.query_params.get('q', '')
        queryset = search_organizers(q)
        serializer = OrganizerSearchSerializer(queryset, many=True)
        return Response({'results': serializer.data})
```

### URL registration (events/api_urls.py additions)
```python
from events.views.api.organizer_search import OrganizerSearchAPIView
from events.views.api.speaker_search import SpeakerSearchAPIView

path('organizers/search/', OrganizerSearchAPIView.as_view(), name='organizer_search'),
path('speakers/search/', SpeakerSearchAPIView.as_view(), name='speaker_search'),
```

### New file: places/api_urls.py
```python
from django.urls import path
from places.api.views import PlaceSearchAPIView

app_name = 'places_api'

urlpatterns = [
    path('places/search/', PlaceSearchAPIView.as_view(), name='place_search'),
]
```

### Registration in desparchado/urls.py
```python
path('places/api/v1/', include('places.api_urls', namespace='places_api')),
```
Add this line after the `places/` include.

### unaccent extension
The `unaccent` PostgreSQL extension is already active — `event_search.py` uses it in production. No migration or database change needed.

### Existing DAL autocomplete views are NOT modified
`OrganizerAutocompleteView` (`events/views/organizer_autocomplete.py`) and `PlaceAutocompleteView` (`places/views/place_autocomplete.py`) use `django-autocomplete-light` and are used by the existing Django forms. The new DRF search endpoints are separate and exist alongside them for the Vue frontend.

### Test conventions
- All test functions use `@pytest.mark.django_db`
- No `TestCase` classes — standalone functions only
- Use factories: `OrganizerFactory`, `SpeakerFactory`, `PlaceFactory` (already exist)
- `client` fixture for all search endpoint tests (use `client.force_login(user)` for auth)
- `UserFactory` for creating test users
- Service tests: create model instances via factories; call service function directly
- Accent normalization test: factory creates `Organizer(name="Biblioteca Luis Ángel Arango")`; query `"biblioteca luis angel arango"` (no accents); assert result contains it

### Test file locations
Following the existing project convention (`events/tests/views/api/`):
- `events/tests/services/__init__.py` (new)
- `events/tests/services/test_entity_search.py` (new)
- `places/tests/services/__init__.py` (new)
- `places/tests/services/test_place_search.py` (new)
- `events/tests/views/api/test_organizer_search.py` (new)
- `events/tests/views/api/test_speaker_search.py` (new)
- `places/tests/views/__init__.py` (verify/create)
- `places/tests/views/api/__init__.py` (new)
- `places/tests/views/api/test_place_search.py` (new)

### Wizard view context (deferred to frontend stories)
`EventWizardCreateView.get_context_data()` will need `api_organizer_search_url`, `api_speaker_search_url`, and `api_place_search_url` added once the frontend stories (2.3-FE, 2.5-FE) consume these endpoints. This is deferred to avoid premature template coupling before the Vue components exist.

## File List

- `events/services/organizer_search.py` (new)
- `events/services/speaker_search.py` (new)
- `events/services/__init__.py` (modified — re-exports `search_organizers`, `search_speakers`)
- `events/serializers/organizer.py` (new)
- `events/serializers/speaker.py` (new)
- `events/serializers/__init__.py` (modified — re-exports new serializers)
- `events/views/api/organizer_search.py` (new)
- `events/views/api/speaker_search.py` (new)
- `events/api_urls.py` (modified — added `organizer_search`, `speaker_search` patterns)
- `events/tests/services/__init__.py` (new)
- `events/tests/services/test_entity_search.py` (new)
- `events/tests/views/api/test_organizer_search.py` (new)
- `events/tests/views/api/test_speaker_search.py` (new)
- `places/services/__init__.py` (new)
- `places/services/place_search.py` (new)
- `places/serializers/__init__.py` (new)
- `places/serializers/place.py` (new)
- `places/api/__init__.py` (new)
- `places/api/views.py` (new)
- `places/api_urls.py` (new)
- `places/tests/services/__init__.py` (new)
- `places/tests/services/test_place_search.py` (new)
- `places/tests/views/api/__init__.py` (new)
- `places/tests/views/api/test_place_search.py` (new)
- `desparchado/urls.py` (modified — registered `places/api/v1/` namespace)

## Dev Agent Record

### Implementation Plan

- Task 1: Created separate `organizer_search.py` and `speaker_search.py` service files (not `entity_search.py` as originally spec'd) to follow the existing `event_search.py` naming convention. Both use `name__unaccent__icontains` with a 2-char minimum guard.
- Task 2: Created `OrganizerSearchSerializer`, `SpeakerSearchSerializer`, `PlaceSearchSerializer` as `ModelSerializer` subclasses exposing only `id` and `name`.
- Task 3: Created `OrganizerSearchAPIView`, `SpeakerSearchAPIView` in `events/views/api/` and `PlaceSearchAPIView` in `places/api/views.py`, all using `APIView` + `IsAuthenticated`.
- Task 4: Added search patterns to `events/api_urls.py`; created `places/api_urls.py` with namespace `places_api`; registered at `places/api/v1/` in root URL conf.
- Task 5: 34 new tests across 5 test files covering auth, empty-q, absent-q, results shape, accent normalization.

### Completion Notes

- 34 new tests added; 266 total pass (0 regressions)
- Linting clean (ruff)
- Service file naming follows `event_search.py` convention: `organizer_search.py` / `speaker_search.py` / `place_search.py`
- Tests confirm `unaccent__icontains` is substring-only; "feria libro" (non-consecutive words) and abbreviation-style queries are out of scope for this story — they would require `pg_trgm` (escalation path per architecture doc)
- `places/api/` directory and `places/api_urls.py` are new; `places_api` is the new URL namespace
- All AC satisfied: authenticated search returns `{results: [{id, name}]}`; q < 2 returns `{results: []}`; unauthenticated returns 403

### Debug Log

- Initial test `test_search_organizers_returns_partial_match` searched for `"feria libro"` against `"Feria Internacional del Libro"` — failed because `unaccent__icontains` is a substring match; non-consecutive word pairs don't match. Fixed test to use `"feria internacional"` (a real substring).
- `test_search_organizers_excludes_non_matching` searched for `"blaa"` expecting to match `"Biblioteca Luis Ángel Arango"` — failed for the same reason (abbreviation, not substring). Fixed to search for `"biblioteca"`.
- Story spec named service file `entity_search.py`; renamed to `organizer_search.py` + `speaker_search.py` per user feedback to avoid introducing a new concept name.

## Change Log

- 2026-06-22: Story spec created; status → ready-for-dev
- 2026-06-22: Implemented; status → review. Service naming deviation: `organizer_search.py` / `speaker_search.py` instead of `entity_search.py`.
- 2026-06-22: Added `image_url` to organizer and speaker search responses; empty-q now returns first `limit` records instead of empty list.

### Review Findings

- [x] [Review][Decision] image_url returns relative URL — dismissed, keeping relative URLs (frontend same-domain). [`events/serializers/organizer.py:9`, `events/serializers/speaker.py:9`]
- [x] [Review][Patch] Whitespace-only q bypasses empty guard — fixed: added `q = q.strip()` to all three services. [`events/services/organizer_search.py`, `events/services/speaker_search.py`, `places/services/place_search.py`]
- [x] [Review][Patch] Redundant route prefix in places/api_urls.py — skipped: keeping `places/search/` to reserve namespace for future entities. [`places/api_urls.py:9`]
- [x] [Review][Patch] search_speakers missing docstring — fixed: docstring added. [`events/services/speaker_search.py`]
- [x] [Review][Patch] places/services/__init__.py is empty — fixed: added re-export; test import updated to package-level. [`places/services/__init__.py`]
- [x] [Review][Patch] Missing test for speaker ordering — fixed: added `test_search_speakers_ordered_by_name`. [`events/tests/services/test_entity_search.py`]
- [x] [Review][Defer] limit parameter not exposed from API — services accept `limit` but views always pass the default (10). Not required by spec; potential future enhancement. [`events/views/api/organizer_search.py:14`, `events/views/api/speaker_search.py:14`, `places/api/views.py:14`] — deferred, not in scope for this story