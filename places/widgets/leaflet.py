import json

from django.contrib.gis import forms
from django.contrib.gis.geos import GEOSGeometry


class LeafletPointFieldWidget(forms.BaseGeometryWidget):
    """Self-contained Leaflet widget for a PostGIS PointField.

    Renders an interactive map that lets the user place a single point
    marker using Leaflet.js and OpenStreetMap tiles. The selected
    coordinates are serialised as a GeoJSON Point string and stored in
    the hidden textarea that Django's ``PointField`` reads during form
    submission.

    Address search is provided by the Photon geocoding API (no API key
    required, Colombia bounding box applied).
    """

    template_name = "places/widgets/leaflet/interactive.html"
    map_srid = 4326

    @property
    def media(self) -> forms.Media:
        return forms.Media(
            css={
                "all": [
                    "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
                    "places/css/map_widgets.css",
                ],
            },
            js=[
                "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
                "places/js/leaflet-picker.js",
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

    def get_context(
        self, name: str, value: str | GEOSGeometry | None, attrs: dict | None,
    ) -> dict:
        context = super().get_context(name, value, attrs)

        serialized: str = context.get("serialized", "") or ""
        field_value: dict | None = None
        if serialized:
            field_value = self._geos_to_dict(self.deserialize(serialized))

        options: dict = {
            "zoom": 5,
            "center": [4.65, -74.08],
            "markerFitZoom": 15,
        }

        widget_attrs: dict = context.get("widget", {}).get("attrs", {})
        widget_id: str = widget_attrs.get("id", f"id_{name}")

        context.update(
            {
                "name": name,
                "widget_id": widget_id,
                "serialized": serialized,
                "options": json.dumps(options),
                "field_value": json.dumps(field_value),
            },
        )
        return context
