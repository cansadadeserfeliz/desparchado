from datetime import timedelta

import pytest

from django.utils import timezone

from users.tests.factories import UserFactory
from events.tests.factories import EventFactory
from books.tests.factories import BookFactory


@pytest.fixture
def user():
    return UserFactory(
        is_superuser=False,
        is_staff=False,
        is_active=True,
    )


@pytest.fixture
def event():
    return EventFactory()


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
