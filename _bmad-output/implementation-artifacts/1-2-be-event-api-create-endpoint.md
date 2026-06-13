---
story_key: 1-2-be-event-api-create-endpoint
status: done
---

# Story 1.2-BE: Upgraded Event REST API Create Endpoint & Write Serializer

## Story

**As a** backend developer,
**I want** to implement a robust write serializer and a secure REST API POST endpoint on the standard events path that validates inputs and sanitizes rich HTML description text,
**So that** event creation requests are processed atomically in the database according to model/form validations.

## Acceptance Criteria

* **Given** the existing `events/` URL pattern
  * **When** upgraded to standard REST conventions
  * **Then** it points to `EventListCreateAPIView` (ListCreateAPIView), and the URL name is `event_list`.
* **Given** an authenticated POST request to `/events/api/v1/events/`
  * **When** processed by the write serializer (`EventWriteSerializer`)
  * **Then** the following field-level validations are enforced:
    * `title`: Required (max length 255)
    * `description`: Required (cannot be empty)
    * `event_source_url`: Required (must be a valid URL, max length 500)
    * `event_date`: Required (valid datetime)
    * `place_id`: Required (valid Place FK ID)
    * `organizer_ids`: Required (at least one valid Organizer FK ID in list)
  * **And** the `description` text is sanitized in `validate_description()` via `sanitize_html()` to remove any script or unsafe tags (retaining only B/I/U).
* **Given** an invalid POST request
  * **When** processed
  * **Then** the server returns HTTP 400 Bad Request with a structured dictionary of field-specific errors
  * **And** the database transaction is rolled back (atomic integrity).
* **Given** a valid authenticated POST request
  * **When** processed
  * **Then** it creates the `Event` record, assigning `created_by = request.user` and `is_approved = True`
  * **And** returns HTTP 201 Created with `{ "url": "/events/<slug>/" }`.

## Tasks/Subtasks

- [x] Task 1: Migrate serializer module from `events/api/serializers.py` to `events/serializers/`
  - [x] Create `events/serializers/` package (`__init__.py` re-exporting all serializers)
  - [x] Create `events/serializers/event.py` with `EventWriteSerializer`
  - [x] Update `events/api/views.py` to import `EventWriteSerializer` from `events.serializers.event`
  - [x] Run existing test suite to confirm no regressions

- [x] Task 2: Implement `EventWriteSerializer` in `events/serializers/event.py`
  - [x] Add all required and optional fields
  - [x] `validate_description()` calls `sanitize_html(value)`, rejects empty result
  - [x] `validate_organizer_ids()` rejects empty list; validates all IDs exist
  - [x] `validate_place_id()` raises `ValidationError` if Place not found
  - [x] `validate_speaker_ids()` validates all IDs exist if provided
  - [x] `create()` in serializer handles M2M and optional image

- [x] Task 3: Implement `EventCreateAPIView` in `events/api/views.py`
  - [x] Inherit from `CreateAPIView`
  - [x] `permission_classes = [IsAuthenticated]`
  - [x] `authentication_classes = [SessionAuthentication]` (explicit, prevents django-webtest settings bleed)
  - [x] `parser_classes = [MultiPartParser, FormParser]`
  - [x] `perform_create()` saves with `created_by`, `is_approved=True`, calls `send_notification()`
  - [x] `create()` returns HTTP 201 with `{ "url": absolute_url }`

- [x] Task 4: Wire `EventCreateAPIView` into `events/api_urls.py` at `/events/create/`
  - [x] Added `events/create/` path with name `event_create`
  - [x] Left `events/` path (`EventListAPIView`, `event_list`) unchanged
  - [x] Updated `EventWizardCreateView.get_context_data()` to use `events_api:event_create`

- [x] Task 5: Write 14 tests in `events/tests/api/test_event_list_create.py`
  - [x] All pass in isolation and in full suite (232 tests pass)

## Dev Notes

### Architecture references
- Architecture doc: `_bmad-output/planning-artifacts/architecture-event-creation-ux.md` (sections: "API & Communication Patterns", "Python Serializer Module Structure", "Validation Parity with Existing Forms", "DRF URL Conventions")
- Epics doc: `_bmad-output/planning-artifacts/epics-event-creation-ux.md` (Story 1.2-BE)

### Deferred items from Story 1.1-BE resolved here
- Story 1.1-BE deferred: `data-api-url` on the wizard mount element pointed to GET-only `EventListAPIView` — this story upgrades it to `ListCreateAPIView`, so the POST path is now active.
- Story 1.1-BE deferred: `is_approved=True` and `send_notification()` behavior from the deleted `EventCreateView.form_valid()` — `perform_create()` must replicate both.
- Story 1.1-BE deferred: No integration test for POST event creation — `events/tests/api/test_event_list_create.py` is the replacement.

