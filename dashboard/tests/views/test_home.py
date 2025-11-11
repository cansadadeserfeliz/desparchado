import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home(django_app, admin_user):
    response = django_app.get(reverse('dashboard:home'), user=admin_user, status=200)
    assert 'future_events_count' in response.context
