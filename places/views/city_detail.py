from django.views.generic import DetailView

from events.models import Event
from places.models import City


class CityDetailView(DetailView):
    model = City

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events = list(
            Event.objects.published()
            .filter(
                place__city=self.object,
            )
            .future()
            .select_related("place")
            .all()[:9]
        )
        context['events'] = events

        if len(events) <= 3:
            past_events_limit = 9
        else:
            past_events_limit = 3

        context["past_events"] = (
            Event.objects.published()
            .filter(
                place__city=self.object,
            )
            .past()
            .order_by("-event_date")
            .select_related("place")
            .all()[:past_events_limit]
        )

        return context
