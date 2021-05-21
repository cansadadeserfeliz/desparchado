from datetime import timedelta

import pytest

from django.utils import timezone

from users.tests.factories import UserFactory
from events.tests.factories import EventFactory
from events.tests.factories import OrganizerFactory
from events.tests.factories import SpeakerFactory
from books.tests.factories import BookFactory
from places.tests.factories import PlaceFactory
from places.tests.factories import CityFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def other_user():
    return UserFactory()


@pytest.fixture
def organizer():
    return OrganizerFactory()


@pytest.fixture
def event():
    return EventFactory()


@pytest.fixture
def event_with_organizer(event, organizer):
    event.organizers.add(organizer)
    return event


@pytest.fixture
def other_event():
    return EventFactory()


@pytest.fixture
def not_published_event():
    return EventFactory(is_published=False)


@pytest.fixture
def not_approved_event():
    return EventFactory(is_approved=False)


@pytest.fixture
def past_event():
    return EventFactory(
        event_date=timezone.now() - timedelta(days=1)
    )


@pytest.fixture
def book(event):
    return BookFactory(related_events=[event])


@pytest.fixture
def other_event_book(other_event):
    return BookFactory(related_events=[other_event])


@pytest.fixture
def place():
    return PlaceFactory()


@pytest.fixture
def speaker():
    return SpeakerFactory()


@pytest.fixture
def city():
    return CityFactory()
