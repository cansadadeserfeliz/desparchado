import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_show_home_view(django_app):
    django_app.get(reverse('history:index'), status=200)


@pytest.mark.django_db
def test_show_historical_figure_list(django_app):
    django_app.get(reverse('history:historical_figure_list'), status=200)
