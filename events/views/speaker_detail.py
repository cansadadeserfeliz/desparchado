import logging

from django.views.generic import DetailView

from events.models import Speaker

logger = logging.getLogger(__name__)


class SpeakerDetailView(DetailView):
    model = Speaker

    def get_context_data(self, **kwargs):
        """
        Populate the template context with the speaker and two event querysets: upcoming and past.
        
        Adds the following keys to the returned context dictionary:
        - "events": QuerySet of the speaker's published future events limited to 30 items.
        - "past_events": QuerySet of the speaker's published past events ordered by event_date descending limited to 9 items.
        
        Returns:
            dict: The original context augmented with "events" and "past_events".
        """
        context = super().get_context_data(**kwargs)
        speaker = self.get_object()
        context["events"] = (
            speaker.events.published()
            .future()
            .select_related("place")
            .prefetch_related("speakers")[:30]
        )
        context['past_events'] = (
            speaker.events.published()
            .past()
            .order_by('-event_date')
            .select_related('place')
            .prefetch_related('speakers')
            .all()[:9]
        )
        return context