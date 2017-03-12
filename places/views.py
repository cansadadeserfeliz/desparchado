from django.views.generic import ListView, DetailView

from .models import Place


class PlaceListView(ListView):
    model = Place
    context_object_name = 'places'
    paginate_by = 9


class PlaceDetailView(DetailView):
    model = Place

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.get_object().event_set.filter(
            is_published=True,
        ).all()[:9]
        return context
