from rest_framework import serializers

from places.models import Place


class PlaceSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name']
