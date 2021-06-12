import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_press_article_list(django_app, press_article):
    resource = django_app.get(reverse('news:press_article_list'), status=200)
    assert press_article.title in resource


@pytest.mark.django_db
def test_press_article_detail(django_app, press_article):
    resource = django_app.get(reverse('news:press_article_detail', args=[press_article.slug]), status=200)
    assert press_article.title in resource
