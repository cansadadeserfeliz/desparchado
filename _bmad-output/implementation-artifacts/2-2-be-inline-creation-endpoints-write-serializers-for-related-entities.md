---
story_key: 2-2-be-inline-creation-endpoints-write-serializers-for-related-entities
status: done
---

# Story 2.2-BE: Inline Creation Endpoints & Write Serializers for Related Entities

## Story

**As a** backend developer,
**I want** to create robust REST write serializers and POST creation endpoints for Organizers, Speakers, and Places,
**So that** new entities can be created inline from the event wizard with complete validation parity to the existing Django forms.

## Acceptance Criteria

* **Given** creation endpoints `/events/api/v1/organizers/create/`, `/events/api/v1/speakers/create/`, and `/places/api/v1/places/create/`
  * **When** accessed by an unauthenticated session
  * **Then** they return HTTP 403 Forbidden — consistent with `SessionAuthentication` behavior across all other DRF endpoints in this project (no `WWW-Authenticate` header is sent, so 403 is returned rather than 401).
* **Given** an authenticated POST request to `/events/api/v1/organizers/create/`
  * **When** processed by `OrganizerCreateSerializer`
  * **Then** the following validations are enforced:
    * `name`: Required; max 255 chars; unique across Organizer records
    * `image`: Required (overrides model `blank=True` — matches `OrganizerForm.__init__` behavior)
    * `description`: Optional; run through `sanitize_html()` in `validate_description()` before saving
    * `website_url`: Optional; valid URL format if provided
    * `image_source_url`: Optional; valid URL format if provided
  * **And** on success: HTTP 201 Created is returned with `{"id": <int>, "name": "<str>"}` and `created_by` is set to `request.user`.
* **Given** an authenticated POST request to `/events/api/v1/speakers/create/`
  * **When** processed by `SpeakerCreateSerializer`
  * **Then** the following validations are enforced:
    * `name`: Required; max 255 chars; unique across Speaker records
    * `image`: Required (overrides model `blank=True` — matches `SpeakerForm.__init__` behavior)
    * `description`: Optional; run through `sanitize_html()` in `validate_description()` before saving
    * `image_source_url`: Optional; valid URL format if provided
  * **And** on success: HTTP 201 Created is returned with `{"id": <int>, "name": "<str>"}` and `created_by` is set to `request.user`.
* **Given** an authenticated POST request to `/places/api/v1/places/create/`
  * **When** processed by `PlaceCreateSerializer`
  * **Then** the following validations are enforced:
    * `name`: Required; max 255 chars; min 3 chars; unique across Place records
    * `address`: Required; max 100 chars; min 3 chars
    * `lat`: Required write-only `FloatField` representing latitude
    * `lng`: Required write-only `FloatField` representing longitude
    * `city`: Required FK to `places.City` (ID integer)
    * `image`: Optional
    * `website_url`: Optional; valid URL format if provided
    * `image_source_url`: Optional; valid URL format if provided
  * **And** on success: HTTP 201 Created is returned with `{"id": <int>, "name": "<str>"}`, `location` is set to `Point(lng, lat)`, and `created_by` is set to `request.user`.
* **Given** an invalid POST to any creation endpoint (missing required field, failing validation)
  * **When** processed
  * **Then** the server returns HTTP 400 Bad Request with a structured dict of field-specific errors; no record is created.

## Tasks/Subtasks

- [x] Task 1: Add `OrganizerCreateSerializer` to `events/serializers/organizer.py`
  - [x] Add `OrganizerCreateSerializer(serializers.ModelSerializer)` with fields: `name`, `description`, `image`, `website_url`, `image_source_url`
  - [x] Make `image` required in `__init__`: `self.fields['image'].required = True`
  - [x] Add `validate_description(self, value: str) -> str` calling `sanitize_html(value)`
  - [x] Update `events/serializers/__init__.py` to re-export `OrganizerCreateSerializer`
  - [x] Write unit tests for `OrganizerCreateSerializer` in `events/tests/views/api/test_organizer_create.py` (serializer-level only: missing image → invalid; valid data → valid; description sanitized)

