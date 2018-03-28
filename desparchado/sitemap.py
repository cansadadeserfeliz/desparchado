from django.contrib import sitemaps
from django.urls import reverse

from events.models import Event
from places.models import Place


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return ['home', 'about']

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


sitemaps = {
    'static': StaticViewSitemap,
    'events': EventSitemap,
    'places': PlaceSitemap,
}
