from django.views.generic import ListView

from places.models import Place


class PlaceListView(ListView):
    model = Place
    context_object_name = 'places'
    paginate_by = 20
    ordering = 'name'
