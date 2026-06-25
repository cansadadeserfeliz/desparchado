---
story_key: 4-1-be-django-edit-view-permission-gate
status: done
---

# Story 4.1-BE: Django Edit View Permission Gate & Custom 403 Template

## Story

**As a** backend developer,
**I want** to implement a secure, view-level permission gate for the edit path that intercepts unauthorized requests at the server level,
**So that** only authorized editors can load the template, and unauthorized users see a clear, custom 403 page.

## Acceptance Criteria

* **Given** an unauthenticated request to `/events/<slug>/edit/`
  * **When** processed by `EventWizardUpdateView`
  * **Then** the request is redirected to the login page with `?next=/events/<slug>/edit/`.
* **Given** an authenticated user who is **not** the creator, a listed editor, or a superuser for that event
  * **When** requesting `/events/<slug>/edit/`
  * **Then** the view raises `UserFacingPermissionDenied("No tienes permiso para editar este evento.")`
  * **And** the server returns an HTTP 403 response rendering `desparchado/templates/403.html`
  * **And** the response body contains "No tienes permiso para editar este evento." (the custom 403 handler surfaces the message because the exception is `UserFacingPermissionDenied`).
* **Given** a slug that does not match any event
  * **When** requesting `/events/<slug>/edit/`
  * **Then** the server returns HTTP 404.
* **Given** an authorized editor (creator, listed editor, or superuser) requests `/events/<slug>/edit/`
  * **When** processed
  * **Then** the view returns HTTP 200 and renders `events/templates/events/event_wizard.html`
  * **And** the response HTML contains a mount element with `data-vue-component="event-wizard"`, `data-wizard-mode="edit"`, `data-csrf`, and `data-api-url` set to `/events/api/v1/events/<slug>/`.

## Tasks/Subtasks

- [x] Task 1: Update `event_wizard.html` template to make `wizard_mode` dynamic
  - [x] Replace the hardcoded `data-wizard-mode="create"` attribute with `data-wizard-mode="{{ wizard_mode }}"`
  - [x] Add `context['wizard_mode'] = 'create'` to `EventWizardCreateView.get_context_data()`
  - [x] Confirm all existing wizard create tests still pass after this change

- [x] Task 2: Create `events/views/event_wizard_update.py`
  - [x] Define `EDIT_DENIED_MESSAGE = 'No tienes permiso para editar este evento.'` as module-level constant
  - [x] Implement `EventWizardUpdateView(EditorPermissionRequiredMixin, TemplateView)` with `template_name = 'events/event_wizard.html'`
  - [x] Override `dispatch()`: guard with `request.user.is_authenticated` before fetching event; fetch `Event.objects.get(slug=kwargs['slug'])` inside a `try/except Event.DoesNotExist: raise Http404`; call `obj.can_edit(request.user)` and raise `UserFacingPermissionDenied(EDIT_DENIED_MESSAGE)` if it returns `False`; store the fetched object as `self.object`; then call `super().dispatch()`
  - [x] Override `get_context_data()`: set `wizard_mode='edit'` and `api_url = f'/events/api/v1/events/{self.object.slug}/'`

- [x] Task 3: Register the edit URL pattern and remove the old update URL from `events/urls.py`
  - [x] Import `EventWizardUpdateView` from `events.views.event_wizard_update`
  - [x] Add `path('<slug:slug>/edit/', EventWizardUpdateView.as_view(), name='event_wizard_update')` **before** the catch-all `<slug:slug>/` event detail pattern
  - [x] Remove the `from events.views.event_update import EventUpdateView` import
  - [x] Remove the `path('<int:pk>/edit/', EventUpdateView.as_view(), name='event_update')` pattern

