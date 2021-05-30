import pytest

from .factories import EventFactory


@pytest.fixture
def history_event():
    return EventFactory()
