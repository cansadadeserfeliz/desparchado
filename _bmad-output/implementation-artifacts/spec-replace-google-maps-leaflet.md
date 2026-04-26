---
title: 'Replace Google Maps with Leaflet + OpenStreetMap'
type: 'refactor'
created: '2026-04-25'
status: 'done'
baseline_commit: '0d5ba837f49c6bd3a077d7b58774407b0d4525fb'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** All maps use the Google Maps JavaScript API, incurring Dynamic Maps charges ($7/1,000 loads) on every public page. Three JS files and the `places/widgets/googlemap.py` module are copies extracted from `django-map-widgets`; docs and `CLAUDE.md` still reference that library and `GoogleMapPointFieldWidget`. The whole stack needs a clean replacement.

**Approach:** Replace every Google Maps touchpoint with Leaflet.js + OpenStreetMap tiles (free, no key). Write a self-contained `leaflet-picker.js` (no django-map-widgets inheritance) replacing all three copied JS files. Update all docs to match.

## Boundaries & Constraints

**Always:**
- Leaflet loaded via CDN (unpkg, v1.9.4) — no npm/Vite bundling
- Address search restricts to Colombia (`bbox=-81.7,-4.2,-66.9,12.5` on Photon API)
- Widget serializes location as GeoJSON Point string into the hidden textarea — unchanged contract for Django's `PointField`
- `leaflet-picker.js` must be self-contained: no inheritance from deleted base class files

**Never:**
- Do not use Mapbox (requires API key); leave `MAP_WIDGETS["Mapbox"]` block untouched
- Do not change the GeoJSON wire format consumed by Django's `PointField`
- Do not add Leaflet as an npm dependency

</frozen-after-approval>

## Code Map

**Delete entirely:**
- `places/widgets/googlemap.py` — `GoogleMapPointFieldWidget`; all django-map-widgets extraction comments
- `places/static/places/js/mw_init.js` — extracted from django-map-widgets; jQuery + `$.Class.extend` bootstrap
- `places/static/places/js/mw_pointfield_base.js` — extracted from django-map-widgets; base widget class
- `places/static/places/js/mw_pointfield.js` — extracted from django-map-widgets; Google Maps implementation
- `places/templates/places/widgets/googlemap/` — entire directory (interactive.html template)

**Create:**
- `places/widgets/leaflet.py` — new `LeafletPointFieldWidget`
- `places/templates/places/widgets/leaflet/interactive.html` — new picker template
- `places/static/places/js/leaflet-picker.js` — self-contained Leaflet picker; replaces all 3 deleted JS files

**Modify:**
- `places/widgets/__init__.py` — swap export
- `places/admin.py` — update import + `formfield_overrides`
- `places/forms.py` — update import + `Meta.widgets`
- `places/static/places/css/map_widgets.css` — add Photon results dropdown styles
- `desparchado/templates/includes/_map.html` — replace gmp-map with Leaflet
- `events/templates/events/event_detail.html` — remove Google script; replace `<gmp-map>` block
- `dashboard/templates/dashboard/index.html` — replace Google Maps script + JS block
- `dashboard/templates/dashboard/places.html` — same
- `desparchado/settings/base.py` — remove `GOOGLE_MAPS_API_KEY` + `MAP_WIDGETS["GoogleMap"]` + `MAP_WIDGETS["Leaflet"]` (django-map-widgets config, no longer needed)
- `desparchado/template/context_processors.py` — remove `GOOGLE_MAPS_API_KEY`
- `CLAUDE.md` — update Map Widget section (line ~133) to describe `LeafletPointFieldWidget`
- `docs/development-guide.md` — remove `GOOGLE_MAPS_API_KEY` env var row
- `docs/architecture.md` — update map widget paragraph (currently says "via django-map-widgets")
- `docs/technology-stack.md` — update/remove `django-map-widgets` row
- `docs/source-tree.md` — fix `places/widgets/` entry (currently says `googlemap.py — LeafletPointFieldWidget wrapper`)
- `_bmad-output/project-context.md` — update `GoogleMapPointFieldWidget` references (lines ~29-30, ~225)

## Tasks & Acceptance

