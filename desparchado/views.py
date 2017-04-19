from django.views.generic import TemplateView
from django.utils import timezone

from events.models import Event


class HomeView(TemplateView):
    template_name = 'desparchado/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(
            is_published=True,
            is_approved=True,
            event_date__gte=timezone.now(),
        ).all()[:12]

        context['past_events'] = Event.objects.filter(
            event_date__lt=timezone.now(),
            is_published=True,
            is_approved=True,
        ).order_by('-event_date').all()[:9]
        return context
