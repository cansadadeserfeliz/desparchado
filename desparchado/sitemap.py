from django.contrib import sitemaps
from django.urls import reverse

from events.models import Event
from events.models import Speaker
from places.models import Place
from blog.models import Post


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.7
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
    changefreq = 'daily'
    priority = 1

    def items(self):
        return Event.objects.published().all()

    def lastmod(self, item):
        return item.event_date


class PlaceSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Place.objects.all()

    def lastmod(self, item):
        return item.created


class PostSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Post.objects.all()

    def lastmod(self, item):
        return item.created


class SpeakerSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Speaker.objects.all()

    def lastmod(self, item):
        return item.created

sitemaps = {
    'static': StaticViewSitemap,
    'events': EventSitemap,
    'places': PlaceSitemap,
    'posts': PostSitemap,
    'speakers': SpeakerSitemap,
}
