import pytest
from django.urls import reverse

VIEW_NAME = 'events:speaker_detail'


@pytest.mark.django_db
def test_successfully_show_details_of_speaker(django_app, speaker):
    response = django_app.get(
        reverse(VIEW_NAME, args=[speaker.slug]), status=200,
    )
    assert response.context['speaker'] == speaker
