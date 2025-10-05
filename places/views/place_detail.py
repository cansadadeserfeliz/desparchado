from django.views.generic import DetailView

from places.models import Place


class PlaceDetailView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        """
        Add Place-related event lists to the template context.
        
        Args:
            **kwargs: Additional keyword arguments passed through to the superclass.
        
        Returns:
            dict: The updated context mapping including:
                - "events": up to 15 upcoming published events for this place, optimized with
                  select_related("place") and prefetch_related("speakers"); useful for showing
                  future events and their speakers/organizers associated with the place.
                - "past_events": up to 9 past published events for this place ordered by
                  most recent `event_date`, also optimized with select_related("place") and
                  prefetch_related("speakers"); useful for displaying historical events and
                  their speakers/organizers.
        """
        context = super().get_context_data(**kwargs)
        context["events"] = (
            self.get_object()
            .events.published()
            .future()
            .select_related("place")
            .prefetch_related("speakers")
            .all()[:15]
        )
        context["past_events"] = (
            self.get_object()
            .events.published()
            .past()
            .order_by("-event_date")
            .select_related("place")
            .prefetch_related("speakers")
            .all()[:9]
        )
        return context