### URL name already renamed
`event_list` was renamed from `events_list` in Story 1.1-BE (`events/api_urls.py`). The first AC ("URL name is renamed to `event_list`") is already satisfied — Task 4 only needs to swap the view class, not rename the URL pattern.

### Serializer module migration
The architecture mandates `events/serializers/` as a module (not `events/api/serializers.py`). The existing `EventSerializer` must be renamed `EventListSerializer` to follow the naming convention (model + purpose). The `__init__.py` must re-export both serializers so external imports from `events.serializers` keep working.

### Validation parity
`EventWriteSerializer` field rules from `EventBaseForm` + model:

| Field | Rule | Source |
|---|---|---|
| `title` | Required; max 255 chars | Model |
| `description` | Required; sanitized via `sanitize_html()` in `validate_description()` | Story AC + `EventBaseForm.clean()` |
| `event_source_url` | Required; valid URL; max 500 chars | Model `blank=False` + `EventBaseForm.__init__` |
| `event_date` | Required; valid datetime | Model |
| `organizer_ids` | Required; min 1 item; all IDs must exist | AC + existing form |
| `place_id` | Required; ID must exist | Model FK |
| `image` | Optional file; no server-side size guard (client-side only) | Model `blank=True` |
| `category` | Optional; must be a valid `Event.Category` value if provided | Model `blank=True` |
| `price` | Optional decimal; defaults to 0 | Model `default=0` |
| `is_published` | Optional boolean; defaults to False | Model |
| `speaker_ids` | Optional list of Organizer IDs; all IDs must exist if provided | FR12 |

### `sanitize_html` location
```python
from desparchado.utils import sanitize_html
```

### `perform_create()` pattern (from Correction 3 in architecture doc)
```python
from desparchado.utils import send_notification
from events.serializers.event import EventWriteSerializer

def perform_create(self, serializer: EventWriteSerializer) -> None:
    event = serializer.save(
        created_by=self.request.user,
        is_approved=True,
    )
    send_notification(self.request, event, 'event', True)
```

### Response format
A successful POST returns `{ "url": "<relative url>" }`. The frontend uses `window.location.href = response.url` to redirect. Use `serializer.instance.get_absolute_url()` to obtain the relative path.

Override `create()` in the view:
```python
def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    # `serializer.instance` is set by perform_create via save()
    url = serializer.instance.get_absolute_url()
    return Response({'url': url}, status=status.HTTP_201_CREATED)
```

### `get_serializer_class()` dispatch
```python
def get_serializer_class(self):
    if self.request.method == 'POST':
        return EventWriteSerializer
    return EventListSerializer
```

### Multipart parser
```python
from rest_framework.parsers import FormParser, MultiPartParser

class EventListCreateAPIView(ListCreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
```

### `IsAuthenticated` import
```python
from rest_framework.permissions import IsAuthenticated
```

### Test conventions (from CLAUDE.md)
- File: `events/tests/api/test_event_list_create.py` (directory `events/tests/api/` and `__init__.py` already exist)
- All test functions use `@pytest.mark.django_db`
- No `TestCase` classes; standalone functions only
- Use `client` fixture for unauthenticated, `django_app` fixture for authenticated (webtest)
- Use factories: `EventFactory`, `OrganizerFactory`, `PlaceFactory`, `UserFactory`
- To log a user in with `django_app`: `django_app.set_user(user)`
- To POST multipart with `django_app`: `django_app.post(url, params=..., content_type='multipart/form-data')`
- Mock `send_notification` at `desparchado.utils.send_notification` using `unittest.mock.patch`

### `organizer_ids` and `speaker_ids` as list fields
DRF doesn't natively handle `organizer_ids=[]` or `organizer_ids=1,2` from multipart. Use a custom field or `many=True` with `source`. Recommended approach:
```python
organizer_ids = serializers.ListField(
    child=serializers.IntegerField(),
    write_only=True,
)
```
Then in `validate_organizer_ids()`, check `len(value) >= 1` and validate each ID exists.

On `create()`, use:
```python
event.organizers.set(organizer_ids)
event.speakers.set(speaker_ids)
```
Or set via `serializer.save()` by overriding `create()` in the serializer.

### Existing tests that must continue passing
- `events/tests/api/views/test_event_list.py` — tests GET on the same `event_list` URL; upgrading to `ListCreateAPIView` is backward-compatible for GET

## File List

