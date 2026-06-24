---
story_key: 3-1-be-drf-quota-permission-classes
status: done
---

# Story 3.1-BE: DRF Quota Permission Classes (DRY Integration)

## Story

**As a** backend developer,
**I want** to implement lightweight DRF custom permission classes that utilize the existing `UserSettings` model quota checks,
**So that** new REST write endpoints enforce the same daily limits as traditional forms with zero code duplication.

## Acceptance Criteria

* **Given** creation endpoints `/events/api/v1/events/create/`, `/events/api/v1/organizers/create/`, `/events/api/v1/speakers/create/`, and `/places/api/v1/places/create/`
  * **When** queried with write mutations (`POST`)
  * **Then** they enforce their respective lightweight permission classes: `EventCreationQuotaPermission`, `OrganizerCreationQuotaPermission`, `SpeakerCreationQuotaPermission` in `events/permissions.py`, and `PlaceCreationQuotaPermission` in `places/permissions.py`.
  * **And** these permissions delegate entirely to the corresponding pre-existing model method on `request.user.settings` (e.g. `reached_organizer_creation_quota()`), relying on its built-in superuser bypass — no duplicated `is_superuser` check in the permission class itself.
* **Given** a user has reached their daily limit
  * **When** attempting to `POST` to a quota-restricted endpoint
  * **Then** the permission class returns HTTP 403 Forbidden with the Spanish error message in `{"detail": "..."}` (see message constants in Dev Notes).
* **Given** a superuser attempts to `POST` to a quota-restricted endpoint
  * **When** their `UserSettings` quota limit would otherwise be exceeded
  * **Then** the request is allowed through (HTTP 201) — the superuser bypass inside `reached_*_quota()` returns `False`, so the permission grants access.
* **Given** an authenticated, non-superuser user is within their daily limit
  * **When** they `POST` to a quota-restricted endpoint
  * **Then** the request proceeds normally (quota permission returns `True`).
* **Given** an authenticated user who has reached their daily event creation quota
  * **When** they request `GET /events/add/` (the HTML wizard page)
  * **Then** `EventWizardCreateView.dispatch()` raises `PermissionDenied` before the template renders
  * **And** the server returns HTTP 403 rendering `desparchado/templates/403.html`
  * **And** the response body contains the exact quota message (`QUOTA_EXCEEDED_MESSAGE`) — rendered by the `{% if exception %}<p>{{ exception }}</p>{% endif %}` block in `403.html` — so the user understands why access was denied, not just that it was denied.
  * **And** the wizard template is never loaded.
  * **Note:** This behavior is already implemented in `events/views/event_wizard_create.py` (Story 1.1-BE) and covered by `test_quota_exceeded_returns_403` in `events/tests/views/test_event_wizard.py` (asserts both `QUOTA_EXCEEDED_MESSAGE in response.text` and that `403.html` was used). The implementing agent must confirm this test still passes; no new implementation is required for this AC.

## Tasks/Subtasks

- [x] Task 1: Create `events/permissions.py` with three quota permission classes
  - [x] Add `EventCreationQuotaPermission(BasePermission)`: `message = "Hoy alcanzaste el límite de eventos que puedes crear. Vuelve mañana para continuar publicando."` — `has_permission` returns `True` for `SAFE_METHODS`; otherwise returns `not request.user.settings.reached_event_creation_quota()`
  - [x] Add `OrganizerCreationQuotaPermission(BasePermission)`: `message = "Hoy alcanzaste el límite de nuevos organizadores."` — same pattern
  - [x] Add `SpeakerCreationQuotaPermission(BasePermission)`: `message = "Hoy alcanzaste el límite de nuevos presentadores."` — same pattern

- [x] Task 2: Create `places/permissions.py` with one quota permission class
  - [x] Add `PlaceCreationQuotaPermission(BasePermission)`: `message = "Hoy alcanzaste el límite de nuevos lugares."` — same pattern calling `reached_place_creation_quota()`

