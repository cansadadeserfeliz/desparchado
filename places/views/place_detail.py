from django.views.generic import DetailView

from places.models import Place


class PlaceDetailView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
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
