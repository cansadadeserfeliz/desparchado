import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_home_page(django_app):
    response = django_app.get(reverse('home'), status=200)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
# pylint: disable=too-many-arguments,too-many-positional-arguments
def test_home_page_featured_events(
    django_app,
    not_published_event,
    featured_not_published_event,
    not_approved_event,
    featured_not_approved_event,
    past_event,
    featured_past_event,
    future_event,
    featured_future_event,
):
    response = django_app.get(reverse('home'), status=200)
    assert response.status_code == status.HTTP_200_OK

    assert 'featured_events' in response.context
    assert not_published_event not in response.context['featured_events']
    assert featured_not_published_event not in response.context['featured_events']
    assert not_approved_event not in response.context['featured_events']
    assert featured_not_approved_event not in response.context['featured_events']
    assert past_event not in response.context['featured_events']
    assert featured_past_event not in response.context['featured_events']
    assert featured_future_event in response.context['featured_events']
    assert (
        future_event in response.context['featured_events']
    ), 'because there is not enough featured future events'


def test_about_page(django_app):
    django_app.get(reverse('about'), status=200)


@pytest.mark.django_db
def test_sitemap(django_app, event, place, organizer, speaker, blog_post, special):
    django_app.get(reverse('django.contrib.sitemaps.views.sitemap'), status=200)