- [x] Task 2: Add `SpeakerCreateSerializer` to `events/serializers/speaker.py`
  - [x] Add `SpeakerCreateSerializer(serializers.ModelSerializer)` with fields: `name`, `description`, `image`, `image_source_url`
  - [x] Make `image` required in `__init__`: `self.fields['image'].required = True`
  - [x] Add `validate_description(self, value: str) -> str` calling `sanitize_html(value)`
  - [x] Update `events/serializers/__init__.py` to re-export `SpeakerCreateSerializer`
  - [x] Write unit tests for `SpeakerCreateSerializer` in `events/tests/views/api/test_speaker_create.py` (serializer-level only: same coverage)

- [x] Task 3: Add `PlaceCreateSerializer` to `places/serializers/place.py`
  - [x] Add `PlaceCreateSerializer(serializers.ModelSerializer)` with model fields: `name`, `address`, `city`, `image`, `website_url`, `image_source_url`; make `city` required in `__init__`: `self.fields['city'].required = True`
  - [x] Add write-only `lat = serializers.FloatField(write_only=True)` and `lng = serializers.FloatField(write_only=True)` to the serializer
  - [x] Override `create(self, validated_data: dict) -> Place`: pop `lat`/`lng`, set `validated_data['location'] = Point(lng, lat)`, call `super().create(validated_data)`
  - [x] Update `places/serializers/__init__.py` to re-export `PlaceCreateSerializer`
  - [x] Write unit tests for `PlaceCreateSerializer` in `places/tests/views/api/test_place_create.py` (serializer-level only: missing lat → invalid; valid data → valid; location Point constructed correctly)

- [x] Task 4: Create `OrganizerCreateAPIView` in `events/views/api/organizer_create.py`
  - [x] Inherit from `CreateAPIView`; `serializer_class = OrganizerCreateSerializer`; `permission_classes = [IsAuthenticated]`; `parser_classes = [MultiPartParser, FormParser]`
  - [x] `perform_create(self, serializer)`: `serializer.save(created_by=self.request.user)`
  - [x] Override `create()` to return HTTP 201 with `{"id": serializer.instance.pk, "name": serializer.instance.name}`
  - [x] Add `@extend_schema` decorator (summary, request, tags, responses)

- [x] Task 5: Create `SpeakerCreateAPIView` in `events/views/api/speaker_create.py`
  - [x] Same structure as `OrganizerCreateAPIView` using `SpeakerCreateSerializer`

- [x] Task 6: Add `PlaceCreateAPIView` to `places/api/views.py`
  - [x] Add `PlaceCreateAPIView(CreateAPIView)` to the existing file
  - [x] `serializer_class = PlaceCreateSerializer`; `permission_classes = [IsAuthenticated]`; `parser_classes = [MultiPartParser, FormParser]`
  - [x] `perform_create(self, serializer)`: `serializer.save(created_by=self.request.user)`
  - [x] Override `create()` to return HTTP 201 with `{"id": serializer.instance.pk, "name": serializer.instance.name}`
  - [x] Add `@extend_schema` decorator

- [x] Task 7: Wire URL patterns
  - [x] Add `path('organizers/create/', OrganizerCreateAPIView.as_view(), name='organizer_create')` to `events/api_urls.py`
  - [x] Add `path('speakers/create/', SpeakerCreateAPIView.as_view(), name='speaker_create')` to `events/api_urls.py`
  - [x] Add `path('places/create/', PlaceCreateAPIView.as_view(), name='place_create')` to `places/api_urls.py`

- [x] Task 8: Write API-level integration tests
  - [x] Expand `events/tests/views/api/test_organizer_create.py` with endpoint tests: unauthenticated → 403; valid multipart POST → 201 with `{id, name}`; missing `name` → 400; missing `image` → 400; `created_by` set correctly
  - [x] Expand `events/tests/views/api/test_speaker_create.py`: same coverage for speakers
  - [x] Expand `places/tests/views/api/test_place_create.py`: unauthenticated → 403; valid POST → 201 with `{id, name}`; missing `lat`/`lng` → 400; `location` is a Point with correct coordinates; missing `address` → 400; missing `city` → 400; `created_by` set correctly