**Execution:**
- [x] `places/widgets/leaflet.py` — create `LeafletPointFieldWidget(forms.BaseGeometryWidget)`: `template_name = "places/widgets/leaflet/interactive.html"`; `media` serves Leaflet CSS CDN, Leaflet JS CDN, `map_widgets.css`, `leaflet-picker.js`; `get_context` passes `field_value` JSON (lat/lng from saved point or null) and `options` JSON (`{zoom:5, center:[4.65,-74.08], markerFitZoom:15}`)
- [x] `places/static/places/js/leaflet-picker.js` — self-contained IIFE accepting `(mapId, djangoInputId, fieldValue, options)`: initializes `L.map()` + OSM tile layer; if `fieldValue` is set places a draggable `L.marker`; "mark on map" button toggles click-to-place mode; "my location" uses `navigator.geolocation`; coordinates overlay inputs directly update marker; delete button removes marker; address search: debounced fetch to Photon API, renders `<ul class="mw-photon-results">` dropdown beneath the input, on item click places marker and closes list; on any marker change, serializes `{type:"Point", coordinates:[lng,lat]}` to the hidden textarea
- [x] `places/templates/places/widgets/leaflet/interactive.html` — HTML chrome matching current googlemap template (toolbar buttons, coordinate overlay, address input, map div, hidden textarea); inline `<script>` calls `initLeafletPicker(mapId, djangoInputId, fieldValue, options)` — no mapWidgets globals needed
- [x] `places/static/places/css/map_widgets.css` — add `.mw-photon-results` (absolute, z-index 1000, white bg, border, li items with hover); keep existing widget chrome styles; remove any Google-specific rules
- [x] `places/widgets/__init__.py` — `from .leaflet import LeafletPointFieldWidget`; `__all__ = ["LeafletPointFieldWidget"]`
- [x] `places/admin.py` — import `LeafletPointFieldWidget`; update `formfield_overrides` in `PlaceAdmin` and `CityAdmin`
- [x] `places/forms.py` — import `LeafletPointFieldWidget`; update `PlaceForm.Meta.widgets`
- [x] `desparchado/templates/includes/_map.html` — replace entire file: load Leaflet CSS + JS from CDN; `<div id="map-{{ css_class|slugify }}">` with fixed height; inline script: `L.map(id).setView([lat,lng],15)` + OSM tiles + `L.marker([lat,lng]).bindPopup(title).addTo(map)`
- [x] `events/templates/events/event_detail.html` — remove Google Maps `<script>` from `{% block extra_scripts %}`; replace `<gmp-map>` block with same Leaflet pattern (CDN load + `L.map` init using `event.get_latitude_str`/`event.get_longitude_str`)
- [x] `dashboard/templates/dashboard/index.html` — replace Google Maps CDN script + `google.maps.*` JS: load Leaflet CDN, `L.map()` + OSM tiles, loop `locations[]` creating `L.marker().bindPopup(title)`, collect into bounds array, `map.fitBounds()`
- [x] `dashboard/templates/dashboard/places.html` — same replacement for places map
- [x] `desparchado/settings/base.py` — remove `GOOGLE_MAPS_API_KEY = getenvvar(...)` line; remove `MAP_WIDGETS["GoogleMap"]` block; remove `MAP_WIDGETS["Leaflet"]` block
- [x] `desparchado/template/context_processors.py` — remove `"GOOGLE_MAPS_API_KEY"` entry
- [x] Delete: `places/widgets/googlemap.py`, `places/static/places/js/mw_init.js`, `places/static/places/js/mw_pointfield_base.js`, `places/static/places/js/mw_pointfield.js`, `places/templates/places/widgets/googlemap/` directory
- [x] `CLAUDE.md` — replace Map Widget paragraph with: "The location `PointField` on Place and City uses `LeafletPointFieldWidget` (custom widget in `places/widgets/leaflet.py`) with Leaflet.js and OpenStreetMap tiles. Address search uses the Photon geocoding API (no API key required)."
- [x] `docs/development-guide.md` — remove the `GOOGLE_MAPS_API_KEY` row from the environment variables table
- [x] `docs/architecture.md` — update map widget sentence to remove "django-map-widgets" reference; reflect custom `LeafletPointFieldWidget`
- [x] `docs/technology-stack.md` — update or remove `django-map-widgets` row
- [x] `docs/source-tree.md` — update `places/widgets/` entry: rename `googlemap.py` → `leaflet.py` with correct description
- [x] `_bmad-output/project-context.md` — replace `GoogleMapPointFieldWidget` / `settings.MAP_WIDGETS["GoogleMap"]` / `GOOGLE_MAPS_API_KEY` references with the new `LeafletPointFieldWidget` description

