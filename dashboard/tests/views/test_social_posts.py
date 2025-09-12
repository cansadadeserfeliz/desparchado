import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_social_posts(django_app, admin_user):
    django_app.get(reverse('dashboard:social_posts'), user=admin_user, status=200)
