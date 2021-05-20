import pytest

from users.tests.factories import UserFactory


@pytest.fixture
def user():
    return UserFactory(
        is_superuser=False,
        is_staff=False,
        is_active=True,
    )
