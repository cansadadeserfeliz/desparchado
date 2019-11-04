from django.views.generic import TemplateView
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from django.utils import timezone

from events.models import Event
from events.models import SocialNetworkPost
from blog.models import Post


class HomeView(TemplateView):
    template_name = 'desparchado/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.published().future().order_by('?').all()[:6]
        context['events'] = events
        if events.count() <= 3:
            context['past_events'] = \
                Event.objects.published().past().order_by('-event_date').all()[:6]
        else:
            context['past_events'] = []

        context['blog_posts'] = Post.objects.published().order_by('?').all()[:6]
        return context


class RssSiteEventsFeed(Feed):
    title = 'Eventos en Desparchado.co'
    link = '/events/'
    description = 'Futuros eventos en Desparchado.co'

    def items(self):
        return Event.objects.published().filter(
            event_date__gte=timezone.now(),
        ).order_by('event_date')[:10]


class SocialNetworksRssSiteEventsFeed(Feed):
    title = 'Eventos en Desparchado.co'
    link = '/events/'
    description = 'Futuros eventos en Desparchado.co'

    def item_title(self, item):
        return item.event.title

    def item_guid(self, item):
        return '{}-{}'.format(
            item.event.slug,
            item.id,
        )

    def item_link(self, item):
        return reverse('events:event_detail', args=[item.event.slug])

    def item_guid_is_permalink(self, item):
        return False

    def item_description(self, item):
        return item.description

    def item_author_name(self, item):
        return 'Desparchado.co'

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.published_at

    def items(self):
        return SocialNetworkPost.objects.filter(
            event__is_published=True,
            event__is_approved=True,
            published_at__lte=timezone.now(),
            published_at__gte=timezone.datetime(2019, 2, 27),
        ).select_related('event').order_by('published_at')


class AtomSiteEventsFeed(RssSiteEventsFeed):
    feed_type = Atom1Feed
    subtitle = RssSiteEventsFeed.description
