# Deferred Work

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