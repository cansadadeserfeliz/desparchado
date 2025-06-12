# ruff: noqa: S311
import random
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.tests.factories import EventFactory, OrganizerFactory, SpeakerFactory
from places.tests.factories import CityFactory, PlaceFactory
from users.tests.factories import UserFactory


class Command(BaseCommand):
    help = "Generate random event data for local environment"

    def handle(self, *args, **options):
        user = UserFactory(username='test')

        city_bogota = CityFactory(
            name='Bogotá',
            center_location=Point(-74.083655, 4.653411),
        )
        city_cali = CityFactory(
            name='Cali',
            center_location=Point(-76.5812127, 3.410844),
        )
        city_cartagena = CityFactory(
            name='Cartagena',
            center_location=Point(-75.51554870, 10.404008865),
        )

        place_bogota = PlaceFactory(
            name='Biblioteca Virgilio Barco',
            city=city_bogota,
            created_by=user,
        )
        place_cali = PlaceFactory(
            name="Biblioteca Virgilio Barco",
            city=city_cali,
            created_by=user,
        )
        place_cartagena = PlaceFactory(
            name="Cinemateca La Tertulia",
            city=city_cartagena,
            created_by=user,
        )
        places = [place_bogota, place_cali, place_cartagena]

        organizer_1 = OrganizerFactory(name='Banco de la República', created_by=user)
        organizer_2 = OrganizerFactory(name='Compensar', created_by=user)
        organizer_3 = OrganizerFactory(name='MUSA Museo Arqueológico', created_by=user)
        organizers = [organizer_1, organizer_2, organizer_3]

        speaker_1 = SpeakerFactory(name='Mario Mendoza', created_by=user)
        speaker_2 = SpeakerFactory(name='Javier Cassiani', created_by=user)
        speaker_3 = SpeakerFactory(name='Florence Thomas', created_by=user)
        speakers = [speaker_1, speaker_2, speaker_3]

        def _create_random_event(event_date):
            event = EventFactory(
                event_date=event_date,
                is_featured_on_homepage=True,
                place=random.choice(places),
                organizers=random.sample(organizers, random.randint(1, 3)),
                speakers=random.sample(speakers, random.randint(0, 3)),
                created_by=user,
            )

        # Future events
        _create_random_event(
            event_date=timezone.now() + timedelta(days=random.randint(1, 90)))
        _create_random_event(
            event_date=timezone.now() + timedelta(days=random.randint(1, 90)))
        # Past event
        _create_random_event(
            event_date=timezone.now() - timedelta(days=random.randint(1, 90)))

        self.stdout.write(
            self.style.SUCCESS('Successfully created random event data'),
        )
