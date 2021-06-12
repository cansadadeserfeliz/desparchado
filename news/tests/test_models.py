import pytest


@pytest.mark.django_db
@pytest.mark.parametrize('source_url', [
    'http://youtu.be/SA2iWivDJiE',
    'http://www.youtube.com/watch?v=SA2iWivDJiE&feature=feedu',
    'http://www.youtube.com/embed/SA2iWivDJiE',
    'http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US',
])
def test_get_press_article_youtube_video_id(press_article, source_url):
    press_article.source_url = source_url
    press_article.save()

    assert press_article.get_youtube_video_id() == 'SA2iWivDJiE'


@pytest.mark.django_db
def test_get_press_article_youtube_video_id_broken_youtube_url(press_article):
    press_article.source_url = 'http://www.youtube.com/XXX'
    press_article.save()

    assert press_article.get_youtube_video_id() is None


@pytest.mark.django_db
def test_get_press_article_youtube_video_id_non_youtube_url(press_article):
    press_article.source_url = 'http://example.com'
    press_article.save()

    assert press_article.get_youtube_video_id() is None
