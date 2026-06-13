from django.db import transaction
from rest_framework import serializers

from desparchado.utils import sanitize_html
from events.models import Event, Organizer, Speaker
from places.models import Place


class EventWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    event_source_url = serializers.URLField(max_length=500)
    event_date = serializers.DateTimeField()
    place_id = serializers.IntegerField(write_only=True)
    organizer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )
    speaker_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        default=list,
    )
    category = serializers.ChoiceField(
        choices=Event.Category.choices,
        required=False,
        allow_blank=True,
        default='',
    )
    price = serializers.DecimalField(
        max_digits=9,
        decimal_places=2,
        required=False,
        default=0,
    )
    is_published = serializers.BooleanField(required=False, default=False)
    image = serializers.ImageField(required=False, allow_null=True, default=None)

    def validate_description(self, value: str) -> str:
        sanitized = sanitize_html(value)
        if not sanitized.strip():
            raise serializers.ValidationError('Este campo es requerido.')
        return sanitized

    def validate_organizer_ids(self, value: list[int]) -> list[int]:
        if not value:
            raise serializers.ValidationError(
                'Debes seleccionar al menos un organizador.',
            )
        existing = set(
            Organizer.objects.filter(pk__in=value).values_list('pk', flat=True),
        )
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(
                f'Organizadores no encontrados: {sorted(missing)}',
            )
        return value

    def validate_place_id(self, value: int) -> int:
        if not Place.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Lugar no encontrado.')
        return value

    def validate_speaker_ids(self, value: list[int]) -> list[int]:
        if not value:
            return value
        existing = set(
            Speaker.objects.filter(pk__in=value).values_list('pk', flat=True),
        )
        missing = set(value) - existing
        if missing:
            raise serializers.ValidationError(
                f'Presentadores no encontrados: {sorted(missing)}',
            )
        return value

    def create(self, validated_data: dict) -> Event:
        organizer_ids = validated_data.pop('organizer_ids')
        speaker_ids = validated_data.pop('speaker_ids')
        place_id = validated_data.pop('place_id')
        image = validated_data.pop('image', None)

        with transaction.atomic():
            event = Event(place_id=place_id, **validated_data)
            if image:
                event.image = image
            event.save()
            event.organizers.set(organizer_ids)
            event.speakers.set(speaker_ids)
        return event
