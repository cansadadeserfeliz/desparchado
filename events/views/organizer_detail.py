import logging

from django.views.generic import DetailView

from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerDetailView(DetailView):
    model = Organizer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = (
            self.get_object().events.published()
            .future()
            .select_related('place')[:30]
        )
        context["past_events"] = (
            self.get_object()
            .events.published()
            .past()
            .order_by("-event_date")
            .select_related("place")
            .prefetch_related("speakers")[:30]
        )
        return context