- [x] Task 3: Wire quota permissions into existing create views
  - [x] `events/views/api/event_create.py` — add `EventCreationQuotaPermission` to `permission_classes = [IsAuthenticated, EventCreationQuotaPermission]`
  - [x] `events/views/api/organizer_create.py` — add `OrganizerCreationQuotaPermission` to `permission_classes`
  - [x] `events/views/api/speaker_create.py` — add `SpeakerCreationQuotaPermission` to `permission_classes`
  - [x] `places/api/views.py` — add `PlaceCreationQuotaPermission` to `PlaceCreateAPIView.permission_classes`

- [x] Task 4: Write unit tests for the permission classes in `events/tests/test_permissions.py`
  - [x] `test_event_quota_permission_blocks_user_at_limit` — set `user.settings.event_creation_quota = 0`, assert `has_permission` returns `False`
  - [x] `test_event_quota_permission_allows_user_under_limit` — default settings, assert `has_permission` returns `True`
  - [x] `test_event_quota_permission_allows_superuser_at_limit` — set quota to 0, `user.is_superuser = True`, assert `has_permission` returns `True`
  - [x] `test_event_quota_permission_allows_safe_methods` — assert GET/HEAD/OPTIONS return `True` regardless of quota
  - [x] Repeat the three non-safe-method cases for `OrganizerCreationQuotaPermission`, `SpeakerCreationQuotaPermission`, and `PlaceCreationQuotaPermission` (12 additional tests)

- [x] Task 5: Add quota integration tests to existing endpoint test files
  - [x] `events/tests/views/api/test_event_create.py` — add `test_quota_exceeded_returns_403` (set quota to 0, POST → 403 + check `detail` key) and `test_superuser_bypasses_quota` (superuser + quota 0 → 201)
  - [x] `events/tests/views/api/test_organizer_create.py` — same two tests
  - [x] `events/tests/views/api/test_speaker_create.py` — same two tests
  - [x] `places/tests/views/api/test_place_create.py` — same two tests

## Dev Notes

### Architecture references
- Architecture doc: `_bmad-output/planning-artifacts/architecture-event-creation-ux.md` (section "Authentication & Security → DRF permission classes — one per entity type")
- Epics doc: `_bmad-output/planning-artifacts/epics-event-creation-ux.md` (Story 3.1-BE)
- Deferred work doc: `_bmad-output/implementation-artifacts/deferred-work.md` (section "Deferred from: code review of 2-2-be…")

### URL correction vs. epics spec
The epics doc lists endpoint URLs without the `/create/` suffix (e.g. `/events/api/v1/organizers/`). Story 2.2-BE was implemented with a `/create/` suffix to match the existing `events/create/` web-view pattern. The actual URL names in effect are:
- `events_api:event_create` → `POST /events/api/v1/events/create/`
- `events_api:organizer_create` → `POST /events/api/v1/organizers/create/`
- `events_api:speaker_create` → `POST /events/api/v1/speakers/create/`
- `places_api:place_create` → `POST /places/api/v1/places/create/`

### Permission class pattern
```python
# events/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class OrganizerCreationQuotaPermission(BasePermission):
    message = "Hoy alcanzaste el límite de nuevos organizadores."

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return not request.user.settings.reached_organizer_creation_quota()
```

`reached_organizer_creation_quota()` already returns `False` for superusers (built-in bypass), so no additional `is_superuser` check is needed in the permission class. This satisfies the AC requirement of zero duplicated checks.

### Spanish error messages (exact strings)
| Permission class | `message` attribute |
|---|---|
| `EventCreationQuotaPermission` | `"Hoy alcanzaste el límite de eventos que puedes crear. Vuelve mañana para continuar publicando."` |
| `OrganizerCreationQuotaPermission` | `"Hoy alcanzaste el límite de nuevos organizadores."` |
| `SpeakerCreationQuotaPermission` | `"Hoy alcanzaste el límite de nuevos presentadores."` |
| `PlaceCreationQuotaPermission` | `"Hoy alcanzaste el límite de nuevos lugares."` |

The `message` attribute on `BasePermission` becomes the `detail` field in the DRF 403 response body: `{"detail": "<message>"}`.

### Simulating quota exhaustion in tests
`UserSettings` is auto-created via signal when `UserFactory()` is called. To simulate an exhausted quota without creating actual entities:

```python
user = UserFactory()
user.settings.organizer_creation_quota = 0
user.settings.save()
# reached_organizer_creation_quota() → count(0) >= quota(0) → True
```

Setting the quota limit to `0` immediately exhausts it without needing to create any organizers.

### Permission class unit test pattern
Unit tests in `events/tests/test_permissions.py` test `has_permission()` directly without going through the full DRF view pipeline. Use `APIRequestFactory` and build a fake POST request:

```python
from rest_framework.test import APIRequestFactory
from events.permissions import OrganizerCreationQuotaPermission
from users.tests.factories import UserFactory

def test_organizer_quota_permission_blocks_user_at_limit():
    factory = APIRequestFactory()
    request = factory.post('/')
    user = UserFactory()
    user.settings.organizer_creation_quota = 0
    user.settings.save()
    request.user = user
    permission = OrganizerCreationQuotaPermission()
    assert permission.has_permission(request, None) is False
```

### `UserSettings.reached_*_quota()` method names
The four existing methods on `UserSettings` (confirmed in `users/models.py`):
- `reached_event_creation_quota()` — used by `EventCreationQuotaPermission`
- `reached_organizer_creation_quota()` — used by `OrganizerCreationQuotaPermission`
- `reached_speaker_creation_quota()` — used by `SpeakerCreationQuotaPermission`
- `reached_place_creation_quota()` — used by `PlaceCreationQuotaPermission`

### HTML view quota check — already implemented and tested
`EventWizardCreateView.dispatch()` in `events/views/event_wizard_create.py` already enforces the event quota before the wizard template renders. The test `test_quota_exceeded_returns_403` in `events/tests/views/test_event_wizard.py` covers this path (sets `user.settings.event_creation_quota = 0`, asserts 403 and `QUOTA_EXCEEDED_MESSAGE` in response). The implementing agent should run the full test suite to confirm this test still passes after the 3.1-BE changes — no new code is needed here.

### Pre-existing `UserSettings` risk (do not guard)
`request.user.settings` raises `RelatedObjectDoesNotExist` for users created before the auto-create signal was added. This is a pre-existing architectural concern noted in the deferred work doc. The existing `EventWizardCreateView` does not guard against it either. Do NOT add a guard in the permission classes — follow the same pattern as the existing view code.

### `IsAuthenticated` ordering
Place `IsAuthenticated` before the quota permission in the `permission_classes` list so unauthenticated requests short-circuit at 403 before `request.user.settings` is ever accessed:
```python
permission_classes = [IsAuthenticated, EventCreationQuotaPermission]
```

### Test conventions
- All test functions use `@pytest.mark.django_db`; no `TestCase` classes
- Use `client` fixture for endpoint integration tests; `client.force_login(user)` for authenticated requests
- Use `UserFactory()` (auto-creates `UserSettings` via signal)
- Integration tests that hit quota: set `user.settings.<entity>_creation_quota = 0` + `user.settings.save()` before the POST

### Existing files that will be modified
- `events/views/api/event_create.py` — only `permission_classes` list changes
- `events/views/api/organizer_create.py` — only `permission_classes` list changes
- `events/views/api/speaker_create.py` — only `permission_classes` list changes
- `places/api/views.py` — only `PlaceCreateAPIView.permission_classes` list changes
- `events/tests/views/api/test_event_create.py` — add 2 quota tests
- `events/tests/views/api/test_organizer_create.py` — add 2 quota tests
- `events/tests/views/api/test_speaker_create.py` — add 2 quota tests
- `places/tests/views/api/test_place_create.py` — add 2 quota tests

## File List

- `events/permissions.py` (new)
- `places/permissions.py` (new)
- `events/views/api/event_create.py` (modified — add quota permission)
- `events/views/api/organizer_create.py` (modified — add quota permission)
- `events/views/api/speaker_create.py` (modified — add quota permission)
- `places/api/views.py` (modified — add quota permission to `PlaceCreateAPIView`)
- `events/tests/test_permissions.py` (new)
- `events/tests/views/api/test_event_create.py` (modified — add quota tests)
- `events/tests/views/api/test_organizer_create.py` (modified — add quota tests)
- `events/tests/views/api/test_speaker_create.py` (modified — add quota tests)
- `places/tests/views/api/test_place_create.py` (modified — add quota tests)

