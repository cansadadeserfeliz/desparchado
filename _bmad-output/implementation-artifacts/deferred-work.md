# Deferred Work

## Deferred from: code review of 4-2-be-rest-api-get-hydration-patch-update-endpoints (2026-06-24)

- **Image cannot be cleared via PATCH** — `if image is not None` guard in `EventWriteSerializer.update()` means sending `image=null` silently preserves the existing image; no way to remove an image through this endpoint. Address when image-clearing is a product requirement.
- **Response URL may become stale if post_save changes the slug** — `get_absolute_url()` is called on the in-memory instance after `save()`; if a signal or override mutates the slug during save, the returned URL could immediately 404. Low probability given `AutoSlugField(always_update=False)`; monitor if slug mutation logic is ever added.
- **`organizer_ids=[]` raises 400 but `speaker_ids=[]` silently clears all speakers** — pre-existing asymmetry in `EventWriteSerializer` field validation: `validate_organizer_ids` rejects empty lists but `validate_speaker_ids` does not; a PATCH with `speaker_ids=[]` wipes the speaker list while a PATCH with `organizer_ids=[]` returns 400. Surfaced by the new `update()` method. Normalise both validators when the product decides whether clearing is allowed.
- **`IntegrityError` from `instance.save()` not caught as 400** — a DB unique-constraint violation inside `EventWriteSerializer.update()` (e.g. slug collision on concurrent saves) raises `IntegrityError` which bubbles up as a 500 with no structured error body. Low probability given `AutoSlugField(always_update=False)`; add `try/except IntegrityError` → `ValidationError` if slug mutation is ever added.
- **`image_url` field returns site-relative path for default image but potentially absolute URL for S3-backed uploads** — `Event.get_image_url()` returns `/static/images/default_event_image.jpg` (relative) when no image is set and `storage.url(...)` (absolute in production) otherwise. Frontend must handle both forms. Normalise to always return an absolute URL if consistent behaviour is needed.

## Deferred from: code review of 4-1-be-django-edit-view-permission-gate (2026-06-24)

- **`self.object` unset for unauthenticated requests — latent `AttributeError` in `get_context_data`** — `EventWizardUpdateView.dispatch` only sets `self.object` inside `if request.user.is_authenticated`. Currently safe because `LoginRequiredMixin` (raise_exception=False) redirects before `get_context_data` is called. Would crash if `raise_exception=True` were ever set on the mixin. Same pattern as `EventWizardCreateView`. Monitor if mixin ever gains `raise_exception = True`.
- **No test for unauthenticated + nonexistent slug** — unauthenticated path skips slug lookup entirely, so the response is a login redirect rather than 404. Behavior is unspecified by the AC (which only specifies 404 without regard to auth state). Conventional Django ordering (auth check before content check) makes the redirect correct. Test if the AC is ever tightened.
- **`test_edit_unauthenticated_redirects_to_login` cannot cover the latent `self.object` crash** — redirect fires before `get_context_data` is invoked, making the crash path untestable via standard request cycle. Accept as a known test gap while the latent crash remains deferred.

## Deferred from: code review of 3-1-be-drf-quota-permission-classes (2026-06-24)

- **`RelatedObjectDoesNotExist` when UserSettings row is missing** — `request.user.settings` raises on users created before the auto-create signal; spec explicitly says do not guard; same pre-existing risk as `EventWizardCreateView`. Monitor production logs for the error.
- **Race condition: quota check and `perform_create` are non-atomic** — two concurrent POSTs at the quota boundary can both pass; no `select_for_update` or DB-level enforcement; pre-existing pattern across the entire project quota system.
- **`quota_period_seconds = 0` silently bypasses quota enforcement** — `timedelta(seconds=0)` makes the window instantaneous, so count always returns 0; pre-existing issue in `UserSettings` model; add a validation or guard in `UserSettings.save()` if this is a real risk.
- **No boundary test at `count == quota`** — all quota tests use `quota=0` (immediate exhaustion); an off-by-one in `reached_*_quota()` (`>` vs `>=`) would pass all current tests; proper tests belong in `users/tests/test_models.py`.
- **Superuser bypass in `reached_*_quota()` untested in isolation** — bypass logic verified only indirectly through permission classes; dedicated model-level tests belong in `users/tests/test_models.py`.

