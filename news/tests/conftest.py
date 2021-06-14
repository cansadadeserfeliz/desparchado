import pytest

from .factories import MediaSourceFactory
from .factories import PressArticleFactory


@pytest.fixture
def media_source():
    return MediaSourceFactory()


@pytest.fixture
def press_article():
    return PressArticleFactory()