## Dev Agent Record

### Implementation Plan

_To be filled in by the implementing agent._

### Completion Notes

All 5 tasks implemented. New files:
- `events/permissions.py` — `EventCreationQuotaPermission`, `OrganizerCreationQuotaPermission`, `SpeakerCreationQuotaPermission`
- `places/permissions.py` — `PlaceCreationQuotaPermission`
- `events/tests/test_permissions.py` — 13 unit tests covering block/allow/superuser-bypass for all 4 permission classes + safe-methods pass-through for event quota

Modified files:
- `events/views/api/event_create.py` — `permission_classes` extended with `EventCreationQuotaPermission`
- `events/views/api/organizer_create.py` — extended with `OrganizerCreationQuotaPermission`
- `events/views/api/speaker_create.py` — extended with `SpeakerCreationQuotaPermission`
- `places/api/views.py` — `PlaceCreateAPIView.permission_classes` extended with `PlaceCreationQuotaPermission`
- `events/tests/views/api/test_event_create.py` — 2 quota integration tests added
- `events/tests/views/api/test_organizer_create.py` — 2 quota integration tests added
- `events/tests/views/api/test_speaker_create.py` — 2 quota integration tests added
- `places/tests/views/api/test_place_create.py` — 2 quota integration tests added

Key design decisions:
- Permission classes delegate entirely to `UserSettings.reached_*_quota()` which carries the superuser bypass internally — no `is_superuser` check duplicated in the permission layer
- `IsAuthenticated` placed first in every `permission_classes` list so anonymous requests short-circuit before `request.user.settings` is accessed
- HTML view quota enforcement (Story 1.1-BE) confirmed still passing: `test_quota_exceeded_returns_403` in `events/tests/views/test_event_wizard.py` passes with no changes required
- Full suite: 323 passed, 0 failures

### Debug Log

_To be filled in by the implementing agent._

## Review Findings

- [x] [Review][Patch] Missing safe-method (GET) tests for Organizer, Speaker, Place permission classes [`events/tests/test_permissions.py`] — fixed: added `test_organizer/speaker/place_quota_permission_allows_safe_methods`
- [x] [Review][Patch] Integration tests assert `'detail' in response` but never verify the Spanish error message content [`events/tests/views/api/test_event_create.py`, `test_organizer_create.py`, `test_speaker_create.py`, `places/tests/views/api/test_place_create.py`] — fixed: assertions now check exact Spanish message string
- [x] [Review][Patch] Missing newline at EOF in both new permission files [`events/permissions.py`, `places/permissions.py`] — fixed: trailing newlines added (auto-fixed by linter)
- [x] [Review][Defer] `RelatedObjectDoesNotExist` when UserSettings row is missing [`events/permissions.py:15`, `places/permissions.py:10`] — deferred, pre-existing; spec explicitly says do not guard (same pattern as EventWizardCreateView)
- [x] [Review][Defer] Race condition: quota check and `perform_create` are non-atomic [`events/permissions.py`, `places/api/views.py`] — deferred, pre-existing; no atomic enforcement anywhere in the project's quota system
- [x] [Review][Defer] `quota_period_seconds = 0` silently bypasses quota enforcement [`users/models.py`] — deferred, pre-existing issue in UserSettings model unrelated to this story
- [x] [Review][Defer] No boundary test at `count == quota` (all tests use `quota=0`) [`events/tests/test_permissions.py`] — deferred, pre-existing gap in UserSettings model test coverage
- [x] [Review][Defer] Superuser bypass in `reached_*_quota()` untested in isolation [`users/models.py`] — deferred, pre-existing gap in model-level test coverage

## Change Log

- 2026-06-23: Story spec created; status → ready-for-dev
- 2026-06-23: Implementation complete; status → review
- 2026-06-24: Code review complete; 3 patches applied, 5 deferred; status → done
