import pytest

from .factories import HuntingOfSnarkGameFactory
from .factories import HuntingOfSnarkCriteriaFactory


@pytest.fixture
def hunting_of_snark_game():
    return HuntingOfSnarkGameFactory()


@pytest.fixture
def hunting_of_snark_criteria_batch():
    return HuntingOfSnarkCriteriaFactory.create_batch(50)
