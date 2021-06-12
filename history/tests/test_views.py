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

    assert written_post.title in response
    assert mention_post.title in response
    assert not_related_post.title not in response


@pytest.mark.django_db
def test_show_group_detail(django_app, history_group):
    response = django_app.get(
        reverse('history:group_detail', args=(history_group.token,)),
        status=200,
    )
    assert history_group.title in response