## Dev Notes

### Architecture references
- Architecture doc: `_bmad-output/planning-artifacts/architecture-event-creation-ux.md` (sections: "Validation Parity with Existing Forms", "Python Serializer Module Structure", "DRF URL Conventions")
- Epics doc: `_bmad-output/planning-artifacts/epics-event-creation-ux.md` (Story 2.2-BE)

### What already exists from Story 2.1-BE
The following are already in place — do NOT recreate them:
- `events/serializers/organizer.py` → `OrganizerSearchSerializer`
- `events/serializers/speaker.py` → `SpeakerSearchSerializer`
- `places/serializers/place.py` → `PlaceSearchSerializer`
- `events/views/api/organizer_search.py` → `OrganizerSearchAPIView`
- `events/views/api/speaker_search.py` → `SpeakerSearchAPIView`
- `places/api/views.py` → `PlaceSearchAPIView`
- `events/api_urls.py` has `organizer_search` and `speaker_search` patterns
- `places/api_urls.py` has `place_search` pattern

### 403 vs 401 clarification
The AC in the epics says "HTTP 401 Unauthorized" but `SessionAuthentication` always returns 403 for anonymous users (it does not set `WWW-Authenticate`). The existing `EventCreateAPIView` test confirms this pattern. Tests should assert `status.HTTP_403_FORBIDDEN`.

### Serializer pattern — `OrganizerCreateSerializer`
```python
# events/serializers/organizer.py (add to existing file)
from desparchado.utils import sanitize_html

class OrganizerCreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True

    def validate_description(self, value: str) -> str:
        return sanitize_html(value)

    class Meta:
        model = Organizer
        fields = ['name', 'description', 'image', 'website_url', 'image_source_url']
```

Same pattern applies to `SpeakerCreateSerializer` (fields: `name`, `description`, `image`, `image_source_url`).

### Serializer pattern — `PlaceCreateSerializer`
```python
# places/serializers/place.py (add to existing file)
from django.contrib.gis.geos import Point

class PlaceCreateSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(write_only=True)
    lng = serializers.FloatField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].required = True  # model allows null=True, blank=True; override here

    def create(self, validated_data: dict) -> 'Place':
        lat = validated_data.pop('lat')
        lng = validated_data.pop('lng')
        validated_data['location'] = Point(lng, lat)  # Point(x=lng, y=lat) — PostGIS convention
        return super().create(validated_data)

    class Meta:
        model = Place
        fields = ['name', 'address', 'city', 'image', 'website_url', 'image_source_url', 'lat', 'lng']
```

Note: PostGIS `Point(x, y)` = `Point(longitude, latitude)` — pass `lng` first.

### View pattern — `OrganizerCreateAPIView`
```python
# events/views/api/organizer_create.py (new file)
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from events.serializers.organizer import OrganizerCreateSerializer


@extend_schema(
    summary='Create a new organizer',
    request=OrganizerCreateSerializer,
    responses={status.HTTP_201_CREATED: OpenApiResponse(description='Organizer created. Returns id and name.')},
    tags=['events'],
)
class OrganizerCreateAPIView(CreateAPIView):
    serializer_class = OrganizerCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer: OrganizerCreateSerializer) -> None:
        serializer.save(created_by=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'id': serializer.instance.pk, 'name': serializer.instance.name},
            status=status.HTTP_201_CREATED,
        )
```

Same structure for `SpeakerCreateAPIView` and `PlaceCreateAPIView`.

### URL registration
```python
# events/api_urls.py — add to existing urlpatterns:
from events.views.api.organizer_create import OrganizerCreateAPIView
from events.views.api.speaker_create import SpeakerCreateAPIView

path('organizers/create/', OrganizerCreateAPIView.as_view(), name='organizer_create'),
path('speakers/create/', SpeakerCreateAPIView.as_view(), name='speaker_create'),
```

