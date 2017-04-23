from django.contrib import sitemaps
from django.urls import reverse

from events.models import Event


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
       return Event.published.all()

    def lastmod(self, item):
       return item.event_date


sitemaps = {
    'static': StaticViewSitemap,
    'events': EventSitemap,
}
