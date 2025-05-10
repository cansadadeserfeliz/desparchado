from django.utils.formats import date_format
from django.utils import timezone
from django.template.defaultfilters import truncatewords_html
from rest_framework import serializers

from events.models import Event
from places.models import Place

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = [
            'name',
            'slug',
        ]


class EventSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    url = serializers.SerializerMethodField()
    formatted_hour = serializers.SerializerMethodField()
    formatted_day = serializers.SerializerMethodField()
    is_recurrent = serializers.SerializerMethodField()
    truncated_description = serializers.SerializerMethodField()

    def get_formatted_hour(self, obj):
        return date_format(obj.event_date, 'H:i')

    def get_formatted_day(self, obj):
        return date_format(obj.event_date, 'j M')

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_is_recurrent(self, obj):
        return False

    def get_truncated_description(self, obj):
        return truncatewords_html(obj.description, 50)

    class Meta:
        model = Event
        fields = [
            'title',
            'slug',
            'url',
            'event_date',
            'formatted_hour',
            'formatted_day',
            'place',
            'image_url',
            'description',
            'truncated_description',
            'is_recurrent',
        ]
