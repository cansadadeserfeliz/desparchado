from django.views.generic import DetailView

from .models import Special
from events.models import Speaker


class SpecialDetailView(DetailView):
    model = Special

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_events = self.object.events.all()
        speaker_ids = related_events.values_list('speakers__id', flat=True)
        context['speakers'] = Speaker.objects.filter(
            id__in=speaker_ids,
        ).exclude(image='').all()
        context['related_events'] = related_events
        return context
