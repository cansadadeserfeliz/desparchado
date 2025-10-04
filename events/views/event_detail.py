import logging

from django.views.generic import DetailView

from events.models import Event

logger = logging.getLogger(__name__)


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'

    def get_queryset(self):
        """
        Return a queryset of published Event objects with the related `place` prefetched via select_related.
        
        The queryset is restricted to events marked as published and includes the `place` relation to avoid extra database queries when accessing an event's place.
        
        Returns:
            QuerySet[Event]: A queryset of published Event instances with `place` selected.
        """
        return (
            Event.objects.published()
            .select_related(
                'place',
            )
            .all()
        )

    def get_context_data(self, **kwargs):
        """
        Augment the template context for the event detail view with related events, organizers, and speakers.
        
        Adds the following keys to the returned context:
        - `related_events`: a queryset of up to three published future events (excluding the current event) with their `place` relation selected, ordered randomly.
        - `organizers`: a list of Organizer instances related to the current event.
        - `speakers`: a list of Speaker instances related to the current event.
        
        Returns:
            dict: The context mapping for the template, including the added keys above.
        """
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