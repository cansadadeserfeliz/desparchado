import pytest
from django.urls import reverse

VIEW_NAME = 'events:organizer_detail'


@pytest.mark.django_db
def test_show_details_of_organizer(django_app, organizer):
    response = django_app.get(
        reverse(VIEW_NAME, args=[organizer.slug]), status=200,
    )
    assert response.context['organizer'] == organizer
    assert organizer.name in response
