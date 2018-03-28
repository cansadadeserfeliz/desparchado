from django.views.generic import ListView, DetailView
from django.utils import timezone

from .models import Place


class PlaceListView(ListView):
    model = Place
    context_object_name = 'places'
    paginate_by = 9


class PlaceDetailView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = \
            self.get_object().events.published().future().all()[:9]
        context['past_events'] = \
            self.get_object().events.published().past().order_by('-event_date').all()[:9]
        return context
