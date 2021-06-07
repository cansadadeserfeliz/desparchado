import pytest

from .factories import EventFactory, HistoricalFigureFactory, PostFactory


@pytest.fixture
def history_event():
    return EventFactory()


@pytest.fixture
def history_historical_figure():
    return HistoricalFigureFactory()


@pytest.fixture
def history_historical_figure_without_image():
    history_historical_figure = HistoricalFigureFactory()
    history_historical_figure.image = None
    return history_historical_figure


@pytest.fixture
def history_post():
    return PostFactory()
