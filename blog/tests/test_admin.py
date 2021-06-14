import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_show_posts_list(django_app, user_admin, blog_post):
    response = django_app.get(
        reverse('admin:blog_post_changelist'),
        user=user_admin,
        status=200
    )
    assert blog_post.title in response