- [x] Task 4: Remove the old form-based update view and its dependencies
  - [x] Delete `events/views/event_update.py`
  - [x] Delete `events/forms/event.py` (contains only `EventBaseForm` and `EventUpdateForm`, both now unused)
  - [x] Delete `events/templates/events/event_form.html`
  - [x] Delete `events/tests/views/test_event_update.py`
  - [x] Remove `from .event import EventUpdateForm` from `events/forms/__init__.py`

- [x] Task 5: Update templates that linked to `events:event_update`
  - [x] In `events/templates/events/event_detail.html:128`: change `{% url 'events:event_update' event.pk %}` to `{% url 'events:event_wizard_update' event.slug %}`
  - [x] In `users/templates/auth/user_added_events_list.html:42`: change `{% url 'events:event_update' event.pk %}` to `{% url 'events:event_wizard_update' event.slug %}`

- [x] Task 6: Write tests in `events/tests/views/test_event_wizard.py`
  - [x] Import `EDIT_DENIED_MESSAGE` from `events.views.event_wizard_update` and the `EventFactory` from `events.tests.factories`
  - [x] `test_edit_unauthenticated_redirects_to_login` — unauthenticated GET to `events:event_wizard_update` → 302 with `account_login` and `next=<edit_url>` in `response.location`
  - [x] `test_edit_non_editor_receives_403` — authenticated user who is not creator/editor → 403 (use `django_app` with `user=other_user`)
  - [x] `test_edit_403_contains_permission_message` — same scenario; assert `EDIT_DENIED_MESSAGE in response.text` and `any('403.html' in t.name for t in response.templates)`
  - [x] `test_edit_authorized_creator_receives_200` — `event.created_by` requests edit URL → 200 with `event_wizard.html` in templates
  - [x] `test_edit_wizard_template_contains_mount_attributes` — creator request; assert response contains `data-vue-component="event-wizard"`, `data-wizard-mode="edit"`, `data-csrf=`, and `data-api-url=/events/api/v1/events/<slug>/`
  - [x] `test_edit_superuser_can_edit_any_event` — superuser who is not creator → 200
  - [x] `test_edit_nonexistent_event_returns_404` — GET to `/events/nonexistent-slug/edit/` → 404
  - [x] Confirm the old `events:event_update` URL name no longer resolves (i.e. `reverse('events:event_update', args=[event.pk])` raises `NoReverseMatch`) — a single assertion in one of the new tests is sufficient

## Dev Notes

### Architecture references
- Architecture doc: `_bmad-output/planning-artifacts/architecture-event-creation-ux.md` (sections "Authentication & Security", "Project Structure & Boundaries → Django Views")
- Epics doc: `_bmad-output/planning-artifacts/epics-event-creation-ux.md` (Story 4.1-BE)
- Existing create view: `events/views/event_wizard_create.py` — mirror its `dispatch()` pattern

### `UserFacingPermissionDenied` — required to surface message in template

The project has a custom 403 handler in `desparchado/views/errors.py` that only passes the exception message to `403.html` when the exception is `UserFacingPermissionDenied`. A bare `PermissionDenied` logs a warning and renders the template with an empty message. This is why:

- `EventWizardCreateView` uses `UserFacingPermissionDenied(QUOTA_EXCEEDED_MESSAGE)` (not bare `PermissionDenied`)
- `EventWizardUpdateView` must raise `UserFacingPermissionDenied(EDIT_DENIED_MESSAGE)` for the AC to be satisfied

Import: `from desparchado.exceptions import UserFacingPermissionDenied`

The existing `EditorPermissionRequiredMixin.get_object()` raises bare `PermissionDenied` without a message — that mixin was written before `UserFacingPermissionDenied` existed. Do NOT use the mixin's `get_object()` for the edit view's permission check.

### Why `dispatch()` instead of relying on `get_object()`

`EventWizardUpdateView` extends `TemplateView`, which has no `get_object()` lifecycle method. The `EditorPermissionRequiredMixin.get_object()` override is never called automatically by `TemplateView`. The permission check **must** live in `dispatch()` — same architecture as `EventWizardCreateView.dispatch()` for the quota check.

