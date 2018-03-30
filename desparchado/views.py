from django.views.generic import TemplateView

from events.models import Event


class HomeView(TemplateView):
    template_name = 'desparchado/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.published().future().all()[:18]

        context['past_events'] = \
            Event.objects.published().past().order_by('-event_date').all()[:9]
        return context
