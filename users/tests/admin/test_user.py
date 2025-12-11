import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_successfully_get_user_list(client, admin_user):
    client.force_login(admin_user)

    response = client.get(reverse('admin:auth_user_changelist'))
    assert response.status_code == status.HTTP_200_OK
