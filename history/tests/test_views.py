import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_show_home_view(django_app):
    django_app.get(reverse('history:home'), status=200)
