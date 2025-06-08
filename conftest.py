# pylint: disable=redefined-outer-name
from datetime import timedelta

import pytest
from django.utils import timezone

from blog.tests.factories import PostFactory as BlogPostFactory
from events.tests.factories import EventFactory, OrganizerFactory, SpeakerFactory
from places.tests.factories import CityFactory, PlaceFactory
from specials.tests.factories import SpecialFactory
from users.tests.factories import UserFactory


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
    return EventFactory(title='Unpublished event title', is_published=False)


@pytest.fixture
def featured_not_published_event(not_published_event):
    not_published_event.is_featured_on_homepage = True
    not_published_event.save()

    return not_published_event


@pytest.fixture
def not_approved_event():
    return EventFactory(title='Not approved event title', is_approved=False)


@pytest.fixture
def featured_not_approved_event(not_approved_event):
    not_approved_event.is_featured_on_homepage = True
    not_approved_event.save()

    return not_approved_event


@pytest.fixture
def past_event():
    return EventFactory(event_date=timezone.now() - timedelta(days=1))


@pytest.fixture
def featured_past_event(past_event):
    past_event.is_featured_on_homepage = True
    past_event.save()

    return past_event


@pytest.fixture
def future_event():
    return EventFactory(event_date=timezone.now() + timedelta(days=1))


@pytest.fixture
def featured_future_event(future_event):
    future_event.is_featured_on_homepage = True
    future_event.save()

    return future_event


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
def special(event, not_published_event, not_approved_event):
    return SpecialFactory(
        related_events=[event, not_published_event, not_approved_event],
    )
