import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_show_home_view(django_app):
    django_app.get(reverse('history:index'), status=200)


@pytest.mark.django_db
def test_show_historical_figure_list(django_app, history_historical_figure, history_historical_figure_without_image):
    response = django_app.get(reverse('history:historical_figure_list'), status=200)
    assert history_historical_figure.name in response
    assert history_historical_figure_without_image.name in response


@pytest.mark.django_db
def test_show_event_list(django_app, history_event):
    response = django_app.get(reverse('history:event_list'), status=200)
    assert history_event.title in response


@pytest.mark.django_db
def test_show_event_detail(django_app, history_event):
    response = django_app.get(reverse('history:event_detail', kwargs={'token': history_event.token}), status=200)
    assert history_event.title in response
    assert history_event.description in response
    # assert history_event.event_date in response