## Deferred from: code review of 2-2-be-inline-creation-endpoints-write-serializers-for-related-entities (2026-06-23)

- **Quota enforcement not implemented** — explicitly deferred to Story 3.1-BE; `OrganizerCreateAPIView`, `SpeakerCreateAPIView`, and `PlaceCreateAPIView` have no quota `permission_classes`.
- **Three view classes share identical `create()` override** — copy-paste of `validate → perform_create → return {id, name}`; premature abstraction per project conventions; Story 3.1-BE will add per-entity quota classes that differentiate them.
- **`sanitize_html()` returning empty string for `description` is untested** — when all tags are stripped, `''` is stored silently; model default is `''` so this is acceptable behavior, but the edge case is undocumented in tests.
- **`UserSettings` may not exist for legacy users** — `request.user.settings` access raises `RelatedObjectDoesNotExist` for users created before the signal was added; pre-existing architectural concern; latent risk for whoever adds quota enforcement to these views.

## Deferred from: code review of 2-1-be-autocomplete-fuzzy-search-services-endpoints (2026-06-22)

- **limit not exposed from API** — services accept `limit` but all three views hardcode the default (10). Not required by spec. Potential future enhancement to expose as a `?limit=` query parameter.

## Deferred from: code review of 1-2-be-event-api-create-endpoint (2026-06-13)

See `1-2-be-event-api-create-endpoint` (Review Findings) for deferred items.

## Deferred from: code review of 1-1-be-django-routing-views-quota (2026-06-06)

- **Wizard renders empty `<div>`** — Vue component not yet registered; expected, Story 1.3-FE adds `EventWizard.vue`.
- **`data-api-url` resolves to GET-only `EventListAPIView`** — expected, Story 1.2-BE upgrades it to `ListCreateAPIView`.
- **Missing `UserSettings` crashes with `RelatedObjectDoesNotExist`** — pre-existing risk from signal-based creation; add a guard if `RelatedObjectDoesNotExist` errors appear in production logs.
- **No test for real quota count path** — the zero-quota trick bypasses the DB count; a proper unit test belongs in `users/tests/test_models.py` covering `reached_event_creation_quota()` with actual created events.
- **`is_approved=True` and `send_notification()` removed** — the deleted `EventCreateView.form_valid()` auto-approved events and sent admin notifications; Story 1.2-BE must explicitly re-implement both on the API create endpoint.
- **POST integration test deleted** — `test_successfully_create_event` verified DB row creation, `created_by`, category, and redirect; Story 1.2-BE should add equivalent API-level creation tests.
- **`app_name = 'events'` in `events/api_urls.py` mismatches instance namespace `events_api`** — explicit `reverse('events_api:...')` calls still resolve correctly but the mismatch is a code smell; fix by setting `app_name = 'events_api'` in `events/api_urls.py`.

## Special detail: pagination drops search query when date + search are combined

**Source:** Review of `spec-special-detail-unified-filters`
**Finding:** `pagination_query_params` is built from `selected_dates` and `target_audience_filter_value` only. When both a text search (`q`) and date chips are active simultaneously (currently mutually exclusive in the view, but may change), paginating would drop the search term.
**Action if needed:** Include `q` in `pagination_query_params` if search and date filtering are ever made combinable.

## Special detail: arbitrary `fecha` values pollute pagination params

**Source:** Review of `spec-special-detail-unified-filters`
**Finding:** A user-supplied `fecha` value that is a valid date but not in `event_dates` is parsed and included in `pagination_query_params`. It produces no visible chip but persists across pagination links. Low severity since it doesn't affect displayed results.
**Action if needed:** Filter `selected_dates` against `event_dates` before building `param_pairs`.