```python
# places/api_urls.py — add to existing urlpatterns:
from places.api.views import PlaceCreateAPIView

path('places/create/', PlaceCreateAPIView.as_view(), name='place_create'),
```

### Quota enforcement — deferred to Story 3.1-BE
This story does NOT add quota `permission_classes`. Story 3.1-BE adds `OrganizerCreationQuotaPermission`, `SpeakerCreationQuotaPermission`, and `PlaceCreationQuotaPermission` to these views. The architecture doc's permission pattern:
```python
class OrganizerCreationQuotaPermission(BasePermission):
    message = "Hoy alcanzaste el límite de nuevos organizadores."
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS and not request.user.is_superuser:
            return not request.user.settings.reached_organizer_creation_quota()
        return True
```

### `sanitize_html` import
```python
from desparchado.utils import sanitize_html
```

### `Point` import
```python
from django.contrib.gis.geos import Point
```

### Test conventions
- All test functions use `@pytest.mark.django_db`; no `TestCase` classes
- Use `client` fixture for unauthenticated tests; `client.force_login(user)` for authenticated
- Use factories: `OrganizerFactory`, `SpeakerFactory`, `PlaceFactory`, `CityFactory`, `UserFactory`
- For multipart POSTs with image: create an in-memory image using `io.BytesIO` + `PIL.Image` (see `events/tests/views/api/test_event_create.py` for the `_make_image_file()` helper pattern)
- `OrganizerFactory`, `SpeakerFactory` already include `image = factory.django.ImageField()` — do NOT pass `image` in tests that want to test the missing-image 400 scenario; pass `image=None` explicitly or omit it from the payload
- `PlaceFactory` includes `location = FuzzyPoint()` — for `PlaceCreateSerializer` tests, you are testing the API which accepts `lat`/`lng` form fields, not the factory's Point directly
- Test file locations:
  - `events/tests/views/api/test_organizer_create.py` (new)
  - `events/tests/views/api/test_speaker_create.py` (new)
  - `places/tests/views/api/test_place_create.py` (new)

### URL name references for tests
- `reverse('events_api:organizer_create')`
- `reverse('events_api:speaker_create')`
- `reverse('places_api:place_create')`

Note: the `events` app_name in `events/api_urls.py` is `events` but the root URL config registers it as namespace `events_api` — always use `events_api:` prefix in `reverse()` calls.

### `image` required guard — serializer `__init__` vs `Meta`
Model `image = ImageField(blank=True, null=True)` — DRF infers `required=False`. Setting `self.fields['image'].required = True` in `__init__` overrides this at the serializer level (matching the form behavior). This is the same approach used in `OrganizerForm` and `SpeakerForm`.

### `Place.name` MinLengthValidator
`Place.name` has `validators=[MinLengthValidator(5)]` on the model. DRF `ModelSerializer` auto-generates validators from the model field, so the min-length constraint is included automatically — no need to declare it explicitly in the serializer.

### Existing view file `places/api/views.py` currently contains only `PlaceSearchAPIView`
Add `PlaceCreateAPIView` to the same file rather than creating a new file.

## File List

- `events/serializers/organizer.py` (modified — add `OrganizerCreateSerializer`)
- `events/serializers/speaker.py` (modified — add `SpeakerCreateSerializer`)
- `events/serializers/__init__.py` (modified — re-export `OrganizerCreateSerializer`, `SpeakerCreateSerializer`)
- `places/serializers/place.py` (modified — add `PlaceCreateSerializer`)
- `places/serializers/__init__.py` (modified — re-export `PlaceCreateSerializer`)
- `events/views/api/organizer_create.py` (new)
- `events/views/api/speaker_create.py` (new)
- `places/api/views.py` (modified — add `PlaceCreateAPIView`)
- `events/api_urls.py` (modified — add `organizer_create`, `speaker_create` patterns)
- `places/api_urls.py` (modified — add `place_create` pattern)
- `events/tests/views/api/test_organizer_create.py` (new)
- `events/tests/views/api/test_speaker_create.py` (new)
- `places/tests/views/api/test_place_create.py` (new)

