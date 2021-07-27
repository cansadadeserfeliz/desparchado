import pytest

from django.urls import reverse

from .factories import PostFactory


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
    written_post = PostFactory(historical_figure=history_historical_figure)
    mention_post = PostFactory()
    mention_post.historical_figure_mentions.add(history_historical_figure)
    not_related_post = PostFactory()

    response = django_app.get(
        reverse('history:historical_figure_detail', args=(history_historical_figure.token,)),
        status=200,
    )
    assert history_historical_figure.name in response

    assert str(written_post.token) in response
    assert str(mention_post.token) in response
    assert str(not_related_post.token) not in response


@pytest.mark.django_db
def test_show_post_detail(django_app, history_post):
    response = django_app.get(
        reverse('history:post_detail', args=(history_post.token,)),
        status=200,
    )
    assert history_post.historical_figure.name in response


@pytest.mark.django_db
def test_show_group_detail(django_app, history_group):
    response = django_app.get(
        reverse('history:group_detail', args=(history_group.token,)),
        status=200,
    )
    assert history_group.title in response


@pytest.mark.django_db
def test_show_event_list(django_app, history_event):
    response = django_app.get(reverse('history:event_list'), status=200)
    assert history_event.title in response


@pytest.mark.django_db
def test_show_event_detail(django_app, history_event):
    response = django_app.get(reverse('history:event_detail', kwargs={'token': history_event.token}), status=200)
    assert history_event.title in response
    assert history_event.description in response


@pytest.mark.django_db
def test_show_post_preloaded_list(django_app, history_post):
    response = django_app.get(reverse('history:index'), status=200)
    assert history_post.historical_figure.name in response


@pytest.mark.django_db
def test_posts_api_retrieve_page(django_app, history_post_batch):
    response = django_app.get(reverse('history:api_post_list'), params={'page': 2},  status=200)
    assert 'application/json' == response.content_type


@pytest.mark.django_db
def test_posts_api_response_without_query_parameter(django_app, history_post_batch):
    django_app.get(reverse('history:api_post_list'),  status=422)


@pytest.mark.django_db
def test_posts_api_response_when_page_number_is_not_integer(django_app, history_post_batch):
    django_app.get(reverse('history:api_post_list'), params={'page': 'xdxdxd'}, status=422)


@pytest.mark.django_db
def test_posts_api_response_with_empty_page(django_app, history_post):
    """
    This test verifies response status code 400 when a request to an empty page is made.
    In this case only exists a page with one post, history_post, then test ask for a non existent page number 2
    """
    django_app.get(reverse('history:api_post_list'), params={'page': 2}, status=400)
