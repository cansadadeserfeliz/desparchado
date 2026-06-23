from rest_framework import serializers

from events.models import Organizer


class OrganizerSearchSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj: Organizer) -> str:
        return obj.get_image_url()

    class Meta:
        model = Organizer
        fields = ['id', 'name', 'image_url']
