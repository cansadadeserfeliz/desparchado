from django.contrib.gis.geos import Point
from rest_framework import serializers

from places.models import Place


class PlaceSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name']


class PlaceCreateSerializer(serializers.ModelSerializer):
    # Bounding box for Colombia; rejects coordinates clearly outside the country.
    lat = serializers.FloatField(write_only=True, min_value=-4.23, max_value=12.45)
    lng = serializers.FloatField(write_only=True, min_value=-79.02, max_value=-66.87)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].required = True

    def create(self, validated_data: dict) -> Place:
        lat = validated_data.pop('lat')
        lng = validated_data.pop('lng')
        # Point(x=lng, y=lat) — PostGIS convention
        validated_data['location'] = Point(lng, lat)
        return super().create(validated_data)

    class Meta:
        model = Place
        fields = [
            'name',
            'address',
            'city',
            'image',
            'website_url',
            'image_source_url',
            'lat',
            'lng',
        ]
