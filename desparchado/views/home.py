from django.views.generic import TemplateView

from events.models import Event
from blog.models import Post


class HomeView(TemplateView):
    template_name = 'desparchado/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        future_events_limit = 18
        past_events_limit = 18
        blog_posts_limit = 6

        events = Event.objects.published().future()

        featured_events = events.filter(is_featured_on_homepage=True).order_by('?').all()[:future_events_limit]
        featured_events_count = featured_events.count()

        if featured_events_count < future_events_limit:
            featured_events |= events.filter(is_featured_on_homepage=False).order_by('?').all()[:future_events_limit - featured_events_count]

        context['events'] = featured_events
        if events.count() <= 6:
            context['past_events'] = \
                Event.objects.published().past().order_by('-event_date').all()[:past_events_limit]
        else:
            context['past_events'] = []

        context['blog_posts'] = Post.objects.published().order_by('?').all()[:blog_posts_limit]
        return context
