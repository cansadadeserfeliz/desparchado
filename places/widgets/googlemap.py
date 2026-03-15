# Adapted from django-map-widgets v0.5.1 (https://github.com/erdem/django-map-widgets)
# Reason: google.maps.places.Autocomplete is deprecated for new customers as of
# March 2025, and the library had no immediate plan to migrate. The widget was
# extracted and rewritten
# as a self-contained local class to own the migration path.
# Changes applied:
#   - Rewritten as a standalone Django widget with no imports from mapwidgets.
#   - Configuration is read directly from settings.MAP_WIDGETS["GoogleMap"].
#   - Google Maps CDN URL is built at runtime from settings (no mw_settings dependency).
import json
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.gis import forms
from django.contrib.gis.geos import GEOSGeometry

# Default map options used when MAP_WIDGETS settings are absent or incomplete.
_DEFAULT_MAP_OPTIONS: dict = {
    "zoom": 5,
    "scrollwheel": False,
    "streetViewControl": True,
}

_DEFAULT_CDN_PARAMS: dict = {
    "callback": "googleMapWidgetsCallback",
    "language": "es",
    "libraries": "places,marker",
    "loading": "async",
    "v": "quarterly",
}

_DEFAULT_AUTOCOMPLETE_OPTIONS: dict = {}


def _get_google_map_settings() -> dict:
    """Read GoogleMap configuration from Django settings.

    Returns:
        A dict with keys ``api_key``, ``map_options``,
        ``cdn_url_params``, ``autocomplete_options``, and
        ``map_center_location_name``.
    """
    map_widgets_conf: dict = getattr(settings, "MAP_WIDGETS", {})
    google_conf: dict = map_widgets_conf.get("GoogleMap", {})
    point_field_conf: dict = google_conf.get("PointField", {}).get("interactive", {})

    api_key: str = (google_conf.get("apiKey")
                    or getattr(settings, "GOOGLE_MAPS_API_KEY", ""))

    cdn_params: dict = {**_DEFAULT_CDN_PARAMS}
    cdn_params.update(google_conf.get("CDNURLParams", {}))
    cdn_params["callback"] = "googleMapWidgetsCallback"

    map_options: dict = {**_DEFAULT_MAP_OPTIONS}
    map_options.update(point_field_conf.get("mapOptions", {}))

    autocomplete_options: dict = {**_DEFAULT_AUTOCOMPLETE_OPTIONS}
    autocomplete_options.update(
        point_field_conf.get("GooglePlaceAutocompleteOptions", {}),
    )

    return {
        "api_key": api_key,
        "map_options": map_options,
        "cdn_url_params": cdn_params,
        "autocomplete_options": autocomplete_options,
        "map_center_location_name": point_field_conf.get("mapCenterLocationName", ""),
        "marker_fit_zoom": point_field_conf.get("markerFitZoom", None),
    }


class GoogleMapPointFieldWidget(forms.BaseGeometryWidget):
    """Self-contained Google Maps widget for a PostGIS PointField.

    Renders an interactive map that lets the user place a single point
    marker. The selected coordinates are serialised as a GeoJSON Point
    string and stored in the hidden textarea that Django's
    ``PointField`` reads during form submission.

    Configuration is read from ``settings.MAP_WIDGETS["GoogleMap"]``
    (the project-wide map-widgets config) and from
    ``settings.GOOGLE_MAPS_API_KEY`` as a fallback for the API key.
    """

    template_name = "places/widgets/googlemap/interactive.html"
    map_srid = 4326

    @property
    def _google_map_js_url(self) -> str:
        config = _get_google_map_settings()
        api_key: str = config["api_key"]
        if not api_key:
            raise ValueError(
                "Google Maps API key is not set. "
                "Configure MAP_WIDGETS['GoogleMap']['apiKey'] or "
                "GOOGLE_MAPS_API_KEY in settings.",
            )
        cdn_params = {"key": api_key, **config["cdn_url_params"]}
        return f"https://maps.googleapis.com/maps/api/js?{urlencode(cdn_params)}"

    @property
    def media(self) -> forms.Media:
        return forms.Media(
            css={"all": ["places/css/map_widgets.css"]},
            js=[
                "places/js/mw_init.js",
                "places/js/mw_pointfield_base.js",
                "places/js/mw_pointfield.js",
                self._google_map_js_url,
            ],
        )

    def _geos_to_dict(self, geom: GEOSGeometry) -> dict | None:
        """Decompose a GEOSGeometry point into a plain dict for the template.

        Args:
            geom: A GEOSGeometry instance representing a Point.

        Returns:
            A dict with ``srid``, ``wkt``, ``coords``, ``geom_type``,
            ``lng``, and ``lat`` keys, or ``None`` if *geom* is falsy.
        """
        if not geom:
            return None

        longitude, latitude = geom.coords
        return {
            "srid": geom.srid,
            "wkt": str(geom),
            "coords": geom.coords,
            "geom_type": geom.geom_type,
            "lng": longitude,
            "lat": latitude,
        }

    def get_context(self, name: str, value, attrs: dict | None) -> dict:
        context = super().get_context(name, value, attrs)

        serialized: str = context.get("serialized", "") or ""
        field_value: dict | None = None
        if serialized:
            field_value = self._geos_to_dict(self.deserialize(serialized))

        config = _get_google_map_settings()
        widget_options: dict = {
            "mapOptions": config["map_options"],
            "mapCenterLocationName": config["map_center_location_name"],
            "markerFitZoom": config["marker_fit_zoom"],
            "GooglePlaceAutocompleteOptions": config["autocomplete_options"],
        }

        # widget_id is the HTML id attribute for the hidden textarea; the
        # template uses it to build the jQuery selector the JS widget reads.
        widget_attrs: dict = context.get("widget", {}).get("attrs", {})
        widget_id: str = widget_attrs.get("id", f"id_{name}")

        context.update(
            {
                "name": name,
                "widget_id": widget_id,
                "serialized": serialized,
                "options": json.dumps(widget_options),
                "field_value": json.dumps(field_value),
            },
        )
        return context
