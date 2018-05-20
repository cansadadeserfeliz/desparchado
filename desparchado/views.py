from django.views.generic import TemplateView
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from events.models import Event


class HomeView(TemplateView):
    template_name = 'desparchado/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.published().future().all()[:18]

        context['past_events'] = \
            Event.objects.published().past().order_by('-event_date').all()[:9]
        return context


class RssSiteEventsFeed(Feed):
    title = 'Futuros eventos en desparchado.co'
    link = '/events/'
    description = 'Futuros eventos en desparchado.co'

    def items(self):
        return Event.objects.published().order_by('-event_date')[:10]


class AtomSiteEventsFeed(RssSiteEventsFeed):
    feed_type = Atom1Feed
    subtitle = RssSiteEventsFeed.description
