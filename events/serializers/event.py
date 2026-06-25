from django.db import transaction
from django.template.defaultfilters import truncatewords_html
from django.utils import timezone
from django.utils.formats import date_format
from rest_framework import serializers

from desparchado.utils import sanitize_html
from events.models import Event, Organizer, Speaker
from events.serializers.organizer import OrganizerReadSerializer
from events.serializers.speaker import SpeakerReadSerializer
from places.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = [
            'name',
            'slug',
        ]


class PlaceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'city_id']


class EventDetailSerializer(serializers.ModelSerializer):
    organizers = OrganizerReadSerializer(many=True, read_only=True)
    speakers = SpeakerReadSerializer(many=True, read_only=True)
    place = PlaceReadSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj: Event) -> str:
        return obj.get_image_url()

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'image_url',
            'event_date',
            'category',
            'price',
            'event_source_url',
            'is_published',
            'organizers',
            'speakers',
            'place',
        ]


class EventListSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    url = serializers.SerializerMethodField()
    formatted_hour = serializers.SerializerMethodField()
    formatted_day = serializers.SerializerMethodField()
    is_recurrent = serializers.SerializerMethodField()
    truncated_description = serializers.SerializerMethodField()

    def get_formatted_hour(self, obj: Event) -> str:
        return date_format(timezone.localtime(obj.event_date), 'H:i')

    def get_formatted_day(self, obj: Event) -> str:
        return date_format(timezone.localtime(obj.event_date), 'j M')

    def get_url(self, obj: Event) -> str:
        return obj.get_absolute_url()

    def get_is_recurrent(self, obj: Event) -> bool:  # pylint: disable=unused-argument
        return False

    def get_truncated_description(self, obj: Event) -> str:
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

    def update(self, instance: Event, validated_data: dict) -> Event:
        organizer_ids = validated_data.pop('organizer_ids', None)
        speaker_ids = validated_data.pop('speaker_ids', None)
        place_id = validated_data.pop('place_id', None)
        update_image = 'image' in validated_data
        image = validated_data.pop('image', None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            if place_id is not None:
                instance.place_id = place_id
            if update_image:
                instance.image = image
            instance.save()
            if organizer_ids is not None:
                instance.organizers.set(organizer_ids)
            if speaker_ids is not None:
                instance.speakers.set(speaker_ids)
        return instance

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
