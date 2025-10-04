import logging

from django.views.generic import DetailView

from events.models import Event

logger = logging.getLogger(__name__)


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'

    def get_queryset(self):
        return (
            Event.objects.published()
            .select_related(
                'place',
            )
            .all()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_events'] = (
            Event.objects.exclude(id=self.object.id)
            .published()
            .future()
            .select_related('place')
            .order_by('?')[:3]
        )
        context['organizers'] = list(self.object.organizers.all())
        context['speakers'] = list(self.object.speakers.all())
        return context
