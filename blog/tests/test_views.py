import pytest

from django.urls import reverse

from .factories import PostFactory


@pytest.mark.django_db
def test_posts_appear_in_list(django_app):
    first_post = PostFactory()
    second_post = PostFactory()
    not_published_post = PostFactory(is_published=False)
    not_approved_post = PostFactory(is_approved=False)

    response = django_app.get(reverse('blog:post_list'), status=200)

    assert len(response.context['posts']) == 2
    assert first_post in response.context['posts']
    assert second_post in response.context['posts']
    assert not_published_post not in response.context['posts']
    assert not_approved_post not in response.context['posts']


@pytest.mark.django_db
def test_show_post_detail(django_app, blog_post):
    django_app.get(reverse('blog:post_detail', args=[blog_post.slug]), status=200)


@pytest.mark.django_db
def test_don_not_show_not_published_post_detail(django_app, blog_post):
    blog_post.is_published = False
    blog_post.save()
    django_app.get(reverse('blog:post_detail', args=[blog_post.slug]), status=404)


@pytest.mark.django_db
def test_don_not_show_not_approved_post_detail(django_app, blog_post):
    blog_post.is_approved = False
    blog_post.save()
    django_app.get(reverse('blog:post_detail', args=[blog_post.slug]), status=404)
