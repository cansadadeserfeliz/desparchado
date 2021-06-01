import pytest

from .factories import EventFactory, HistoricalFigureFactory


@pytest.fixture
def history_event():
    return EventFactory()


@pytest.fixture
def history_historical_figure():
    return HistoricalFigureFactory()
