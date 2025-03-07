from django.contrib import sitemaps
from django.urls import reverse

from events.models import Event
from events.models import Speaker
from events.models import Organizer
from places.models import Place
from blog.models import Post
from history.models import Post as HistoryPost
from history.models import HistoricalFigure


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 1
    changefreq = 'daily'

    def items(self):
        return [
            'home',
            'about',
            'blog:post_list',
            'events:event_list',
            'events:speaker_list',
            'events:organizer_list',
            'places:place_list',
        ]

    def location(self, item):
        return reverse(item)


class EventSitemap(sitemaps.Sitemap):
    changefreq = 'always'
    priority = 1

    def items(self):
        return Event.objects.published().all()

    def lastmod(self, item):
        return item.modified


class OrganizerSitemap(sitemaps.Sitemap):
    changefreq = 'hourly'
    priority = 1.0

    def items(self):
        return Organizer.objects.all()

    def lastmod(self, item):
        return item.modified


class PlaceSitemap(sitemaps.Sitemap):
    changefreq = 'hourly'
    priority = 0.9

    def items(self):
        return Place.objects.all()

    def lastmod(self, item):
        return item.modified


class PostSitemap(sitemaps.Sitemap):
    changefreq = 'hourly'
    priority = 0.9

    def items(self):
        return Post.objects.all()

    def lastmod(self, item):
        return item.modified


class SpeakerSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Speaker.objects.all()

    def lastmod(self, item):
        return item.modified


class HistoryPostSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    priority = 1

    def items(self):
        return HistoryPost.objects.all()

    def lastmod(self, item):
        return item.modified


class HistoricalFigureSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return HistoricalFigure.objects.all()

    def lastmod(self, item):
        return item.modified


sitemaps = {
    'static': StaticViewSitemap,
    'events': EventSitemap,
    'places': PlaceSitemap,
    'posts': PostSitemap,
    'speakers': SpeakerSitemap,
    'history_posts': HistoryPostSitemap,
    'history_figure': HistoricalFigureSitemap,
}
