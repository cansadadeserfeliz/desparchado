from django.views.generic import TemplateView
from django.utils import timezone

from events.models import Event


class HomeView(TemplateView):
    template_name = 'desparchado/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.published.filter(
            event_date__gte=timezone.now(),
        ).all()[:12]

        context['past_events'] = Event.published.filter(
            event_date__lt=timezone.now(),
        ).order_by('-event_date').all()[:9]
        return context
