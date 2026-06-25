from rest_framework import serializers

from desparchado.utils import sanitize_html
from events.models import Organizer


class OrganizerReadSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj: Organizer) -> str:
        return obj.get_image_url()

    class Meta:
        model = Organizer
        fields = ['id', 'name', 'image_url']


class OrganizerCreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True

    def validate_description(self, value: str) -> str:
        return sanitize_html(value)

    class Meta:
        model = Organizer
        fields = ['name', 'description', 'image', 'website_url', 'image_source_url']