`EditorPermissionRequiredMixin` is still the correct base class: its `LoginRequiredMixin` parent handles the login redirect for unauthenticated users. The mixin's `get_object()` override is harmless dead code in this context.

### `is_authenticated` guard in `dispatch()`

`EventWizardUpdateView.dispatch()` runs before `LoginRequiredMixin.dispatch()` in the MRO. An anonymous user calling `Event.objects.get(slug=...)` is fine, but accessing `request.user.settings` or calling `can_edit()` without an authenticated user raises `AttributeError`. Guard with `if request.user.is_authenticated:` before fetching the event — same pattern as `EventWizardCreateView`.

### `data-api-url` is a temporary manually-constructed path

The architecture requires all API URLs to be pre-reversed by Django views (the frontend never constructs URL paths). Story 4.2-BE will register the `events_api:event_detail` URL pattern. Until then, the URL is constructed with string interpolation:

```python
context['api_url'] = f'/events/api/v1/events/{self.object.slug}/'
```

**When implementing Story 4.2-BE**, replace this with:
```python
context['api_url'] = reverse('events_api:event_detail', args=[self.object.slug])
```

Tests for this story should assert the attribute contains the slug, not the exact `reverse()` output (since the URL pattern does not exist yet).

### Existing URL conflict: `<slug:slug>/edit/` vs `<slug:slug>/`

`events/urls.py` has a catch-all `path('<slug:slug>/', ...)` for event detail. The new `<slug:slug>/edit/` path must be registered **before** it in `urlpatterns` — otherwise Django matches the catch-all first and never reaches the edit pattern. Django evaluates URL patterns top-to-bottom and stops at the first match.

### URL naming

- New URL name: `events:event_wizard_update`
- The old `events:event_update` (PK-based, form-based update) is removed — the wizard is the only edit path

### `EventWizardUpdateView` implementation sketch

```python
# events/views/event_wizard_update.py
import logging

from django.core.exceptions import Http404
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from desparchado.exceptions import UserFacingPermissionDenied
from desparchado.mixins import EditorPermissionRequiredMixin
from events.models import Event

logger = logging.getLogger(__name__)

EDIT_DENIED_MESSAGE = 'No tienes permiso para editar este evento.'


class EventWizardUpdateView(EditorPermissionRequiredMixin, TemplateView):
    template_name = 'events/event_wizard.html'

    def dispatch(
        self, request: HttpRequest, *args: object, **kwargs: object,
    ) -> HttpResponse:
        if request.user.is_authenticated:
            try:
                self.object = Event.objects.get(slug=kwargs['slug'])
            except Event.DoesNotExist:
                raise Http404
            if not self.object.can_edit(request.user):
                logger.warning(
                    'Edit permission denied for user %s on event %s',
                    request.user.pk,
                    self.object.pk,
                )
                raise UserFacingPermissionDenied(EDIT_DENIED_MESSAGE)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context['wizard_mode'] = 'edit'
        context['api_url'] = f'/events/api/v1/events/{self.object.slug}/'
        return context
```

### Test factory notes

```python
# Typical test setup pattern
from events.tests.factories import EventFactory
from users.tests.factories import UserFactory

event = EventFactory()          # created_by is set on the factory
other_user = UserFactory()      # has no relation to event
```

Use `django_app.get(url, user=other_user, status=403)` — the `django_app` fixture is pytest-webtest's `WebTestClient`. For the `?next=` assertion, test against `response.location` after a 302 response.

### Test conventions
- All test functions use `@pytest.mark.django_db`; no `TestCase` classes
- Use `django_app` fixture for view tests (not `client`)
- Use `UserFactory()` and `EventFactory()` — never `Model.objects.create()` directly
- Import `EDIT_DENIED_MESSAGE` from the view module and compare against response text; do not hardcode the string in tests

