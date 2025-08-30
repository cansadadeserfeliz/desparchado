from django.views.generic import TemplateView

from events.models import Event


class HomeView(TemplateView):
    template_name = 'desparchado/home.html'
    featured_events_limit = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        future_events = Event.objects.published().future()

        featured_events = (
            future_events.filter(
                is_featured_on_homepage=True,
            )
            .order_by('?')
            .all()[: self.featured_events_limit]
        )
        featured_events_count = featured_events.count()

        # If there are not enough featured events,
        # choose random future events
        if featured_events_count < self.featured_events_limit:
            featured_events |= (
                future_events.filter(is_featured_on_homepage=False)
                .order_by('?')
                .all()[: self.featured_events_limit - featured_events_count]
            )

        context['featured_events'] = featured_events.select_related('place')
        return context
