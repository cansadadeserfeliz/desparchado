import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_home_page(django_app, event):
    response = django_app.get(reverse('home'), status=200)
    assert 'AÑADIR EVENTO' in response

    assert event.title in response


def test_about_page(django_app):
    django_app.get(reverse('about'), status=200)


@pytest.mark.django_db
def test_sitemap(django_app):
    django_app.get(reverse('django.contrib.sitemaps.views.sitemap'), status=200)
