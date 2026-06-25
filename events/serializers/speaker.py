from rest_framework import serializers

from desparchado.utils import sanitize_html
from events.models import Speaker


class SpeakerReadSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj: Speaker) -> str:
        return obj.get_image_url()

    class Meta:
        model = Speaker
        fields = ['id', 'name', 'image_url']


class SpeakerCreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True

    def validate_description(self, value: str) -> str:
        return sanitize_html(value)

    class Meta:
        model = Speaker
        fields = ['name', 'description', 'image', 'image_source_url']