## Dev Agent Record

### Implementation Plan

_To be filled in by the implementing agent._

### Completion Notes

All 8 tasks implemented. New files:
- `events/views/api/organizer_create.py` — `OrganizerCreateAPIView`
- `events/views/api/speaker_create.py` — `SpeakerCreateAPIView`
- `events/tests/views/api/test_organizer_create.py` — 8 tests covering auth, 201, created_by, missing fields, XSS sanitization
- `events/tests/views/api/test_speaker_create.py` — same coverage for speakers
- `places/tests/views/api/test_place_create.py` — 9 tests covering auth, 201, created_by, Point construction, all required fields

Modified files:
- `events/serializers/organizer.py` — added `OrganizerCreateSerializer`
- `events/serializers/speaker.py` — added `SpeakerCreateSerializer`
- `events/serializers/__init__.py` — re-exported both new serializers
- `places/serializers/place.py` — added `PlaceCreateSerializer` with `lat`/`lng` write-only fields and `create()` override building `Point(lng, lat)`
- `places/serializers/__init__.py` — populated with `PlaceCreateSerializer` and `PlaceSearchSerializer` exports
- `places/api/views.py` — added `PlaceCreateAPIView`
- `events/api_urls.py` — wired `organizer_create` and `speaker_create` patterns
- `places/api_urls.py` — wired `place_create` pattern

Key design decisions:
- `city` field on `Place` is `null=True, blank=True` in the model; overridden to `required=True` in `PlaceCreateSerializer.__init__` to match intended UX behavior
- `image` fields on `Organizer` and `Speaker` are `blank=True, null=True` in models; similarly overridden to `required=True` to match existing form behavior
- `PlaceCreateSerializer.create()` pops `lat`/`lng` before calling `super().create()` to prevent passing unknown fields to the ORM; constructs `Point(lng, lat)` per PostGIS `Point(x, y)` convention

### Debug Log

_To be filled in by the implementing agent._

### Review Findings

- [x] [Review][Decision] Serializer-level unit tests missing — dismissed; API integration tests accepted as sufficient serializer coverage.
- [x] [Review][Patch] No test for duplicate `name` rejection returning 400 — fixed: added `test_duplicate_name_returns_400` to all three test files
- [x] [Review][Patch] `lat`/`lng` FloatFields accept out-of-range values — fixed: added `min_value=-90.0, max_value=90.0` to `lat` and `min_value=-180.0, max_value=180.0` to `lng` in `PlaceCreateSerializer`
- [x] [Review][Patch] `test_valid_post_sets_created_by` does not assert `response.status_code == 201` before querying DB — fixed: added status assertion in all three test files
- [x] [Review][Patch] `Place.name`/`Place.address` MinLengthValidator untested — fixed: changed validator to `MinLengthValidator(3)` in model; added `test_name_too_short_returns_400` and `test_address_too_short_returns_400`
- [x] [Review][Defer] Quota enforcement not implemented — explicitly deferred to Story 3.1-BE per Dev Notes — deferred, pre-existing
- [x] [Review][Defer] Three view classes share identical `create()` override — copy-pasted pattern; premature abstraction per project conventions; Story 3.1-BE will add per-entity quota classes that differentiate them — deferred, pre-existing
- [x] [Review][Defer] `sanitize_html()` returning empty string for `description` is untested — model accepts `''` as default; acceptable behavior — deferred, pre-existing
- [x] [Review][Defer] `UserSettings` may not exist for legacy users — `RelatedObjectDoesNotExist` risk if quota is ever accessed via `request.user.settings`; pre-existing architectural concern — deferred, pre-existing

## Change Log

- 2026-06-23: Story spec created; status → ready-for-dev
- 2026-06-23: Updated creation endpoints to use `/create/` suffix, matching `events/create/` pattern
- 2026-06-23: Code review complete; 1 decision-needed, 4 patches, 4 deferred, 5 dismissed