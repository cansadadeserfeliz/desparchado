from rest_framework import serializers

from events.models import Speaker


class SpeakerSearchSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj: Speaker) -> str:
        return obj.get_image_url()

    class Meta:
        model = Speaker
        fields = ['id', 'name', 'image_url']
