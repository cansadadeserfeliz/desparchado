import logging

from django.views.generic import DetailView

from events.models import Speaker

logger = logging.getLogger(__name__)


class SpeakerDetailView(DetailView):
    model = Speaker

    def get_context_data(self, **kwargs):
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