## Static error pages: 500.html Vite asset fragility during server errors

**Source:** Review of `spec-static-pages-new-design`
**Finding:** `500.html` uses `{% load django_vite %}` and `{% vite_asset %}`, as does `base.html` which it extends. If the Vite manifest is unavailable when a 500 error occurs (e.g. corrupt build artifact), template rendering will itself fail, causing Django to return a bare HTML-less 500 response. This is a pre-existing risk introduced by the existing `base.html` Vite usage and was not worsened by this story, but it is worth addressing.
**Action if needed:** Consider making `500.html` self-contained (no template inheritance, inline critical CSS) to guarantee it always renders, even if the build pipeline is broken.

## Maps: NULL location crashes public pages and dashboard

**Source:** Review of `spec-replace-google-maps-leaflet`
**Finding:** `Place.get_latitude_str()` and `get_longitude_str()` call `self.location.x/y` unconditionally. If a Place has `location=None` (possible via raw DB ops or migration edge cases), loading the event detail, place detail, or dashboard pages will raise `AttributeError` and return a 500. The DB `null=False` constraint makes this unlikely in normal usage. Pre-existing issue, not introduced by the Leaflet migration.
**Action if needed:** Add `{% if place.location %}` guards in `place_detail.html`, `event_detail.html`, and the dashboard querysets; add a null check in `get_latitude_str`/`get_longitude_str`.

## Maps: Dashboard queryset unbounded — full event/place list in HTML

**Source:** Review of `spec-replace-google-maps-leaflet`
**Finding:** `HomeView` passes the full `Event.objects.published().future()` queryset to the dashboard map. On large datasets this renders thousands of coordinates into the HTML response. Pre-existing issue, shared with the old Google Maps implementation.
**Action if needed:** Limit the queryset to a reasonable cap (e.g. 500) or paginate the map markers via an API endpoint.

## Maps: 3D PostGIS Point breaks `LeafletPointFieldWidget._geos_to_dict`

**Source:** Review of `spec-replace-google-maps-leaflet`
**Finding:** `longitude, latitude = geom.coords` assumes a 2D point (2-tuple). A 3D point (XYZ) stored in PostGIS returns a 3-tuple and raises `ValueError: too many values to unpack`. The same pattern existed in the deleted `googlemap.py`. No 3D points are currently stored, but the method has no guard.
**Action if needed:** Change to `longitude, latitude = geom.coords[0], geom.coords[1]`.

## Maps: `LeafletPointFieldWidget` breaks for dynamically added admin inlines

