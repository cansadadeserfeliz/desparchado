from datetime import timedelta

import pytest

from django.utils import timezone

from users.tests.factories import UserFactory
from events.tests.factories import EventFactory
from events.tests.factories import OrganizerFactory
from events.tests.factories import SpeakerFactory
from places.tests.factories import PlaceFactory
from places.tests.factories import CityFactory
from blog.tests.factories import PostFactory as BlogPostFactory
from specials.tests.factories import SpecialFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def other_user():
    return UserFactory()


@pytest.fixture
def user_admin():
    return UserFactory(
        is_staff=True,
        is_superuser=True,
    )


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
def place():
    return PlaceFactory()


@pytest.fixture
def speaker():
    return SpeakerFactory()


@pytest.fixture
def city():
    return CityFactory()


@pytest.fixture
def blog_post():
    return BlogPostFactory()


@pytest.fixture
def special(event):
    return SpecialFactory(related_events=[event])
