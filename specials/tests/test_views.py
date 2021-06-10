import pytest

from django.urls import reverse

from events.tests.factories import EventFactory
from .factories import SpecialFactory


@pytest.mark.django_db
def test_successfully_show_special(django_app, special):
    response = django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        status=200
    )
    assert response.context['special'] == special


@pytest.mark.django_db
def test_does_not_show_not_published_event(django_app, special):
    special.is_published = False
    special.save()

    django_app.get(
        reverse('specials:special_detail', args=[special.slug]),
        status=404
    )
