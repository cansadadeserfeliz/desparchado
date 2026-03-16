---
name: GoogleMapPointFieldWidget local extraction
description: Self-contained GoogleMapPointFieldWidget extracted from django-map-widgets v0.5.1 into places app; mapwidgets package no longer used for this widget
type: project
---

## What was done

The `GoogleMapPointFieldWidget` was extracted from `django-map-widgets` v0.5.1 into a local, self-contained implementation inside the `places` app. The `mapwidgets` package is no longer imported in `places/forms.py` or `places/admin.py`.

## File structure created

- `places/widgets/__init__.py` — exports `GoogleMapPointFieldWidget`
- `places/widgets/googlemap.py` — the widget class (no mapwidgets imports)
- `places/static/places/js/mw_init.js` — verbatim copy from mapwidgets v0.5.1
- `places/static/places/js/mw_pointfield_base.js` — verbatim copy (base JS class)
- `places/static/places/js/mw_pointfield.js` — verbatim copy (Google Maps JS class)
- `places/static/places/css/map_widgets.css` — verbatim copy; references `../font/fontello.*` and `../images/ripple.gif` (those font/image files are NOT copied — still served from the mapwidgets package or must be copied separately)
- `places/templates/places/widgets/googlemap/interactive.html` — adapted from upstream; uses `{{ widget_id }}` instead of `{{ id }}`

## Key design decisions in googlemap.py

- Extends `django.contrib.gis.forms.BaseGeometryWidget` to get PointField serialization for free
- Configuration read from `settings.MAP_WIDGETS["GoogleMap"]` (existing project config) with `settings.GOOGLE_MAPS_API_KEY` as fallback for the API key
- Template context adds `widget_id`, `name`, `serialized`, `options` (JSON), `field_value` (JSON)
- `options` JSON contains `mapOptions`, `mapCenterLocationName`, `markerFitZoom`, `GooglePlaceAutocompleteOptions` — matching what the upstream JS widget expects
- Google Maps CDN URL built in `_google_map_js_url` property; loaded as a plain `<script>` src in the `Media` class

## Note on font/image assets

The CSS references:
- `../font/fontello.*` (5 font files: eot, woff2, woff, ttf, svg)
- `../images/ripple.gif` (loader animation)

These are NOT yet copied into `places/static/places/`. They are still referenced from the mapwidgets package path. To fully remove the mapwidgets dependency for static assets, copy:
- `mapwidgets/static/mapwidgets/font/fontello.*` → `places/static/places/font/`
- `mapwidgets/static/mapwidgets/images/ripple.gif` → `places/static/places/images/`
