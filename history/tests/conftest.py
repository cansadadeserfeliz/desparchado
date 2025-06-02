import pytest

from .factories import EventFactory, GroupFactory, HistoricalFigureFactory, PostFactory


@pytest.fixture
def history_event():
    return EventFactory()


@pytest.fixture
def history_historical_figure():
    return HistoricalFigureFactory()


@pytest.fixture
def history_historical_figure_without_image():
    historical_figure = HistoricalFigureFactory()
    historical_figure.image = None
    return historical_figure


@pytest.fixture
def history_post():
    return PostFactory()


@pytest.fixture
def history_group():
    return GroupFactory()


@pytest.fixture
def history_post_batch():
    return PostFactory.create_batch(21)
