from django.views.generic import DetailView
from django.utils.timezone import localtime

from .models import Special
from events.models import Speaker


class SpecialDetailView(DetailView):
    model = Special

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_events = self.object.events.order_by('event_date').all()
        speaker_ids = related_events.values_list('speakers__id', flat=True)
        context['speakers'] = Speaker.objects.filter(
            id__in=speaker_ids,
        ).exclude(image='').all()

        related_events_by_date = dict()
        for event in related_events:
            related_events_by_date.setdefault(
                localtime(event.event_date).date(),
                []
            ).append(event)

        context['related_events_by_date'] = related_events_by_date
        return context