### Files added, modified, and deleted by this story

**New:**
- `events/views/event_wizard_update.py`

**Modified:**
- `events/templates/events/event_wizard.html` — make `wizard_mode` dynamic
- `events/views/event_wizard_create.py` — add `wizard_mode` to `get_context_data()`
- `events/urls.py` — add new wizard update URL; remove old `event_update` pattern
- `events/forms/__init__.py` — remove `EventUpdateForm` re-export
- `events/templates/events/event_detail.html` — update edit button URL
- `users/templates/auth/user_added_events_list.html` — update edit link URL
- `events/tests/views/test_event_wizard.py` — add 8 new tests

**Deleted:**
- `events/views/event_update.py`
- `events/forms/event.py`
- `events/templates/events/event_form.html`
- `events/tests/views/test_event_update.py`

### `events/forms/event.py` deletion note

`EventBaseForm` and `EventUpdateForm` become fully dead code once `EventUpdateView` is removed:
- `EventBaseForm` has no subclasses other than `EventUpdateForm`
- `EventUpdateForm` is imported only by the deleted view and the old test file
- Delete the whole file; remove its line from `events/forms/__init__.py`

## File List

**New:**
- `events/views/event_wizard_update.py`

**Modified:**
- `events/templates/events/event_wizard.html`
- `events/views/event_wizard_create.py`
- `events/urls.py`
- `events/forms/__init__.py`
- `events/templates/events/event_detail.html`
- `users/templates/auth/user_added_events_list.html`
- `events/tests/views/test_event_wizard.py`

**Deleted:**
- `events/views/event_update.py`
- `events/forms/event.py`
- `events/templates/events/event_form.html`
- `events/tests/views/test_event_update.py`_

## Dev Agent Record

### Implementation Plan

_To be filled in by the implementing agent._

### Completion Notes

All 6 tasks implemented. 315 tests pass, 0 regressions.

Key decisions:
- `Http404` imported from `django.http` (not `django.core.exceptions` as the sketch showed — fixed during implementation)
- `UserFacingPermissionDenied` used instead of bare `PermissionDenied` so the "No tienes permiso..." message is surfaced by the custom 403 handler in `desparchado/views/errors.py`
- `EditorPermissionRequiredMixin` retained as base class for `LoginRequiredMixin` behavior only; permission check lives in `dispatch()` since `TemplateView` never calls `get_object()`
- `api_url` in context uses string interpolation (`f'/events/api/v1/events/{slug}/'`) pending Story 4.2-BE registering the `events_api:event_detail` URL pattern

### Debug Log

_To be filled in by the implementing agent._

### Review Findings

- [x] [Review][Defer] `self.object` unset for unauthenticated requests — latent `AttributeError` in `get_context_data` if `raise_exception=True` ever set on mixin [events/views/event_wizard_update.py:38] — deferred, pre-existing; currently safe because `LoginRequiredMixin` (raise_exception=False) returns redirect before `get_context_data` is called; same pattern as `EventWizardCreateView`
- [x] [Review][Defer] No test for unauthenticated request to nonexistent slug — unauthenticated path skips slug lookup so returns login redirect, not 404; behavior is unspecified in AC [events/tests/views/test_event_wizard.py] — deferred, pre-existing; conventional Django auth-before-content ordering
- [x] [Review][Defer] `test_edit_unauthenticated_redirects_to_login` cannot exercise `get_context_data` — 302 fires before `get()` is called, so the latent `self.object` crash is untestable via this test [events/tests/views/test_event_wizard.py:102] — deferred, pre-existing

## Change Log

- 2026-06-24: Story spec created; status → ready-for-dev
- 2026-06-24: Extended to include removal of old `EventUpdateView`, `event_form.html`, `EventUpdateForm`, and related test file; edit button links in templates updated to new wizard URL
- 2026-06-24: Implementation complete; 315 tests pass; status → review