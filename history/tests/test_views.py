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
def test_show_historical_figure_detail(django_app, history_historical_figure):
    response = django_app.get(
        reverse('history:historical_figure_detail', args=(history_historical_figure.token,)),
        status=200,
    )
    assert history_historical_figure.name in response
