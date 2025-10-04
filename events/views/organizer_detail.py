import logging

from django.views.generic import DetailView

from events.models import Organizer

logger = logging.getLogger(__name__)


class OrganizerDetailView(DetailView):
    model = Organizer

    def get_context_data(self, **kwargs):
        """
        Add the organizer's upcoming and past published events to the template context.
        
        The returned context is the base context augmented with:
        - 'events': up to 30 published future events for the organizer with related 'place' selected.
        - 'past_events': up to 30 published past events for the organizer, ordered by descending event_date, with related 'place' selected and 'speakers' prefetched.
        
        Returns:
            dict: Template context including the added 'events' and 'past_events' querysets.
        """
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