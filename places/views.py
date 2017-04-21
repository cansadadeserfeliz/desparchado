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
        context['events'] = self.get_object().events(manager='published').filter(
            event_date__gte=timezone.now(),
        ).all()[:9]
        context['past_events'] = self.get_object().events(manager='published').filter(
            event_date__lt=timezone.now(),
        ).order_by('-event_date').all()[:9]
        return context
