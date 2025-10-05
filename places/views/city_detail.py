from django.views.generic import DetailView

from events.models import Event
from places.models import City


class CityDetailView(DetailView):
    model = City

    def get_context_data(self, **kwargs):
        """
        Provide template context for the city detail page containing upcoming and past events
        associated with the city's places.
        
        The context will include:
        - 'events': a queryset of up to 9 published future events linked to places in this city.
        - 'past_events': a queryset of published past events linked to places in this city,
          limited to 9 when 'events' contains 3 or fewer items, otherwise limited to 3.
        
        Returns:
            dict: Template context containing the 'events' and 'past_events' querysets.
        """
        context = super().get_context_data(**kwargs)

        events = (
            Event.objects.published()
            .filter(
                place__city=self.object,
            )
            .future()
            .select_related("place")
            .all()[:9]
        )
        context['events'] = events

        if events.count() <= 3:
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