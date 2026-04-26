---
name: LeafletPointFieldWidget — Google Maps replaced with Leaflet
description: All Google Maps usage replaced with Leaflet.js + OpenStreetMap; custom LeafletPointFieldWidget in places/widgets/leaflet.py
type: project
---

The Google Maps widget and all associated JS files have been replaced with a self-contained Leaflet implementation.

**Why:** Google Maps Dynamic Maps API incurs charges; Leaflet + OSM is free and requires no API key.

**How to apply:** When touching map-related code, use `LeafletPointFieldWidget` from `places/widgets/leaflet.py`. Do not reference `GoogleMapPointFieldWidget`, `GOOGLE_MAPS_API_KEY`, or `django-map-widgets`.

Key facts:
- Widget: `places/widgets/leaflet.py` — `LeafletPointFieldWidget(forms.BaseGeometryWidget)`
- JS picker: `places/static/places/js/leaflet-picker.js` — self-contained, no jQuery dependency
- Template: `places/templates/places/widgets/leaflet/interactive.html`
- Address search: Photon geocoding API (`https://photon.komoot.io/api/`), Colombia bbox, no key
- Stub tombstone files still exist on disk and should be deleted manually:
  `places/widgets/googlemap.py`, `places/static/places/js/mw_init.js`,
  `places/static/places/js/mw_pointfield_base.js`, `places/static/places/js/mw_pointfield.js`,
  `places/templates/places/widgets/googlemap/interactive.html`
- `GOOGLE_MAPS_API_KEY` removed from settings (`base.py`) and context processor
- `MAP_WIDGETS` in `base.py` now only has the `"Mapbox"` key
- CSS font/image assets (`places/static/places/font/fontello.*`, `places/static/places/images/ripple.gif`) were already present from the prior extraction