**Source:** Review of `spec-replace-google-maps-leaflet`
**Finding:** `initLeafletPicker` is triggered by `window.load` in the widget template. Dynamically added inline rows (via Django admin's "add another" mechanism) clone the HTML but the `load` event has already fired, so the picker never initialises in the cloned row. Place is not currently used as an admin inline, so this is not a current bug.
**Action if needed:** If Place is ever added as an inline, wire `initLeafletPicker` to Django admin's `formset:added` jQuery event and pass the new row's element IDs.

## Social sharing: hard-coded `https://desparchado.co` prefix in `og:image` / `twitter:image`

**Source:** Review of `spec-social-sharing-link-previews`
**Finding:** All `og:image` and `twitter:image` tags across the site use a hard-coded `https://desparchado.co` prefix rather than `{{ request.scheme }}://{{ request.get_host }}`. This breaks previews in development and staging environments. Pre-existing pattern not introduced by this story.
**Action if needed:** Replace the hard-coded prefix with `{{ request.scheme }}://{{ request.get_host }}` in all affected templates.

## Social sharing: `Special.get_image_url()` crashes when image is null

**Source:** Review of `spec-social-sharing-link-previews`
**Finding:** `Special.get_image_url()` calls `self.image.url` without checking if `self.image` is null (field is `null=True, blank=True`). If a Special has no image, the `og:image` and `twitter:image` tags will raise `AttributeError`. Pre-existing bug, not introduced by this story.
**Action if needed:** Add a null guard to `Special.get_image_url()` consistent with how other models (Event, Organizer, etc.) handle it.

## Social sharing: history `post_detail.html` accesses nullable `post.historical_figure`

**Source:** Review of `spec-social-sharing-link-previews`
**Finding:** `post.historical_figure` is `null=True, blank=True` on the model, but the template uses `{{ post.historical_figure.name }}` without a null guard in both the `<title>` block and the meta tags. Will raise `AttributeError` if a Post has no associated figure. Pre-existing issue.
**Action if needed:** Wrap accesses in `{% if post.historical_figure %}` or provide a fallback title.

## Social sharing: `{{ game.game }}` renders empty — `HuntingOfSnarkGame` has no `game` attribute

**Source:** Review of `spec-social-sharing-link-previews`
**Finding:** `hunting_of_snark_detail.html` uses `{{ game.game }}` in `og:title`, but the model has no `game` field; it has a `name` property. Django silently renders an empty string. Pre-existing issue in the template.
**Action if needed:** Replace `{{ game.game }}` with the correct property (`{{ game.name }}` or similar).

## Multi-value target_audience cells in FILBo sync

**Source:** Review of `feature/filbo-target-audience` (spec-event-target-audience)
**Finding:** Column F in the FILBo spreadsheet could theoretically contain comma- or semicolon-separated values (e.g. `age_6_12,age_13_27`). The current implementation treats the entire cell as a single lookup key, which would log a warning and store `''`. The `target_audience` field is a single `CharField`, so storing multiple audiences would require a structural change (M2M or ArrayField).
**Action if needed:** Confirm with FILBo data whether multi-value cells actually occur; if so, decide on storage strategy before implementing.

## Deferred from: code review of 1-3-fe-vite-entry-root-state-multi-step-skeleton-layout (2026-06-27)

- **Dead Code and Unused API Helpers / Props** — `useEntitySearch.ts`, `organizers.ts`, `places.ts`, and `speakers.ts` are created but never imported or used. `csrf` is accepted as a prop in `EventWizard.vue` but never used. These are prepared skeleton files/props for future stories but they were removed from story.
- **Standard <textarea> Used Instead of Quill Editor** — The specification requires Quill for rich text (bold, italic, underline), but the implementation uses a standard <textarea> in Step1.vue. Quill implementation will be done at story 1.4.
- **Missing Image Upload Field in Step 1** — Step 1 lacks any file input, drag-and-drop container, or file upload logic. A new story 1.3b will be created for the image component.
- **Missing Mobile Live Preview Modal** — FR5 requires a "Ver vista previa" button opening an overlay/modal on viewports < 768px. Currently, the preview is always rendered inline. A new story 1.3c will be created for the mobile preview.

## Deferred from: code review of 1-3-fe-vite-entry-root-state-multi-step-skeleton-layout.md (2026-06-28)

- **Form controls lack <form> wrapper, bypassing native Enter submit and browser validations** — Bypasses Enter key form submission and native HTML5 constraint validations.
- **Tightly coupled and uncached get_cities_json database query in Django views** — `get_cities_json` in `event_wizard_create.py` is imported directly by `event_wizard_update.py`, causing tight coupling and synchronously executing query without caching.

## Deferred from: code review of 1-4-fe-step-1-ui-real-time-card-preview.md (2026-06-30)

- **URL Sanitizer Bypassed via Uppercase Schemes** — URL scheme verification does not normalize scheme strings to lowercase, allowing scheme verification bypass using uppercase schemes (e.g. `javascript:` bypasses via `JavaScript:` or similar if not normalized). Pre-existing issue in `desparchado/frontend/scripts/utils/sanitize.ts:39-44`.
- **Hardcoded Stacking Context Magic Numbers** — Arbitrary `z-index` values (`99`, `1000`, `1010`) are hardcoded across stylesheets (`EventWizard/styles.scss:924`, `Overlay/styles.scss:254`) instead of using centralized variables.