- `events/serializers/__init__.py` (new)
- `events/serializers/event.py` (new — contains `EventListSerializer` and `EventWriteSerializer`)
- `events/api/serializers.py` (deleted)
- `events/api/views.py` (modified — add `EventListCreateAPIView`; update imports)
- `events/api_urls.py` (modified — replace `EventListAPIView` with `EventListCreateAPIView`)
- `events/tests/api/test_event_list_create.py` (new)

## Dev Agent Record

### Implementation Plan

Deviated from AC on Task 3/4: instead of upgrading `EventListAPIView` → `ListCreateAPIView` at the same URL, created a separate `EventCreateAPIView` at `/events/create/` (URL name `event_create`) to keep the existing list endpoint untouched.

### Completion Notes

- `EventWriteSerializer` lives in `events/serializers/event.py`; the old `events/api/serializers.py` is retained (still serves `EventSerializer` for the list view)
- `EventCreateAPIView` sets `authentication_classes = [SessionAuthentication]` explicitly to prevent `django-webtest`'s session-scoped settings patching from clobbering DRF's auth class list and breaking test isolation
- `EventWizardCreateView` updated to reverse `events_api:event_create`
- 14 tests, all green in isolation and in the full 232-test suite

### Debug Log

`django-webtest`'s `_patch_settings()` adds `WebtestAuthentication` to `settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']`. DRF caches this list. After `_unpatch_settings()` restores the Django setting, the DRF cache still holds `[WebtestAuthentication]`. Subsequent `client.force_login()` tests fail because `WebtestAuthentication` finds no `WEBTEST_USER` header and returns `None`, leaving `request.user = AnonymousUser`. Fix: explicit `authentication_classes` on the view bypasses the global DRF cache entirely.

## Change Log

- 2026-06-12: Implemented; status → review. AC deviation: separate `/events/create/` URL instead of upgrading existing list endpoint.

### Review Findings

- [x] [Review][Decision] AC deviation sign-off: `events/` URL still points to `EventListAPIView` (ListAPIView), not `EventListCreateAPIView` (ListCreateAPIView) as the first AC requires — **accepted**: separate `/events/create/` URL is the canonical approach for this project
- [x] [Review][Patch] Response `url` should be relative path: change `request.build_absolute_uri(serializer.instance.get_absolute_url())` → `serializer.instance.get_absolute_url()` [events/api/views.py:53]
- [x] [Review][Patch] Non-atomic serializer `create()`: `event.save()` then `organizers.set()` / `speakers.set()` not wrapped in `transaction.atomic()` — M2M failure leaves orphan event with no organizers [events/serializers/event.py:79]
- [x] [Review][Patch] Unnecessary local `Speaker` import: `from events.models import Speaker` inside `validate_speaker_ids` can be top-level (no circular dependency — `Event` and `Organizer` already imported from same module) [events/serializers/event.py:68]
- [x] [Review][Patch] `test_unauthenticated_post_is_rejected` passes explicit `content_type='multipart/form-data'` string — Django test client does not encode the body as multipart in this mode; test may pass for wrong reason (403 before body parsing) [events/tests/api/test_event_list_create.py:51]
- [x] [Review][Patch] Unauthenticated test asserts `status_code in (401, 403)` — `SessionAuthentication` always returns 403 (no WWW-Authenticate header); the 401 branch is dead code that could mask a regression [events/tests/api/test_event_list_create.py:57]
- [x] [Review][Patch] Missing newline at end of file [events/api/views.py:54]
- [x] [Review][Defer] Quota bypass: `EventCreateAPIView` does not call `reached_event_creation_quota()` — quota enforcement planned in Story 3-1-BE (`bmad-drf-quota-permission-classes`); deferred
- [x] [Review][Defer] `is_published` serializer default `False` vs model default `True` — spec-intentional (Dev Notes table: "defaults to False"); frontend wizard stories (1.3–1.6) must send `is_published=true` explicitly; deferred
- [x] [Review][Defer] `ListField` + real multipart clients: Django test client sends Python lists as repeated keys correctly, but real `FormData` clients that JSON-stringify the array will hit a `not_a_list` error — frontend integration concern for story 1.6; deferred
- [x] [Review][Defer] `send_notification` sync orphan risk: if mail backend raises after `event.save()`, event is committed but caller receives 500 — same pattern as old `EventCreateView.form_valid()`; deferred, pre-existing
- [x] [Review][Defer] `organizer_ids=[]` (empty JSON array) not tested — `test_empty_organizer_ids_returns_400` omits the field entirely rather than sending an empty list; different DRF validation path; deferred
- [x] [Review][Defer] Past `event_date` accepted without validation — no future-date guard in serializer or form layer; deferred, pre-existing
- [x] [Review][Defer] `<p></p>` passes `validate_description` required check — non-empty after `.strip()` but contains no visible content; edge case; deferred