**Acceptance Criteria:**
- Given a visitor on an event detail page, when the page loads, then a Leaflet map with OSM tiles and a marker renders; no request goes to maps.googleapis.com
- Given a visitor on a place detail page, when the page loads, then the same Leaflet map renders
- Given a superuser editing a Place in Django admin, when the form loads, then a Leaflet map renders with saved location; typing in the address box returns Photon suggestions; selecting one places a draggable marker; saving persists the point
- Given a superuser on the dashboard, when the page loads, then a Leaflet multi-marker map renders and clicking a marker shows a popup with the name
- Given any page on the site, no `maps.googleapis.com` network request is made
- Given the codebase, no file contains `google.maps`, `GoogleMapPointFieldWidget`, `django-map-widgets`, `mw_init`, `mw_pointfield_base`, or `GOOGLE_MAPS_API_KEY`

## Verification

**Commands:**
- `docker exec -it desparchado-web-1 sh -c "cd app && pytest places/ -x -q"` — expected: all green
- `docker exec -it desparchado-web-1 sh -c "cd app && ruff check places/ desparchado/ dashboard/ events/"` — expected: no errors
- `grep -r "google.maps\|GOOGLE_MAPS\|GoogleMapPointFieldWidget\|django-map-widgets\|mw_init\|mw_pointfield_base" .` — expected: no matches

**Manual checks:**
- `/events/<slug>/`: Leaflet map visible, no googleapis requests in DevTools
- `/admin/places/place/add/`: Leaflet picker renders; address search returns Photon suggestions; marker draggable; form saves
- `/dashboard/`: event map with markers and popups renders

## Suggested Review Order

**Widget core — new Leaflet picker**

- Entry point: `LeafletPointFieldWidget` class; `media` property and `get_context` are the full API surface.
  [`leaflet.py:7`](../../places/widgets/leaflet.py#L7)

- Self-contained JS picker: `initLeafletPicker` — map init, marker lifecycle, address search, GeoJSON serialization.
  [`leaflet-picker.js:17`](../../places/static/places/js/leaflet-picker.js#L17)

- Photon geocoding with AbortController: debounced fetch, in-flight cancellation, Colombia bbox.
  [`leaflet-picker.js:196`](../../places/static/places/js/leaflet-picker.js#L196)

- Widget template: HTML chrome + inline init script using `window.load` to guarantee scripts loaded.
  [`interactive.html:51`](../../places/templates/places/widgets/leaflet/interactive.html#L51)

- Photon dropdown CSS: `position: relative` on input wrapper ensures correct dropdown placement.
  [`map_widgets.css:743`](../../places/static/places/css/map_widgets.css#L743)

**Public read-only maps**

- Single-marker reusable include for place detail; `{{ title|escapejs }}` XSS fix applied.
  [`_map.html:1`](../../desparchado/templates/includes/_map.html#L1)

- Inline Leaflet map replacing `<gmp-map>` on event detail; loads CDN once per page.
  [`event_detail.html:247`](../../events/templates/events/event_detail.html#L247)

**Dashboard maps**

- Multi-marker map with `L.featureGroup().fitBounds()` replacing `google.maps.LatLngBounds`.
  [`index.html:68`](../../dashboard/templates/dashboard/index.html#L68)

- Same pattern for places map; `|escapejs` applied to place names.
  [`places.html:50`](../../dashboard/templates/dashboard/places.html#L50)

**Consumer wiring**

- `PlaceAdmin` and `CityAdmin`: `formfield_overrides` swap to `LeafletPointFieldWidget`.
  [`admin.py:4`](../../places/admin.py#L4)

- `PlaceForm.Meta.widgets`: same swap for the public place form.
  [`forms.py:4`](../../places/forms.py#L4)

**Cleanup**

- `GOOGLE_MAPS_API_KEY` and `MAP_WIDGETS["GoogleMap"/"Leaflet"]` blocks removed.
  [`base.py:264`](../../desparchado/settings/base.py#L264)

- Context processor no longer exposes `GOOGLE_MAPS_API_KEY` to all templates.
  [`context_processors.py:3`](../../desparchado/template/context_processors.py#L3)

- Stale `"gmp-map"` visual-regression selector removed from backstop config.
  [`backstop.config.js:100`](../../backstop.config.js#L100)
